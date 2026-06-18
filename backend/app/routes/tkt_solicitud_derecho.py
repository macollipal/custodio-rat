"""
Endpoints CRUD para el módulo de ticketing TKT.
Ruta: /tkt-solicitud-derecho/
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
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
    bloquear_ticket,
    desbloquear_ticket,
    rechazar_ticket,
    guardar_portability_data,
    solicitar_subsanacion,
    completar_subsanacion,
)
from app.services.audit_service import log_audit
from app.schemas.tkt_solicitud_derecho import (
    TktTicketCreate,
    TktTicketUpdate,
    TktNotaCreate,
    TktTicketResponse,
    TktListResponse,
    TktDashboardResponse,
    TktBloquearRequest,
    TktExportPortabilidadResponse,
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
        rat_id=ticket.rat_id,
        plazo_bloqueo_vencimiento=ticket.plazo_bloqueo_vencimiento,
        portability_data=ticket.portability_data,
        tracking_token=ticket.tracking_token,
        acuse_enviado_at=ticket.acuse_enviado_at,
        subsanacion_detalle=ticket.subsanacion_detalle,
        subsanacion_fecha_pedido=ticket.subsanacion_fecha_pedido,
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
        titular_rut=data.rut_titular,
        descripcion=data.descripcion,
        created_by=current_user.username,
        rat_id=data.rat_id,
    )
    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="create",
        usuario=current_user.username,
        detalle={"tipo": data.tipo, "titular": data.titular_nombre, "origen": data.origen},
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
    elif data.plantilla_id:
        from app.models.tkt_plantilla import TktPlantilla
        from app.services.plantilla_service import render_plantilla
        plantilla = db.query(TktPlantilla).filter(TktPlantilla.id == data.plantilla_id).first()
        if not plantilla:
            raise HTTPException(status_code=404, detail="Plantilla no encontrada")
        from app.models.company import Company
        empresa = db.query(Company).filter(Company.id == ticket.company_id).first()
        empresa_nombre = empresa.nombre if empresa else "la empresa"
        ticket.respuesta_texto = render_plantilla(
            contenido=plantilla.contenido,
            nombre_titular=ticket.titular_nombre,
            empresa=empresa_nombre,
            numero_solicitud=str(ticket.id),
        )
        if not ticket.respuesta_fecha:
            ticket.respuesta_fecha = datetime.now(timezone.utc)
        if ticket.estado != "resuelto":
            ticket, error = cambiar_estado_ticket(
                db=db,
                ticket_id=ticket_id,
                nuevo_estado="resuelto",
                user_id=current_user.id,
                descripcion="Estado cambiado a resuelto (por plantilla)",
                auto_commit=False,
            )
            if error:
                raise HTTPException(status_code=400, detail=error)

    db.commit()
    db.refresh(ticket)
    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="update",
        usuario=current_user.username,
        detalle={
            "estado": data.estado,
            "prioridad": data.prioridad,
            "responsable_id": data.responsable_id,
            "plantilla_id": data.plantilla_id,
            "con_respuesta": bool(ticket.respuesta_texto),
        },
    )
    logger.info(f"Ticket {ticket_id} actualizado por user {current_user.id}")

    if ticket.respuesta_texto and ticket.titular_email:
        from app.models.company import Company
        from app.services.email_service import notificar_respuesta_arco
        empresa = db.query(Company).filter(Company.id == ticket.company_id).first()
        try:
            notificar_respuesta_arco(
                email_titular=ticket.titular_email,
                nombre_titular=ticket.titular_nombre,
                tipo_derecho=ticket.tipo,
                respuesta=ticket.respuesta_texto,
                empresa_nombre=empresa.nombre if empresa else "la empresa",
            )
        except Exception as e:
            logger.error(
                f"Ticket {ticket_id}: fallo enviando respuesta ARCO a "
                f"{ticket.titular_email}: {e}"
            )

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
    log_audit(
        db=db,
        entidad="tkt_nota",
        entidad_id=nota.id,
        accion="create",
        usuario=current_user.username,
        detalle={"ticket_id": ticket_id},
    )
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


@router.post("/{ticket_id}/bloquear", summary="Bloquear RAT temporalmente (Art. 8 ter)")
def bloquear_rat_ticket(
    ticket_id: int,
    data: TktBloquearRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Bloquea un RAT y marca el ticket como bloqueado."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden bloquear RATs")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = bloquear_ticket(
        db=db,
        ticket_id=ticket_id,
        rat_id=data.rat_id,
        dias_bloqueo=data.dias_bloqueo,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="bloquear",
        usuario=current_user.username,
        detalle={"rat_id": data.rat_id, "dias_bloqueo": data.dias_bloqueo},
    )
    return _ticket_to_response(ticket_out)


@router.post("/{ticket_id}/desbloquear", summary="Desbloquear RAT antes del vencimiento")
def desbloquear_rat_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Desbloquea un RAT antes del vencimiento y marca ticket como resuelto."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden desbloquear RATs")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = desbloquear_ticket(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="desbloquear",
        usuario=current_user.username,
        detalle={},
    )
    return _ticket_to_response(ticket_out)


class RechazarRequest(BaseModel):
    motivo: str


@router.post("/{ticket_id}/rechazar", summary="Rechazar solicitud con motivo fundado (Art. 12.5)")
def rechazar_solicitud_ticket(
    ticket_id: int,
    data: RechazarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Rechaza una solicitud ARCO con motivo fundado."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden rechazar solicitudes")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = rechazar_ticket(
        db=db,
        ticket_id=ticket_id,
        motivo=data.motivo,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="rechazar",
        usuario=current_user.username,
        detalle={"motivo": data.motivo},
    )
    return _ticket_to_response(ticket_out)


@router.get("/{ticket_id}/portabilidad/export", response_model=TktExportPortabilidadResponse, summary="Exportar datos de portabilidad (Art. 9)")
def exportar_portabilidad_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Exporta los datos de portabilidad de un ticket."""
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    if ticket.tipo != "portabilidad":
        raise HTTPException(status_code=400, detail="El ticket no es de portabilidad")

    exportado_en = datetime.now(timezone.utc)

    return TktExportPortabilidadResponse(
        id=ticket.id,
        company_id=ticket.company_id,
        tipo=ticket.tipo,
        titular_nombre=ticket.titular_nombre,
        titular_email=ticket.titular_email,
        titular_rut=ticket.titular_rut,
        descripcion=ticket.descripcion,
        estado=ticket.estado,
        fecha_recepcion=ticket.fecha_recepcion.isoformat() if ticket.fecha_recepcion else None,
        portability_data=ticket.portability_data,
        exportado_en=exportado_en.isoformat(),
    )


