"""
Dependencias compartidas entre rutas: extracción y validación del token JWT.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import decode_access_token
from app.services.user_service import get_current_user as _get_current_user

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado. Inicie sesión nuevamente.",
        )
    return _get_current_user(db, payload)


def require_admin(current_user=Depends(get_current_user)):
    if current_user.rol_global != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción restringida a superadministradores.",
        )
    return current_user


def require_editor_or_admin_empresa(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Exige rol editor/admin en la empresa. Admin global o admin_empresa siempre pasa."""
    from app.services.user_company_service import get_rol_usuario
    from app.models.user_company import RolEmpresa

    if current_user.rol_global in ("superadmin", "admin_empresa"):
        return current_user
    rol = get_rol_usuario(db, current_user.id, company_id)
    if rol is None or rol == RolEmpresa.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol editor o administrador en esta empresa.",
        )
    return current_user


def require_company_admin(company_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Exige rol admin en la empresa. Admin global o admin_empresa siempre pasa."""
    from app.services.user_company_service import get_rol_usuario
    from app.models.user_company import RolEmpresa

    if current_user.rol_global in ("superadmin", "admin_empresa"):
        return current_user
    rol = get_rol_usuario(db, current_user.id, company_id)
    if rol != RolEmpresa.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador en esta empresa.",
        )
    return current_user