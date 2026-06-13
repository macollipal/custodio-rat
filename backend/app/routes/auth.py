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
from app.core.security import (
    revoke_token, create_refresh_token, decode_refresh_token,
)
from app.core.config import settings
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Autenticación"])

COOKIE_NAME = "custodio_token"
REFRESH_COOKIE_NAME = "custodio_refresh"
COOKIE_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _cookie_options(max_age: int = None) -> dict:
    return {
        "max_age": max_age or COOKIE_MAX_AGE,
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "path": "/",
    }


@router.post("/login", response_model=Token, summary="Iniciar sesión")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: Session = Depends(get_db), response: Response = None):
    """
    Autentica un usuario, retorna access token (8h) + refresh token (30d) y setea cookies httpOnly.
    El access token se renueva automaticamente con el refresh token.
    """
    result = authenticate_user(db, data.username, data.password)
    if response is not None:
        response.set_cookie(COOKIE_NAME, result.access_token, **_cookie_options())
        if result.refresh_token:
            response.set_cookie(REFRESH_COOKIE_NAME, result.refresh_token, **_cookie_options(REFRESH_COOKIE_MAX_AGE))
    return result


@router.post("/refresh", response_model=Token, summary="Refrescar access token")
@limiter.limit("30/minute")
async def refresh_token(request: Request, db: Session = Depends(get_db), response: Response = None):
    """
    Intercambia un refresh token valido por un nuevo access token + refresh token.
    Implementa rotacion de refresh tokens: el antiguo se revoca y se emite uno nuevo.
    """
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="No se proporciono refresh token.")

    payload = decode_refresh_token(token, db)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token invalido o expirado.")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Refresh token invalido.")

    from app.models.user import User
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo.")

    # Revocar el refresh token antiguo (rotacion)
    revoke_token(token, db)

    # Emitir nuevos tokens
    from app.services.user_service import create_token_response
    result = create_token_response(db, user)

    if response is not None:
        response.set_cookie(COOKIE_NAME, result.access_token, **_cookie_options())
        if result.refresh_token:
            response.set_cookie(REFRESH_COOKIE_NAME, result.refresh_token, **_cookie_options(REFRESH_COOKIE_MAX_AGE))

    return result


@router.post("/logout", summary="Cerrar sesión")
@limiter.limit("10/minute")
async def logout(request: Request, response: Response = None, db: Session = Depends(get_db)):
    """Revoca ambos tokens (access + refresh) y elimina las cookies de sesion."""
    access_token = request.cookies.get(COOKIE_NAME)
    if not access_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header[7:]
    if access_token:
        revoke_token(access_token, db)

    refresh_tok = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_tok:
        revoke_token(refresh_tok, db)

    if response is not None:
        response.delete_cookie(COOKIE_NAME, path="/")
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return {"message": "Sesion cerrada correctamente."}


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