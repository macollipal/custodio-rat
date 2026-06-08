"""
Servicio compartido de auditoría.
Centraliza el logging de todas las acciones del sistema.
Implementa hash chain para inmutabilidad (Art. 12 Ley 21.719).
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models.audit_log import AuditLog, GENESIS_HASH

logger = logging.getLogger(__name__)


def _compute_hash(prev_hash: str, timestamp: datetime, accion: str, entidad: str,
                 entidad_id: int, usuario: Optional[str], detalle: Optional[str]) -> str:
    """
    Computa el hash SHA-256 para el registro de auditoría.
    Fórmula: sha256(prev_hash + timestamp.isoformat() + accion + entidad + str(entidad_id) + usuario + detalle)
    """
    data = (
        f"{prev_hash}"
        f"{timestamp.isoformat()}"
        f"{accion}"
        f"{entidad}"
        f"{entidad_id}"
        f"{usuario or ''}"
        f"{detalle or ''}"
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def log_audit(
    db: Session,
    entidad: str,
    entidad_id: int,
    accion: str,
    usuario: str,
    detalle: dict,
    ip_origen: Optional[str] = None,
) -> AuditLog:
    """
    Registra una acción en audit_logs con hash chain para inmutabilidad.
    - Obtiene el hash del último registro para encadenar
    - Calcula el hash del nuevo registro
    - PostgreSQL/Neon: usa nextval() directo para evitar problemas con el pooler.
    - SQLite (tests): deja que la BD asigne el ID automáticamente.
    """
    prev_hash = GENESIS_HASH
    last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    if last_log:
        prev_hash = last_log.hash

    timestamp = datetime.now(timezone.utc)
    detalle_str = json.dumps(detalle, ensure_ascii=False, default=str)

    record_hash = _compute_hash(
        prev_hash, timestamp, accion, entidad, entidad_id, usuario, detalle_str
    )

    dialect = db.bind.dialect.name if db.bind else "unknown"

    if dialect == "postgresql":
        seq_name = db.execute(
            text("SELECT pg_get_serial_sequence('audit_logs', 'id')")
        ).scalar()
        next_id = db.execute(
            text("SELECT nextval(:seq_name)"),
            {"seq_name": seq_name},
        ).scalar()
        log = AuditLog(
            id=next_id,
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            usuario=usuario,
            detalle=detalle_str,
            ip_origen=ip_origen,
            timestamp=timestamp,
            prev_hash=prev_hash,
            hash=record_hash,
        )
    else:
        log = AuditLog(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            usuario=usuario,
            detalle=detalle_str,
            ip_origen=ip_origen,
            timestamp=timestamp,
            prev_hash=prev_hash,
            hash=record_hash,
        )
    db.add(log)
    return log


def verify_audit_chain(db: Session, limit: Optional[int] = None) -> dict:
    """
    Verifica la integridad de la cadena de hashes de auditoría.
    Retorna dict con:
      - valid: bool
      - total_records: int
      - broken_at: int | None (ID del primer registro roto)
      - message: str
    """
    query = db.query(AuditLog).order_by(AuditLog.id.asc())
    if limit:
        query = query.limit(limit)

    records = query.all()
    if not records:
        return {"valid": True, "total_records": 0, "broken_at": None, "message": "No hay registros"}

    for i, record in enumerate(records):
        if i == 0:
            expected_prev = GENESIS_HASH
        else:
            expected_prev = records[i - 1].hash

        if record.prev_hash != expected_prev:
            return {
                "valid": False,
                "total_records": len(records),
                "broken_at": record.id,
                "message": f"Hash chain roto en registro {record.id}. Esperado prev_hash={expected_prev}, encontrado {record.prev_hash}",
            }

        computed = _compute_hash(
            record.prev_hash,
            record.timestamp,
            record.accion,
            record.entidad,
            record.entidad_id,
            record.usuario,
            record.detalle,
        )
        if record.hash != computed:
            return {
                "valid": False,
                "total_records": len(records),
                "broken_at": record.id,
                "message": f"Hash corrupto en registro {record.id}. Registro puede haber sido modificado.",
            }

    return {
        "valid": True,
        "total_records": len(records),
        "broken_at": None,
        "message": f"Cadena intacta. {len(records)} registros verificados.",
    }