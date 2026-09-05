"""
Service para ModulePermission — feature gates por empresa y modulo.

Logica:
- Si no existe fila para (company, modulo), modulo esta enabled (opt-out)
- Si existe enabled=False, modulo esta deshabilitado
- get_active_modules() retorna lista de modulos activos (para sidebar/menu)
- bulk_update() permite activar/desactivar varios modulos a la vez
"""
from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.module_permission import ModuloEnum, ModulePermission


ALL_MODULOS = [
    ModuloEnum.RAT,
    ModuloEnum.ARCO,
    ModuloEnum.BRECHAS,
    ModuloEnum.EIPD,
    ModuloEnum.CONSENTIMIENTOS,
    ModuloEnum.ENCARGADOS,
    ModuloEnum.TRANSPARENCIA,
    ModuloEnum.REPORTES,
    ModuloEnum.ASESOR,
]


def is_module_enabled(db: Session, company_id: int, modulo: str) -> bool:
    """Retorna True si el modulo esta activo para la empresa (default: True)."""
    if modulo not in ALL_MODULOS:
        return True
    perm = (
        db.query(ModulePermission)
        .filter(ModulePermission.company_id == company_id, ModulePermission.modulo == modulo)
        .first()
    )
    if perm is None:
        return True
    return perm.enabled


def get_company_modules(db: Session, company_id: int) -> Dict[str, bool]:
    """Retorna dict {modulo: enabled} con TODOS los modulos."""
    perms = (
        db.query(ModulePermission)
        .filter(ModulePermission.company_id == company_id)
        .all()
    )
    perm_map = {p.modulo: p.enabled for p in perms}
    return {m: perm_map.get(m, True) for m in ALL_MODULOS}


def get_active_modules(db: Session, company_id: int) -> List[str]:
    """Retorna lista de modulos activos para la empresa (para sidebar/menu)."""
    mods = get_company_modules(db, company_id)
    return [m for m, enabled in mods.items() if enabled]


def set_module_enabled(db: Session, company_id: int, modulo: str, enabled: bool) -> ModulePermission:
    """Crea o actualiza el permiso de un modulo. Upsert."""
    if modulo not in ALL_MODULOS:
        raise HTTPException(status_code=400, detail=f"Modulo invalido: {modulo}")
    perm = (
        db.query(ModulePermission)
        .filter(ModulePermission.company_id == company_id, ModulePermission.modulo == modulo)
        .first()
    )
    if perm is None:
        perm = ModulePermission(company_id=company_id, modulo=modulo, enabled=enabled)
        db.add(perm)
    else:
        perm.enabled = enabled
    db.commit()
    db.refresh(perm)
    return perm


def bulk_update_modules(
    db: Session, company_id: int, updates: Dict[str, bool]
) -> Dict[str, bool]:
    """Actualiza varios modulos a la vez. Retorna estado final."""
    for modulo, enabled in updates.items():
        if modulo not in ALL_MODULOS:
            raise HTTPException(status_code=400, detail=f"Modulo invalido: {modulo}")
        set_module_enabled(db, company_id, modulo, enabled)
    return get_company_modules(db, company_id)


def require_module_enabled(db: Session, company_id: int, modulo: str) -> None:
    """Levanta HTTPException 403 si el modulo esta deshabilitado."""
    if not is_module_enabled(db, company_id, modulo):
        raise HTTPException(
            status_code=403,
            detail=f"El modulo {modulo} esta deshabilitado para esta empresa. Contacta al administrador.",
        )