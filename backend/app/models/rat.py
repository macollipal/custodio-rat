"""
Modelo del Registro de Actividades de Tratamiento (RAT).
Basado en los requisitos del Art. 16 de la Ley 21.719 de Chile.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Date, Enum, ForeignKey, Integer, String, Text, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class EstadoRAT(str, PyEnum):
    BORRADOR = "borrador"
    COMPLETO = "completo"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"


class EstadoEIPD(str, PyEnum):
    NO_REQUERIDA = "no_requerida"
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"


class RAT(Base):
    __tablename__ = "rats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Campos principales (Art. 16 Ley 21.719)
    nombre_proceso: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria_datos: Mapped[str] = mapped_column(String(500), nullable=False)
    finalidad: Mapped[str] = mapped_column(Text, nullable=False)
    base_legal: Mapped[str] = mapped_column(String(300), nullable=False)
    fuente_datos: Mapped[str] = mapped_column(String(300), nullable=False)
    transferencia_datos: Mapped[str] = mapped_column(Text, nullable=True)
    plazo_retencion: Mapped[str] = mapped_column(String(200), nullable=False)

    # Categorías de titulares (Art. 16 Ley 21.719 — campo mínimo obligatorio)
    categoria_titulares: Mapped[str] = mapped_column(String(500), nullable=True)

    # Campos adicionales de cumplimiento
    medidas_seguridad: Mapped[str] = mapped_column(Text, nullable=True)
    destinatarios: Mapped[str] = mapped_column(Text, nullable=True)
    transferencia_internacional: Mapped[bool] = mapped_column(Boolean, default=False)
    pais_destino: Mapped[str] = mapped_column(String(200), nullable=True)
    garantias_transferencia_int: Mapped[str] = mapped_column(String(500), nullable=True)
    datos_sensibles: Mapped[bool] = mapped_column(Boolean, default=False)
    tipo_dato_sensible: Mapped[str] = mapped_column(String(500), nullable=True)
    evaluacion_impacto: Mapped[bool] = mapped_column(Boolean, default=False)
    estado_eipd: Mapped[str] = mapped_column(String(50), nullable=True, default="no_requerida")
    fecha_eipd: Mapped[datetime] = mapped_column(Date, nullable=True)
    decisiones_automatizadas: Mapped[bool] = mapped_column(Boolean, default=False)

    # Encargado del tratamiento (Art. 16 Ley 21.719)
    nombre_encargado: Mapped[str] = mapped_column(String(500), nullable=True)
    tiene_contrato_encargado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bloqueo temporal (Art. 8 ter — REC-01)
    bloqueado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Test interés legítimo (Art. 16 — 3 pasos obligatorios)
    test_interes_legitimo: Mapped[str] = mapped_column(Text, nullable=True)

    # Documento que respalda la base legal (MVP: almacena en la BD)
    # Nombre original del archivo
    archivo_base_legal_nombre: Mapped[str] = mapped_column(String(500), nullable=True)
    # Tipo MIME del archivo
    archivo_base_legal_tipo: Mapped[str] = mapped_column(String(100), nullable=True)
    # Contenido del archivo como binario (PostgreSQL BYTEA)
    archivo_base_legal_datos: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    # Hash SHA-256 para verificar integridad
    archivo_base_legal_hash: Mapped[str] = mapped_column(String(64), nullable=True)

    # Estado y auditoría
    estado: Mapped[EstadoRAT] = mapped_column(
        Enum(EstadoRAT), default=EstadoRAT.BORRADOR, nullable=False
    )
    observaciones_auditoria: Mapped[str] = mapped_column(Text, nullable=True)
    aprobado_por: Mapped[str] = mapped_column(String(100), nullable=True)
    fecha_aprobacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    company: Mapped["Company"] = relationship("Company", back_populates="rats")  # noqa: F821
    eipd: Mapped["EIPD"] = relationship("EIPD", back_populates="rat", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    consentimientos: Mapped[list["Consentimiento"]] = relationship("Consentimiento", back_populates="rat", cascade="all, delete-orphan")  # noqa: F821

    def calcular_completitud(self) -> int:
        """Retorna el porcentaje de completitud del registro."""
        campos_obligatorios = [
            self.nombre_proceso,
            self.categoria_datos,
            self.categoria_titulares,
            self.finalidad,
            self.base_legal,
            self.fuente_datos,
            self.plazo_retencion,
        ]
        campos_recomendados = [
            self.medidas_seguridad,
            self.destinatarios,
            self.transferencia_datos,
        ]
        total = len(campos_obligatorios) + len(campos_recomendados)
        completados = sum(1 for c in campos_obligatorios + campos_recomendados if c and str(c).strip())

        # Penalización: si base legal ≠ "Otra" y no hay documento que la respalde
        if self.base_legal and self.base_legal.strip().lower() != "otra":
            if not self.archivo_base_legal_datos:
                completados = max(completados - 1, 0)

        return round((completados / total) * 100)

    def calcular_nivel_riesgo(self) -> str:
        """Calcula el nivel de riesgo del proceso según factores de la Ley 21.719."""
        score = 0
        if self.datos_sensibles:
            score += 2
        if self.evaluacion_impacto and (self.estado_eipd or "pendiente") != "completada":
            score += 2
        if self.decisiones_automatizadas:
            score += 2
        if self.transferencia_internacional and not self.garantias_transferencia_int:
            score += 1
        tipo = (self.tipo_dato_sensible or "").lower()
        if "biométric" in tipo or "biometric" in tipo or "menor" in tipo:
            score += 1
        if self.nombre_encargado and not self.tiene_contrato_encargado:
            score += 1
        if score >= 7:
            return "critico"
        if score >= 5:
            return "alto"
        if score >= 3:
            return "medio"
        return "bajo"
