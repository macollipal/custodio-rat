from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class SolicitudHistorial(Base):
    __tablename__ = "solicitud_derecho_historial"

    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes_derecho.id"), nullable=False, index=True)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha = Column(DateTime, default=func.now())
    usuario_nombre = Column(String(255), nullable=True)
