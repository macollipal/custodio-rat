"""
Asesor Retriever: búsqueda por cosine similarity sobre chunks del corpus.

v1.0 implementación en Python puro (cosine top-k) compatible con SQLite y
PostgreSQL. En v1.1 migra a pgvector con SQL nativo.
"""
from __future__ import annotations
import json
import math
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asesor import AsesorChunk


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(
    db: Session,
    query_embedding: List[float],
    top_k: int = None,
    min_similarity: float = None,
) -> List[dict]:
    """
    Retorna los top-k chunks más similares a la query.
    Cada item: {content, source, source_type, title, chunk_index, score, snippet, chunk_id}
    """
    if top_k is None:
        top_k = settings.ASESOR_TOP_K
    if min_similarity is None:
        min_similarity = settings.ASESOR_MIN_SIMILARITY

    chunks = db.query(AsesorChunk).all()
    if not chunks:
        return []

    scored: List[Tuple[float, AsesorChunk]] = []
    for c in chunks:
        if not c.embedding_json:
            continue
        try:
            emb = json.loads(c.embedding_json)
        except (ValueError, TypeError):
            continue
        score = _cosine(query_embedding, emb)
        if score >= min_similarity:
            scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    scored = scored[:top_k]

    results: List[dict] = []
    for score, c in scored:
        snippet = (c.content or "")[:200]
        results.append({
            "content": c.content,
            "source": c.source,
            "source_type": c.source_type,
            "title": c.title,
            "chunk_index": c.chunk_index,
            "score": round(score, 4),
            "snippet": snippet,
            "chunk_id": c.id,
        })
    return results
