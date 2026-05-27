"""
Solicitud de ejercicio de derechos ARCO (Acceso, Rectificación, Cancelación, Oposición).
Art. 12 y 14 Ley 21.719 — Los titulares tienen derecho a ejercer estos derechos
ante el responsable del tratamiento.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TipoSolicitud(str, Enum):
    ACCESO = "acceso"
    RECTIFICACION = "rectificacion"
    CANCELACION = "cancelacion"
    OPOSICION = "oposicion"


class EstadoSolicitud(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    RECHAZADA = "rechazada"


class SolicitudDerecho(Base):
    __tablename__ = "solicitudes_derecho"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)

    tipo: Mapped[TipoSolicitud] = mapped_column(
        SAEnum(TipoSolicitud, name="tipo_solicitud"), nullable=False
    )
    nombre_titular: Mapped[str] = mapped_column(String(200), nullable=False)
    email_titular: Mapped[str] = mapped_column(String(200), nullable=False)
    rut_titular: Mapped[str] = mapped_column(String(20), nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    estado: Mapped[EstadoSolicitud] = mapped_column(
        SAEnum(EstadoSolicitud, name="estado_solicitud"),
        default=EstadoSolicitud.PENDIENTE,
        nullable=False,
    )
    respuesta: Mapped[str] = mapped_column(Text, nullable=True)
    fecha_respuesta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    company: Mapped["Company"] = relationship("Company", back_populates="solicitudes_derecho")
