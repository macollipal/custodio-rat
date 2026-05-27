"""
Endpoints para Ejercicio de Derechos ARCO (Acceso, Rectificación, Cancelación, Oposición).
Art. 12 y 14 Ley 21.719.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.solicitud_derecho import SolicitudDerecho, TipoSolicitud, EstadoSolicitud
from app.schemas.solicitud_derecho import (
    SolicitudDerechoCreate,
    SolicitudDerechoOut,
    SolicitudDerechoUpdate,
)
from app.services.user_company_service import get_empresas_usuario
from app.routes.deps import get_current_user

router = APIRouter(prefix="/solicitudes-derecho", tags=["Ejercicio de Derechos"])


def _check_company_access(current_user, company_id: int, db: Session):
    if current_user.rol_global == "superadmin":
        return
    if company_id not in get_empresas_usuario(db, current_user.id):
        raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")


def _validar_tipo(tipo: str) -> TipoSolicitud:
    try:
        return TipoSolicitud(tipo)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Use: {', '.join(t.value for t in TipoSolicitud)}",
        )


def _validar_estado(estado: str) -> EstadoSolicitud:
    try:
        return EstadoSolicitud(estado)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Use: {', '.join(e.value for e in EstadoSolicitud)}",
        )


@router.post("/", response_model=SolicitudDerechoOut, status_code=status.HTTP_201_CREATED, summary="Crear solicitud de ejercicio de derechos")
async def crear(
    data: SolicitudDerechoCreate,
    db: Session = Depends(get_db),
):
    from app.models.company import Company
    empresa = db.query(Company).filter(Company.id == data.company_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    tipo = _validar_tipo(data.tipo)
    solicitud = SolicitudDerecho(
        company_id=data.company_id,
        tipo=tipo,
        nombre_titular=data.nombre_titular,
        email_titular=data.email_titular,
        rut_titular=data.rut_titular,
        descripcion=data.descripcion,
        estado=EstadoSolicitud.PENDIENTE,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    empresa_nombre = empresa.nombre if empresa else "Empresa"
    from app.services.email_service import notificar_cambio_estado_solicitud, notificar_nueva_solicitud_arco
    notificar_cambio_estado_solicitud(
        email_titular=solicitud.email_titular,
        nombre_titular=solicitud.nombre_titular,
        tipo_derecho=solicitud.tipo.value,
        estado="pendiente",
        respuesta="Tu solicitud ha sido recibida y se encuentra en estado Pendiente. Te notificaremos cuando sea procesada.",
        empresa_nombre=empresa_nombre,
    )
    if empresa and empresa.email_dpo:
        notificar_nueva_solicitud_arco(
            email_dpo=empresa.email_dpo,
            nombre_dpo=empresa.contacto_dpo or "",
            nombre_titular=solicitud.nombre_titular,
            tipo_derecho=solicitud.tipo.value,
            empresa_nombre=empresa_nombre,
        )
    return solicitud


@router.get("/", response_model=list[SolicitudDerechoOut], summary="Listar solicitudes de una empresa")
async def listar(
    company_id: int = Query(..., description="ID de la empresa"),
    estado: str = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_company_access(current_user, company_id, db)
    query = db.query(SolicitudDerecho).filter(SolicitudDerecho.company_id == company_id)
    if estado:
        estado_enum = _validar_estado(estado)
        query = query.filter(SolicitudDerecho.estado == estado_enum)
    return query.order_by(SolicitudDerecho.created_at.desc()).all()


@router.get("/{solicitud_id}", response_model=SolicitudDerechoOut, summary="Obtener solicitud por ID")
async def obtener(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    solicitud = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    _check_company_access(current_user, solicitud.company_id, db)
    return solicitud


@router.patch("/{solicitud_id}", response_model=SolicitudDerechoOut, summary="Actualizar estado o respuesta de una solicitud")
async def actualizar(
    solicitud_id: int,
    data: SolicitudDerechoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    solicitud = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    _check_company_access(current_user, solicitud.company_id, db)

    if data.estado:
        solicitud.estado = _validar_estado(data.estado)
    if data.respuesta is not None:
        solicitud.respuesta = data.respuesta
        if data.estado == EstadoSolicitud.RESUELTA.value or data.estado == EstadoSolicitud.RECHAZADA.value:
            solicitud.fecha_respuesta = datetime.now(timezone.utc)

    estado_anterior = solicitud.estado
    db.commit()
    db.refresh(solicitud)

    if data.estado and data.estado != estado_anterior.value:
        from app.models.company import Company
        empresa = db.query(Company).filter(Company.id == solicitud.company_id).first()
        empresa_nombre = empresa.nombre if empresa else "Empresa"
        from app.services.email_service import notificar_cambio_estado_solicitud
        notificar_cambio_estado_solicitud(
            email_titular=solicitud.email_titular,
            nombre_titular=solicitud.nombre_titular,
            tipo_derecho=solicitud.tipo.value,
            estado=data.estado,
            respuesta=data.respuesta or "",
            empresa_nombre=empresa_nombre,
        )

    return solicitud


@router.delete("/{solicitud_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar solicitud")
async def eliminar(
    solicitud_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    solicitud = db.query(SolicitudDerecho).filter(SolicitudDerecho.id == solicitud_id).first()
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    _check_company_access(current_user, solicitud.company_id, db)
    db.delete(solicitud)
    db.commit()
