"""
Utilidades para validacion de archivos subidos (Z-03).

Valida:
- Extension (whitelist por contexto)
- Tamano maximo (max_bytes)
- Content-Type (opcional, para double-check)
- Magic bytes (S3.1) — verifica que el contenido REAL del archivo coincida con
  su content_type declarado. Previene subir un .exe renombrado a .pdf.

Levanta HTTPException 400 (magic bytes invalidos, extension invalida o
content_type invalido) o 413 (muy grande).
"""
import os
from typing import Iterable, Optional

from fastapi import HTTPException, UploadFile, status


# Magic bytes por content-type. Se validan los primeros N bytes del archivo.
# Refs:
#   - PDF: %PDF- — https://www.iso.org/standard/63534.html
#   - JPEG: FF D8 FF — https://www.w3.org/Graphics/JPEG/itu-t81.pdf
#   - PNG:  89 50 4E 47 0D 0A 1A 0A — RFC 2083
#   - GIF:  GIF87a / GIF89a
_MAGIC_BYTES: dict[str, list[bytes]] = {
    "application/pdf": [b"%PDF-"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/gif": [b"GIF87a", b"GIF89a"],
}


def _get_extension(filename: Optional[str]) -> str:
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower().lstrip(".")


def _validate_magic_bytes(content: bytes, content_type: Optional[str]) -> None:
    """Verifica que los primeros bytes del archivo coincidan con el content_type.

    Solo aplica a content_types conocidos (PDF/JPEG/PNG/GIF). Si el content_type
    no esta en la lista, no validamos (extensibilidad).
    """
    if not content_type or not content:
        return
    signatures = _MAGIC_BYTES.get(content_type.lower())
    if not signatures:
        return
    for sig in signatures:
        if content.startswith(sig):
            return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"El contenido del archivo no coincide con el tipo declarado "
            f"'{content_type}'. Posible renombrado malicioso."
        ),
    )


def validate_upload(
    file: UploadFile,
    allowed_extensions: Iterable[str],
    max_bytes: int,
    *,
    check_content_type_prefix: Optional[str] = None,
    validate_magic_bytes: bool = False,
) -> bytes:
    """Lee y valida el archivo subido.

    Args:
        file: UploadFile de FastAPI.
        allowed_extensions: Lista de extensiones permitidas SIN punto (ej. ["pdf", "md"]).
        max_bytes: Tamano maximo en bytes.
        check_content_type_prefix: Si se setea, valida que el content_type
            empiece con este prefijo (ej. "image/" o "application/pdf").
        validate_magic_bytes: Si True, valida que el contenido REAL del archivo
            coincida con su content_type declarado (S3.1).

    Returns:
        Contenido en bytes.

    Raises:
        HTTPException 400: extension invalida, content_type invalido o magic bytes invalidos.
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

    if validate_magic_bytes:
        _validate_magic_bytes(content, file.content_type)

    return content
