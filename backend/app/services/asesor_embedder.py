"""
Asesor Embedder: genera embeddings vía MiniMax (primario) con fallback automático a OpenAI.

Si MiniMax no expone endpoint de embeddings o falla, se cae transparentemente
a OpenAI (text-embedding-3-small, 1536 dim).
"""
from __future__ import annotations
import logging
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"


async def _embed_openai(texts: List[str]) -> List[List[float]]:
    """Llama a OpenAI embeddings API."""
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY no configurada")
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENAI_EMBEDDING_MODEL,
        "input": texts,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(OPENAI_EMBEDDINGS_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return [item["embedding"] for item in data["data"]]


async def _embed_minimax(texts: List[str]) -> Optional[List[List[float]]]:
    """Intenta embeddings vía MiniMax. Retorna None si no está disponible."""
    if not settings.MINIMAX_API_KEY:
        return None
    # Endpoint hipotético: muchos proveedores exponen /v1/embeddings compatible con OpenAI
    url = "https://api.minimaxi.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.MINIMAX_EMBEDDING_MODEL,
        "input": texts,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 404:
                logger.warning("MiniMax no expone /v1/embeddings. Fallback a OpenAI.")
                return None
            resp.raise_for_status()
            data = resp.json()
        return [item["embedding"] for item in data["data"]]
    except Exception as e:
        logger.warning(f"MiniMax embeddings falló: {e}. Fallback a OpenAI.")
        return None


async def embed_texts(texts: List[str], provider_hint: Optional[str] = None) -> tuple[List[List[float]], str]:
    """
    Genera embeddings con fallback automático.
    Retorna (embeddings, provider_usado).
    """
    if not texts:
        return [], provider_hint or "none"

    if provider_hint == "minimax" or (provider_hint is None and settings.MINIMAX_API_KEY):
        result = await _embed_minimax(texts)
        if result is not None:
            return result, "minimax"

    if settings.OPENAI_API_KEY:
        result = await _embed_openai(texts)
        return result, "openai"

    raise RuntimeError(
        "No hay proveedor de embeddings configurado. "
        "Define MINIMAX_API_KEY u OPENAI_API_KEY en backend/.env."
    )


async def embed_query(text: str) -> tuple[List[float], str]:
    """Genera embedding de una sola query."""
    embs, provider = await embed_texts([text])
    return embs[0], provider
