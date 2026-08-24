"""
Modelos para el módulo Data Discovery & Mapping.
Permite escanear bases de datos externas en busca de columnas con datos personales.
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TipoConector(str, PyEnum):
    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"


class EstadoEscaneo(str, PyEnum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    ERROR = "error"


class CategoriaDetectada(str, PyEnum):
    IDENTIFICADOR = "IDENTIFICADOR"
    CONTACTO = "CONTACTO"
    UBICACION_PRECISA = "UBICACION_PRECISA"
    FINANCIERO = "FINANCIERO"
    SENSIBLE_SALUD = "SENSIBLE_SALUD"
    SENSIBLE_BIOMETRICO = "SENSIBLE_BIOMETRICO"
    SENSIBLE_RELIGIOSO = "SENSIBLE_RELIGIOSO"
    SENSIBLE_POLITICO = "SENSIBLE_POLITICO"
    DEMOGRAFICO = "DEMOGRAFICO"
    TECNICO = "TECNICO"


class DataSource(Base):
    __tablename__ = "discovery_sources"
    __table_args__ = (
        Index("ix_discovery_sources_company", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # TipoConector
    host: Mapped[str] = mapped_column(String(300), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    database_name: Mapped[str] = mapped_column(String(200), nullable=False)
    username: Mapped[str] = mapped_column(String(200), nullable=False)
    password_enc: Mapped[str] = mapped_column(Text, nullable=False)  # Fernet encrypted
    schema_name: Mapped[str] = mapped_column(String(100), nullable=True)  # default: public / dbo

    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    runs = relationship("DiscoveryRun", back_populates="source", cascade="all, delete-orphan")


class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"
    __table_args__ = (
        Index("ix_discovery_runs_source", "source_id"),
        Index("ix_discovery_runs_company", "company_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("discovery_sources.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False)

    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True)
    total_tablas: Mapped[int] = mapped_column(Integer, nullable=True)
    total_columnas: Mapped[int] = mapped_column(Integer, nullable=True)
    total_hallazgos: Mapped[int] = mapped_column(Integer, nullable=True)
    total_gaps: Mapped[int] = mapped_column(Integer, nullable=True)
    ejecutado_por: Mapped[str] = mapped_column(String(100), nullable=True)

    source = relationship("DataSource", back_populates="runs")
    findings = relationship("DiscoveryFinding", back_populates="run", cascade="all, delete-orphan")


class DiscoveryFinding(Base):
    __tablename__ = "discovery_findings"
    __table_args__ = (
        Index("ix_discovery_findings_run", "run_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("discovery_runs.id"), nullable=False)

    table_name: Mapped[str] = mapped_column(String(300), nullable=False)
    column_name: Mapped[str] = mapped_column(String(300), nullable=False)
    data_type_sql: Mapped[str] = mapped_column(String(100), nullable=True)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)  # CategoriaDetectada
    descripcion: Mapped[str] = mapped_column(String(300), nullable=True)
    confianza: Mapped[int] = mapped_column(Integer, nullable=False, default=70)  # 0-100

    # Vinculación al RAT (manual, el usuario asigna)
    rat_id: Mapped[int] = mapped_column(Integer, ForeignKey("rats.id"), nullable=True)
    descartado: Mapped[bool] = mapped_column(Boolean, default=False)
    es_gap: Mapped[bool] = mapped_column(Boolean, default=False)  # sin RAT que lo cubra

    run = relationship("DiscoveryRun", back_populates="findings")
