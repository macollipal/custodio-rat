"""
Asesor Embedder: genera embeddings via Cohere.
URL: https://api.cohere.com/v1/embed
Modelo: embed-english-v3.0 (dimension 1024, free tier)
"""
from __future__ import annotations
import logging
from typing import List, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

COHERE_URL = "https://api.cohere.com/v1/embed"
COHERE_MODEL = "embed-english-v3.0"


def _embed_cohere(texts: List[str], input_type: str) -> List[List[float]]:
    """Llama a Cohere embeddings y retorna vectores."""
    if not settings.COHERE_API_KEY:
        raise RuntimeError(
            "COHERE_API_KEY no configurada. "
            "Agrega COHERE_API_KEY en Vercel QA Environment Variables."
        )
    payload = {
        "model": COHERE_MODEL,
        "texts": texts,
        "input_type": input_type,
    }
    headers = {
        "Authorization": f"Bearer {settings.COHERE_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(COHERE_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if "embeddings" not in data:
        raise RuntimeError(
            f"Cohere embeddings formato inesperado. Keys: {list(data.keys())}. "
            f"Response (first 300): {str(data)[:300]}"
        )

    return data["embeddings"]


def embed_texts(texts: List[str], provider_hint: Optional[str] = None) -> tuple[List[List[float]], str]:
    """
    Genera embeddings de chunks para indexar en BD.
    input_type=search_document (para corpus).
    """
    if not texts:
        return [], provider_hint or "none"
    vectors = _embed_cohere(texts, input_type="search_document")
    return vectors, "cohere"


def embed_query(text: str) -> tuple[List[float], str]:
    """
    Genera embedding de una query para retrieval.
    input_type=search_query.
    """
    vectors = _embed_cohere([text], input_type="search_query")
    return vectors[0], "cohere"
