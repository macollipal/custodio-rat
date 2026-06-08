"""
Registro de auditoría: cada acción sobre el RAT queda trazada.
Permite cumplir con el principio de responsabilidad proactiva (Art. 14 Ley 21.719).

Hash chain para inmutabilidad:
- Cada registro incluye hash del registro anterior (prev_hash)
- El hash del registro actual se calcula como sha256(prev_hash + timestamp + accion + ...)
- Cualquier modificación rompe la cadena (verificable con verify_audit_chain)
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base

GENESIS_HASH = "0" * 64  # 64 zeros for the first record


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entidad_entidad_id", "entidad", "entidad_id"),
        Index("ix_audit_logs_timestamp", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entidad: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    accion: Mapped[str] = mapped_column(String(20), nullable=False)
    usuario: Mapped[str] = mapped_column(String(100), nullable=True)
    detalle: Mapped[str] = mapped_column(Text, nullable=True)
    ip_origen: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False, default=GENESIS_HASH)
    hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
