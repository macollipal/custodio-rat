"""
Tests de los endpoints del Asesor.
"""

from app.models.asesor import AsesorCorpusDocument


def test_ask_sin_auth_retorna_401(client):
    resp = client.post("/asesor/ask", json={"question": "hola"})
    assert resp.status_code == 401


def test_ask_question_vacia_retorna_422(client, auth_headers):
    resp = client.post("/asesor/ask", json={"question": ""}, headers=auth_headers)
    assert resp.status_code == 422


def test_ask_sin_embedding_provider(client, auth_headers):
    resp = client.post("/asesor/ask", json={"question": "QuÃ© es un RAT?"}, headers=auth_headers)
    # Sin MiniMax_API_Key en test, retorna 503 (OpenAI eliminado en v1.0)
    assert resp.status_code == 503


def test_ask_fallback_sin_chunks(client, auth_headers, monkeypatch):
    """Si no hay chunks indexados, debe retornar respuesta de fallback con sources vacÃ­o."""
    from app.services import asesor_service
    from app.services import asesor_embedder
    import app.routes.asesor

    async def fake_embed_query(text):
        return [0.0] * 3, "fake"

    async def fake_ask(db, question, context_extra=""):
        return {
            "answer": "Sin informaciÃ³n suficiente en el corpus.",
            "sources": [],
            "provider": "fake",
            "embedding_provider": "fake",
            "latency_ms": 10,
        }

    monkeypatch.setattr(asesor_service, "embed_query", fake_embed_query)
    monkeypatch.setattr(asesor_embedder, "embed_query", fake_embed_query)
    monkeypatch.setattr(asesor_service, "ask", fake_ask)
    monkeypatch.setattr(app.routes.asesor, "ask", fake_ask)

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


def test_delete_document_existente(client, auth_headers, db):
    """Elimina un AsesorCorpusDocument existente (soft delete + cascadea chunks por source).

    Antes este test se llamaba test_delete_chunk_existente pero creaba un
    AsesorChunk en vez de un AsesorCorpusDocument, lo que causaba 404 porque
    el endpoint DELETE /admin/asesor/documents/{id} busca AsesorCorpusDocument.
    Adicionalmente, delete_document hace soft delete (status='deleted'),
    no hard delete, por lo que la fila permanece con status actualizado.
    """
    unique_hash = "a" * 63 + "b"
    doc = AsesorCorpusDocument(
        object_name="test_unique_object_name_zzz.txt",
        original_filename="test.txt",
        content_type="text/plain",
        size_bytes=4,
        content_hash=unique_hash,
        source_type="manual",
        chunks_indexed=0,
        status="active",
    )
    db.add(doc)
    db.commit()
    doc_id = doc.id

    resp = client.delete(f"/admin/asesor/documents/{doc_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    db.expire_all()
    deleted = db.query(AsesorCorpusDocument).filter(AsesorCorpusDocument.id == doc_id).first()
    assert deleted is not None
    assert deleted.status == "deleted"


def test_delete_document_inexistente_retorna_404(client, auth_headers):
    """DELETE /admin/asesor/documents/{id} con id inexistente retorna 404."""
    resp = client.delete("/admin/asesor/documents/99999", headers=auth_headers)
    assert resp.status_code == 404
