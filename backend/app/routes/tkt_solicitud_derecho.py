"""
Endpoints CRUD para el módulo de ticketing TKT.
Ruta: /tkt-solicitud-derecho/
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.models.tkt_nota import TktNota
from app.models.tkt_historial import TktHistorial
from app.models.company import Company
from app.services.user_company_service import get_empresas_usuario
from app.services.ticket_service import (
    crear_ticket_desde_solicitud,
    crear_ticket,
    cambiar_estado_ticket,
    get_dashboard_stats,
    calcular_dias_restantes,
    get_sla_color,
)
from app.schemas.tkt_solicitud_derecho import (
    TktTicketCreate,
    TktTicketUpdate,
    TktNotaCreate,
    TktTicketResponse,
    TktListResponse,
    TktDashboardResponse,
)
import logging

router = APIRouter(prefix="/tkt-solicitud-derecho", tags=["TKT - Solicitudes ARCO"])
logger = logging.getLogger(__name__)


def _ticket_to_response(ticket: TktSolicitudDerecho) -> dict:
    dias_rest = calcular_dias_restantes(ticket.fecha_vencimiento) if ticket.fecha_vencimiento else None
    sla_color = get_sla_color(dias_rest) if dias_rest is not None else None
    estado_sla = "cumplido" if ticket.estado == "resuelto" else ("vencido" if dias_rest and dias_rest < 0 else "activo")

    return TktTicketResponse(
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
        fecha_recepcion=ticket.fecha_recepcion,
        fecha_vencimiento=ticket.fecha_vencimiento,
        responsable_id=ticket.responsable_id,
        respuesta_texto=ticket.respuesta_texto,
        respuesta_fecha=ticket.respuesta_fecha,
        created_by=ticket.created_by,
        created_at=ticket.created_at,
        dias_restantes=dias_rest,
        sla_color=sla_color,
        estado_sla=estado_sla,
    ).model_dump()


@router.get("/dashboard", response_model=TktDashboardResponse)
def dashboard(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard KPIs de tickets TKT."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            return TktDashboardResponse(
                total=0, abiertos=0, en_proceso=0, pendientes=0,
                resueltos=0, vencidos=0, cumplimiento_sla=100.0, tiempo_promedio_horas=0
            )
        if company_id and company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")
        if not company_id:
            company_id = empresas[0]

    stats = get_dashboard_stats(db, company_id)
    return stats


@router.post("/", response_model=TktTicketResponse)
def crear_ticket_endpoint(
    data: TktTicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Crea un ticket TKT manualmente (solo admin_empresa y superadmin)."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden crear tickets")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    ticket = crear_ticket(
        db=db,
        company_id=data.company_id,
        tipo=data.tipo,
        prioridad=data.prioridad,
        origen=data.origen,
        titular_nombre=data.titular_nombre,
        titular_email=data.titular_email,
        titular_rut=data.titular_rut,
        descripcion=data.descripcion,
        created_by=current_user.username,
    )
    return _ticket_to_response(ticket)


MAX_TKT_LIMIT = 100


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
    limit = min(limit, MAX_TKT_LIMIT)

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            return TktListResponse(tickets=[], total=0, skip=skip, limit=limit, stats=None)
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


@router.get("/{ticket_id}", response_model=TktTicketResponse)
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


@router.patch("/{ticket_id}", response_model=TktTicketResponse)
def actualizar_ticket(
    ticket_id: int,
    data: TktTicketUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Actualiza ticket (estado, prioridad, responsable, respuesta)."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden editar tickets")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    if data.responsable_id is not None:
        from app.models.user import User
        if data.responsable_id > 0:
            user_exists = db.query(User).filter(User.id == data.responsable_id).first()
            if not user_exists:
                raise HTTPException(status_code=400, detail="El usuario responsable no existe")
            ticket.responsable_id = data.responsable_id
        else:
            ticket.responsable_id = None

    if data.prioridad:
        ticket.prioridad = data.prioridad

    if data.estado and data.estado != ticket.estado:
        ticket, error = cambiar_estado_ticket(
            db=db,
            ticket_id=ticket_id,
            nuevo_estado=data.estado,
            user_id=current_user.id,
            descripcion=f"Estado cambiado a {data.estado}",
            auto_commit=False,
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
        if data.estado == "resuelto" and not ticket.respuesta_fecha:
            ticket.respuesta_fecha = datetime.now(timezone.utc)

    if data.respuesta_texto:
        ticket.respuesta_texto = data.respuesta_texto
        if not ticket.respuesta_fecha:
            ticket.respuesta_fecha = datetime.now(timezone.utc)
        if ticket.estado != "resuelto":
            ticket, error = cambiar_estado_ticket(
                db=db,
                ticket_id=ticket_id,
                nuevo_estado="resuelto",
                user_id=current_user.id,
                descripcion="Estado cambiado a resuelto (por respuesta)",
                auto_commit=False,
            )
            if error:
                raise HTTPException(status_code=400, detail=error)

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
