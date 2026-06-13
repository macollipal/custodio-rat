"""
Lógica de negocio para Solicitudes de Derecho ARCO (Art. 14, 14 bis, 14 ter, 14 quater Ley 21.719).
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.solicitud_derecho import SolicitudDerecho, TipoSolicitud, EstadoSolicitud
from app.models.solicitud_historial import SolicitudHistorial
from app.models.solicitud_token import SolicitudToken
from app.models.company import Company
from app.models.rat import RAT as RATModel
from app.services.ticket_service import crear_ticket_desde_solicitud
from app.services.user_company_service import get_empresas_usuario
import logging

logger = logging.getLogger(__name__)


class SolicitudNotFoundError(Exception):
    pass


class RATNotFoundError(Exception):
    pass


class EmpresaNotFoundError(Exception):
    pass


class TokenInvalidoError(Exception):
    pass


class SinAccesoError(Exception):
    pass


class EstadoInvalidoError(Exception):
    pass


def generate_token(db: Session, ip_address: Optional[str] = None) -> str:
    token = str(uuid.uuid4())
    db_token = SolicitudToken(token=token, ip_address=ip_address)
    db.add(db_token)
    db.commit()
    return token


def validate_token(db: Session, token: str) -> bool:
    result = db.query(SolicitudToken).filter(
        SolicitudToken.token == token,
        SolicitudToken.used == False,
        SolicitudToken.created_at > datetime.now(timezone.utc) - timedelta(minutes=5)
    ).update({SolicitudToken.used: True})
    db.commit()
    return result > 0


def crear_solicitud(
    db: Session,
    company_id: int,
    tipo: str,
    nombre_titular: str,
    rut_titular: Optional[str],
    email_titular: str,
    descripcion: Optional[str],
    token: str,
    ip_address: Optional[str] = None,
) -> SolicitudDerecho:
    if not validate_token(db, token):
        raise TokenInvalidoError("Token inválido o expirado. Recargá la página e intentá de nuevo.")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise EmpresaNotFoundError("Empresa no encontrada")

    ahora = datetime.now(timezone.utc)
    solicitud = SolicitudDerecho(
        company_id=company_id,
        tipo=tipo,
        nombre_titular=nombre_titular,
        rut_titular=rut_titular,
        email_titular=email_titular,
        descripcion=descripcion,
        estado="pendiente",
        solicitud_fecha=ahora,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    ticket = crear_ticket_desde_solicitud(
        db=db,
        company_id=company_id,
        tipo=tipo,
        titular_nombre=nombre_titular,
        titular_email=email_titular,
        descripcion=descripcion,
        titular_rut=rut_titular,
        origen="web",
    )

    logger.info(f"Solicitud ARCO creada: id={solicitud.id} company={company_id} tipo={tipo} ticket_id={ticket.id} ip={ip_address or 'unknown'}")
    return solicitud


def listar_solicitudes(
    db: Session,
    current_user,
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[SolicitudDerecho], int]:
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if company_id is None:
            company_id = empresas[0] if empresas else 0
        if company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta empresa")

    q = db.query(SolicitudDerecho)
    if company_id:
        q = q.filter(SolicitudDerecho.company_id == company_id)
    if estado:
        q = q.filter(SolicitudDerecho.estado == estado)

    total = q.count()
    solicitudes = q.order_by(SolicitudDerecho.solicitud_fecha.desc()).offset(skip).limit(limit).all()
    return solicitudes, total


def obtener_solicitud(db: Session, solicitud_id: int, current_user) -> SolicitudDerecho:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")
    return s


def obtener_historial(db: Session, solicitud_id: int, current_user) -> List[SolicitudHistorial]:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")

    return db.query(SolicitudHistorial).filter(
        SolicitudHistorial.solicitud_id == solicitud_id
    ).order_by(SolicitudHistorial.fecha.asc()).all()


def responder_solicitud(
    db: Session,
    solicitud_id: int,
    estado: str,
    respuesta: str,
    descripcion_accion: Optional[str],
    current_user,
) -> SolicitudDerecho:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")

    historial = SolicitudHistorial(
        solicitud_id=s.id,
        estado_anterior=s.estado,
        estado_nuevo=estado,
        descripcion=descripcion_accion or respuesta,
        usuario_nombre=current_user.username,
    )
    db.add(historial)

    s.estado = estado
    s.respuesta = respuesta
    s.respuesta_fecha = datetime.now(timezone.utc)

    from app.services.audit_service import log_audit
    log_audit(
        db=db,
        entidad="solicitud_derecho",
        entidad_id=solicitud_id,
        accion="responder",
        usuario=current_user.username,
        detalle={"estado_anterior": s.estado, "estado_nuevo": estado},
    )
    db.commit()
    return s


def calcular_fecha_vencimiento(dias: int) -> datetime:
    hoy = datetime.now(timezone.utc)
    dias_habiles = 0
    dia_actual = hoy
    while dias_habiles < dias:
        dia_actual += timedelta(days=1)
        if dia_actual.weekday() < 5:
            dias_habiles += 1
    return dia_actual


def bloquear_rat(
    db: Session,
    solicitud_id: int,
    rat_id: int,
    dias_bloqueo: int,
    current_user,
) -> dict:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")

    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise RATNotFoundError("RAT no encontrado")
    if rat.company_id != s.company_id:
        raise ValueError("El RAT no pertenece a la empresa de la solicitud")

    historial = SolicitudHistorial(
        solicitud_id=s.id,
        estado_anterior=s.estado,
        estado_nuevo=EstadoSolicitud.BLOQUEADO.value,
        descripcion=f"Bloqueo temporal del RAT id={rat.id} por {dias_bloqueo} días hábiles",
        usuario_nombre=current_user.username,
    )
    db.add(historial)

    s.estado = EstadoSolicitud.BLOQUEADO.value
    s.rat_id = rat_id
    s.plazo_bloqueo_vencimiento = calcular_fecha_vencimiento(dias_bloqueo)
    rat.bloqueado = True
    db.commit()
    return {
        "ok": True,
        "rat_id": rat.id,
        "bloqueado": True,
        "plazo_vencimiento": s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
    }


def desbloquear_rat(db: Session, solicitud_id: int, current_user) -> dict:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")

    if s.estado != EstadoSolicitud.BLOQUEADO.value:
        raise EstadoInvalidoError("Esta solicitud no está en estado bloqueado")

    rat_id = s.rat_id
    if rat_id:
        rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
        if rat:
            rat.bloqueado = False

    historial = SolicitudHistorial(
        solicitud_id=s.id,
        estado_anterior=s.estado,
        estado_nuevo=EstadoSolicitud.EN_PROCESO.value,
        descripcion="Desbloqueo anticipado del RAT",
        usuario_nombre=current_user.username,
    )
    db.add(historial)

    s.estado = EstadoSolicitud.EN_PROCESO.value
    s.plazo_bloqueo_vencimiento = None
    db.commit()
    return {"ok": True, "rat_id": rat_id, "bloqueado": False}


def exportar_portabilidad(db: Session, solicitud_id: int, current_user) -> dict:
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise SolicitudNotFoundError("Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise SinAccesoError("No tiene acceso a esta solicitud")

    if s.tipo != TipoSolicitud.PORTABILIDAD.value:
        raise ValueError("Esta solicitud no es de portabilidad")

    exportado_en = datetime.now(timezone.utc)
    return {
        "id": s.id,
        "company_id": s.company_id,
        "tipo": s.tipo,
        "nombre_titular": s.nombre_titular,
        "rut_titular": s.rut_titular,
        "email_titular": s.email_titular,
        "descripcion": s.descripcion,
        "estado": s.estado,
        "solicitud_fecha": s.solicitud_fecha.isoformat() if s.solicitud_fecha else None,
        "respuesta": s.respuesta,
        "respuesta_fecha": s.respuesta_fecha.isoformat() if s.respuesta_fecha else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "rat_id": s.rat_id,
        "plazo_bloqueo_vencimiento": s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
        "exportado_en": exportado_en.isoformat(),
    }