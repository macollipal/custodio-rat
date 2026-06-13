"""
Endpoint público del Asesor: POST /asesor/ask
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database.database import get_db
from app.routes.deps import get_current_user
from app.schemas.asesor import AsesorAskRequest, AsesorAskResponse
from app.services.asesor_service import ask
from app.services.audit_service import log_audit

router = APIRouter(prefix="/asesor", tags=["Asesor"])


@router.post("/ask", response_model=AsesorAskResponse)
@limiter.limit("10/minute")
async def ask_endpoint(
    request: Request,
    req: AsesorAskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Consulta al Asesor con RAG.
    Devuelve respuesta con citas a fuentes.
    """
    try:
        result = await ask(db, req.question, req.context or "")
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar el Asesor: {str(e)}",
        )

    # Auditoría
    try:
        log_audit(
            db=db,
            entidad="asesor",
            entidad_id=0,
            accion="consulta",
            usuario=current_user.username,
            detalle={
                "question": req.question[:500],
                "sources": [{"source": s["source"], "score": s["score"]} for s in result["sources"]],
                "top_score": result["sources"][0]["score"] if result["sources"] else None,
                "provider": result["provider"],
                "embedding_provider": result["embedding_provider"],
                "latency_ms": result["latency_ms"],
            },
            ip_origen=request.client.host if request.client else None,
        )
        db.commit()
    except Exception as audit_err:
        import logging
        logging.getLogger(__name__).warning(f"Audit log failed: {audit_err}")

    return result
