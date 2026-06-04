"""
Endpoints CRUD para el módulo de ticketing TKT.
Ruta: /tkt-solicitud-derecho/
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timezone
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho, EstadoTicket, PrioridadTicket, OrigenTicket
from app.models.tkt_nota import TktNota
from app.models.tkt_adjunto import TktAdjunto
from app.models.tkt_historial import TktHistorial
from app.models.company import Company
from app.services.user_company_service import get_empresas_usuario
from app.services.ticket_service import (
    crear_ticket_desde_solicitud,
    cambiar_estado_ticket,
    get_dashboard_stats,
    calcular_dias_restantes,
    get_sla_color,
)
from app.core.limiter import limiter
import logging

router = APIRouter(prefix="/tkt-solicitud-derecho", tags=["TKT - Solicitudes ARCO"])
logger = logging.getLogger(__name__)


class TktCreate(BaseModel):
    company_id: int
    tipo: str
    titular_nombre: str
    titular_email: EmailStr
    titular_rut: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: str = "normal"
    origen: str = "web"

    @field_validator('prioridad')
    @classmethod
    def validate_prioridad(cls, v):
        valid = [e.value for e in PrioridadTicket]
        if v not in valid:
            raise ValueError(f"prioridad debe ser uno de: {valid}")
        return v

    @field_validator('origen')
    @classmethod
    def validate_origen(cls, v):
        valid = [e.value for e in OrigenTicket]
        if v not in valid:
            raise ValueError(f"origen debe ser uno de: {valid}")
        return v


class TktUpdate(BaseModel):
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    responsable_id: Optional[int] = None
    respuesta_texto: Optional[str] = None


class TktNotaCreate(BaseModel):
    nota: str


class TktResponse(BaseModel):
    id: int
    company_id: int
    tipo: str
    estado: str
    prioridad: str
    origen: str
    titular_nombre: str
    titular_email: str
    titular_rut: Optional[str]
    descripcion: Optional[str]
    fecha_recepcion: Optional[str]
    fecha_vencimiento: Optional[str]
    responsable_id: Optional[int]
    respuesta_texto: Optional[str]
    respuesta_fecha: Optional[str]
    created_by: Optional[str]
    created_at: Optional[str]
    dias_restantes: Optional[int] = None
    sla_color: Optional[str] = None
    estado_sla: Optional[str] = None


class TktListResponse(BaseModel):
    tickets: list[TktResponse]
    total: int
    skip: int
    limit: int
    stats: Optional[dict] = None


class DashboardResponse(BaseModel):
    total: int
    abiertos: int
    en_proceso: int
    pendientes: int
    resueltos: int
    vencidos: int
    cumplimiento_sla: float
    tiempo_promedio_horas: float


def _ticket_to_response(ticket: TktSolicitudDerecho) -> dict:
    dias_rest = calcular_dias_restantes(ticket.fecha_vencimiento) if ticket.fecha_vencimiento else None
    sla_color = get_sla_color(dias_rest) if dias_rest is not None else None
    estado_sla = "cumplido" if ticket.estado == "resuelto" else ("vencido" if dias_rest and dias_rest < 0 else "activo")

    return TktResponse(
        id=ticket.id,
        company_id=ticket.company_id,
        tipo=ticket.tipo,
        estado=ticket.estado,
        prioridad=ticket.prioridad,
        origen=ticket.origen,
        titular_nombre=ticket.titular_nombre,
        titular_email=ticket.titular_email,
        titular_rut=ticket.titular_rut,
        descripcion=ticket.descripcion,
        fecha_recepcion=ticket.fecha_recepcion.isoformat() if ticket.fecha_recepcion else None,
        fecha_vencimiento=ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        responsable_id=ticket.responsable_id,
        respuesta_texto=ticket.respuesta_texto,
        respuesta_fecha=ticket.respuesta_fecha.isoformat() if ticket.respuesta_fecha else None,
        created_by=ticket.created_by,
        created_at=ticket.created_at.isoformat() if ticket.created_at else None,
        dias_restantes=dias_rest,
        sla_color=sla_color,
        estado_sla=estado_sla,
    ).model_dump()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard KPIs de tickets TKT."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if company_id and company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")
        if not company_id and empresas:
            company_id = empresas[0]
    stats = get_dashboard_stats(db, company_id)
    return stats


@router.get("/", response_model=TktListResponse)
def listar_tickets(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista tickets con filtros."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            return TktListResponse(tickets=[], total=0, skip=skip, limit=limit)
        if company_id and company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")
        if not company_id:
            company_id = empresas[0]

    q = db.query(TktSolicitudDerecho)
    if company_id:
        q = q.filter(TktSolicitudDerecho.company_id == company_id)
    if estado:
        q = q.filter(TktSolicitudDerecho.estado == estado)
    if prioridad:
        q = q.filter(TktSolicitudDerecho.prioridad == prioridad)

    total = q.count()
    tickets = q.order_by(TktSolicitudDerecho.fecha_recepcion.desc()).offset(skip).limit(limit).all()
    stats = get_dashboard_stats(db, company_id)

    return TktListResponse(
        tickets=[_ticket_to_response(t) for t in tickets],
        total=total,
        skip=skip,
        limit=limit,
        stats=stats,
    )


@router.get("/{ticket_id}", response_model=TktResponse)
def obtener_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Detalle de un ticket."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    return _ticket_to_response(ticket)


@router.patch("/{ticket_id}", response_model=TktResponse)
def actualizar_ticket(
    ticket_id: int,
    data: TktUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Actualiza ticket (estado, prioridad, responsable, respuesta)."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    if data.estado:
        ticket.estado = data.estado
        if data.estado == "resuelto" and not ticket.respuesta_fecha:
            ticket.respuesta_fecha = datetime.now(timezone.utc)

    if data.prioridad:
        ticket.prioridad = data.prioridad
    if data.responsable_id:
        ticket.responsable_id = data.responsable_id
    if data.respuesta_texto:
        ticket.respuesta_texto = data.respuesta_texto
        if not ticket.respuesta_fecha:
            ticket.respuesta_fecha = datetime.now(timezone.utc)
        if ticket.estado != "resuelto":
            ticket.estado = "resuelto"

    db.commit()
    db.refresh(ticket)
    logger.info(f"Ticket {ticket_id} actualizado por user {current_user.id}")
    return _ticket_to_response(ticket)


@router.post("/{ticket_id}/notas", response_model=dict)
def agregar_nota(
    ticket_id: int,
    data: TktNotaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Agrega nota interna a un ticket."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    nota = TktNota(
        ticket_id=ticket_id,
        user_id=current_user.id,
        nota=data.nota,
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    return {"id": nota.id, "created_at": nota.created_at.isoformat()}


@router.get("/{ticket_id}/notas")
def listar_notas(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista notas de un ticket."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    notas = db.query(TktNota).filter(TktNota.ticket_id == ticket_id).order_by(TktNota.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "nota": n.nota,
            "user_id": n.user_id,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notas
    ]


@router.get("/{ticket_id}/historial")
def listar_historial(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista historial de cambios de estado."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    historial = db.query(TktHistorial).filter(TktHistorial.ticket_id == ticket_id).order_by(TktHistorial.created_at.desc()).all()
    return [
        {
            "id": h.id,
            "estado_anterior": h.estado_anterior,
            "estado_nuevo": h.estado_nuevo,
            "descripcion": h.descripcion,
            "user_id": h.user_id,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in historial
    ]