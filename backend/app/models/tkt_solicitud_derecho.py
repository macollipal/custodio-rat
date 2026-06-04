from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class TktTipo(str, enum.Enum):
    ACCESO = "acceso"
    RECTIFICACION = "rectificacion"
    CANCELACION = "cancelacion"
    OPOSICION = "oposicion"


class EstadoTicket(str, enum.Enum):
    ABIERTO = "abierto"
    EN_PROCESO = "en_proceso"
    PENDIENTE = "pendiente"
    RESUELTO = "resuelto"


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


class TktSolicitudDerecho(Base):
    __tablename__ = "tkt_solicitud_derecho"
    __table_args__ = (
        Index("idx_tkt_estado_company", "estado", "company_id"),
        Index("idx_tkt_fecha_vencimiento", "fecha_vencimiento"),
        Index("idx_tkt_estado_prioridad", "estado", "prioridad"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)
    estado = Column(String(50), default=EstadoTicket.ABIERTO.value)
    prioridad = Column(String(20), default=PrioridadTicket.NORMAL.value, nullable=False)
    origen = Column(String(20), default=OrigenTicket.WEB.value, nullable=False)

    titular_nombre = Column(String(255), nullable=False)
    titular_email = Column(String(255), nullable=False)
    titular_rut = Column(String(20), nullable=True)

    descripcion = Column(String(2000), nullable=True)

    fecha_recepcion = Column(DateTime, default=func.now(), nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=False)

    responsable_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    respuesta_texto = Column(String(1000), nullable=True)
    respuesta_fecha = Column(DateTime, nullable=True)

    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="tkt_solicitudes")
    responsable = relationship("User", foreign_keys=[responsable_id])
    notas = relationship("TktNota", back_populates="ticket", cascade="all, delete-orphan")
    adjuntos = relationship("TktAdjunto", back_populates="ticket", cascade="all, delete-orphan")
    historial = relationship("TktHistorial", back_populates="ticket", cascade="all, delete-orphan")

    class Meta:
        table_name = "tkt_solicitud_derecho"