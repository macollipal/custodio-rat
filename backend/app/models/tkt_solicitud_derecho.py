import enum
from datetime import datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TktTipo(str, enum.Enum):
    ACCESO = "acceso"
    RECTIFICACION = "rectificacion"
    CANCELACION = "cancelacion"
    OPOSICION = "oposicion"
    BLOQUEO = "bloqueo"
    PORTABILIDAD = "portabilidad"


class EstadoTicket(str, enum.Enum):
    ABIERTO = "abierto"
    EN_PROCESO = "en_proceso"
    PENDIENTE = "pendiente"
    RESUELTO = "resuelto"
    BLOQUEADO = "bloqueado"
    RECHAZADO = "rechazado"
    SUBSANACION = "subsanacion"
    PRORROGA = "prorroga"


class PrioridadTicket(str, enum.Enum):
    BAJA = "baja"
    NORMAL = "normal"
    URGENTE = "urgente"


class OrigenTicket(str, enum.Enum):
    WEB = "web"
    EMAIL = "email"
    TELEFONO = "telefono"
    PRESENCIAL = "presencial"
    MANUAL = "manual"


class CausalRechazo(str, enum.Enum):
    FALTA_IDENTIDAD = "falta_identidad"
    SOLICITUD_INFUNDADA = "solicitud_manifiestamente_infundada"
    SOLICITUD_EXCESIVA = "solicitud_excesiva"
    FALTA_PODER_NOTORIO = "falta_poder_notorial"
    PLAZO_VENCIDO = "plazo_vencido"
    IDENTIDAD_NO_VERIFICADA = "identidad_no_verificada"
    OTRO = "otro"


class TktSolicitudDerecho(Base):
    __tablename__ = "tkt_solicitud_derecho"
    __table_args__ = (
        Index("idx_tkt_estado_company", "estado", "company_id"),
        Index("idx_tkt_fecha_vencimiento", "fecha_vencimiento"),
        Index("idx_tkt_estado_prioridad", "estado", "prioridad"),
        Index("idx_tkt_tracking_token", "tracking_token"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), default=EstadoTicket.ABIERTO.value)
    prioridad: Mapped[str] = mapped_column(String(20), default=PrioridadTicket.NORMAL.value, nullable=False)
    origen: Mapped[str] = mapped_column(String(20), default=OrigenTicket.WEB.value, nullable=False)
    titular_nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    titular_email: Mapped[str] = mapped_column(String(255), nullable=False)
    titular_rut: Mapped[str] = mapped_column(String(20), nullable=True)
    descripcion: Mapped[str] = mapped_column(String(2000), nullable=True)
    fecha_recepcion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responsable_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    respuesta_texto: Mapped[str] = mapped_column(String(1000), nullable=True)
    respuesta_fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), nullable=True)
    plazo_bloqueo_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    portability_data: Mapped[str] = mapped_column(Text, nullable=True)
    tracking_token: Mapped[str] = mapped_column(String(36), nullable=True, unique=True)
    acuse_enviado_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    subsanacion_detalle: Mapped[str] = mapped_column(String(1000), nullable=True)
    subsanacion_fecha_pedido: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    prorroga_fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    prorroga_dias: Mapped[int] = mapped_column(Integer, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    representante_nombre: Mapped[str] = mapped_column(String(255), nullable=True)
    representante_rut: Mapped[str] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str] = mapped_column(String(50), nullable=True)
    fecha_nacimiento: Mapped[datetime] = mapped_column(Date, nullable=True)
    pais: Mapped[str] = mapped_column(String(100), nullable=True)

    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Mapped[str] = mapped_column(String(50), nullable=True)
    evidencia_identidad: Mapped[str] = mapped_column(Text, nullable=True)
    evidencia_respuesta_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    causal_rechazo: Mapped[str] = mapped_column(String(50), nullable=True)
    medio_respuesta: Mapped[str] = mapped_column(String(50), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="tkt_solicitudes")  # noqa: F821
    responsable: Mapped["User"] = relationship("User", foreign_keys=[responsable_id])  # noqa: F821
    rat: Mapped["RAT"] = relationship("RAT", foreign_keys=[rat_id])  # noqa: F821
    notas: Mapped[list["TktNota"]] = relationship("TktNota", back_populates="ticket", cascade="all, delete-orphan")  # noqa: F821
    adjuntos: Mapped[list["TktAdjunto"]] = relationship("TktAdjunto", back_populates="ticket", cascade="all, delete-orphan")  # noqa: F821
    historial: Mapped[list["TktHistorial"]] = relationship("TktHistorial", back_populates="ticket", cascade="all, delete-orphan")  # noqa: F821