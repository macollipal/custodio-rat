from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database.database import Base


class SolicitudToken(Base):
    __tablename__ = "solicitud_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(36), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used = Column(Boolean, default=False, nullable=False)