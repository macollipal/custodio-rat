"""
Endpoints para gestionar qué usuarios tienen acceso a qué empresa.
Accesibles por admin global o admin de la empresa.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user_company import UserCompanyCreate, UserCompanyOut, UserCompanyUpdate
from app.schemas.common import MessageResponse
from app.services.user_company_service import (
    agregar_acceso, actualizar_rol, listar_accesos, remover_acceso, get_rol_usuario,
)
from app.models.user_company import RolEmpresa
from app.routes.deps import get_current_user

router = APIRouter(prefix="/companies/{company_id}/usuarios", tags=["Accesos por empresa"])


def _require_company_admin(db: Session, user, company_id: int):
    if user.rol_global in ("superadmin", "admin_empresa"):
        return
    rol = get_rol_usuario(db, user.id, company_id)
    if rol != RolEmpresa.ADMIN:
        raise HTTPException(status_code=403, detail="Se requiere rol administrador en esta empresa.")


@router.get("/", response_model=list[UserCompanyOut], summary="Listar usuarios con acceso a la empresa")
async def listar(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return listar_accesos(db, company_id)


@router.post("/", response_model=UserCompanyOut, status_code=201, summary="Dar acceso a un usuario")
async def agregar(
    company_id: int,
    data: UserCompanyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_company_admin(db, current_user, company_id)
    return agregar_acceso(db, company_id, data)


@router.put("/{user_id}", response_model=UserCompanyOut, summary="Cambiar rol de un usuario")
async def actualizar(
    company_id: int,
    user_id: int,
    data: UserCompanyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_company_admin(db, current_user, company_id)
    return actualizar_rol(db, company_id, user_id, data)


@router.delete("/{user_id}", response_model=MessageResponse, summary="Remover acceso de un usuario")
async def remover(
    company_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_company_admin(db, current_user, company_id)
    remover_acceso(db, company_id, user_id)
    return MessageResponse(message=f"Acceso del usuario {user_id} removido de la empresa {company_id}.")
