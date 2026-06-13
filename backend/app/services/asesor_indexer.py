"""
Asesor Indexer: indexa el corpus a la BD con embeddings.
Idempotente por sha256 del contenido.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asesor import AsesorChunk
from app.services.asesor_chunker import chunk_text
from app.services.asesor_embedder import embed_texts

logger = logging.getLogger(__name__)

SUPPORTED_EXT = {".md", ".txt", ".markdown"}


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _infer_source_type(path: str) -> str:
    p = path.lower()
    if "ley" in p or "21719" in p:
        return "ley"
    if "caso" in p or "casos_de_uso" in p:
        return "caso_uso"
    if "auditori" in p:
        return "auditoria"
    if "manual" in p or "que_es" in p:
        return "manual"
    return "otros"


def _infer_title(path: str, content: str) -> Optional[str]:
    """Extrae el primer encabezado Markdown como título."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()[:255]
    return os.path.basename(path)[:255]


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def list_corpus_files(corpus_path: Optional[str] = None) -> List[str]:
    """Lista archivos soportados en el corpus."""
    root = corpus_path or settings.ASESOR_CORPUS_PATH
    if not os.path.isdir(root):
        return []
    files: List[str] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in SUPPORTED_EXT:
                files.append(os.path.join(dirpath, fn))
    return files


async def index_corpus(
    db: Session,
    paths: Optional[List[str]] = None,
    force: bool = False,
    corpus_path: Optional[str] = None,
) -> dict:
    """
    Indexa el corpus. Retorna {indexed, skipped, errors, duration_ms}.
    """
    start = time.time()
    files = paths if paths else list_corpus_files(corpus_path)
    if not files:
        return {"indexed": 0, "skipped": 0, "errors": ["No hay archivos para indexar"], "duration_ms": 0}

    indexed = 0
    skipped = 0
    errors: List[str] = []
    provider_used = "none"

    for path in files:
        try:
            if not os.path.exists(path):
                errors.append(f"No existe: {path}")
                continue

            content = _read_file(path)
            chunks = chunk_text(content, title_hint=_infer_title(path, content))
            if not chunks:
                errors.append(f"Sin chunks: {path}")
                continue

            # Si force, eliminar chunks previos del source
            if force:
                db.query(AsesorChunk).filter(AsesorChunk.source == path).delete()

            # Calcular hashes primero para saber cuáles son nuevos
            new_chunks = []
            for c in chunks:
                h = _hash(c["content"])
                existing = db.query(AsesorChunk).filter(AsesorChunk.content_hash == h).first()
                if existing:
                    skipped += 1
                    continue
                new_chunks.append({**c, "content_hash": h})

            if not new_chunks:
                continue

            # Generar embeddings en batch
            texts = [c["content"] for c in new_chunks]
            try:
                embs, provider_used = await embed_texts(texts)
            except Exception as e:
                errors.append(f"Embeddings fallaron para {path}: {e}")
                continue

            for c, emb in zip(new_chunks, embs):
                chunk_row = AsesorChunk(
                    source=path,
                    source_type=_infer_source_type(path),
                    title=c.get("title"),
                    content=c["content"],
                    content_hash=c["content_hash"],
                    chunk_index=c["chunk_index"],
                    token_count=c["token_count"],
                    embedding_json=json.dumps(emb),
                    chunk_metadata=json.dumps({"file_size": len(content), "indexed_at": datetime.now(timezone.utc).isoformat()}),
                )
                db.add(chunk_row)
                indexed += 1

            db.commit()
        except Exception as e:
            db.rollback()
            errors.append(f"Error procesando {path}: {e}")

    duration = int((time.time() - start) * 1000)
    logger.info(f"Asesor indexer: indexed={indexed} skipped={skipped} errors={len(errors)} provider={provider_used} duration={duration}ms")
    return {
        "indexed": indexed,
        "skipped": skipped,
        "errors": errors,
        "duration_ms": duration,
        "provider": provider_used,
    }


def get_stats(db: Session) -> dict:
    """Retorna estadísticas del corpus."""
    total_chunks = db.query(AsesorChunk).count()
    docs = db.query(AsesorChunk.source).distinct().all()
    total_documents = len(docs)
    chunks_por_source: dict = {}
    for row in db.query(AsesorChunk.source).all():
        chunks_por_source[row[0]] = chunks_por_source.get(row[0], 0) + 1
    last = db.query(AsesorChunk).order_by(AsesorChunk.created_at.desc()).first()
    ultimo = last.created_at if last else None
    provider = "minimax" if settings.MINIMAX_API_KEY else ("openai" if settings.OPENAI_API_KEY else "none")
    return {
        "total_chunks": total_chunks,
        "total_documents": total_documents,
        "chunks_por_source": chunks_por_source,
        "ultimo_indexado": ultimo,
        "provider": provider,
    }
