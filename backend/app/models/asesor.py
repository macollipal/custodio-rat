"""
Modelo Asesor: chunks del corpus con embeddings.

v1.0 almacena el embedding como JSON serializado (List[float]) en un
campo Text para máxima portabilidad (SQLite local + Neon prod).

Migración a pgvector (v1.1):
    Reemplazar la columna `embedding_json` por `embedding VECTOR(1536)`
    usando `CREATE EXTENSION vector;` en Neon y `pgvector.sqlalchemy.Vector`
    en el modelo. Mantener `embedding_json` durante la transición.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


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
