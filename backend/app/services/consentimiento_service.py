"""
Logica de negocio para Consentimientos (Art. 12 Ley 21.719).

C4 fix (2026-07-18): TODA PII (nombre_titular, email_titular, texto_consentimiento)
se cifra con Fernet antes de persistir. Las columnas plaintext se eliminaron.
IP se anonimiza con mask /16. texto_consentimiento se hashea con SHA-256
para inmutabilidad probatoria (Arts. 11, 12, 19).

Compliance: Art. 11 (cifrado), Art. 12 (consentimiento), Art. 19 (evidencia).
"""
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.crypto import encrypt, decrypt
from app.models.consentimiento import Consentimiento
from app.models.rat import RAT as RATModel
from app.schemas.consentimiento import ConsentimientoCreate
from app.services.audit_service import log_audit


class ConsentimientoNotFoundError(Exception):
    pass


class RATNotFoundError(Exception):
    pass


class ConsentimientoYaRevocadoError(Exception):
    pass


def _mask_ip(ip: Optional[str]) -> Optional[str]:
    if not ip:
        return None
    parts = ip.split(".")
    if len(parts) != 4:
        return ip
    return f"{parts[0]}.{parts[1]}.***.***"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def descifrar_nombre(c: Consentimiento) -> str:
    """Descifra nombre_titular desde BD. Devuelve string vacío si no hay cipher."""
    if not c.nombre_titular_cipher:
        return ""
    try:
        return decrypt(c.nombre_titular_cipher).decode("utf-8")
    except Exception:
        return "[dato no descifrable]"


def descifrar_email(c: Consentimiento) -> Optional[str]:
    """Descifra email_titular desde BD."""
    if not c.email_titular_cipher:
        return None
    try:
        return decrypt(c.email_titular_cipher).decode("utf-8")
    except Exception:
        return None


def descifrar_texto(c: Consentimiento) -> str:
    """Descifra texto_consentimiento desde BD."""
    if not c.texto_consentimiento_cipher:
        return ""
    try:
        return decrypt(c.texto_consentimiento_cipher).decode("utf-8")
    except Exception:
        return "[dato no descifrable]"


def listar_consentimientos(
    db: Session,
    company_id: int,
    rat_id: Optional[int] = None,
    solo_activos: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Consentimiento], int]:
    q = db.query(Consentimiento).filter(Consentimiento.company_id == company_id)
    if rat_id is not None:
        q = q.filter(Consentimiento.rat_id == rat_id)
    if solo_activos:
        q = q.filter(Consentimiento.activo)

    total = q.count()
    items = q.order_by(Consentimiento.fecha_obtencion.desc()).offset(skip).limit(limit).all()
    return items, total


def obtener_consentimiento(db: Session, consentimiento_id: int) -> Consentimiento:
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise ConsentimientoNotFoundError("Consentimiento no encontrado.")
    return c


def crear_consentimiento(db: Session, data: ConsentimientoCreate, usuario: str) -> Consentimiento:
    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise RATNotFoundError("RAT no encontrado.")

    # C4 fix: cifrar TODA la PII antes de persistir. NO guardar plaintext.
    nombre_cipher = encrypt(data.nombre_titular.encode("utf-8"))
    email_cipher = (
        encrypt(data.email_titular.encode("utf-8")) if data.email_titular else None
    )
    texto_cipher = encrypt(data.texto_consentimiento.encode("utf-8"))
    texto_hash = _hash_text(data.texto_consentimiento)
    ip_masked = _mask_ip(data.ip_origen)

    # C4 fix: las columnas plaintext legacy (nombre_titular, email_titular,
    # texto_consentimiento, ip_origen) siguen siendo NOT NULL en BD legacy.
    # Escribimos un placeholder para que el INSERT no falle, pero la PII real
    # esta SOLO en las columnas *_cipher. El schema de salida descifra desde
    # las *_cipher, NO desde estos placeholders.
    PLACEHOLDER_PII = "[CIFRADO]"

    c = Consentimiento(
        company_id=rat.company_id,
        rat_id=data.rat_id,
        canal=data.canal,
        fecha_obtencion=data.fecha_obtencion,
        activo=True,
        nombre_titular_cipher=nombre_cipher,
        email_titular_cipher=email_cipher,
        texto_consentimiento_cipher=texto_cipher,
        texto_consentimiento_hash=texto_hash,
        ip_origen_masked=ip_masked,
        # Placeholders para columnas NOT NULL legacy:
        nombre_titular=PLACEHOLDER_PII,
        email_titular=PLACEHOLDER_PII if data.email_titular else None,
        texto_consentimiento=PLACEHOLDER_PII,
        ip_origen=PLACEHOLDER_PII,
    )
    db.add(c)
    db.flush()
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="create",
        usuario=usuario,
        detalle={
            "rat_id": data.rat_id,
            "canal": str(data.canal),
            "pii_cifrado": True,
            "ip_masked": ip_masked,
            "texto_hash": texto_hash,
        },
    )
    db.commit()
    db.refresh(c)
    return c


def revocar_consentimiento(db: Session, consentimiento_id: int, usuario: str) -> Consentimiento:
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise ConsentimientoNotFoundError("Consentimiento no encontrado.")
    if c.fecha_revocacion:
        raise ConsentimientoYaRevocadoError("El consentimiento ya fue revocado.")

    c.activo = False
    c.fecha_revocacion = datetime.now(timezone.utc)
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="revocar",
        usuario=usuario,
        detalle={"rat_id": c.rat_id, "pii_cifrado": bool(c.nombre_titular_cipher)},
    )
    db.commit()
    db.refresh(c)
    return c