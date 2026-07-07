"""
Logica de negocio para Consentimientos (Art. 12 Ley 21.719).

PII (nombre_titular, email_titular) se cifra con Fernet en columnas BYTEA.
IP se anonimiza con mask /16. texto_consentimiento se hashea con SHA-256
para inmutabilidad probatoria (Arts. 11, 12, 19).
"""
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.crypto import encrypt
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

    nombre_cipher = encrypt(data.nombre_titular.encode("utf-8")) if data.nombre_titular else None
    email_cipher = encrypt(data.email_titular.encode("utf-8")) if data.email_titular else None
    texto_hash = _hash_text(data.texto_consentimiento) if data.texto_consentimiento else None
    ip_masked = _mask_ip(data.ip_origen)

    c = Consentimiento(
        company_id=rat.company_id,
        rat_id=data.rat_id,
        nombre_titular=data.nombre_titular,
        email_titular=data.email_titular,
        canal=data.canal,
        texto_consentimiento=data.texto_consentimiento,
        fecha_obtencion=data.fecha_obtencion,
        ip_origen=data.ip_origen,
        activo=True,
        nombre_titular_cipher=nombre_cipher,
        email_titular_cipher=email_cipher,
        texto_consentimiento_hash=texto_hash,
        ip_origen_masked=ip_masked,
    )
    db.add(c)
    db.flush()
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="create",
        usuario=usuario,
        detalle={"rat_id": data.rat_id, "canal": str(data.canal), "pii_cifrado": True, "ip_masked": ip_masked},
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
        detalle={"rat_id": c.rat_id, "pII_cifrado": bool(c.nombre_titular_cipher)},
    )
    db.commit()
    db.refresh(c)
    return c