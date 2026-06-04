from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base


class TktHistorial(Base):
    __tablename__ = "tkt_historial"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tkt_solicitud_derecho.id"), nullable=False, index=True)
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    descripcion = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ticket = relationship("TktSolicitudDerecho", back_populates="historial")
    user = relationship("User")

    class Meta:
        table_name = "tkt_historial"