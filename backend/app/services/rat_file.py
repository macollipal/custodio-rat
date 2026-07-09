"""
Manejo de archivos del RAT: subida a OCI y descarga (cifrado E2E con Fernet).
"""
import base64
import hashlib
import logging
from typing import Optional

from fastapi import HTTPException, status

from app.services.file_validation import _validate_magic_bytes

logger = logging.getLogger(__name__)


def procesar_archivo_base_legal(data: dict) -> dict:
    """Sube archivo_base_legal_base64 a OCI y retorna URL. Caida -> BYTEA como fallback. BYTEA cifrado con Fernet."""
    base64_str = data.get("archivo_base_legal_base64")
    if not base64_str:
        return {}
    try:
        datos = base64.b64decode(base64_str)
    except Exception:
        return {}
    hash_val = hashlib.sha256(datos).hexdigest()
    nombre = data.get("archivo_base_legal_nombre", "documento.pdf")
    tipo = data.get("archivo_base_legal_tipo", "application/pdf")
    _validate_magic_bytes(datos, tipo)

    try:
        from app.core.storage import get_storage_backend, generate_object_name
        from app.core.crypto import encrypt
        backend = get_storage_backend()
        object_name = generate_object_name("rats", nombre)
        content_type = tipo or "application/octet-stream"
        datos_cifrados = encrypt(datos)
        url = backend.upload(datos_cifrados, object_name, content_type)
        logger.info(f"Archivo RAT cifrado y migrado a OCI: {object_name}")
        return {
            "archivo_base_legal_storage_url": url,
            "archivo_base_legal_hash": hash_val,
            "archivo_base_legal_nombre": nombre,
            "archivo_base_legal_tipo": tipo,
        }
    except Exception as e:
        logger.warning(f"OCI no disponible, guardando BYTEA cifrado: {e}")
        from app.core.crypto import encrypt
        datos_cifrados = encrypt(datos)
        return {
            "archivo_base_legal_datos": datos_cifrados,
            "archivo_base_legal_hash": hash_val,
            "archivo_base_legal_nombre": nombre,
            "archivo_base_legal_tipo": tipo,
        }


def download_rat_file(db, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> dict:
    """Obtiene el archivo del RAT. Si esta en OCI, descarga y descifra. Si esta en BYTEA, retorna bytes."""
    from app.core.crypto import decrypt
    from app.models.rat import RAT

    rat = db.query(RAT).filter(RAT.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro RAT no encontrado.")

    storage_url = rat.archivo_base_legal_storage_url
    datos = rat.archivo_base_legal_datos
    nombre = rat.archivo_base_legal_nombre or "documento.pdf"

    if storage_url:
        from app.core.storage import get_storage_backend
        backend = get_storage_backend()

        try:
            content = backend.download(storage_url)
            content = decrypt(content)
            return {
                "type": "bytes",
                "content": base64.b64encode(content).decode(),
                "nombre": nombre,
                "content_type": rat.archivo_base_legal_tipo or "application/pdf",
            }
        except Exception as e:
            logger.error(f"OCI direct download failed: {e}")

        if datos:
            datos_planos = decrypt(datos)
            return {
                "type": "bytes",
                "content": base64.b64encode(datos_planos).decode(),
                "nombre": nombre,
                "content_type": rat.archivo_base_legal_tipo or "application/pdf",
            }

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    elif datos:
        datos_planos = decrypt(datos)
        return {
            "type": "bytes",
            "content": base64.b64encode(datos_planos).decode(),
            "nombre": nombre,
            "content_type": rat.archivo_base_legal_tipo or "application/pdf",
        }

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
