"""
Endpoints admin del Asesor (solo superadmin).
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.schemas.asesor import (
    AsesorIndexRequest,
    AsesorIndexResponse,
    AsesorStatsResponse,
)
from app.services.asesor_indexer import index_corpus, get_stats
from app.services.audit_service import log_audit
from app.models.user import User, RolGlobal

router = APIRouter(prefix="/admin/asesor", tags=["Admin · Asesor"])


def require_superadmin(current_user: User) -> User:
    if current_user.rol_global != RolGlobal.SUPERADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo superadmin puede acceder a este endpoint.",
        )
    return current_user


@router.post("/index", response_model=AsesorIndexResponse)
async def index_endpoint(
    req: AsesorIndexRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Indexa o actualiza el corpus."""
    require_superadmin(current_user)
    result = await index_corpus(db, paths=req.paths, force=req.force)

    try:
        log_audit(
            db=db,
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
            ip_origen=request.client.host if request.client else None,
        )
        db.commit()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Audit log failed: {e}")

    return {
        "indexed": result["indexed"],
        "skipped": result["skipped"],
        "errors": result["errors"],
        "duration_ms": result["duration_ms"],
    }


@router.get("/stats", response_model=AsesorStatsResponse)
async def stats_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Estadísticas del corpus."""
    require_superadmin(current_user)
    return get_stats(db)


@router.delete("/documents/{chunk_id}")
async def delete_chunk_endpoint(
    chunk_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un chunk del índice."""
    require_superadmin(current_user)
    from app.models.asesor import AsesorChunk
    chunk = db.query(AsesorChunk).filter(AsesorChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk no encontrado")
    db.delete(chunk)
    db.commit()

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
        import logging
        logging.getLogger(__name__).warning(f"Audit log failed: {e}")

    return {"ok": True, "id": chunk_id}
