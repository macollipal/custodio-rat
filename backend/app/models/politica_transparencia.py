"""
Modelo de Política de Transparencia Pública (Art. 14 ter Ley 21.719 — REC-02).
Generada dinámicamente desde los datos del sistema; no requiere almacenamiento.
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class PoliticaTransparencia(Base):
    __tablename__ = "politicas_transparencia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, unique=True, index=True)

    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=True)

    generado_por: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    company: Mapped["Company"] = relationship("Company")  # noqa: F821
