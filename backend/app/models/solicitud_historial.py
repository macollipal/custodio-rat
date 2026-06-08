from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class SolicitudHistorial(Base):
    __tablename__ = "solicitud_derecho_historial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    solicitud_id: Mapped[int] = mapped_column(Integer, ForeignKey("solicitudes_derecho.id"), nullable=False, index=True)
    estado_anterior: Mapped[str] = mapped_column(String(50), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    usuario_nombre: Mapped[str] = mapped_column(String(255), nullable=True)