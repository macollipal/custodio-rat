from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.solicitud_derecho import SolicitudDerecho, TipoSolicitud, EstadoSolicitud
from app.models.solicitud_historial import SolicitudHistorial
from app.models.company import Company
from app.services.user_company_service import get_empresas_usuario

router = APIRouter(prefix="/solicitudes-derecho", tags=["Solicitudes de Derecho"])


class SolicitudCreate(BaseModel):
    company_id: int
    tipo: str
    nombre_titular: str
    rut_titular: Optional[str] = None
    email_titular: str
    descripcion: Optional[str] = None


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


@router.post("/", response_model=SolicitudResponse)
def crear_solicitud(
    data: SolicitudCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from datetime import datetime, timezone

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

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
    return SolicitudResponse(
        id=solicitud.id,
        company_id=solicitud.company_id,
        tipo=solicitud.tipo,
        nombre_titular=solicitud.nombre_titular,
        rut_titular=solicitud.rut_titular,
        email_titular=solicitud.email_titular,
        descripcion=solicitud.descripcion,
        estado=solicitud.estado,
        solicitud_fecha=solicitud.solicitud_fecha.isoformat() if solicitud.solicitud_fecha else None,
        respuesta=solicitud.respuesta,
        respuesta_fecha=solicitud.respuesta_fecha.isoformat() if solicitud.respuesta_fecha else None,
        created_at=solicitud.created_at.isoformat() if solicitud.created_at else None,
    )


@router.get("/", response_model=list[SolicitudResponse])
def listar_solicitudes(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
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
    solicitudes = q.order_by(SolicitudDerecho.solicitud_fecha.desc()).all()
    return [
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
    ]


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
        usuario_nombre=data.usuario_nombre,
    )
    db.add(historial)

    s.estado = data.estado
    s.respuesta = data.respuesta
    s.respuesta_fecha = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
