"""
Endpoints para ModulePermission — feature gates por empresa.

Solo superadmin puede listar/modificar. Usuarios con acceso a la
empresa pueden consultar el estado de los modulos (read-only).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.models.user import User
from app.models.company import Company
from app.schemas.module_permission import (
    ActiveModulesOut,
    CompanyModulesOut,
    ModuleBulkUpdateIn,
    ModuleStatusOut,
    ModuleToggleIn,
)
from app.services import module_permission_service as svc

router = APIRouter(prefix="/module-permissions", tags=["module-permissions"])


def _require_superadmin(user: User) -> None:
    if user.rol_global != "superadmin":
        raise HTTPException(status_code=403, detail="Requiere rol superadmin")


def _user_has_company_access(db: Session, user_id: int, company_id: int) -> bool:
    if user_id is None:
        return False
    from app.services.user_company_service import get_empresas_usuario
    return company_id in get_empresas_usuario(db, user_id)


@router.get(
    "/{company_id}",
    response_model=CompanyModulesOut,
    summary="Obtener estado de modulos de una empresa",
)
def get_modules(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol_global == "superadmin" or _user_has_company_access(db, current_user.id, company_id):
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return CompanyModulesOut(company_id=company_id, modules=svc.get_company_modules(db, company_id))
    raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa")


@router.get(
    "/{company_id}/active",
    response_model=ActiveModulesOut,
    summary="Lista de modulos activos (para sidebar/menu)",
)
def get_active(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.rol_global != "superadmin" and not _user_has_company_access(db, current_user.id, company_id):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa")
    return ActiveModulesOut(company_id=company_id, active_modules=svc.get_active_modules(db, company_id))


@router.put(
    "/{company_id}/{modulo}",
    response_model=ModuleStatusOut,
    summary="Activar/desactivar un modulo (solo superadmin)",
)
def toggle_module(
    company_id: int,
    modulo: str,
    payload: ModuleToggleIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_superadmin(current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    perm = svc.set_module_enabled(db, company_id, modulo, payload.enabled)
    return ModuleStatusOut(modulo=perm.modulo, enabled=perm.enabled)


@router.put(
    "/{company_id}",
    response_model=CompanyModulesOut,
    summary="Actualizar varios modulos a la vez (solo superadmin)",
)
def bulk_update(
    company_id: int,
    payload: ModuleBulkUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_superadmin(current_user)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    modules = svc.bulk_update_modules(db, company_id, payload.modules)
    return CompanyModulesOut(company_id=company_id, modules=modules)