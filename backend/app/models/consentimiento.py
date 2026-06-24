"""
Modelo de Consentimiento de Titulares de Datos Personales.

PII fields (nombre_titular, email_titular) se almacenan cifrados con Fernet
en columnas *_cipher BYTEA. La columna legacy (String) queda nullable para
backward compatibility durante la transicion (Arts. 11, 19 Ley 21.719).
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class CanalConsentimiento(str, PyEnum):
    WEB = "web"
    PAPEL = "papel"
    FIRMA_DIGITAL = "firma_digital"
    VERBAL = "verbal"
    OTRO = "otro"


class Consentimiento(Base):
    __tablename__ = "consentimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), nullable=True, index=True)

    nombre_titular: Mapped[str] = mapped_column(String(300), nullable=False)
    email_titular: Mapped[str] = mapped_column(String(200), nullable=True)
    canal: Mapped[CanalConsentimiento] = mapped_column(Enum(CanalConsentimiento), nullable=False)
    texto_consentimiento: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_obtencion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_revocacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ip_origen: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    nombre_titular_cipher: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    email_titular_cipher: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    texto_consentimiento_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    ip_origen_masked: Mapped[str] = mapped_column(String(18), nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates="consentimientos")  # noqa: F821
    rat: Mapped["RAT"] = relationship("RAT", back_populates="consentimientos")  # noqa: F821