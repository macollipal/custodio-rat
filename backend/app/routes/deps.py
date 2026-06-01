"""
Dependencias compartidas entre rutas: extracción y validación del token JWT.
Acepta token desde cookie (httpOnly) o desde Authorization header (Bearer).
"""

import re
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.core.security import decode_access_token
from app.services.user_service import get_current_user as _get_current_user

bearer_scheme = HTTPBearer(auto_error=False)
COOKIE_NAME = "custodio_token"


_IPV4_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
_IPV6_RE = re.compile(r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')


def get_client_ip(request: Request) -> str:
    """Extrae y valida la IP real del cliente desde x-forwarded-for o request.client."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        if _IPV4_RE.match(ip) or _IPV6_RE.match(ip):
            return ip
    return request.client.host if request.client else "desconocida"


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = None

    if credentials is not None:
        token = credentials.credentials
    elif COOKIE_NAME in request.cookies:
        token = request.cookies[COOKIE_NAME]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado. Inicie sesión.",
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado o revocado. Inicie sesión nuevamente.",
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
    """
    Exige rol editor/admin en la empresa. Admin global o admin_empresa siempre pasa.
    NOTA: Esta función se llama manualmente con argumentos posicionales.
    No es una dependencia FastAPI estándar (no se puede usar con Depends()).
    """
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
    """
    Exige rol admin en la empresa. Admin global o admin_empresa siempre pasa.
    NOTA: Esta función se llama manualmente con argumentos posicionales.
    No es una dependencia FastAPI estándar (no se puede usar con Depends()).
    """
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