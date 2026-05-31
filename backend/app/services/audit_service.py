"""
Servicio compartido de auditoría.
Centraliza el logging de todas las acciones del sistema.
"""

import json
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    entidad: str,
    entidad_id: int,
    accion: str,
    usuario: str,
    detalle: dict,
    ip_origen: Optional[str] = None,
) -> None:
    """
    Registra una acción en audit_logs.
    - PostgreSQL/Neon: usa nextval() directo para evitar problemas con el pooler.
    - SQLite (tests): deja que la BD asigne el ID automáticamente.
    """
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
            detalle=json.dumps(detalle, ensure_ascii=False, default=str),
            ip_origen=ip_origen,
        )
    else:
        log = AuditLog(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            usuario=usuario,
            detalle=json.dumps(detalle, ensure_ascii=False, default=str),
            ip_origen=ip_origen,
        )
    db.add(log)