from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timezone, timedelta
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.solicitud_derecho import SolicitudDerecho, TipoSolicitud, EstadoSolicitud
from app.models.solicitud_historial import SolicitudHistorial
from app.models.solicitud_token import SolicitudToken
from app.models.company import Company
from app.services.user_company_service import get_empresas_usuario
from app.services.ticket_service import crear_ticket_desde_solicitud
from app.core.limiter import limiter
import uuid
import logging

router = APIRouter(prefix="/solicitudes-derecho", tags=["Solicitudes de Derecho"])
logger = logging.getLogger(__name__)


def _generate_token(db: Session, ip_address: Optional[str] = None) -> str:
    token = str(uuid.uuid4())
    db_token = SolicitudToken(token=token, ip_address=ip_address)
    db.add(db_token)
    db.commit()
    return token


def _validate_token(db: Session, token: str) -> bool:
    result = db.query(SolicitudToken).filter(
        SolicitudToken.token == token,
        SolicitudToken.used == False,
        SolicitudToken.created_at > datetime.now(timezone.utc) - timedelta(minutes=5)
    ).update({SolicitudToken.used: True})
    db.commit()
    return result > 0


class SolicitudCreate(BaseModel):
    company_id: int
    tipo: str
    nombre_titular: str
    rut_titular: Optional[str] = None
    email_titular: EmailStr
    descripcion: Optional[str] = None
    token: str

    @field_validator('company_id')
    @classmethod
    def validate_company_id(cls, v):
        if v <= 0:
            raise ValueError("company_id debe ser mayor a 0")
        return v

    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        valid_types = [e.value for e in TipoSolicitud]
        if v not in valid_types:
            raise ValueError(f"tipo debe ser uno de: {valid_types}")
        return v


class BloquearRequest(BaseModel):
    rat_id: int
    dias_bloqueo: int = 2


class PortabilidadResponse(BaseModel):
    id: int
    company_id: int
    tipo: str
    nombre_titular: str
    rut_titular: Optional[str]
    email_titular: str
    descripcion: Optional[str]
    estado: str
    solicitud_fecha: Optional[str]
    respuesta: Optional[str]
    respuesta_fecha: Optional[str]
    created_at: Optional[str]
    rat_id: Optional[int]
    plazo_bloqueo_vencimiento: Optional[str]
    exportado_en: Optional[str]


class TokenResponse(BaseModel):
    token: str


class SolicitudResponse(BaseModel):
    id: int
    company_id: int
    tipo: str
    nombre_titular: str
    rut_titular: Optional[str]
    email_titular: str
    descripcion: Optional[str]
    estado: str
    solicitud_fecha: Optional[str]
    respuesta: Optional[str]
    respuesta_fecha: Optional[str]
    created_at: Optional[str]


@router.get("/token", response_model=TokenResponse, summary="Obtener token para formulario público")
@limiter.limit("5/minute")
def obtener_token(request: Request, db: Session = Depends(get_db)):
    """Genera un token temporal para el formulario de solicitudes de derechos ARCO."""
    ip = request.client.host if request.client else None
    return {"token": _generate_token(db, ip)}


