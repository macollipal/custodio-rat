from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TktReglaAsignacion(Base):
    __tablename__ = "tkt_reglas_asignacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=True)
    prioridad: Mapped[str] = mapped_column(String(20), nullable=True)
    responsable_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    company: Mapped["Company"] = relationship("Company")  # noqa: F821
    responsable: Mapped["User"] = relationship("User")  # noqa: F821
