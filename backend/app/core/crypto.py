"""
Cifrado simétrico Fernet para datos en reposo (BYTEs).
Cumple Ley 21.719 Art. 16 — medidas técnicas de seguridad.

Comportamiento:
- Producción/QA/Staging sin ENCRYPTION_KEY → fail loudly (RuntimeError).
- Desarrollo sin ENCRYPTION_KEY → usa la dev key por defecto (config._dev_encryption_key).
- En cualquier entorno, una clave Fernet inválida → RuntimeError (no fallback silencioso).
"""

import logging

from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class EncryptionKeyError(RuntimeError):
    """Levantada cuando la configuración de cifrado no es válida para el entorno."""


def generate_key() -> str:
    """Genera una clave Fernet válida. Usar para crear ENCRYPTION_KEY inicial."""
    return Fernet.generate_key().decode()


def _get_fernet() -> Fernet:
    """Retorna instancia Fernet. Falla loudly si la clave no es válida.

    Raises:
        EncryptionKeyError: si ENCRYPTION_KEY no es válida (entorno incorrecto
            o clave Fernet inválida). Esto es deliberado: nunca debemos
            persistir PII en texto plano.
    """
    from app.core.config import settings
    try:
        key = settings.resolved_encryption_key
    except ValueError as e:
        # settings ya hace raise en prod/qa/staging sin key.
        # Convertimos a EncryptionKeyError para que el caller tenga un mensaje claro.
        raise EncryptionKeyError(str(e)) from e
    if not key:
        raise EncryptionKeyError(
            "ENCRYPTION_KEY está vacía. Genera una con: "
            "python -c \"from app.core.crypto import generate_key; print(generate_key())\""
        )
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise EncryptionKeyError(
            f"ENCRYPTION_KEY no es una clave Fernet válida: {e}. "
            "Genera una nueva con generate_key()."
        ) from e


def encrypt(data: bytes) -> bytes:
    """Cifra datos con Fernet.

    Raises:
        EncryptionKeyError: si no hay clave válida en el entorno.

    Returns:
        bytes: datos cifrados. Cadena vacía si input era vacío.
    """
    if not data:
        return data
    fernet = _get_fernet()
    return fernet.encrypt(data)


def decrypt(data: bytes) -> bytes:
    """Descifra datos con Fernet.

    Raises:
        EncryptionKeyError: si no hay clave válida en el entorno.
        InvalidToken: si el dato no fue cifrado o la clave no corresponde.

    Returns:
        bytes: datos descifrados. Cadena vacía si input era vacío.

    Note:
        A diferencia de encrypt(), decrypt() propaga InvalidToken porque en
        producción un dato no descifrable es evidencia de tampering o corrupción
        y debe ser investigado, no silenciado.
    """
    if not data:
        return data
    fernet = _get_fernet()
    return fernet.decrypt(data)