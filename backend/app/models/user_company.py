"""
Tabla de acceso: vincula usuarios con empresas y define su rol.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class RolEmpresa(str, PyEnum):
    ADMIN  = "admin"   # puede invitar/remover usuarios de la empresa
    EDITOR = "editor"  # CRUD completo sobre el RAT
    VIEWER = "viewer"  # solo lectura


class UserCompany(Base):
    __tablename__ = "user_companies"
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_user_company"),)

    id:         Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id:    Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    rol:        Mapped[RolEmpresa] = mapped_column(Enum(RolEmpresa), default=RolEmpresa.EDITOR, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user:    Mapped["User"]    = relationship("User",    lazy="joined")   # noqa: F821
    company: Mapped["Company"] = relationship("Company", lazy="joined")   # noqa: F821
