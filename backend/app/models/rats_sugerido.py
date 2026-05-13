"""
Modelo de RAT Sugerido por rubro.
Plantillas pre-llenadas que aparecen como sugerencia al crear un RAT.
"""

from sqlalchemy import Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class RATSugerido(Base):
    __tablename__ = "rats_sugeridos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rubro_id: Mapped[int] = mapped_column(Integer, ForeignKey("rubros.id"), nullable=False, index=True)
    nombre_proceso: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria_datos: Mapped[str] = mapped_column(String(500), nullable=False)
    categoria_titulares: Mapped[str] = mapped_column(String(500), nullable=True)
    finalidad: Mapped[str] = mapped_column(Text, nullable=True)
    base_legal: Mapped[str] = mapped_column(String(300), nullable=True)
    plazo_retencion: Mapped[str] = mapped_column(String(200), nullable=True)
    datos_sensibles: Mapped[bool] = mapped_column(Boolean, default=False)
    evaluacion_impacto: Mapped[bool] = mapped_column(Boolean, default=False)
    decisiones_automatizadas: Mapped[bool] = mapped_column(Boolean, default=False)

    rubro: Mapped["Rubro"] = relationship("Rubro", back_populates="rats_sugeridos")

    def __repr__(self):
        return f"<RATSugerido {self.nombre_proceso} (rubro={self.rubro_id})>"