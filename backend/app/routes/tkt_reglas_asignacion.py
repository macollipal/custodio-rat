from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.tkt_regla_asignacion import TktReglaAsignacion
from app.schemas.tkt_regla_asignacion import (
    TktReglaAsignacionCreate,
    TktReglaAsignacionUpdate,
    TktReglaAsignacionResponse,
)
from app.services.user_company_service import get_empresas_usuario
from app.services.audit_service import log_audit
import logging

router = APIRouter(prefix="/tkt-reglas-asignacion", tags=["TKT - Reglas de Asignación"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[TktReglaAsignacionResponse])
def listar_reglas(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden ver reglas")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            return []
        if company_id is None:
            company_id = empresas[0]
        if company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    q = db.query(TktReglaAsignacion)
    if company_id is not None:
        q = q.filter(
            (TktReglaAsignacion.company_id == company_id) | (TktReglaAsignacion.company_id.is_(None))
        )
    else:
        q = q.filter(TktReglaAsignacion.company_id.is_(None))

    reglas = q.order_by(TktReglaAsignacion.orden, TktReglaAsignacion.id).all()
    return [TktReglaAsignacionResponse.model_validate(r) for r in reglas]


@router.get("/{regla_id}", response_model=TktReglaAsignacionResponse)
def obtener_regla(
    regla_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden ver reglas")

    regla = db.query(TktReglaAsignacion).filter(TktReglaAsignacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if regla.company_id and regla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta regla")

    return TktReglaAsignacionResponse.model_validate(regla)


@router.post("/", response_model=TktReglaAsignacionResponse)
def crear_regla(
    data: TktReglaAsignacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden crear reglas")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if data.company_id and data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa")

    from app.models.user import User
    user_exists = db.query(User).filter(User.id == data.responsable_id).first()
    if not user_exists:
        raise HTTPException(status_code=400, detail="El usuario responsable no existe")

    if data.company_id is not None:
        from app.models.company import Company
        company_exists = db.query(Company).filter(Company.id == data.company_id).first()
        if not company_exists:
            raise HTTPException(status_code=400, detail="La empresa no existe")

    regla = TktReglaAsignacion(
        company_id=data.company_id,
        tipo=data.tipo,
        prioridad=data.prioridad,
        responsable_id=data.responsable_id,
        activo=data.activo,
        orden=data.orden,
    )
    db.add(regla)
    db.commit()
    db.refresh(regla)
    log_audit(
        db=db,
        entidad="tkt_regla_asignacion",
        entidad_id=regla.id,
        accion="create",
        usuario=current_user.username,
        detalle={"tipo": data.tipo, "prioridad": data.prioridad, "responsable_id": data.responsable_id},
    )
    return TktReglaAsignacionResponse.model_validate(regla)


@router.put("/{regla_id}", response_model=TktReglaAsignacionResponse)
def actualizar_regla(
    regla_id: int,
    data: TktReglaAsignacionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden editar reglas")

    regla = db.query(TktReglaAsignacion).filter(TktReglaAsignacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if regla.company_id and regla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta regla")

    if data.company_id is not None:
        # Verificar que el nuevo company_id también es accesible por este usuario.
        # empresas ya fue cargado arriba si no es superadmin.
        if current_user.rol_global != "superadmin" and data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a la empresa destino.")
        regla.company_id = data.company_id
    if data.tipo is not None:
        regla.tipo = data.tipo
    if data.prioridad is not None:
        regla.prioridad = data.prioridad
    if data.responsable_id is not None:
        from app.models.user import User
        user_exists = db.query(User).filter(User.id == data.responsable_id).first()
        if not user_exists:
            raise HTTPException(status_code=400, detail="El usuario responsable no existe")
        regla.responsable_id = data.responsable_id
    if data.activo is not None:
        regla.activo = data.activo
    if data.orden is not None:
        regla.orden = data.orden

    db.commit()
    db.refresh(regla)
    log_audit(
        db=db,
        entidad="tkt_regla_asignacion",
        entidad_id=regla.id,
        accion="update",
        usuario=current_user.username,
        detalle={"campos_actualizados": data.model_dump(exclude_unset=True)},
    )
    return TktReglaAsignacionResponse.model_validate(regla)


@router.delete("/{regla_id}")
def eliminar_regla(
    regla_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "usuario":
        raise HTTPException(status_code=403, detail="Solo admin_empresa o superadmin pueden eliminar reglas")

    regla = db.query(TktReglaAsignacion).filter(TktReglaAsignacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada")

    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if regla.company_id and regla.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No tiene acceso a esta regla")

    db.delete(regla)
    db.commit()
    log_audit(
        db=db,
        entidad="tkt_regla_asignacion",
        entidad_id=regla_id,
        accion="delete",
        usuario=current_user.username,
        detalle={},
    )
    return {"ok": True}
