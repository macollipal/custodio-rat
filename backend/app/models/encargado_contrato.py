"""
Modelo de Contrato de Encargado del Tratamiento (Art. 14 quater Ley 21.719 — REC-03).
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class EncargadoContrato(Base):
    __tablename__ = "encargados_contrato"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), nullable=True, index=True)

    nombre_encargado: Mapped[str] = mapped_column(String(500), nullable=False)
    objeto: Mapped[str] = mapped_column(Text, nullable=False)
    duracion_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duracion_fin: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finalidad: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_datos: Mapped[str] = mapped_column(Text, nullable=False)
    categorias_titulares: Mapped[str] = mapped_column(Text, nullable=False)
    derechos_obligaciones: Mapped[str] = mapped_column(Text, nullable=False)

    archivo_pdf_datos: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    archivo_pdf_nombre: Mapped[str] = mapped_column(String(500), nullable=True)
    archivo_pdf_tipo: Mapped[str] = mapped_column(String(100), nullable=True)
    archivo_hash: Mapped[str] = mapped_column(String(64), nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_alerta_vencimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    company: Mapped["Company"] = relationship("Company")  # noqa: F821
    rat: Mapped["RAT"] = relationship("RAT")  # noqa: F821
