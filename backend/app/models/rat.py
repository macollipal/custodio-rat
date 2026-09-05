"""
Modelo del Registro de Actividades de Tratamiento (RAT).
Basado en los requisitos del Art. 16 de la Ley 21.719 de Chile.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Date, Enum, ForeignKey, Index, Integer, String, Text, Boolean, LargeBinary, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.services.rat_calculations import (
    UMBRAL_RIESGO_CRITICO,
    UMBRAL_RIESGO_ALTO,
    UMBRAL_RIESGO_MEDIO,
    calcular_completitud_de_modelo,
    calcular_nivel_riesgo_de_modelo,
)


UMBRAL_RIESGO_CRITICO = UMBRAL_RIESGO_CRITICO
UMBRAL_RIESGO_ALTO = UMBRAL_RIESGO_ALTO
UMBRAL_RIESGO_MEDIO = UMBRAL_RIESGO_MEDIO


class EstadoRAT(str, PyEnum):
    BORRADOR = "borrador"
    COMPLETO = "completo"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"
    ARCHIVADO = "archivado"


class EstadoEIPD(str, PyEnum):
    NO_REQUERIDA = "no_requerida"
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"


class RAT(Base):
    __tablename__ = "rats"
    __table_args__ = (
        Index("ix_rats_company_estado", "company_id", "estado"),
    )

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

    # Categoría de titulares (Art. 16 Ley 21.719 — campo mínimo obligatorio)
    categoria_titulares: Mapped[str] = mapped_column(String(500), nullable=False)

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

    # Campos nuevos gaps Ley 21.719 (Iter 10)
    sistema_almacenamiento: Mapped[str] = mapped_column(String(500), nullable=True)
    volumen_titulares_estimado: Mapped[int] = mapped_column(Integer, nullable=True)
    operaciones_tratamiento: Mapped[dict] = mapped_column(JSON, nullable=True)
    logica_automatizada: Mapped[str] = mapped_column(Text, nullable=True)
    responsable_tratamiento_email: Mapped[str] = mapped_column(String(200), nullable=True)

    # Campos Tier 1 - Gaps criticos Ley 21.719 (Iter 11 - analisis ProBest)
    datos_nna: Mapped[str] = mapped_column(String(50), nullable=True)
    nivel_confidencialidad: Mapped[str] = mapped_column(String(20), nullable=True)
    estructura_dato: Mapped[str] = mapped_column(String(50), nullable=True)
    datos_anonimizados: Mapped[bool] = mapped_column(Boolean, default=False)
    datos_seudonimizados: Mapped[bool] = mapped_column(Boolean, default=False)

    # Origen de los datos (Art. 14 ter lit. e) — obligación de informar cuando no viene del titular)
    origen_datos: Mapped[str] = mapped_column(String(50), nullable=True)

    # Campos Tier 2 - Operativos (Iter 11 - analisis ProBest)
    ciclo_procesamiento: Mapped[str] = mapped_column(String(100), nullable=True)
    automatizacion: Mapped[str] = mapped_column(String(100), nullable=True)
    frecuencia: Mapped[str] = mapped_column(String(100), nullable=True)
    transferencia_nacional: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_clausulas: Mapped[str] = mapped_column(Text, nullable=True)
    medidas_organizativas: Mapped[str] = mapped_column(Text, nullable=True)
    mecanismos_eliminacion: Mapped[str] = mapped_column(Text, nullable=True)
    tecnica_anonimizacion: Mapped[str] = mapped_column(String(100), nullable=True)
    origen_dato_portabilidad: Mapped[str] = mapped_column(String(200), nullable=True)
    fecha_levantamiento: Mapped[datetime] = mapped_column(Date, nullable=True)

    # Encargado del tratamiento (Art. 16 Ley 21.719)
    nombre_encargado: Mapped[str] = mapped_column(String(500), nullable=True)
    tiene_contrato_encargado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Bloqueo temporal (Art. 8 ter ÔÇö REC-01)
    bloqueado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Test inter├®s leg├¡timo (Art. 16 ÔÇö 3 pasos obligatorios)
    test_interes_legitimo: Mapped[str] = mapped_column(Text, nullable=True)

    # Documento que respalda la base legal (MVP: almacena en la BD)
    # Nombre original del archivo
    archivo_base_legal_nombre: Mapped[str] = mapped_column(String(500), nullable=True)
    # Tipo MIME del archivo
    archivo_base_legal_tipo: Mapped[str] = mapped_column(String(100), nullable=True)
    # Contenido del archivo como binario (PostgreSQL BYTEA)
    archivo_base_legal_datos: Mapped[bytes] = mapped_column(LargeBinary(10_000_000), nullable=True)
    # Hash SHA-256 para verificar integridad
    archivo_base_legal_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    # URL en OCI Object Storage (cuando se migra el archivo fuera de la BD)
    archivo_base_legal_storage_url: Mapped[str] = mapped_column(String(1000), nullable=True)

    # Estado y auditor├¡a
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
    # F3.2: Soft delete para compliance Art. 19 Ley 21.719.
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Relaciones
    company: Mapped["Company"] = relationship("Company", back_populates="rats")  # noqa: F821
    eipd: Mapped["EIPD"] = relationship("EIPD", back_populates="rat", uselist=False, cascade="all, delete-orphan")  # noqa: F821
    consentimientos: Mapped[list["Consentimiento"]] = relationship("Consentimiento", back_populates="rat", cascade="all, delete-orphan")  # noqa: F821

    def calcular_completitud(self) -> int:
        """Retorna el porcentaje de completitud del registro (0-100).

        H3.1 (auditoria 2026-07-07): delega a app.services.rat_calculations
        para evitar el bug 2026-07-08 donde SQLAlchemy intentaba invocar este
        metodo como columna y lanzaba TypeError en runtime.

        Formula Ley 21.719 (Art. 16) + gaps Tier 1/Tier 2 (Iter 11):
        - 7 obligatorios Art. 16
        - 3 recomendados Art. 16
        - 5 Tier 1 criticos compliance APDP
        - 10 Tier 2 operativos
        Total: 25 campos. Penalizacion -1 si base legal != 'Otra' sin doc adjunto.
        """
        return calcular_completitud_de_modelo(self)

    def calcular_nivel_riesgo(self) -> str:
        """Calcula el nivel de riesgo del proceso segun factores de la Ley 21.719.

        H3.1 (auditoria 2026-07-07): delega a app.services.rat_calculations.
        """
        return calcular_nivel_riesgo_de_modelo(self)
