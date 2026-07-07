"""
Endpoints CRUD para el módulo de Plantillas de respuesta ARCO.
Ruta: /tkt-plantillas/
Solo admin_empresa y superadmin pueden gestionar plantillas.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.tkt_plantilla import TktPlantilla
from app.schemas.tkt_plantilla import (
    TktPlantillaCreate,
    TktPlantillaUpdate,
    TktPlantillaResponse,
)
from app.services.user_company_service import get_empresas_usuario
from app.services.audit_service import log_audit
import logging

router = APIRouter(prefix="/tkt-plantillas", tags=["TKT - Plantillas ARCO"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[TktPlantillaResponse])
def listar_plantillas(
    company_id: Optional[int] = None,
    tipo: Optional[str] = None,
    solo_activas: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista plantillas de respuesta. admin_empresa solo ve las de su empresa."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden ver plantillas")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            return []
        if company_id is None:
            company_id = empresas[0]
        if company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    total_systemwide = db.query(TktPlantilla).filter(TktPlantilla.company_id.is_(None)).count()
    if total_systemwide == 0:
        from app.services.plantilla_service import seed_plantillas_default
        seed_plantillas_default(db)

    q = db.query(TktPlantilla)
    if company_id is not None:
        q = q.filter(
            (TktPlantilla.company_id == company_id) | (TktPlantilla.company_id.is_(None))
        )
    if tipo:
        q = q.filter(TktPlantilla.tipo == tipo)
    if solo_activas:
        q = q.filter(TktPlantilla.activo)

    plantillas = q.order_by(TktPlantilla.tipo, TktPlantilla.nombre).all()
    return [TktPlantillaResponse.model_validate(p) for p in plantillas]


@router.get("/{plantilla_id}", response_model=TktPlantillaResponse)
def obtener_plantilla(
    plantilla_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Detalle de una plantilla."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden ver plantillas")

    plantilla = db.query(TktPlantilla).filter(TktPlantilla.id == plantilla_id).first()
    if not plantilla:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if plantilla.company_id and plantilla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta plantilla")

    return TktPlantillaResponse.model_validate(plantilla)


@router.post("/", response_model=TktPlantillaResponse)
def crear_plantilla(
    data: TktPlantillaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Crea una plantilla de respuesta."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden crear plantillas")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if data.company_id and data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    plantilla = TktPlantilla(
        company_id=data.company_id,
        tipo=data.tipo,
        nombre=data.nombre,
        contenido=data.contenido,
        activo=data.activo,
    )
    db.add(plantilla)
    db.commit()
    db.refresh(plantilla)
    log_audit(
        db=db,
        entidad="tkt_plantilla",
        entidad_id=plantilla.id,
        accion="create",
        usuario=current_user.username,
        detalle={"tipo": data.tipo, "nombre": data.nombre},
    )
    return TktPlantillaResponse.model_validate(plantilla)


@router.put("/{plantilla_id}", response_model=TktPlantillaResponse)
def actualizar_plantilla(
    plantilla_id: int,
    data: TktPlantillaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Actualiza una plantilla."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden editar plantillas")

    plantilla = db.query(TktPlantilla).filter(TktPlantilla.id == plantilla_id).first()
    if not plantilla:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if plantilla.company_id and plantilla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta plantilla")

    if data.tipo is not None:
        plantilla.tipo = data.tipo
    if data.nombre is not None:
        plantilla.nombre = data.nombre
    if data.contenido is not None:
        plantilla.contenido = data.contenido
    if data.activo is not None:
        plantilla.activo = data.activo

    db.commit()
    db.refresh(plantilla)
    log_audit(
        db=db,
        entidad="tkt_plantilla",
        entidad_id=plantilla.id,
        accion="update",
        usuario=current_user.username,
        detalle={"campos_actualizados": data.model_dump(exclude_unset=True)},
    )
    return TktPlantillaResponse.model_validate(plantilla)


@router.delete("/{plantilla_id}")
def eliminar_plantilla(
    plantilla_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Elimina una plantilla (solo superadmin o admin_empresa de la empresa owner)."""
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden eliminar plantillas")

    plantilla = db.query(TktPlantilla).filter(TktPlantilla.id == plantilla_id).first()
    if not plantilla:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if plantilla.company_id and plantilla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta plantilla")

    db.delete(plantilla)
    db.commit()
    log_audit(
        db=db,
        entidad="tkt_plantilla",
        entidad_id=plantilla_id,
        accion="delete",
        usuario=current_user.username,
        detalle={},
    )
    return {"ok": True}
