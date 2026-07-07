import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TipoSolicitud(str, enum.Enum):
    ACCESO = "acceso"
    RECTIFICACION = "rectificacion"
    CANCELACION = "cancelacion"
    OPOSICION = "oposicion"
    BLOQUEO = "bloqueo"
    PORTABILIDAD = "portabilidad"


class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    RECHAZADO = "rechazada"
    BLOQUEADO = "bloqueado"


class SolicitudDerecho(Base):
    __tablename__ = "solicitudes_derecho"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre_titular: Mapped[str] = mapped_column(String(255), nullable=False)
    rut_titular: Mapped[str] = mapped_column(String(20), nullable=True)
    email_titular: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(2000), nullable=True)
    estado: Mapped[str] = mapped_column(String(50), default="pendiente")
    solicitud_fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    respuesta_fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    respuesta: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), nullable=True, index=True)
    plazo_bloqueo_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Mapped[str] = mapped_column(String(50), nullable=True)
    evidencia_identidad: Mapped[str] = mapped_column(Text, nullable=True)
    evidencia_respuesta_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    causal_rechazo: Mapped[str] = mapped_column(String(50), nullable=True)
    medio_respuesta: Mapped[str] = mapped_column(String(50), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="solicitudes_derecho")  # noqa: F821
    rat: Mapped["RAT"] = relationship("RAT")  # noqa: F821