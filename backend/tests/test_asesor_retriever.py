"""
Tests del retriever del Asesor.
"""
import json
import pytest

from app.models.asesor import AsesorChunk
from app.services.asesor_retriever import _cosine, retrieve


def test_cosine_identicos():
    assert _cosine([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)


def test_cosine_ortogonales():
    assert _cosine([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)


def test_cosine_opuestos():
    assert _cosine([1, 0, 0], [-1, 0, 0]) == pytest.approx(-1.0)


def test_cosine_dimensiones_distintas():
    assert _cosine([1, 0, 0], [1, 0]) == 0.0


def test_cosine_vacio():
    assert _cosine([], [1, 0]) == 0.0
    assert _cosine([0, 0], [0, 0]) == 0.0


def test_retrieve_sin_chunks(db):
    result = retrieve(db, [0.1] * 1536)
    assert result == []


def test_retrieve_con_chunks(db):
    db.add(AsesorChunk(
        source="doc0.txt", source_type="manual", title="A",
        content="A", content_hash="a" * 64, chunk_index=0, token_count=5,
        embedding_json=json.dumps([1.0, 0.0, 0.0]),
    ))
    db.add(AsesorChunk(
        source="doc1.txt", source_type="manual", title="B",
        content="B", content_hash="b" * 64, chunk_index=0, token_count=5,
        embedding_json=json.dumps([0.7, 0.7, 0.0]),
    ))
    db.add(AsesorChunk(
        source="doc2.txt", source_type="manual", title="C",
        content="C", content_hash="c" * 64, chunk_index=0, token_count=5,
        embedding_json=json.dumps([0.0, 1.0, 0.0]),
    ))
    db.commit()
    result = retrieve(db, [1.0, 0.0, 0.0], top_k=2, min_similarity=0.5)
    assert len(result) == 2
    assert result[0]["score"] >= result[1]["score"]
    assert result[0]["source"] == "doc0.txt"


def test_retrieve_filtra_por_min_similarity(db):
    for i in range(2):
        db.add(AsesorChunk(
            source=f"doc{i}.txt",
            source_type="manual",
            content=f"C{i}",
            content_hash=f"h{i}" + "0" * 62,
            chunk_index=0,
            token_count=5,
            embedding_json=json.dumps([1.0, 0.0, 0.0]),
        ))
    db.commit()
    result = retrieve(db, [1.0, 0.0, 0.0], top_k=5, min_similarity=0.99)
    assert len(result) == 1
    assert result[0]["score"] >= 0.99
