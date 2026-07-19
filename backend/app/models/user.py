"""
Modelo de usuario para autenticación local.

F3.2 (soft delete): agrega deleted_at + deleted_by para compliance
Art. 19 Ley 21.719 — retencion de registros de auditoria sin hard delete.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class RolGlobal(str, PyEnum):
    SUPERADMIN = "superadmin"
    ADMIN_EMPRESA = "admin_empresa"
    USUARIO = "usuario"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rol_global: Mapped[str] = mapped_column(String(30), default=RolGlobal.USUARIO.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # F3.2: Soft delete para compliance Art. 19 Ley 21.719.
    # Permite "eliminar" usuarios sin perder trazabilidad de auditoria.
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
