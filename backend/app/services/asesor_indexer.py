"""
Asesor Indexer: indexa el corpus a la BD con embeddings.
Idempotente por sha256 del contenido.

Prioriza documentos de BD (AsesorCorpusDocument) sobre filesystem.
Los documentos subidos via /upload se guardan en OCI y se indexan desde ahí.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings, BASE_DIR, BASE_DIR
from app.core.storage import get_storage_backend
from app.models.asesor import AsesorChunk, AsesorCorpusDocument
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


def list_corpus_files(db: Optional[Session] = None, corpus_path: Optional[str] = None) -> List[str]:
    """Lista archivos soportados para indexar.

    Prioriza BD (documentos subidos a OCI) con fallback a filesystem.
    Si la tabla AsesorCorpusDocument tiene documentos activos, retorna solo
    los object_names de OCI (que se descargan durante el index).
    Si la BD está vacía, usa el filesystem local (backwards compatible).
    """
    if db is not None:
        bd_docs = db.query(AsesorCorpusDocument).filter(
            AsesorCorpusDocument.status == "active"
        ).all()
        if bd_docs:
            logger.info(f"list_corpus_files: usando {len(bd_docs)} documentos de BD (OCI)")
            return [doc.object_name for doc in bd_docs]

    rel_path = corpus_path or settings.asesor_config()["corpus_path"]
    root = BASE_DIR / rel_path
    logger.info(f"list_corpus_files: BASE_DIR={BASE_DIR} rel_path={rel_path} root={root} exists={root.exists()}")
    if not root.is_dir():
        logger.warning(f"list_corpus_files: corpus dir does not exist: {root}")
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

    Acepta tanto archivos del filesystem como object_names de OCI
    (asesor_corpus/<nombre>.md). Si el path no existe en el filesystem,
    se intenta descargar desde OCI.

    Solo permite archivos dentro de corpus_path (previene path traversal)
    cuando se usan paths del filesystem.
    """
    start = time.time()
    resolved_corpus = corpus_path or settings.asesor_config()["corpus_path"]
    logger.info(f"Asesor indexer: corpus_path={resolved_corpus}, force={force}, paths={paths}")
    logger.info(f"Asesor indexer: BASE_DIR={BASE_DIR}, cwd={os.getcwd()}")
    files = paths if paths else list_corpus_files(db, corpus_path)
    logger.info(f"Asesor indexer: found {len(files)} files: {files}")
    if not files:
        return {"indexed": 0, "skipped": 0, "errors": ["No hay archivos para indexar"], "duration_ms": 0}

    safe_files: List[str] = []
    if paths:
        root = os.path.abspath(corpus_path or settings.asesor_config()["corpus_path"])
        for p in paths:
            abs_path = os.path.abspath(p)
            if abs_path.startswith(root + os.sep) or abs_path == root:
                if os.path.isfile(abs_path):
                    safe_files.append(abs_path)
            elif p.startswith(CORPUS_PREFIX + "/"):
                safe_files.append(p)
        files = safe_files

    indexed = 0
    skipped = 0
    errors: List[str] = []
    provider_used = "none"
    storage = get_storage_backend() if any(f.startswith(CORPUS_PREFIX + "/") for f in files) else None

    for path in files:
        try:
            is_oci = path.startswith(CORPUS_PREFIX + "/")
            if is_oci and storage:
                try:
                    content_bytes = storage.download(path)
                    content = content_bytes.decode("utf-8")
                except FileNotFoundError:
                    errors.append(f"No se encontró en storage: {path}")
                    continue
            elif os.path.exists(path):
                content = _read_file(path)
            else:
                errors.append(f"No existe: {path}")
                continue

            chunks = chunk_text(content, title_hint=_infer_title(path, content))
            if not chunks:
                errors.append(f"Sin chunks: {path}")
                continue

            if force:
                db.query(AsesorChunk).filter(AsesorChunk.source == path).delete()

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

            texts = [c["content"] for c in new_chunks]
            try:
                embs, provider_used = embed_texts(texts)
            except Exception as e:
                errors.append(f"Embeddings fallaron para {path}: {e}")
                continue

            for c, emb in zip(new_chunks, embs):
                doc_meta = {}
                if is_oci:
                    doc = db.query(AsesorCorpusDocument).filter(
                        AsesorCorpusDocument.object_name == path,
                        AsesorCorpusDocument.status == "active",
                    ).first()
                    if doc:
                        doc_meta["document_id"] = doc.id
                chunk_row = AsesorChunk(
                    source=path,
                    source_type=_infer_source_type(path),
                    title=c.get("title"),
                    content=c["content"],
                    content_hash=c["content_hash"],
                    chunk_index=c["chunk_index"],
                    token_count=c["token_count"],
                    embedding_json=json.dumps(emb),
                    chunk_metadata=json.dumps({
                        "file_size": len(content_bytes) if is_oci else len(content.encode("utf-8")),
                        "indexed_at": datetime.now(timezone.utc).isoformat(),
                        **doc_meta,
                    }),
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
    provider = "cohere" if settings.COHERE_API_KEY else ("groq" if settings.GROQ_API_KEY else "none")
    return {
        "total_chunks": total_chunks,
        "total_documents": total_documents,
        "chunks_por_source": chunks_por_source,
        "ultimo_indexado": ultimo,
        "provider": provider,
    }
