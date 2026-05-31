from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.routes.deps import get_current_user, get_client_ip
from app.core.config import settings
from app.core.limiter import limiter
from app.services.audit_service import log_audit
from app.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/ai", tags=["Asistente IA"])

SYSTEM_PROMPT = (
    "Eres un asistente experto en protección de datos personales, específicamente en la "
    "Ley 21.719 de Chile (norma que regula la protección de la vida privada y el tratamiento "
    "de los datos personales). También conoces la Ley 19.628 sobre protección de la vida "
    "privada y el Decreto con Fuerza de Ley 1/2023 que la reemplaza.\n\n"
    "Tu rol es ayudar a los responsables del tratamiento de datos personales a entender sus "
    "obligaciones, responder preguntas sobre qué es un RAT (Registro de Actividades de "
    "Tratamiento), cómo llenarlo, cuándo se requiere una EIPD (Evaluación de Impacto en la "
    "Protección de Datos), qué garantías aplican para transferencias internacionales, cómo "
    "manejar brechas de seguridad, y cualquier duda relacionada con el cumplimiento de la ley.\n\n"
    "Responde siempre en español, de forma clara y concisa. Si no estás seguro de algo, "
    "indícalo honestamente en lugar de inventar una respuesta. No des consejos legales "
    "profesionales —remite al usuario a un abogado especializado cuando corresponda."
)


class AskRequest(BaseModel):
    question: str
    context: Optional[str] = None


class AskResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AskResponse)
@limiter.limit("10/minute")
async def ask_ai(request: Request, req: AskRequest, current_user = Depends(get_current_user), db=Depends(get_db)):
    """
    Asistente IA sobre Ley 21.719 de Chile.
    Usa MiniMax M2.7 si hay MINIMAX_API_KEY, si no OpenAI si hay OPENAI_API_KEY.
    """
    import httpx

    api_key = settings.MINIMAX_API_KEY or settings.OPENAI_API_KEY
    if not api_key:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay clave API configurada. Establece MINIMAX_API_KEY u OPENAI_API_KEY en el backend."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if req.context:
        messages.append({"role": "user", "content": f"Contexto actual del sistema:\n{req.context}"})
    messages.append({"role": "user", "content": req.question})

    provider = "minimax" if settings.MINIMAX_API_KEY else "openai"

    if settings.MINIMAX_API_KEY:
        payload = {
            "model": settings.MINIMAX_MODEL or "MiniMax-M2.7",
            "messages": messages,
            "max_completion_tokens": 800,
            "temperature": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    "https://api.minimaxi.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            from fastapi import HTTPException as HTTPExc, status
            raise HTTPExc(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error al consultar MiniMax: {str(e)}")
    else:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.3,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            from fastapi import HTTPException as HTTPExc, status
            raise HTTPExc(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error al consultar OpenAI: {str(e)}")

    try:
        log_audit(
            db=db,
            entidad="ai",
            entidad_id=0,
            accion="consulta",
            usuario=current_user.username,
            detalle={"question": req.question[:500], "context": req.context[:500] if req.context else None, "provider": provider},
            ip_origen=get_client_ip(request),
        )
        db.commit()
    except Exception as audit_err:
        import logging
        logging.getLogger(__name__).warning(f"Audit log failed: {audit_err}")

    return {"answer": answer}
