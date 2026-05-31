"""
Endpoints de autenticación: login, registro de usuarios (solo admin) y perfil.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.user import LoginRequest, PasswordChange, PasswordChangeOther, Token, UserCreate, UserOut, UserUpdate
from app.services.user_service import (
    authenticate_user, change_password, create_user, get_users,
    update_user, delete_user, change_password_other,
)
from app.services.user_company_service import get_empresas_usuario
from app.routes.deps import get_current_user, require_admin
from app.core.security import revoke_token
from app.core.config import settings
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Autenticación"])

COOKIE_NAME = "custodio_token"
COOKIE_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def _cookie_options() -> dict:
    return {
        "max_age": COOKIE_MAX_AGE,
        "httponly": True,
        "secure": True,
        "samesite": "none" if settings.ENVIRONMENT == "production" else "lax",
        "path": "/",
    }


@router.post("/login", response_model=Token, summary="Iniciar sesión")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: Session = Depends(get_db), response: Response = None):
    """
    Autentica un usuario, retorna el token y setea una cookie httpOnly.
    El token tiene validez de 8 horas.
    """
    result = authenticate_user(db, data.username, data.password)
    if response is not None:
        response.set_cookie(COOKIE_NAME, result.access_token, **_cookie_options())
    return result


@router.post("/logout", summary="Cerrar sesión")
@limiter.limit("10/minute")
async def logout(request: Request, response: Response = None, db: Session = Depends(get_db)):
    """Revoca el token y elimina la cookie de sesión."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if token:
        revoke_token(token, db)
    if response is not None:
        response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "Sesión cerrada correctamente."}


@router.get("/me", response_model=UserOut, summary="Perfil del usuario actual")
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserOut, summary="Crear nuevo usuario (solo admin)")
async def crear_usuario(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Crea un nuevo usuario. Solo administradores pueden crear usuarios."""
    return create_user(db, data)


@router.put("/users/{user_id}", response_model=UserOut, summary="Actualizar usuario (solo admin)")
async def actualizar_usuario(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return update_user(db, user_id, data.model_dump(exclude_none=True))


@router.delete("/users/{user_id}", summary="Eliminar usuario (solo admin)")
async def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    delete_user(db, user_id)
    return {"message": "Usuario eliminado correctamente."}


@router.put("/users/{user_id}/password", summary="Cambiar contraseña de otro usuario (solo admin)")
async def cambiar_password_otro(
    user_id: int,
    data: PasswordChangeOther,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")
    change_password_other(db, user_id, data.new_password)
    return {"message": "Contraseña actualizada correctamente."}


@router.put("/me/password", response_model=UserOut, summary="Cambiar contraseña del usuario actual")
@limiter.limit("5/minute")
async def cambiar_password(
    request: Request,
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return change_password(db, current_user, data.current_password, data.new_password)


@router.get("/users", summary="Listar usuarios (solo admin)")
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    users, total = get_users(db, skip=skip, limit=limit)
    result = []
    for u in users:
        empresas = get_empresas_usuario(db, u.id)
        empresa_nombre = None
        empresa_id = None
        if empresas:
            from app.models.company import Company
            company = db.query(Company).filter(Company.id == empresas[0]).first()
            if company:
                empresa_nombre = company.nombre
                empresa_id = empresas[0]
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "rol_global": u.rol_global,
            "created_at": u.created_at,
            "empresa_id": empresa_id,
            "empresa_nombre": empresa_nombre,
        })
    return {"usuarios": result, "total": total, "skip": skip, "limit": limit}