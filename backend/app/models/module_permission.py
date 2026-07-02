"""
Modelo ModulePermission — feature gates por empresa y modulo.

Permite activar/desactivar modulos completos (RAT, ARCO, Brechas,
EIPD, Consentimientos) por empresa. Util para:
- Onboarding gradual (activar RAT primero, ARCO despues)
- Empresas que no manejan datos sensibles (no necesitan EIPD)
- Clientes que solo quieren subset de funcionalidades
- Planes de suscripcion futuros

El modelo es (company_id, modulo) UNIQUE. Si no existe fila,
se considera enabled=True (default opt-out).
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ModuloEnum:
    """Modulos disponibles para feature gates."""
    RAT = "RAT"
    ARCO = "ARCO"
    BRECHAS = "BRECHAS"
    EIPD = "EIPD"
    CONSENTIMIENTOS = "CONSENTIMIENTOS"
    ENCARGADOS = "ENCARGADOS"
    TRANSPARENCIA = "TRANSPARENCIA"
    REPORTES = "REPORTES"
    ASESOR = "ASESOR"


class ModulePermission(Base):
    __tablename__ = "module_permissions"
    __table_args__ = (
        UniqueConstraint("company_id", "modulo", name="uq_module_permissions_company_modulo"),
        Index("ix_module_permissions_company", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )