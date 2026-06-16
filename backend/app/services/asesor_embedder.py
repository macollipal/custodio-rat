"""
Asesor Embedder: genera embeddings via MiniMax.
Unico provider: MiniMax (API key en MINIMAX_API_KEY).
"""
from __future__ import annotations
import logging
from typing import List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

MINIMAX_EMBEDDINGS_URL = "https://api.minimaxi.com/v1/embeddings"


async def embed_texts(texts: List[str], provider_hint: Optional[str] = None) -> tuple[List[List[float]], str]:
    """
    Genera embeddings via MiniMax.
    Retorna (embeddings, provider_usado).
    Solo MiniMax — sin fallback OpenAI.
    """
    if not texts:
        return [], provider_hint or "none"

    if not settings.MINIMAX_API_KEY:
        raise RuntimeError(
            "MINIMAX_API_KEY no configurada. "
            "Configura la API key de MiniMax en backend/.env para usar el Asesor."
        )

    cfg = settings.asesor_config()
    headers = {
        "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg["embedding_model"],
        "input": texts,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(MINIMAX_EMBEDDINGS_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return [item["embedding"] for item in data["data"]], "minimax"


async def embed_query(text: str) -> tuple[List[float], str]:
    """Genera embedding de una sola query."""
    embs, provider = await embed_texts([text])
    return embs[0], provider
