from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from app.routes.deps import get_current_user, get_client_ip
from app.core.config import settings
from app.core.limiter import limiter
from app.services.audit_service import log_audit
from app.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/ai", tags=["Asistente IA"])

SYSTEM_PROMPT = (
    "Eres un asistente experto en proteccion de datos personales, especificamente en la "
    "Ley 21.719 de Chile (norma que regula la proteccion de la vida privada y el tratamiento "
    "de los datos personales). Tambien conoces la Ley 19.628 sobre proteccion de la vida "
    "privada y el Decreto con Fuerza de Ley 1/2023 que la reemplaza.\n\n"
    "Tu rol es ayudar a los responsables del tratamiento de datos personales a entender sus "
    "obligaciones, responder preguntas sobre que es un RAT (Registro de Actividades de "
    "Tratamiento), como llenarlo, cuando se requiere una EIPD (Evaluacion de Impacto en la "
    "Proteccion de Datos), que garantias aplican para transferencias internacionales, como "
    "manejar brechas de seguridad, y cualquier duda relacionada con el cumplimiento de la ley.\n\n"
    "Responde siempre en espanol, de forma clara y concisa. Si no estas seguro de algo, "
    "indicalo honestamente en lugar de inventar una respuesta. No des consejos legales "
    "profesionales —remite al usuario a un abogado especializado cuando corresponda."
)


class AskRequest(BaseModel):
    question: str
    context: Optional[str] = None


class AskResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AskResponse)
@limiter.limit("10/minute")
async def ask_ai(request: Request, req: AskRequest, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Asistente IA sobre Ley 21.719 de Chile.
    Usa Groq llama-3.3-70b-versatile (endpoint compatible OpenAI).
    """
    import requests

    if not settings.GROQ_API_KEY:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY no configurada. El Asistente IA requiere una API key de Groq."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if req.context:
        messages.append({"role": "user", "content": f"Contexto actual del sistema:\n{req.context}"})
    messages.append({"role": "user", "content": req.question})

    payload = {
        "model": settings.GROQ_CHAT_MODEL,
        "messages": messages,
        "max_completion_tokens": 800,
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        try:
            answer = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as e:
            from fastapi import HTTPException as HTTPExc, status
            raise HTTPExc(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq formato inesperado. Keys: {list(data.keys())}. Error: {e}"
            )
    except Exception as e:
        from fastapi import HTTPException as HTTPExc, status
        raise HTTPExc(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al consultar Groq: {str(e)}"
        )

    try:
        log_audit(
            db=db,
            entidad="ai",
            entidad_id=0,
            accion="consulta",
            usuario=current_user.username,
            detalle={"question": req.question[:500], "context": req.context[:500] if req.context else None, "provider": "groq"},
            ip_origen=get_client_ip(request),
        )
        db.commit()
    except Exception as audit_err:
        import logging
        logging.getLogger(__name__).warning(f"Audit log failed: {audit_err}")

    return {"answer": answer}
