"""
Utilidades de seguridad: hashing de contraseñas y manejo de JWT.
"""

import uuid
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class _RevokedTokenCache:
    """
    Cache LRU en memoria para JTIs revocados.
    TTL: 5 minutos (coincide con expiry más largo de token access).
    Thread-safe para entornos serverless (cada instance tiene su propio proceso).
    """

    def __init__(self, maxsize: int = 10000, ttl_seconds: int = 300):
        self._cache: OrderedDict[str, float] = OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def add(self, jti: str) -> None:
        with self._lock:
            self._cache[jti] = time.time()
            self._cache.move_to_end(jti)
            if len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def is_revoked(self, jti: str) -> bool:
        with self._lock:
            if jti not in self._cache:
                return False
            expires_at = self._cache[jti]
            if time.time() - expires_at > self._ttl:
                del self._cache[jti]
                return False
            return True

    def invalidate(self, jti: str) -> None:
        with self._lock:
            self._cache.pop(jti, None)


_revoked_cache = _RevokedTokenCache(maxsize=10000, ttl_seconds=300)


def _check_blacklist(jti: str) -> bool:
    """Check if JTI is revoked in cache (fast path)."""
    if _revoked_cache.is_revoked(jti):
        return True
    return False


def _add_to_blacklist_cache(jti: str) -> None:
    _revoked_cache.add(jti)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "access"})
    return jwt.encode(to_encode, settings.resolved_secret_key, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    return jwt.encode(to_encode, settings.resolved_secret_key, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str = "access", db=None) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.resolved_secret_key, algorithms=[settings.ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        jti = payload.get("jti")
        if jti:
            if _check_blacklist(jti):
                return None
            if db is not None:
                from app.models.token_blacklist import TokenBlacklist
                if db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first():
                    _add_to_blacklist_cache(jti)
                    return None
        return payload
    except JWTError:
        return None


def decode_access_token(token: str, db=None) -> Optional[dict]:
    return decode_token(token, expected_type="access", db=db)


def decode_refresh_token(token: str, db=None) -> Optional[dict]:
    return decode_token(token, expected_type="refresh", db=db)


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
        _add_to_blacklist_cache(jti)
        return True
    entry = TokenBlacklist(jti=jti, expires_at=expires_at)
    db.add(entry)
    db.commit()
    _add_to_blacklist_cache(jti)
    return True


def cleanup_expired_tokens(db) -> int:
    from app.models.token_blacklist import TokenBlacklist
    from sqlalchemy import delete
    now = datetime.now(timezone.utc)
    result = db.execute(delete(TokenBlacklist).where(TokenBlacklist.expires_at < now))
    db.commit()
    count = result.rowcount if hasattr(result, 'rowcount') else 0
    return count
