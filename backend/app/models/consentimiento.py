"""
Modelo de Consentimiento de Titulares de Datos Personales.

C4 fix (2026-07-18): TODA PII se almacena cifrada con Fernet en columnas *_cipher.
Las columnas plaintext (nombre_titular, email_titular, texto_consentimiento, ip_origen)
se eliminan en migration 016 pero quedan como nullable para backward compatibility
mientras la migration se aplica a Neon QA.

Compliance: Arts. 11, 12, 19 Ley 21.719.
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

    # PII fields: cifrados en BD. Se descifran on-demand en el schema de salida.
    # Las columnas *_cipher existen en BD legacy (nullable=True) y se hacen
    # NOT NULL despues de aplicar migration 016 (C4).
    nombre_titular_cipher: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    email_titular_cipher: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    texto_consentimiento_cipher: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    texto_consentimiento_hash: Mapped[str] = mapped_column(String(64), nullable=True)

    # Columnas plaintext legacy. Se eliminan en migration 016.
    # Se mantienen como nullable en modelo para no romper el esquema legacy
    # en Neon QA hasta que se aplique la migration.
    nombre_titular: Mapped[str] = mapped_column(String(300), nullable=True)
    email_titular: Mapped[str] = mapped_column(String(200), nullable=True)
    texto_consentimiento: Mapped[str] = mapped_column(Text, nullable=True)
    ip_origen: Mapped[str] = mapped_column(String(50), nullable=True)

    # Versión del aviso de privacidad aceptado — permite probar qué texto aceptó el titular (Art. 12)
    version_politica: Mapped[str] = mapped_column(String(100), nullable=True)

    canal: Mapped[CanalConsentimiento] = mapped_column(Enum(CanalConsentimiento), nullable=False)
    fecha_obtencion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_revocacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ip_origen_masked: Mapped[str] = mapped_column(String(18), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    company: Mapped["Company"] = relationship("Company", back_populates="consentimientos")  # noqa: F821
    rat: Mapped["RAT"] = relationship("RAT", back_populates="consentimientos")  # noqa: F821