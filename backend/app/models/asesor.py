"""
Modelos Asesor: chunks del corpus con embeddings y documentos del corpus.

v1.0 almacena el embedding como JSON serializado (List[float]) en un
campo Text para máxima portabilidad (SQLite local + Neon prod).

Migración a pgvector (v1.1):
    Reemplazar la columna `embedding_json` por `embedding VECTOR(1536)`
    usando `CREATE EXTENSION vector;` en Neon y `pgvector.sqlalchemy.Vector`
    en el modelo. Mantener `embedding_json` durante la transición.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AsesorCorpusDocument(Base):
    __tablename__ = "asesor_corpus_documents"
    __table_args__ = (
        Index("ix_asesor_corpus_documents_object_name", "object_name"),
        Index("ix_asesor_corpus_documents_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    object_name: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="text/markdown")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="otros")
    chunks_indexed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    uploaded_by_id: Mapped[int] = mapped_column(Integer, nullable=True)
    uploaded_by_username: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AsesorChunk(Base):
    __tablename__ = "asesor_chunks"
    __table_args__ = (
        Index("ix_asesor_chunks_source", "source"),
        Index("ix_asesor_chunks_source_type", "source_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    # Almacenamos el embedding como JSON serializado (List[float]).
    # En v1.1 migraremos a VECTOR(1536) con pgvector.
    embedding_json: Mapped[str] = mapped_column(Text, nullable=True)
    chunk_metadata: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AsesorConversacion(Base):
    """Registro de conversaciones con el Asesor IA (Arts. 19, 20 Ley 21.719).

    Permite trazabilidad de las consultas y respuestas generadas por el LLM
    para demostrar compliance ante la autoridad.
    """
    __tablename__ = "asesor_conversaciones"
    __table_args__ = (
        Index("ix_asesor_conversaciones_user", "user_id"),
        Index("ix_asesor_conversaciones_company", "company_id"),
        Index("ix_asesor_conversaciones_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sources_json: Mapped[str] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    provider: Mapped[str] = mapped_column(String(50), nullable=True)
    embedding_provider: Mapped[str] = mapped_column(String(50), nullable=True)
    ip_origen: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
