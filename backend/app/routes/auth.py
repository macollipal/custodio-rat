"""
Endpoints de autenticación: login, registro de usuarios (solo admin) y perfil.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import LoginRequest, PasswordChange, Token, UserCreate, UserOut
from app.services.user_service import (
    authenticate_user, change_password, create_user, get_users,
    update_user, delete_user, change_password_other,
)
from app.services.user_company_service import get_empresas_usuario
from app.routes.deps import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=Token, summary="Iniciar sesión")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna un token JWT de acceso.
    El token tiene validez de 8 horas.
    """
    return authenticate_user(db, data.username, data.password)


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
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return update_user(db, user_id, data)


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
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    new_password = data.get("new_password")
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")
    change_password_other(db, user_id, new_password)
    return {"message": "Contraseña actualizada correctamente."}


@router.put("/me/password", response_model=UserOut, summary="Cambiar contraseña del usuario actual")
async def cambiar_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return change_password(db, current_user, data.current_password, data.new_password)


@router.get("/users", summary="Listar usuarios (solo admin)")
async def listar_usuarios(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    users = get_users(db)
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
    return result