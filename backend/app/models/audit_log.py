"""
Registro de auditoría: cada acción sobre el RAT queda trazada.
Permite cumplir con el principio de responsabilidad proactiva (Art. 14 Ley 21.719).
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entidad: Mapped[str] = mapped_column(String(50), nullable=False)   # "rat", "company", "user"
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    accion: Mapped[str] = mapped_column(String(20), nullable=False)    # "crear", "editar", "eliminar"
    usuario: Mapped[str] = mapped_column(String(100), nullable=True)
    detalle: Mapped[str] = mapped_column(Text, nullable=True)          # JSON con cambios
    ip_origen: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
