from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class TipoSolicitud(str, enum.Enum):
    ACCESO = "acceso"
    RECTIFICACION = "rectificacion"
    CANCELACION = "cancelacion"
    OPOSICION = "oposicion"


class EstadoSolicitud(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    RECHAZADO = "rechazada"


class SolicitudDerecho(Base):
    __tablename__ = "solicitudes_derecho"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)
    nombre_titular = Column(String(255), nullable=False)
    rut_titular = Column(String(20), nullable=True)
    email_titular = Column(String(255), nullable=False)
    descripcion = Column(String(2000), nullable=True)
    estado = Column(String(50), default="pendiente")
    solicitud_fecha = Column(DateTime, default=func.now())
    respuesta_fecha = Column(DateTime, nullable=True)
    respuesta = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="solicitudes_derecho")
