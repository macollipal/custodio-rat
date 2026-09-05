"""
Asesor Corpus Store: gestión de documentos del corpus (upload, delete, list, download).
Los archivos se guardan en OCI Object Storage (o local en dev) y los metadatos en BD.
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.storage import get_storage_backend, StorageBackend
from app.models.asesor import AsesorCorpusDocument, AsesorChunk
from app.services.asesor_chunker import chunk_text
from app.services.asesor_embedder import embed_texts

logger = logging.getLogger(__name__)

SUPPORTED_EXT = {".md", ".txt", ".markdown"}
MAX_FILE_SIZE = 5 * 1024 * 1024
CORPUS_PREFIX = "asesor_corpus"

SOURCE_TYPE_KEYWORDS = {
    "ley": ["ley", "21719"],
    "caso_uso": ["caso", "casos_de_uso"],
    "auditoria": ["auditori"],
    "manual": ["manual", "que_es"],
}


def _infer_source_type(filename: str) -> str:
    fname_lower = filename.lower()
    for source_type, keywords in SOURCE_TYPE_KEYWORDS.items():
        if any(kw in fname_lower for kw in keywords):
            return source_type
    return "otros"


def _generate_object_name(original_filename: str) -> str:
    ext = Path(original_filename).suffix.lower()
    unique = uuid.uuid4().hex[:12]
    safe_name = Path(original_filename).stem[:50]
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in ("-", "_")).rstrip()
    return f"{CORPUS_PREFIX}/{safe_name}_{unique}{ext}"


def _compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _extract_title(content: str) -> Optional[str]:
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()[:255]
    return None


def get_storage() -> StorageBackend:
    return get_storage_backend()


class AsesorCorpusStore:
    def list_documents(self, db: Session) -> List[AsesorCorpusDocument]:
        return (
            db.query(AsesorCorpusDocument)
            .filter(AsesorCorpusDocument.status == "active")
            .order_by(AsesorCorpusDocument.created_at.desc())
            .all()
        )

    def get_document(self, db: Session, doc_id: int) -> Optional[AsesorCorpusDocument]:
        return (
            db.query(AsesorCorpusDocument)
            .filter(
                AsesorCorpusDocument.id == doc_id,
                AsesorCorpusDocument.status == "active",
            )
            .first()
        )

    def upload(
        self,
        db: Session,
        file_content: bytes,
        original_filename: str,
        content_type: str,
        uploaded_by_id: Optional[int],
        uploaded_by_username: Optional[str],
    ) -> Tuple[AsesorCorpusDocument, dict]:
        content_hash = _compute_hash(file_content)

        existing = (
            db.query(AsesorCorpusDocument)
            .filter(AsesorCorpusDocument.content_hash == content_hash)
            .first()
        )
        if existing and existing.status == "active":
            raise ValueError(
                f"Este archivo ya existe en el corpus: {existing.original_filename} "
                f"(subido el {existing.created_at.strftime('%d %b %Y')})"
            )

        ext = Path(original_filename).suffix.lower()
        if ext not in SUPPORTED_EXT:
            raise ValueError(
                f"Extensión no soportada: {ext}. Solo: {', '.join(SUPPORTED_EXT)}"
            )

        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(
                f"El archivo excede el tamaño máximo de {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        try:
            content_str = file_content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("El archivo debe ser texto UTF-8 ( .md o .txt )")

        object_name = _generate_object_name(original_filename)
        storage = get_storage()
        storage.upload(file_content, object_name, content_type)

        title = _extract_title(content_str) or original_filename
        source_type = _infer_source_type(original_filename)

        if existing and existing.status == "deleted":
            existing.status = "active"
            existing.object_name = object_name
            existing.original_filename = original_filename
            existing.content_type = content_type
            existing.size_bytes = len(file_content)
            existing.title = title
            existing.source_type = source_type
            existing.uploaded_by_id = uploaded_by_id
            existing.uploaded_by_username = uploaded_by_username
            existing.updated_at = datetime.now(timezone.utc)
            doc = existing
        else:
            doc = AsesorCorpusDocument(
                object_name=object_name,
                original_filename=original_filename,
                content_type=content_type,
                size_bytes=len(file_content),
                content_hash=content_hash,
                title=title,
                source_type=source_type,
                chunks_indexed=0,
                status="active",
                uploaded_by_id=uploaded_by_id,
                uploaded_by_username=uploaded_by_username,
            )
            db.add(doc)

        db.commit()
        db.refresh(doc)

        index_result = self._index_document_content(
            db, doc, content_str, object_name
        )

        doc.chunks_indexed = index_result["indexed"]
        db.commit()

        return doc, index_result

    def _index_document_content(
        self,
        db: Session,
        doc: AsesorCorpusDocument,
        content: str,
        object_name: str,
    ) -> dict:
        chunks = chunk_text(content, title_hint=doc.title)
        if not chunks:
            return {"indexed": 0, "skipped": 0, "errors": ["Sin chunks"]}

        existing_hashes = set(
            row[0]
            for row in db.query(AsesorChunk.content_hash)
            .filter(AsesorChunk.source == object_name)
            .all()
        )

        new_chunks = []
        for c in chunks:
            h = _compute_hash(c["content"].encode("utf-8"))
            if h in existing_hashes:
                continue
            new_chunks.append({**c, "content_hash": h})

        if not new_chunks:
            return {"indexed": 0, "skipped": len(chunks), "errors": []}

        texts = [c["content"] for c in new_chunks]
        embs, provider_used = embed_texts(texts)

        indexed = 0
        errors: List[str] = []
        for c, emb in zip(new_chunks, embs):
            chunk_row = AsesorChunk(
                source=object_name,
                source_type=doc.source_type,
                title=c.get("title"),
                content=c["content"],
                content_hash=c["content_hash"],
                chunk_index=c["chunk_index"],
                token_count=c["token_count"],
                embedding_json=__import__("json").dumps(emb),
                chunk_metadata=__import__("json").dumps({
                    "document_id": doc.id,
                    "file_size": doc.size_bytes,
                    "indexed_at": datetime.now(timezone.utc).isoformat(),
                }),
            )
            db.add(chunk_row)
            indexed += 1

        db.commit()
        logger.info(
            f"Indexed doc {doc.id} ({doc.original_filename}): "
            f"{indexed} chunks indexed, provider={provider_used}"
        )
        return {"indexed": indexed, "skipped": len(chunks) - indexed, "errors": errors}

    def download_content(self, db: Session, doc_id: int) -> bytes:
        doc = self.get_document(db, doc_id)
        if not doc:
            raise FileNotFoundError(f"Documento {doc_id} no encontrado")
        storage = get_storage()
        return storage.download(doc.object_name)

    def get_download_url(self, db: Session, doc_id: int, expires_in: int = 300) -> str:
        doc = self.get_document(db, doc_id)
        if not doc:
            raise FileNotFoundError(f"Documento {doc_id} no encontrado")
        storage = get_storage()
        if hasattr(storage, "create_presigned_url"):
            return storage.create_presigned_url(doc.object_name, expires_in)
        return storage.get_url(doc.object_name)

    def delete_document(
        self,
        db: Session,
        doc_id: int,
        deleted_by_username: Optional[str],
    ) -> AsesorCorpusDocument:
        doc = self.get_document(db, doc_id)
        if not doc:
            raise FileNotFoundError(f"Documento {doc_id} no encontrado")

        db.query(AsesorChunk).filter(AsesorChunk.source == doc.object_name).delete()

        doc.status = "deleted"
        doc.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(doc)

        try:
            storage = get_storage()
            storage.delete(doc.object_name)
        except Exception as e:
            logger.warning(f"OCI delete failed for {doc.object_name}: {e}")

        logger.info(f"Deleted corpus document {doc_id} ({doc.original_filename})")
        return doc

    def reindex_document(self, db: Session, doc_id: int) -> dict:
        doc = self.get_document(db, doc_id)
        if not doc:
            raise FileNotFoundError(f"Documento {doc_id} no encontrado")

        db.query(AsesorChunk).filter(AsesorChunk.source == doc.object_name).delete()
        db.commit()

        content = self.download_content(db, doc_id).decode("utf-8")
        return self._index_document_content(db, doc, content, doc.object_name)


_asesor_corpus_store: Optional[AsesorCorpusStore] = None


def get_asesor_corpus_store() -> AsesorCorpusStore:
    global _asesor_corpus_store
    if _asesor_corpus_store is None:
        _asesor_corpus_store = AsesorCorpusStore()
    return _asesor_corpus_store
