"""
Modelo de Evaluación de Impacto en la Protección de Datos (EIPD / DPIA).
"""

from datetime import date, datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class ResultadoEIPD(str, PyEnum):
    COMPLETADA = "completada"
    NO_REQUERIDA = "no_requerida"
    EN_PROCESO = "en_proceso"


class EIPD(Base):
    __tablename__ = "eipds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), unique=True, nullable=False, index=True)

    metodologia: Mapped[str] = mapped_column(String(500), nullable=True)
    objetivos: Mapped[str] = mapped_column(Text, nullable=True)
    necesidad_proporcionalidad: Mapped[str] = mapped_column(Text, nullable=True)
    riesgos_identificados: Mapped[str] = mapped_column(Text, nullable=True)
    medidas_propuestas: Mapped[str] = mapped_column(Text, nullable=True)
    parecer_dpo: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_elaboracion: Mapped[date] = mapped_column(Date, nullable=True)
    fecha_aprobacion: Mapped[date] = mapped_column(Date, nullable=True)
    resultado: Mapped[ResultadoEIPD] = mapped_column(
        Enum(ResultadoEIPD), default=ResultadoEIPD.EN_PROCESO, nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    rat: Mapped["RAT"] = relationship("RAT", back_populates="eipd")  # noqa: F821