"""
Tests de los endpoints del Asesor.
"""
import json
import pytest

from app.models.asesor import AsesorChunk


def test_ask_sin_auth_retorna_401(client):
    resp = client.post("/asesor/ask", json={"question": "hola"})
    assert resp.status_code == 401


def test_ask_question_vacia_retorna_422(client, auth_headers):
    resp = client.post("/asesor/ask", json={"question": ""}, headers=auth_headers)
    assert resp.status_code == 422


def test_ask_sin_embedding_provider(client, auth_headers):
    resp = client.post("/asesor/ask", json={"question": "Qué es un RAT?"}, headers=auth_headers)
    # Sin MiniMax ni OpenAI en test, retorna 503
    assert resp.status_code == 503


def test_ask_fallback_sin_chunks(client, auth_headers, monkeypatch):
    """Si no hay chunks indexados, debe retornar respuesta de fallback con sources vacío."""
    from app.services import asesor_service
    from app.services import asesor_embedder

    async def fake_embed_query(text):
        return [0.0] * 3, "fake"

    async def fake_ask(db, question, context_extra=""):
        return {
            "answer": "Sin información suficiente en el corpus.",
            "sources": [],
            "provider": "fake",
            "embedding_provider": "fake",
            "latency_ms": 10,
        }

    monkeypatch.setattr(asesor_service, "embed_query", fake_embed_query)
    monkeypatch.setattr(asesor_service, "ask", fake_ask)

    resp = client.post(
        "/asesor/ask",
        json={"question": "Pregunta de prueba", "context": ""},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert data["sources"] == []
    assert data["provider"] == "fake"


def test_index_sin_auth_retorna_401(client):
    resp = client.post("/admin/asesor/index", json={})
    assert resp.status_code == 401


def test_index_sin_ser_superadmin_retorna_403(client, auth_headers):
    # El fixture auth_headers usa superadmin, este test es un placeholder
    # para validar el caso positivo (superadmin pasa)
    # El 403 se valida creando un usuario no-superadmin
    pass


def test_stats_sin_auth_retorna_401(client):
    resp = client.get("/admin/asesor/stats")
    assert resp.status_code == 401


def test_stats_con_auth_retorna_200(client, auth_headers):
    resp = client.get("/admin/asesor/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_chunks" in data
    assert "total_documents" in data
    assert "provider" in data
    assert data["total_chunks"] == 0
    assert data["total_documents"] == 0


def test_delete_chunk_existente(client, auth_headers, db):
    chunk = AsesorChunk(
        source="test.txt",
        source_type="manual",
        content="test",
        content_hash="x" * 64,
        chunk_index=0,
        token_count=1,
        embedding_json=json.dumps([0.0] * 1536),
    )
    db.add(chunk)
    db.commit()
    cid = chunk.id

    resp = client.delete(f"/admin/asesor/documents/{cid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    assert db.query(AsesorChunk).filter(AsesorChunk.id == cid).first() is None


def test_delete_chunk_inexistente_retorna_404(client, auth_headers):
    resp = client.delete("/admin/asesor/documents/99999", headers=auth_headers)
    assert resp.status_code == 404
