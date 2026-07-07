"""
Endpoints admin del Asesor (solo superadmin).
"""
import logging
import threading
import time
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.schemas.asesor import (
    AsesorCorpusDocumentSchema,
    AsesorDeleteResponse,
    AsesorDocumentsListResponse,
    AsesorIndexRequest,
    AsesorIndexResponse,
    AsesorStatsResponse,
    AsesorUploadResponse,
)
from app.services.asesor_corpus_store import get_asesor_corpus_store
from app.services.asesor_indexer import index_corpus, get_stats
from app.services.audit_service import log_audit
from app.models.user import User, RolGlobal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/asesor", tags=["Admin · Asesor"])


def require_superadmin(current_user: User) -> User:
    if current_user.rol_global != RolGlobal.SUPERADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo superadmin puede acceder a este endpoint.",
        )
    return current_user


@router.post("/index", response_model=AsesorIndexResponse)
@limiter.limit("5/minute")
async def index_endpoint(
    request: Request,
    req: AsesorIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Indexa o actualiza el corpus.

    Para evitar CORS timeout en cold start con OCI + Cohere,
    el trabajo pesado se ejecuta en un thread daemon y el endpoint
    responde inmediatamente. El resultado se audita via log_audit.
    """

    require_superadmin(current_user)
    ip_origen = request.client.host if request.client else None

    result_holder: dict = {}
    error_holder: list = []

    def _index_in_thread():
        from app.database.database import SessionLocal as _SessionLocal
        _db = _SessionLocal()
        try:
            result = index_corpus(_db, paths=req.paths, force=req.force)
            result_holder.update(result)
            try:
                log_audit(
                    db=_db,
                    entidad="asesor",
                    entidad_id=0,
                    accion="index",
                    usuario=current_user.username,
                    detalle={
                        "indexed": result["indexed"],
                        "skipped": result["skipped"],
                        "errors_count": len(result["errors"]),
                        "duration_ms": result["duration_ms"],
                        "force": req.force,
                    },
                    ip_origen=ip_origen,
                )
                _db.commit()
            except Exception as e:
                logger.warning(f"Background audit log failed: {e}")
        except Exception as e:
            error_holder.append(str(e))
            logger.exception(f"Index background task failed: {e}")
        finally:
            _db.close()

    thread = threading.Thread(target=_index_in_thread, daemon=True)
    thread.start()

    time.sleep(0.1)

    return {
        "indexed": result_holder.get("indexed", 0),
        "skipped": result_holder.get("skipped", 0),
        "errors": error_holder if error_holder else result_holder.get("errors", []),
        "duration_ms": result_holder.get("duration_ms", 0),
        "status": "processing" if not result_holder and not error_holder else "done",
    }


@router.get("/stats", response_model=AsesorStatsResponse)
@limiter.limit("10/minute")
async def stats_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Estadísticas del corpus."""
    require_superadmin(current_user)
    return get_stats(db)


@router.get("/documents", response_model=AsesorDocumentsListResponse)
@limiter.limit("30/minute")
async def list_documents_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos los documentos del corpus con metadata."""
    require_superadmin(current_user)
    store = get_asesor_corpus_store()
    docs = store.list_documents(db)
    return {
        "documents": [AsesorCorpusDocumentSchema.model_validate(d) for d in docs],
        "total": len(docs),
    }


@router.post("/upload", response_model=AsesorUploadResponse)
@limiter.limit("10/minute")
async def upload_document_endpoint(
    request: Request,
    file: UploadFile = File(..., description="Archivo .md o .txt (max 5MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sube un archivo al corpus y lo indexa automáticamente."""
    require_superadmin(current_user)

    from app.services.file_validation import validate_upload
    content = validate_upload(
        file,
        allowed_extensions=["md", "txt"],
        max_bytes=5 * 1024 * 1024,  # 5MB
    )
    content_type = file.content_type or "text/plain"

    try:
        store = get_asesor_corpus_store()
        doc, index_result = store.upload(
            db=db,
            file_content=content,
            original_filename=file.filename or "documento.txt",
            content_type=content_type,
            uploaded_by_id=current_user.id,
            uploaded_by_username=current_user.username,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivo: {e}",
        )

    try:
        log_audit(
            db=db,
            entidad="asesor",
            entidad_id=doc.id,
            accion="upload",
            usuario=current_user.username,
            detalle={
                "filename": doc.original_filename,
                "size_bytes": doc.size_bytes,
                "chunks_indexed": doc.chunks_indexed,
            },
            ip_origen=request.client.host if request.client else None,
        )
        db.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Audit log failed: {e}")

    return {
        "doc_id": doc.id,
        "original_filename": doc.original_filename,
        "title": doc.title or doc.original_filename,
        "source_type": doc.source_type,
        "size_bytes": doc.size_bytes,
        "chunks_indexed": doc.chunks_indexed,
        "indexed": index_result["indexed"],
        "skipped": index_result["skipped"],
    }


@router.get("/documents/{doc_id}/download")
@limiter.limit("30/minute")
async def download_document_endpoint(
    doc_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Genera una URL de descarga para el documento (presigned URL si es OCI)."""
    require_superadmin(current_user)
    store = get_asesor_corpus_store()
    try:
        url = store.get_download_url(db, doc_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    except Exception as e:
        logger.error(f"Download URL failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar URL: {e}",
        )
    return {"download_url": url}


@router.delete("/documents/{doc_id}", response_model=AsesorDeleteResponse)
@limiter.limit("10/minute")
async def delete_document_endpoint(
    doc_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un documento del corpus (soft delete + borra chunks de BD + borra de OCI)."""
    require_superadmin(current_user)
    store = get_asesor_corpus_store()
    try:
        doc = store.delete_document(db, doc_id, deleted_by_username=current_user.username)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    except Exception as e:
        logger.error(f"Delete document failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar documento: {e}",
        )

    try:
        log_audit(
            db=db,
            entidad="asesor",
            entidad_id=doc_id,
            accion="delete_document",
            usuario=current_user.username,
            detalle={
                "filename": doc.original_filename,
                "chunks_indexed": doc.chunks_indexed,
            },
            ip_origen=request.client.host if request.client else None,
        )
        db.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Audit log failed: {e}")

    from app.models.asesor import AsesorChunk
    chunks_removed = db.query(AsesorChunk).filter(
        AsesorChunk.source == doc.object_name
    ).count()

    return {
        "ok": True,
        "doc_id": doc_id,
        "original_filename": doc.original_filename,
        "chunks_removed": chunks_removed,
    }


@router.delete("/documents/{chunk_id}")
@limiter.limit("10/minute")
async def delete_chunk_endpoint(
    chunk_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un chunk individual del índice (compatibilidad)."""
    require_superadmin(current_user)
    from app.models.asesor import AsesorChunk
    chunk = db.query(AsesorChunk).filter(AsesorChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk no encontrado")
    db.delete(chunk)
    try:
        log_audit(
            db=db,
            entidad="asesor",
            entidad_id=chunk_id,
            accion="delete",
            usuario=current_user.username,
            detalle={"source": chunk.source},
            ip_origen=request.client.host if request.client else None,
        )
        db.commit()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Audit log failed: {e}")
        db.rollback()

    return {"ok": True, "id": chunk_id}
