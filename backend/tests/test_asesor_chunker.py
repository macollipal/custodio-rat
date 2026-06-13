"""
Tests unitarios del Asesor Chunker.
"""
import pytest

from app.services.asesor_chunker import chunk_text, estimate_tokens, split_by_hierarchy


def test_estimate_tokens_minimo():
    assert estimate_tokens("") == 1
    assert estimate_tokens("a") == 1
    assert estimate_tokens("a" * 400) == 100
    assert estimate_tokens("a" * 1000) == 250


def test_split_by_hierarchy_basico():
    text = "# Título\n\nPárrafo 1.\n\n## Subtítulo\n\nPárrafo 2."
    parts = split_by_hierarchy(text)
    assert len(parts) >= 2
    assert any("Subtítulo" in p for p in parts)


def test_split_by_hierarchy_vacio():
    assert split_by_hierarchy("") == []
    assert split_by_hierarchy("   \n\n  ") == []


def test_chunk_text_vacio():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_basico():
    text = "Este es un texto corto de prueba para el Asesor."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0]["content"] == text
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["token_count"] > 0


def test_chunk_text_con_titulo():
    chunks = chunk_text("Contenido de prueba", title_hint="Documento X")
    assert chunks[0]["title"] == "Documento X"


def test_chunk_text_multiple():
    text = "\n\n".join([f"Párrafo {i} con suficiente contenido para alcanzar tokens." for i in range(20)])
    chunks = chunk_text(text)
    assert len(chunks) >= 1
    for c in chunks:
        assert "content" in c
        assert "chunk_index" in c
        assert c["token_count"] > 0
