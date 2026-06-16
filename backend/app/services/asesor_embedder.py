"""
Asesor Embedder: genera embeddings via MiniMax.
Unico provider: MiniMax (API key en MINIMAX_API_KEY).
"""
from __future__ import annotations
import logging
from typing import List, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

MINIMAX_EMBEDDINGS_URL = "https://api.minimaxi.com/v1/embeddings"


def embed_texts(texts: List[str], provider_hint: Optional[str] = None) -> tuple[List[List[float]], str]:
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
    resp = requests.post(MINIMAX_EMBEDDINGS_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    logger.info(f"MiniMax embeddings response keys: {list(data.keys())[:10]}")
    if len(str(data)) > 200:
        logger.debug(f"MiniMax embeddings full response (truncated): {str(data)[:500]}")

    if "data" in data and isinstance(data["data"], list):
        return [item["embedding"] for item in data["data"]], "minimax"

    if "embedding" in data:
        return [data["embedding"]], "minimax"

    raise RuntimeError(
        f"MiniMax embeddings formato inesperado. Keys: {list(data.keys())}. "
        f"Response (first 300 chars): {str(data)[:300]}"
    )


def embed_query(text: str) -> tuple[List[float], str]:
    """Genera embedding de una sola query."""
    embs, provider = embed_texts([text])
    return embs[0], provider
