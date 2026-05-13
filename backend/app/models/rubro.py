"""
Modelo de Rubros de empresas.
Ordenados por prioridad para sugerir los más comunes primero.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Rubro(Base):
    __tablename__ = "rubros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    rats_sugeridos: Mapped[list["RATSugerido"]] = relationship(
        "RATSugerido", back_populates="rubro", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Rubro {self.nombre} (orden={self.orden})>"