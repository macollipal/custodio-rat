"""
Cifrado simétrico Fernet para datos en reposo (BYTEs).
Cumple Ley 21.719 Art. 16 — medidas técnicas de seguridad.
"""

import base64
import logging

from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


def generate_key() -> str:
    """Genera una clave Fernet válida. Usar para crear ENCRYPTION_KEY inicial."""
    return Fernet.generate_key().decode()


def _get_fernet() -> Optional[Fernet]:
    """Retorna instancia Fernet o None si no hay clave válida."""
    from app.core.config import settings
    key = settings.resolved_encryption_key
    if not key:
        logger.warning("ENCRYPTION_KEY no configurada — datos se almacenarán sin cifrar")
        return None
    try:
        return Fernet(key.encode())
    except Exception as e:
        logger.warning(f"ENCRYPTION_KEY inválida (no es clave Fernet válida) — datos se almacenarán sin cifrar: {e}")
        return None


def encrypt(data: bytes) -> bytes:
    """Cifra datos con Fernet. Si no hay clave válida, retorna sin cifrar."""
    if not data:
        return data
    fernet = _get_fernet()
    if fernet is None:
        logger.warning("ENCRYPTION_KEY no configurada, almacenando dato sin cifrar")
        return data
    return fernet.encrypt(data)


def decrypt(data: bytes) -> bytes:
    """Descifra datos con Fernet. Si no hay clave o falla, retorna tal cual."""
    if not data:
        return data
    fernet = _get_fernet()
    if fernet is None:
        return data
    try:
        return fernet.decrypt(data)
    except InvalidToken:
        logger.debug("Dato no cifrado o key mismatch, retornando tal cual")
        return data
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return data