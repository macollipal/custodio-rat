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


def _anonymize_ip(ip: str) -> str:
    if not ip or ip in ('unknown', '127.0.0.1'):
        return ip
    parts = ip.split('.')
    if len(parts) == 4:
        return f"***.***.***.{parts[3]}"
    return '***'


def _generate_token(db: Session, ip_address: Optional[str] = None) -> str:
    token = str(uuid.uuid4())
    db_token = SolicitudToken(token=token, ip_address=ip_address)
    db.add(db_token)
    db.commit()
    return token


def _validate_token(db: Session, token: str) -> bool:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=5)
    row = db.query(SolicitudToken).filter(
        SolicitudToken.token == token,
        not SolicitudToken.used,
        SolicitudToken.created_at > cutoff
    ).first()
    if not row:
        return False
    row.used = True
    db.flush()
    return True


class SolicitudCreate(BaseModel):
    company_id: int
    tipo: str
    nombre_titular: str
    rut_titular: Optional[str] = None
    email_titular: EmailStr
    descripcion: Optional[str] = None
    token: str
    representante_nombre: Optional[str] = None
    representante_rut: Optional[str] = None

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
    rat_id: Optional[int] = None
    plazo_bloqueo_vencimiento: Optional[str] = None
    # S2.4: campos compliance Ley 21.719 (Art. 12, 12.5)
    metodo_verificacion_identidad: Optional[str] = None
    evidencia_identidad: Optional[str] = None
    evidencia_respuesta_hash: Optional[str] = None
    causal_rechazo: Optional[str] = None
    medio_respuesta: Optional[str] = None
    representante_nombre: Optional[str] = None
    representante_rut: Optional[str] = None
    tracking_token: Optional[str] = None
    acuse_enviado_at: Optional[str] = None


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
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type.lower():
        body = await request.json()
        company_id_val = body.get("company_id")
        tipo = body.get("tipo")
        nombre_titular = body.get("nombre_titular")
        rut_titular = body.get("rut_titular")
        email_titular = body.get("email_titular")
        descripcion = body.get("descripcion")
        token = body.get("token")
        representante_nombre = body.get("representante_nombre")
        representante_rut = body.get("representante_rut")
        files_data = None
    else:
        form = await request.form()
        company_id_val = form.get("company_id")
        tipo = form.get("tipo")
        nombre_titular = form.get("nombre_titular")
        rut_titular = form.get("rut_titular")
        email_titular = form.get("email_titular")
        descripcion = form.get("descripcion")
        token = form.get("token")
        representante_nombre = form.get("representante_nombre")
        representante_rut = form.get("representante_rut")
        files_data = [f for f in form.getlist("files") if f] if "files" in form else None

    if not token or not _validate_token(db, token):
        return JSONResponse(status_code=400, content={"detail": "Token inválido o expirado. Recargá la página e intentá de nuevo."})

    try:
        company_id_int = int(company_id_val)
        if company_id_int <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"detail": "company_id es obligatorio y debe ser mayor a 0."})

    valid_types = [e.value for e in TipoSolicitud]
    if tipo not in valid_types:
        return JSONResponse(status_code=400, content={"detail": f"tipo debe ser uno de: {valid_types}"})

    if not nombre_titular or not nombre_titular.strip():
        return JSONResponse(status_code=400, content={"detail": "nombre_titular es obligatorio."})

    if not email_titular or not email_titular.strip():
        return JSONResponse(status_code=400, content={"detail": "email_titular es obligatorio."})

    company = db.query(Company).filter(Company.id == company_id_int).first()
    if not company:
        return JSONResponse(status_code=400, content={"detail": "Datos inválidos. Verificá los datos ingresados e intentá de nuevo."})

    ticket = crear_ticket_desde_solicitud(
        db=db,
        company_id=company_id_int,
        tipo=tipo,
        titular_nombre=nombre_titular,
        titular_email=email_titular,
        descripcion=descripcion,
        titular_rut=rut_titular,
        origen="web",
        company_nombre=company.nombre,
        representante_nombre=representante_nombre,
        representante_rut=representante_rut,
    )

    # S2.2: crear también la fila legacy ``SolicitudDerecho`` en la misma
    # transacción, vinculada 1:1 al TKT. Mantener la legacy permite conservar
    # historial mientras se deprecua gradualmente.
    try:
        from app.models.solicitud_derecho import SolicitudDerecho
        legacy = SolicitudDerecho(
            id=ticket.id,  # comparte id para facilitar join histórico
            company_id=company_id_int,
            tipo=tipo,
            nombre_titular=nombre_titular,
            rut_titular=rut_titular,
            email_titular=email_titular,
            descripcion=descripcion,
            estado="pendiente",
            solicitud_fecha=ticket.fecha_recepcion or datetime.now(timezone.utc),
            rat_id=ticket.rat_id,
        )
        db.add(legacy)
        db.flush()
    except Exception as e:
        # Si falla la legacy no bloqueamos al titular — el TKT ya está creado.
        logger.warning(f"No se pudo crear SolicitudDerecho legacy para ticket {ticket.id}: {e}")
        db.rollback()
        # recomiteamos el TKT ya persistido
        db.commit()

    if files_data:
        from app.models.tkt_adjunto import TktAdjunto
        allowed_types = {"image/jpeg", "image/png", "image/gif", "application/pdf"}
        max_size = 5 * 1024 * 1024
        for f in files_data[:5]:
            filename = getattr(f, "filename", "archivo") or "archivo"
            content_type_file = getattr(f, "content_type", None) or "application/octet-stream"
            file_bytes = await f.read()
            if len(file_bytes) > max_size:
                return JSONResponse(status_code=400, content={"detail": f"El archivo '{filename}' supera el límite de 5MB."})
            if content_type_file not in allowed_types:
                return JSONResponse(status_code=400, content={"detail": f"El archivo '{filename}' tiene tipo no permitido. Solo PDF, JPEG, PNG o GIF."})
            adjunto = TktAdjunto(
                ticket_id=ticket.id,
                filename=filename,
                content_type=content_type_file,
                data=file_bytes,
            )
            db.add(adjunto)
        db.commit()

    logger.info(f"Solicitud ARCO creada (TKT only): company={company_id_int} tipo={tipo} ticket_id={ticket.id} ip={_anonymize_ip(request.client.host if request.client else 'unknown')}")
    return {
        "id": ticket.id,
        "company_id": company_id_int,
        "tipo": tipo,
        "nombre_titular": nombre_titular,
        "rut_titular": rut_titular,
        "email_titular": email_titular,
        "descripcion": descripcion,
        "estado": "abierto",
        "solicitud_fecha": ticket.fecha_recepcion.isoformat() if ticket.fecha_recepcion else None,
        "respuesta": None,
        "respuesta_fecha": None,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "tracking_token": ticket.tracking_token,
        "acuse_enviado_at": ticket.acuse_enviado_at.isoformat() if ticket.acuse_enviado_at else None,
        "representante_nombre": representante_nombre,
        "representante_rut": representante_rut,
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
                rat_id=s.rat_id,
                plazo_bloqueo_vencimiento=s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
                metodo_verificacion_identidad=s.metodo_verificacion_identidad,
                evidencia_identidad=s.evidencia_identidad,
                evidencia_respuesta_hash=s.evidencia_respuesta_hash,
                causal_rechazo=s.causal_rechazo,
                medio_respuesta=s.medio_respuesta,
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
        rat_id=s.rat_id,
        plazo_bloqueo_vencimiento=s.plazo_bloqueo_vencimiento.isoformat() if s.plazo_bloqueo_vencimiento else None,
        metodo_verificacion_identidad=s.metodo_verificacion_identidad,
        evidencia_identidad=s.evidencia_identidad,
        evidencia_respuesta_hash=s.evidencia_respuesta_hash,
        causal_rechazo=s.causal_rechazo,
        medio_respuesta=s.medio_respuesta,
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
    """S2.3: delega al service ``responder_solicitud`` (legacy router) que ya
    enruta hacia ``responder_ticket_service`` cuando hay TKT vinculado.
    """
    from app.services.solicitud_derecho_service import (
        EstadoInvalidoError,
        SinAccesoError,
        SolicitudNotFoundError,
        responder_solicitud as responder_solicitud_service,
    )
    try:
        responder_solicitud_service(
            db=db,
            solicitud_id=solicitud_id,
            estado=data.estado,
            respuesta=data.respuesta,
            descripcion_accion=data.descripcion_accion,
            current_user=current_user,
        )
    except SolicitudNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SinAccesoError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except EstadoInvalidoError as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    """Calcula la fecha de vencimiento del bloqueo sumando días hábiles (lunes a viernes, considera feriados Chile).

    Usa el helper centralizado ``ticket_service.calcular_dias_habiles`` que tiene
    hardcodeados los feriados fijos y Semana Santa 2025-2040.
    """
    from app.services.ticket_service import calcular_dias_habiles
    from datetime import datetime, timezone

    hoy = datetime.now(timezone.utc)
    return calcular_dias_habiles(hoy, dias)


@router.get("/tracking/{tracking_token}", summary="Consulta pública de estado por tracking token")
def consultar_tracking_publico(
    tracking_token: str,
    db: Session = Depends(get_db),
):
    """Permite al titular consultar el estado de su solicitud ARCO mediante el tracking token.

    Endpoint público (sin auth) - solo expone campos seguros (sin representante,
    sin archivos). Devuelve información mínima para proteger PII.

    Art. 14 Ley 21.719 — el titular tiene derecho a conocer el estado de su solicitud.
    """
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho

    ticket = (
        db.query(TktSolicitudDerecho)
        .filter(TktSolicitudDerecho.tracking_token == tracking_token)
        .first()
    )
    if not ticket:
        return JSONResponse(
            status_code=404,
            content={"detail": "Tracking token no encontrado. Verificá el número e intentá de nuevo."},
        )

    ahora = datetime.now(timezone.utc)
    fecha_vencimiento = ticket.fecha_vencimiento
    dias_restantes = None
    vencido = False
    if fecha_vencimiento:
        if fecha_vencimiento.tzinfo is None:
            fecha_vencimiento = fecha_vencimiento.replace(tzinfo=timezone.utc)
        delta = fecha_vencimiento - ahora
        dias_restantes = delta.days
        vencido = dias_restantes < 0 and ticket.estado not in ("resuelto", "rechazado")

    ultima_accion = None
    if ticket.historial:
        ultima_accion = ticket.historial[-1].fecha.isoformat() if ticket.historial[-1].fecha else None

    return {
        "tracking_token": ticket.tracking_token,
        "estado": ticket.estado,
        "tipo": ticket.tipo,
        "titular_nombre": ticket.titular_nombre,
        "fecha_recepcion": ticket.fecha_recepcion.isoformat() if ticket.fecha_recepcion else None,
        "fecha_vencimiento": ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        "dias_restantes": dias_restantes,
        "vencido": vencido,
        "respuesta_texto": ticket.respuesta_texto if ticket.estado == "resuelto" else None,
        "evidencia_respuesta_hash": ticket.evidencia_respuesta_hash if ticket.estado == "resuelto" else None,
        "ultima_accion": ultima_accion,
    }
