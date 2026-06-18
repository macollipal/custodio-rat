"""
Endpoints administrativos de empresas (solo superadmin).
"""
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user, get_client_ip
from app.services.company_service import hard_delete_company
from app.models.user import User, RolGlobal


router = APIRouter(prefix="/admin/companies", tags=["Admin · Empresas"])


def require_superadmin(current_user: User) -> User:
    if current_user.rol_global != RolGlobal.SUPERADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo superadmin puede acceder a este endpoint.",
        )
    return current_user


class HardDeleteRequest(BaseModel):
    password: str


@router.post("/{company_id}/hard-delete", summary="Eliminar empresa permanentemente (superadmin + password)")
async def hard_delete(
    request: Request,
    company_id: int,
    body: HardDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_superadmin(current_user)
    return hard_delete_company(
        db=db,
        company_id=company_id,
        admin_username=current_user.username,
        admin_password=body.password,
        ip_origen=get_client_ip(request),
    )
