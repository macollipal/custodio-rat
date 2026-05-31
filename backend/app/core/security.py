"""
Utilidades de seguridad: hashing de contraseñas y manejo de JWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.resolved_secret_key, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.resolved_secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def revoke_token(token: str, db) -> bool:
    from app.models.token_blacklist import TokenBlacklist
    try:
        payload = jwt.decode(token, settings.resolved_secret_key, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
    except JWTError:
        return False
    jti = payload.get("jti")
    if not jti:
        return False
    exp = payload.get("exp")
    if not exp:
        return False
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    existing = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    if existing:
        return True
    entry = TokenBlacklist(jti=jti, expires_at=expires_at)
    db.add(entry)
    db.commit()
    return True


def cleanup_expired_tokens(db) -> int:
    from app.models.token_blacklist import TokenBlacklist
    from sqlalchemy import delete
    now = datetime.now(timezone.utc)
    result = db.execute(delete(TokenBlacklist).where(TokenBlacklist.expires_at < now))
    db.commit()
    count = result.rowcount if hasattr(result, 'rowcount') else 0
    return count