class GuardarPortabilidadRequest(BaseModel):
    portability_data: str


@router.post("/{ticket_id}/portabilidad/guardar", summary="Guardar datos de portabilidad en ticket")
def guardar_portabilidad_ticket(
    ticket_id: int,
    data: GuardarPortabilidadRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Guarda los datos de portabilidad JSON en el ticket y lo marca como resuelto."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden guardar portabilidad")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = guardar_portability_data(
        db=db,
        ticket_id=ticket_id,
        portability_data=data.portability_data,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="exportar_portabilidad",
        usuario=current_user.username,
        detalle={},
    )
    return _ticket_to_response(ticket_out)


class SubsanarRequest(BaseModel):
    detalle: str = Field(..., min_length=10, max_length=1000, description="Información faltante requerida al titular")


@router.post("/{ticket_id}/subsanar", summary="Solicitar subsanación al titular (Art. 12)")
def solicitar_subsanacion_ticket(
    ticket_id: int,
    data: SubsanarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Solicita información faltante al titular cuando la solicitud ARCO está incompleta. Extiende el plazo en 10 días hábiles."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden solicitar subsanación")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = solicitar_subsanacion(
        db=db,
        ticket_id=ticket_id,
        detalle=data.detalle,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="subsanacion_solicitar",
        usuario=current_user.username,
        detalle={"detalle": data.detalle},
    )
    return _ticket_to_response(ticket_out)


@router.post("/{ticket_id}/completar-subsanacion", summary="Completar subsanación (volver a en_proceso)")
def completar_subsanacion_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Marca la subsanación como completada y vuelve a poner el ticket en proceso con nuevo plazo de 10 días hábiles."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden completar subsanación")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = completar_subsanacion(
        db=db,
        ticket_id=ticket_id,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="subsanacion_completar",
        usuario=current_user.username,
        detalle={},
    )
    return _ticket_to_response(ticket_out)