@router.post("/", response_model=dict)
@limiter.limit("3/hour")
async def crear_solicitud(
    request: Request,
    data: SolicitudCreate,
    db: Session = Depends(get_db),
):
    if not _validate_token(db, data.token):
        return JSONResponse(status_code=400, content={"detail": "Token inválido o expirado. Recargá la página e intentá de nuevo."})

    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        return JSONResponse(status_code=404, content={"detail": "Empresa no encontrada"})

    ahora = datetime.now(timezone.utc)
    solicitud = SolicitudDerecho(
        company_id=data.company_id,
        tipo=data.tipo,
        nombre_titular=data.nombre_titular,
        rut_titular=data.rut_titular,
        email_titular=data.email_titular,
        descripcion=data.descripcion,
        estado="pendiente",
        solicitud_fecha=ahora,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    ticket = crear_ticket_desde_solicitud(
        db=db,
        company_id=data.company_id,
        tipo=data.tipo,
        titular_nombre=data.nombre_titular,
        titular_email=data.email_titular,
        descripcion=data.descripcion,
        titular_rut=data.rut_titular,
        origen="web",
    )

    logger.info(f"Solicitud ARCO creada: id={solicitud.id} company={data.company_id} tipo={data.tipo} ticket_id={ticket.id} ip={request.client.host if request.client else 'unknown'}")
    return {
        "id": solicitud.id,
        "company_id": solicitud.company_id,
        "tipo": solicitud.tipo,
        "nombre_titular": solicitud.nombre_titular,
        "rut_titular": solicitud.rut_titular,
        "email_titular": solicitud.email_titular,
        "descripcion": solicitud.descripcion,
        "estado": solicitud.estado,
        "solicitud_fecha": solicitud.solicitud_fecha.isoformat() if solicitud.solicitud_fecha else None,
        "respuesta": solicitud.respuesta,
        "respuesta_fecha": solicitud.respuesta_fecha.isoformat() if solicitud.respuesta_fecha else None,
        "created_at": solicitud.created_at.isoformat() if solicitud.created_at else None,
    }


@router.get("/", summary="Listar solicitudes de derechos ARCO")
def listar_solicitudes(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if company_id is None:
            company_id = empresas[0] if empresas else 0
        if company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    q = db.query(SolicitudDerecho)
    if company_id:
        q = q.filter(SolicitudDerecho.company_id == company_id)
    if estado:
        q = q.filter(SolicitudDerecho.estado == estado)

    total = q.count()
    solicitudes = q.order_by(SolicitudDerecho.solicitud_fecha.desc()).offset(skip).limit(limit).all()
    return {
        "solicitudes": [
            SolicitudResponse(
                id=s.id,
                company_id=s.company_id,
                tipo=s.tipo,
                nombre_titular=s.nombre_titular,
                rut_titular=s.rut_titular,
                email_titular=s.email_titular,
                descripcion=s.descripcion,
                estado=s.estado,
                solicitud_fecha=s.solicitud_fecha.isoformat() if s.solicitud_fecha else None,
                respuesta=s.respuesta,
                respuesta_fecha=s.respuesta_fecha.isoformat() if s.respuesta_fecha else None,
                created_at=s.created_at.isoformat() if s.created_at else None,
            )
            for s in solicitudes
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{solicitud_id}", response_model=SolicitudResponse)
def obtener_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")
    return SolicitudResponse(
        id=s.id,
        company_id=s.company_id,
        tipo=s.tipo,
        nombre_titular=s.nombre_titular,
        rut_titular=s.rut_titular,
        email_titular=s.email_titular,
        descripcion=s.descripcion,
        estado=s.estado,
        solicitud_fecha=s.solicitud_fecha.isoformat() if s.solicitud_fecha else None,
        respuesta=s.respuesta,
        respuesta_fecha=s.respuesta_fecha.isoformat() if s.respuesta_fecha else None,
        created_at=s.created_at.isoformat() if s.created_at else None,
    )


class HistorialEntry(BaseModel):
    id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    descripcion: Optional[str]
    fecha: Optional[str]
    usuario_nombre: Optional[str]


@router.get("/{solicitud_id}/historial", response_model=list[HistorialEntry])
def obtener_historial(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")

    registros = db.query(SolicitudHistorial).filter(
        SolicitudHistorial.solicitud_id == solicitud_id
    ).order_by(SolicitudHistorial.fecha.asc()).all()
    return [
        HistorialEntry(
            id=r.id,
            estado_anterior=r.estado_anterior,
            estado_nuevo=r.estado_nuevo,
            descripcion=r.descripcion,
            fecha=r.fecha.isoformat() if r.fecha else None,
            usuario_nombre=r.usuario_nombre,
        )
        for r in registros
    ]


class ResponderRequest(BaseModel):
    estado: str
    respuesta: str
    descripcion_accion: Optional[str] = None
    usuario_nombre: Optional[str] = None


@router.patch("/{solicitud_id}/responder")
def responder_solicitud(
    solicitud_id: int,
    data: ResponderRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from datetime import datetime, timezone

    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")

    historial = SolicitudHistorial(
        solicitud_id=s.id,
        estado_anterior=s.estado,
        estado_nuevo=data.estado,
        descripcion=data.descripcion_accion or data.respuesta,
        usuario_nombre=current_user.username,
    )
    db.add(historial)

    s.estado = data.estado
    s.respuesta = data.respuesta
    s.respuesta_fecha = datetime.now(timezone.utc)
    from app.services.audit_service import log_audit
    log_audit(
        db=db,
        entidad="solicitud_derecho",
        entidad_id=solicitud_id,
        accion="responder",
        usuario=current_user.username,
        detalle={"estado_anterior": s.estado, "estado_nuevo": data.estado},
    )
    db.commit()
    return {"ok": True}


@router.post("/{solicitud_id}/bloquear", summary="Bloquear temporalmente un RAT (Art. 8 ter — REC-01)")
def bloquear_rat(
    solicitud_id: int,
    data: BloquearRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.rat import RAT as RATModel

    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")

    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado")
    if rat.company_id != s.company_id:
        raise HTTPException(status_code=400, detail="El RAT no pertenece a la empresa de la solicitud")

    historial = SolicitudHistorial(
        solicitud_id=s.id,
        estado_anterior=s.estado,
        estado_nuevo=EstadoSolicitud.BLOQUEADO.value,
        descripcion=f"Bloqueo temporal del RAT id={rat.id} por {data.dias_bloqueo} días hábiles",
        usuario_nombre=current_user.username,
    )
    db.add(historial)

    s.estado = EstadoSolicitud.BLOQUEADO.value
    s.rat_id = data.rat_id
    s.plazo_bloqueo_vencimiento = _calcular_fecha_vencimiento(data.dias_bloqueo)
    rat.bloqueado = True
    db.commit()
    return {
        "ok": True,
        "rat_id": rat.id,
        "bloqueado": True,
        "plazo_vencimiento": s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
    }


@router.post("/{solicitud_id}/desbloquear", summary="Desbloquear un RAT antes del vencimiento (REC-01)")
def desbloquear_rat(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")

    if s.estado != EstadoSolicitud.BLOQUEADO.value:
        raise HTTPException(status_code=400, detail="Esta solicitud no está en estado bloqueado")

    rat_id = s.rat_id
    if rat_id:
        from app.models.rat import RAT as RATModel
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


@router.get("/{solicitud_id}/portabilidad/export", summary="Exportar datos de portabilidad en JSON (Art. 9 — REC-04)")
def exportar_portabilidad(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    s = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if s.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta solicitud")

    if s.tipo != TipoSolicitud.PORTABILIDAD.value:
        raise HTTPException(status_code=400, detail="Esta solicitud no es de portabilidad")

    from datetime import datetime, timezone
    exportado_en = datetime.now(timezone.utc)

    return PortabilidadResponse(
        id=s.id,
        company_id=s.company_id,
        tipo=s.tipo,
        nombre_titular=s.nombre_titular,
        rut_titular=s.rut_titular,
        email_titular=s.email_titular,
        descripcion=s.descripcion,
        estado=s.estado,
        solicitud_fecha=s.solicitud_fecha.isoformat() if s.solicitud_fecha else None,
        respuesta=s.respuesta,
        respuesta_fecha=s.respuesta_fecha.isoformat() if s.respuesta_fecha else None,
        created_at=s.created_at.isoformat() if s.created_at else None,
        rat_id=s.rat_id,
        plazo_bloqueo_vencimiento=s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
        exportado_en=exportado_en.isoformat(),
    )


def _calcular_fecha_vencimiento(dias: int) -> datetime:
    """Calcula la fecha de vencimiento del bloqueo sumando días hábiles (lunes a viernes)."""
    from datetime import datetime, timezone, timedelta
    hoy = datetime.now(timezone.utc)
    dias_habiles = 0
    dia_actual = hoy
    while dias_habiles < dias:
        dia_actual += timedelta(days=1)
        if dia_actual.weekday() < 5:
            dias_habiles += 1
    return dia_actual
