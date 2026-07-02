"""
Utilidades para validacion de archivos subidos (Z-03).

Valida:
- Extension (whitelist por contexto)
- Tamano maximo (max_bytes)
- Content-Type (opcional, para double-check)

Levanta HTTPException 400 (extension invalida) o 413 (muy grande).
"""
import os
from typing import Iterable, Optional

from fastapi import HTTPException, UploadFile, status


def _get_extension(filename: Optional[str]) -> str:
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower().lstrip(".")


def validate_upload(
    file: UploadFile,
    allowed_extensions: Iterable[str],
    max_bytes: int,
    *,
    check_content_type_prefix: Optional[str] = None,
) -> bytes:
    """Lee y valida el archivo subido.

    Args:
        file: UploadFile de FastAPI.
        allowed_extensions: Lista de extensiones permitidas SIN punto (ej. ["pdf", "md"]).
        max_bytes: Tamano maximo en bytes.
        check_content_type_prefix: Si se setea, valida que el content_type
            empiece con este prefijo (ej. "image/" o "application/pdf").

    Returns:
        Contenido en bytes.

    Raises:
        HTTPException 400: extension invalida o content_type invalido.
        HTTPException 413: tamano excedido.
    """
    allowed = {ext.lower().lstrip(".") for ext in allowed_extensions}
    ext = _get_extension(file.filename)
    if not ext or ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Extension '{ext or 'sin extension'}' no permitida. "
                f"Extensiones validas: {', '.join(sorted(allowed))}."
            ),
        )

    content = file.file.read() if hasattr(file, "file") else b""

    if len(content) > max_bytes:
        size_mb = len(content) / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Archivo demasiado grande ({size_mb:.1f}MB). "
                f"Maximo permitido: {max_mb:.1f}MB."
            ),
        )

    if check_content_type_prefix and file.content_type:
        if not file.content_type.lower().startswith(check_content_type_prefix.lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Content-Type '{file.content_type}' no coincide con el esperado "
                    f"('{check_content_type_prefix}*')."
                ),
            )

    return content