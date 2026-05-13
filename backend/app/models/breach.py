"""
Modelo de Brechas de Seguridad (Art. 14 bis Ley 21.719).
Plazos: notificación APDC en 72 horas; titulares sin dilación si son datos sensibles/menores/financieros.
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class SecurityBreach(Base):
    __tablename__ = "security_breaches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_deteccion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rats_afectados: Mapped[str] = mapped_column(Text, nullable=True)
    datos_comprometidos: Mapped[str] = mapped_column(Text, nullable=True)
    medidas_adoptadas: Mapped[str] = mapped_column(Text, nullable=True)

    # Notificación APDC (72 horas desde detección)
    notificado_apdc: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_notificacion_apdc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notificación a titulares (sin dilación cuando hay datos sensibles/menores/financieros)
    notificado_titulares: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_notificacion_titulares: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    creado_por: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    company: Mapped["Company"] = relationship("Company")  # noqa: F821
