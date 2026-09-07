"""
Endpoints CRUD para el módulo de ticketing TKT.
Ruta: /tkt-solicitud-derecho/
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.models.tkt_nota import TktNota
from app.models.tkt_historial import TktHistorial
from app.models.company import Company
from app.services.user_company_service import get_empresas_usuario
from app.services.ticket_service import (
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
    prorrogar_ticket,
)
from app.services.audit_service import log_audit
from app.services.email_service import notificar_acuse_solicitud
from app.schemas.tkt_solicitud_derecho import (
    TktTicketCreate,
    TktTicketUpdate,
    TktNotaCreate,
    TktTicketResponse,
    TktListResponse,
    TktDashboardResponse,
    TktBloquearRequest,
    TktExportPortabilidadResponse,
    TktProrrogarRequest,
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
        prorroga_fecha=ticket.prorroga_fecha,
        prorroga_dias=ticket.prorroga_dias,
        created_by=ticket.created_by,
        created_at=ticket.created_at,
        representante_nombre=ticket.representante_nombre,
        representante_rut=ticket.representante_rut,
        representante_poder_notarial_notas=ticket.representante_poder_notarial_notas,
        telefono=ticket.telefono,
        fecha_nacimiento=ticket.fecha_nacimiento,
        pais=ticket.pais,
        dias_restantes=dias_rest,
        sla_color=sla_color,
        estado_sla=estado_sla,
        # Campos nuevos gaps Ley 21.719 (Iter 10)
        metodo_verificacion_identidad=ticket.metodo_verificacion_identidad,
        evidencia_identidad=ticket.evidencia_identidad,
        evidencia_respuesta_hash=ticket.evidencia_respuesta_hash,
        causal_rechazo=ticket.causal_rechazo,
        medio_respuesta=ticket.medio_respuesta,
    ).model_dump()


@router.get("/check-duplicado")
def check_duplicado(
    email: str,
    tipo: str,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Detecta posibles solicitudes duplicadas (QW6)."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    desde = datetime.now(timezone.utc) - timedelta(days=90)
    query = db.query(TktSolicitudDerecho).filter(
        TktSolicitudDerecho.titular_email.ilike(email),
        TktSolicitudDerecho.tipo == tipo,
        TktSolicitudDerecho.company_id == company_id,
        TktSolicitudDerecho.fecha_recepcion >= desde,
    )
    if current_user.rol_global != "superadmin":
        query = query.filter(TktSolicitudDerecho.estado.notin_(["rechazado"]))

    duplicados = query.order_by(TktSolicitudDerecho.fecha_recepcion.desc()).limit(5).all()
    return {
        "es_duplicado": len(duplicados) > 0,
        "cantidad": len(duplicados),
        "solicitudes": [_ticket_to_response(d) for d in duplicados],
    }


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
        representante_nombre=data.representante_nombre,
        representante_rut=data.representante_rut,
        representante_poder_notarial_notas=data.representante_poder_notarial_notas,
        telefono=data.telefono,
        fecha_nacimiento=data.fecha_nacimiento,
        pais=data.pais,
        # Campos nuevos gaps Ley 21.719 (Iter 10)
        metodo_verificacion_identidad=data.metodo_verificacion_identidad,
        evidencia_identidad=data.evidencia_identidad,
        evidencia_respuesta_hash=data.evidencia_respuesta_hash,
        causal_rechazo=data.causal_rechazo,
        medio_respuesta=data.medio_respuesta,
    )
    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="create",
        usuario=current_user.username,
        detalle={"tipo": data.tipo, "titular": data.titular_nombre, "origen": data.origen},
    )
    if data.titular_email:
        try:
            notificar_acuse_solicitud(
                email_titular=data.titular_email,
                nombre_titular=data.titular_nombre,
                tipo_derecho=data.tipo,
                empresa_nombre=company.nombre,
                ticket_id=ticket.id,
                tracking_token=ticket.tracking_token or "",
            )
            ticket.acuse_enviado_at = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            logger.warning("No se pudo enviar acuse de recibo para ticket %s", ticket.id)
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

    # Feature gate N-02: modulo ARCO debe estar habilitado
    if company_id is not None:
        from app.services.module_permission_service import require_module_enabled
        require_module_enabled(db, company_id, "ARCO")

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

    if data.estado == "resuelto" and not ticket.evidencia_respuesta_hash:
        from app.models.tkt_adjunto import TktAdjunto
        adjuntos = db.query(TktAdjunto).filter(TktAdjunto.ticket_id == ticket_id).all()
        if adjuntos:
            import hashlib
            sha = hashlib.sha256()
            for adj in sorted(adjuntos, key=lambda a: a.id):
                sha.update(adj.data)
            ticket.evidencia_respuesta_hash = sha.hexdigest()
        elif not data.respuesta_texto and not data.plantilla_id:
            raise HTTPException(
                status_code=400,
                detail="No se puede resolver sin evidencia: adjunte documentos o informe antes de cerrar.",
            )

    # S1.3: Validación de identidad (Art. 12 Ley 21.719).
    # Si el ticket pasa a estado 'resuelto', debe existir método de verificación de identidad registrado.
    if data.estado == "resuelto" and not ticket.metodo_verificacion_identidad and not data.metodo_verificacion_identidad:
        raise HTTPException(
            status_code=422,
            detail=(
                "Antes de marcar una solicitud ARCO como resuelta, debe registrar el método "
                "de verificación de identidad del titular (Art. 12 Ley 21.719). Editá el "
                "ticket y agregá 'Metodo verificacion identidad' (ej: 'email_verificado', "
                "'cedula_escaneada', 'pin_telefono') antes de cerrar."
            ),
        )

    # S1.4: Calcular evidencia_respuesta_hash si no existe aún (SHA-256 sobre
    # respuesta_texto + username + timestamp UTC ISO) — Art. 12.5 integridad.
    # Usar data.respuesta_texto si viene en este request, pues aún no se ha
    # aplicado al ticket (se aplica más abajo), evitando hashear string vacío.
    if data.estado == "resuelto" and not ticket.evidencia_respuesta_hash:
        import hashlib
        _respuesta_final = data.respuesta_texto or ticket.respuesta_texto or ""
        hash_input = (
            f"{_respuesta_final.strip()}"
            f"|{current_user.username}"
            f"|{datetime.now(timezone.utc).isoformat()}"
        )
        ticket.evidencia_respuesta_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

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

    # Campos nuevos gaps Ley 21.719 (Iter 10)
    if data.metodo_verificacion_identidad is not None:
        ticket.metodo_verificacion_identidad = data.metodo_verificacion_identidad
    if data.evidencia_identidad is not None:
        ticket.evidencia_identidad = data.evidencia_identidad
    if data.causal_rechazo is not None:
        ticket.causal_rechazo = data.causal_rechazo
    if data.medio_respuesta is not None:
        ticket.medio_respuesta = data.medio_respuesta

    # ARCO-QW10: editar RUT titular/representante post-creación
    if data.titular_rut is not None:
        ticket.titular_rut = data.titular_rut or None
    if data.representante_rut is not None:
        ticket.representante_rut = data.representante_rut or None

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
    db.commit()
    logger.info(f"Ticket {ticket_id} actualizado por user {current_user.id}")

    respuesta_enviada_en_este_request = data.respuesta_texto or data.plantilla_id
    if respuesta_enviada_en_este_request and ticket.respuesta_texto and ticket.titular_email:
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
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Los usuarios de solo-lectura no pueden agregar notas.")

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

    notas = db.query(TktNota).filter(TktNota.ticket_id == ticket_id).order_by(TktNota.created_at.desc()).limit(200).all()
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

    historial = db.query(TktHistorial).filter(TktHistorial.ticket_id == ticket_id).order_by(TktHistorial.created_at.desc()).limit(500).all()
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
    # Causal de rechazo según Art. 12.5 Ley 21.719 (enum CausalRechazo).
    # Valores: falta_identidad | solicitud_manifiestamente_infundada | solicitud_excesiva
    #          | falta_poder_notorial | plazo_vencido | identidad_no_verificada | otro.
    causal_rechazo: str
    motivo_detalle: Optional[str] = None  # Texto libre explicando la causal


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

    from app.models.tkt_solicitud_derecho import CausalRechazo

    # Validar que causal_rechazo pertenezca al enum (Art. 12.5).
    causal_validas = [e.value for e in CausalRechazo]
    if data.causal_rechazo not in causal_validas:
        raise HTTPException(
            status_code=422,
            detail=(
                f"causal_rechazo inválida. Valores permitidos (Art. 12.5 Ley 21.719): {causal_validas}"
            ),
        )

    ticket_out, error = rechazar_ticket(
        db=db,
        ticket_id=ticket_id,
        motivo=data.causal_rechazo,
        motivo_detalle=data.motivo_detalle,
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
        detalle={"causal_rechazo": data.causal_rechazo, "motivo_detalle": data.motivo_detalle},
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


@router.post("/{ticket_id}/prorrogar", summary="Extender plazo de respuesta (Art. 12 bis)")
def prorrogar_solicitud_ticket(
    ticket_id: int,
    data: TktProrrogarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Extiende el plazo de respuesta hasta 10 días hábiles adicionales (Art. 12 bis). Solo se puede prorrogar una vez."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden prorrogar")

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if ticket.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a este ticket")

    ticket_out, error = prorrogar_ticket(
        db=db,
        ticket_id=ticket_id,
        dias=data.dias,
        motivo=data.motivo,
        user_id=current_user.id,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket_id,
        accion="prorrogar",
        usuario=current_user.username,
        detalle={"dias": data.dias, "motivo": data.motivo},
    )
    return _ticket_to_response(ticket_out)
