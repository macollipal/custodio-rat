"""
Asesor Chunker: divide documentos en chunks de tokens.
Estrategia: 800 tokens con overlap 100, separadores jerárquicos.
"""
from __future__ import annotations
import re
from typing import List

from app.core.config import settings


def estimate_tokens(text: str) -> int:
    """Estimación rápida: ~4 chars por token."""
    return max(1, len(text) // 4)


def split_by_hierarchy(text: str) -> List[str]:
    """Divide por encabezados Markdown primero, luego por párrafos."""
    if not text.strip():
        return []

    parts: List[str] = []
    # 1) Separar por encabezados (##, ###)
    sections = re.split(r"(?m)^(#{1,6}\s+.*)$", text)
    buffer: List[str] = []
    for s in sections:
        if re.match(r"(?m)^#{1,6}\s+", s):
            if buffer:
                parts.append("\n".join(buffer).strip())
                buffer = []
            parts.append(s.strip())
        else:
            buffer.append(s)
    if buffer:
        parts.append("\n".join(buffer).strip())

    # 2) Si una sección es muy larga (> chunk_size * 6 chars), dividir por párrafos
    final_parts: List[str] = []
    char_limit = settings.ASESOR_CHUNK_SIZE * 6  # margen 6x tokens->chars
    for p in parts:
        if len(p) <= char_limit:
            final_parts.append(p)
        else:
            for para in re.split(r"\n\s*\n", p):
                if para.strip():
                    final_parts.append(para.strip())
    return [p for p in final_parts if p]


def chunk_text(text: str, title_hint: str = "") -> List[dict]:
    """
    Divide un texto en chunks.
    Retorna lista de {content, chunk_index, title, token_count}.
    """
    if not text or not text.strip():
        return []

    parts = split_by_hierarchy(text)
    chunk_size = settings.ASESOR_CHUNK_SIZE
    overlap = settings.ASESOR_CHUNK_OVERLAP

    chunks: List[dict] = []
    buf = ""
    buf_tokens = 0
    idx = 0

    for part in parts:
        part_tokens = estimate_tokens(part)
        if buf_tokens + part_tokens > chunk_size and buf:
            chunks.append({
                "content": buf.strip(),
                "chunk_index": idx,
                "title": title_hint,
                "token_count": buf_tokens,
            })
            idx += 1
            # Overlap: mantener las últimas ~overlap tokens
            if overlap > 0:
                words = buf.split()
                overlap_words = max(1, int(overlap * 4 / 5))
                buf = " ".join(words[-overlap_words:]) + "\n\n" + part
                buf_tokens = estimate_tokens(buf)
            else:
                buf = part
                buf_tokens = part_tokens
        else:
            buf = (buf + "\n\n" + part) if buf else part
            buf_tokens += part_tokens

    if buf.strip():
        chunks.append({
            "content": buf.strip(),
            "chunk_index": idx,
            "title": title_hint,
            "token_count": buf_tokens,
        })

    return chunks
