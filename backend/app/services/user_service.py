"""
Lógica de negocio para usuarios y autenticación.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, RolGlobal
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, Token, UserOut


def is_admin(user: User) -> bool:
    return user.rol_global == RolGlobal.SUPERADMIN.value


def is_admin_empresa(user: User) -> bool:
    return user.rol_global == RolGlobal.ADMIN_EMPRESA.value


def can_access_company(user: User, company_id: int, db: Session) -> bool:
    """superadmin ve todo, admin_empresa/usuario solo su empresa."""
    if user.rol_global == RolGlobal.SUPERADMIN.value:
        return True
    from app.services.user_company_service import get_empresas_usuario
    return company_id in get_empresas_usuario(db, user.id)


def create_user(db: Session, data: UserCreate) -> User:
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está en uso.")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado.")
    if data.rol_global not in [r.value for r in RolGlobal]:
        raise HTTPException(status_code=400, detail="Rol global inválido.")

    if data.rol_global in ("admin_empresa", "usuario") and not data.company_ids:
        raise HTTPException(status_code=400, detail="Debes asignar al menos una empresa a este usuario.")

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        is_active=True,
        is_admin=data.rol_global == "superadmin",
        rol_global=data.rol_global,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if data.company_ids:
        from app.models.user_company import UserCompany, RolEmpresa
        for cid in data.company_ids:
            uc = UserCompany(
                user_id=user.id,
                company_id=cid,
                rol=RolEmpresa.ADMIN if data.rol_global == "admin_empresa" else RolEmpresa.EDITOR,
            )
            db.add(uc)
        db.commit()

    return user


def authenticate_user(db: Session, username: str, password: str) -> Token:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifique su usuario y contraseña.",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo. Contacte al administrador.")

    token, _ = create_access_token({"sub": user.username, "rol_global": user.rol_global})
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


def get_current_user(db: Session, token_data: dict) -> User:
    username = token_data.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return users, total


def update_user(db: Session, user_id: int, data: dict) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    new_company_id = data.pop("company_id", None)
    new_rol_global = data.get("rol_global")

    for key, value in data.items():
        if hasattr(user, key) and key != "hashed_password":
            setattr(user, key, value)

    if new_company_id and new_rol_global in ("admin_empresa", "usuario"):
        from app.models.user_company import UserCompany, RolEmpresa
        db.query(UserCompany).filter(UserCompany.user_id == user_id).delete()
        uc = UserCompany(
            user_id=user_id,
            company_id=new_company_id,
            rol=RolEmpresa.ADMIN if new_rol_global == "admin_empresa" else RolEmpresa.EDITOR,
        )
        db.add(uc)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    db.delete(user)
    db.commit()


def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres.")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user


def change_password_other(db: Session, user_id: int, new_password: str) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
