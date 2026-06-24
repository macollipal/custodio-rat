"""
Endpoint público del Asesor: POST /asesor/ask
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.limiter import limiter
from app.database.database import get_db
from app.models.asesor import AsesorConversacion
from app.routes.deps import get_current_user
from app.schemas.asesor import AsesorAskRequest, AsesorAskResponse
from app.services.asesor_service import ask
from app.services.audit_service import log_audit

logger = logging.getLogger(__name__)

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
    Persiste la conversacion en AsesorConversacion para trazabilidad (Arts. 19, 20).
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

    ip_cliente = request.client.host if request.client else None
    company_id = getattr(current_user, "company_id", None)

    try:
        conv = AsesorConversacion(
            user_id=current_user.id,
            company_id=company_id,
            question=req.question,
            answer=result["answer"],
            sources_json=json.dumps(
                [{"source": s["source"], "score": s["score"]} for s in result["sources"]],
                ensure_ascii=False,
            ),
            latency_ms=result["latency_ms"],
            provider=result["provider"],
            embedding_provider=result["embedding_provider"],
            ip_origen=ip_cliente,
        )
        db.add(conv)
        db.flush()
        log_audit(
            db=db,
            entidad="asesor",
            entidad_id=conv.id,
            accion="consulta",
            usuario=current_user.username,
            detalle={
                "conversacion_id": conv.id,
                "provider": result["provider"],
                "embedding_provider": result["embedding_provider"],
                "latency_ms": result["latency_ms"],
                "n_sources": len(result["sources"]),
            },
            ip_origen=ip_cliente,
        )
        db.commit()
    except Exception as persist_err:
        logger.warning(f"No se pudo persistir conversacion del Asesor: {persist_err}")
        db.rollback()

    return result
