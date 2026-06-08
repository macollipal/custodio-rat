from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TktHistorial(Base):
    __tablename__ = "tkt_historial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tkt_solicitud_derecho.id"), nullable=False, index=True)
    estado_anterior: Mapped[str] = mapped_column(String(50), nullable=True)
    estado_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    ticket: Mapped["TktSolicitudDerecho"] = relationship("TktSolicitudDerecho", back_populates="historial")  # noqa: F821
    user: Mapped["User"] = relationship("User")  # noqa: F821