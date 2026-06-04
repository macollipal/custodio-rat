"""
Modelo de empresa (responsable del tratamiento de datos).
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import List
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(300), nullable=False)
    rut: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    rubro: Mapped[str] = mapped_column(String(200), nullable=True)
    rubro_id: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id"), nullable=True)
    direccion: Mapped[str] = mapped_column(String(400), nullable=True)
    contacto_dpo: Mapped[str] = mapped_column(String(200), nullable=True)  # Delegado de Protección
    email_dpo: Mapped[str] = mapped_column(String(200), nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    canal_ejercicio_derechos: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relación con registros RAT
    rats: Mapped[list["RAT"]] = relationship("RAT", back_populates="company", cascade="all, delete-orphan")
    consentimientos: Mapped[list["Consentimiento"]] = relationship("Consentimiento", back_populates="company", cascade="all, delete-orphan")  # noqa: F821
    rubro_rel: Mapped["Rubro"] = relationship("Rubro")
    solicitudes_derecho: Mapped[list["SolicitudDerecho"]] = relationship(
        "SolicitudDerecho", back_populates="company", cascade="all, delete-orphan"
    )
    tkt_solicitudes: Mapped[list["TktSolicitudDerecho"]] = relationship(
        "TktSolicitudDerecho", back_populates="company", cascade="all, delete-orphan"
    )
