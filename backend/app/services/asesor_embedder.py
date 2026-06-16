"""
Asesor Embedder: genera embeddings via MiniMax.
Usa api.minimax.io con Subscription Key (sk-cp-).
Body: {"model": "embo-01", "texts": [...], "type": "db"|"query"}
Respuesta: {"vectors": [[...], ...], "base_resp": {...}}
"""
from __future__ import annotations
import logging
import time
from typing import List, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

MINIMAX_EMBEDDINGS_URL = "https://api.minimax.io/v1/embeddings"

MINIMAX_RATELIMIT_CODES = {1002, 1003}


def _embed(texts: List[str], emb_type: str) -> List[List[float]]:
    """Helper que llama a MiniMax embeddings con retry en rate limit."""
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
        "texts": texts,
        "type": emb_type,
    }

    max_retries = 3
    for attempt in range(max_retries):
        resp = requests.post(MINIMAX_EMBEDDINGS_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        base_resp = data.get("base_resp", {})
        code = base_resp.get("status_code", 0)

        if code == 0:
            vectors = data.get("vectors")
            if isinstance(vectors, list):
                return vectors
            raise RuntimeError(
                f"MiniMax embeddings formato inesperado. vectors no es lista: {type(vectors)}. "
                f"Keys: {list(data.keys())}. Response (first 300): {str(data)[:300]}"
            )

        if code in MINIMAX_RATELIMIT_CODES and attempt < max_retries - 1:
            wait = 2 ** attempt
            logger.warning(
                f"MiniMax embeddings rate limited (attempt {attempt+1}/{max_retries}). "
                f"Waiting {wait}s before retry."
            )
            time.sleep(wait)
            continue

        raise RuntimeError(
            f"MiniMax embeddings error. status_code={code} "
            f"status_msg={base_resp.get('status_msg')} url={MINIMAX_EMBEDDINGS_URL}"
        )

    raise RuntimeError("Max retries exceeded for MiniMax embeddings")


def embed_texts(texts: List[str], provider_hint: Optional[str] = None) -> tuple[List[List[float]], str]:
    """
    Genera embeddings de chunks para indexar en BD.
    Usa type="db" (para indexing).
    Retorna (embeddings, provider_usado).
    """
    if not texts:
        return [], provider_hint or "none"
    vectors = _embed(texts, emb_type="db")
    return vectors, "minimax"


def embed_query(text: str) -> tuple[List[float], str]:
    """
    Genera embedding de una query para retrieval.
    Usa type="query".
    Retorna (embedding_vector, provider_usado).
    """
    vectors = _embed([text], emb_type="query")
    return vectors[0], "minimax"
