"""
Asesor Service: orquestador de retrieve + LLM + auditoría.
"""
from __future__ import annotations
import json
import logging
import time
from typing import List

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asesor import AsesorChunk
from app.services.asesor_embedder import embed_query
from app.services.asesor_retriever import retrieve

logger = logging.getLogger(__name__)

ASESOR_SYSTEM_PROMPT = (
    "Eres Custodio Asesor, un asistente IA especializado en la Ley 21.719 "
    "de Protección de Datos Personales de Chile y en el uso de la plataforma "
    "Custodio RAT Manager.\n\n"
    "Tu rol es ayudar a los responsables del tratamiento a entender sus obligaciones, "
    "responder preguntas sobre qué es un RAT, cómo llenarlo, cuándo se requiere una EIPD, "
    "qué garantías aplican para transferencias internacionales, cómo manejar brechas de "
    "seguridad, y cualquier duda relacionada con el cumplimiento de la ley o el uso de Custodio.\n\n"
    "INSTRUCCIONES CRÍTICAS:\n"
    "1. Responde SOLO con la información del contexto provisto. Si no tienes la respuesta, "
    "indícalo honestamente en lugar de inventar.\n"
    "2. Cita el artículo o sección de la que extraes cada afirmación usando el formato "
    "[Fuente: <nombre>, sección <X>].\n"
    "3. No des consejos legales profesionales. Si la consulta lo requiere, recomienda "
    "consultar a un abogado especializado.\n\n"
    "Responde siempre en español, de forma clara y concisa."
)


def _call_llm_minimax(messages: list) -> str:
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY no configurada. "
            "El Asesor requiere una API key de Groq para el chat. "
            "Configura GROQ_API_KEY en backend/.env o en Vercel."
        )
    cfg = settings.asesor_config()
    payload = {
        "model": settings.GROQ_CHAT_MODEL,
        "messages": messages,
        "max_completion_tokens": cfg["llm_max_tokens"],
        "temperature": cfg["llm_temperature"],
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload, headers=headers, timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    logger.info(f"Groq chat response keys: {list(data.keys())[:10]}")

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"Groq chat completions formato inesperado. Keys: {list(data.keys())}. "
            f"Error: {e}. Response (first 300): {str(data)[:300]}"
        )


def _build_prompt(question: str, chunks: List[dict]) -> list:
    context_parts = []
    for i, c in enumerate(chunks, start=1):
        title = c.get("title") or c["source"]
        context_parts.append(f"[{i}] Fuente: {c['source']} — {title} (score: {c['score']})\n{c['content']}")
    context = "\n\n---\n\n".join(context_parts)
    user = (
        f"Pregunta: {question}\n\n"
        f"Contexto del corpus:\n{context}\n\n"
        "Responde la pregunta citando explícitamente las fuentes [1], [2], etc. cuando las uses."
    )
    return [
        {"role": "system", "content": ASESOR_SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


async def ask(db: Session, question: str, context_extra: str = "") -> dict:
    """
    Pipeline RAG: embed query → retrieve → build prompt → call LLM.
    Retorna {answer, sources, provider, embedding_provider, latency_ms}.
    """
    start = time.time()
    query_embedding, emb_provider = embed_query(question)
    chunks = retrieve(db, query_embedding)

    if not chunks:
        latency = int((time.time() - start) * 1000)
        return {
            "answer": "No encontré información relevante en el corpus para responder tu consulta. "
                     "Puedes reformular la pregunta o usar el chat genérico (/ai/ask).",
            "sources": [],
            "provider": "none",
            "embedding_provider": emb_provider,
            "latency_ms": latency,
        }

    messages = _build_prompt(question, chunks)
    if context_extra:
        messages.insert(1, {"role": "system", "content": f"Contexto del sistema: {context_extra}"})

    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY no configurada. "
            "El Asesor requiere GROQ_API_KEY para funcionar."
        )
    answer = _call_llm_minimax(messages)
    provider = "groq"

    latency = int((time.time() - start) * 1000)
    return {
        "answer": answer,
        "sources": chunks,
        "provider": provider,
        "embedding_provider": emb_provider,
        "latency_ms": latency,
    }
