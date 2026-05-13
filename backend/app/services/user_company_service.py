"""
Lógica para gestionar el acceso de usuarios a empresas.
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.company import Company
from app.models.user_company import UserCompany, RolEmpresa
from app.schemas.user_company import UserCompanyCreate, UserCompanyOut, UserCompanyUpdate


def _get_company_or_404(db: Session, company_id: int) -> Company:
    c = db.query(Company).filter(Company.id == company_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Empresa no encontrada.")
    return c


def _get_user_by_username(db: Session, username: str) -> User:
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(status_code=404, detail=f"Usuario '{username}' no encontrado.")
    return u


def _to_out(uc: UserCompany) -> UserCompanyOut:
    return UserCompanyOut(
        id=uc.id,
        user_id=uc.user_id,
        company_id=uc.company_id,
        rol=uc.rol,
        created_at=uc.created_at,
        username=uc.user.username,
        full_name=uc.user.full_name,
        email=uc.user.email,
    )


def listar_accesos(db: Session, company_id: int) -> list[UserCompanyOut]:
    _get_company_or_404(db, company_id)
    ucs = db.query(UserCompany).filter(UserCompany.company_id == company_id).all()
    return [_to_out(uc) for uc in ucs]


def agregar_acceso(db: Session, company_id: int, data: UserCompanyCreate) -> UserCompanyOut:
    _get_company_or_404(db, company_id)
    user = _get_user_by_username(db, data.username)

    existing = db.query(UserCompany).filter(
        UserCompany.user_id == user.id,
        UserCompany.company_id == company_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"'{data.username}' ya tiene acceso a esta empresa.")

    uc = UserCompany(user_id=user.id, company_id=company_id, rol=data.rol)
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return _to_out(uc)


def actualizar_rol(db: Session, company_id: int, user_id: int, data: UserCompanyUpdate) -> UserCompanyOut:
    uc = db.query(UserCompany).filter(
        UserCompany.company_id == company_id,
        UserCompany.user_id == user_id,
    ).first()
    if not uc:
        raise HTTPException(status_code=404, detail="Acceso no encontrado.")
    uc.rol = data.rol
    db.commit()
    db.refresh(uc)
    return _to_out(uc)


def remover_acceso(db: Session, company_id: int, user_id: int) -> dict:
    uc = db.query(UserCompany).filter(
        UserCompany.company_id == company_id,
        UserCompany.user_id == user_id,
    ).first()
    if not uc:
        raise HTTPException(status_code=404, detail="Acceso no encontrado.")
    db.delete(uc)
    db.commit()
    return {"message": "Acceso removido correctamente."}


def get_empresas_usuario(db: Session, user_id: int) -> list[int]:
    """Retorna los IDs de empresa a los que el usuario tiene acceso."""
    ucs = db.query(UserCompany).filter(UserCompany.user_id == user_id).all()
    return [uc.company_id for uc in ucs]


def get_rol_usuario(db: Session, user_id: int, company_id: int) -> Optional[RolEmpresa]:
    uc = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id,
    ).first()
    return uc.rol if uc else None
