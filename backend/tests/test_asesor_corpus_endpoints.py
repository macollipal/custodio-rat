"""
Tests para los endpoints de gestiÃ³n de corpus del Asesor:
GET  /admin/asesor/documents
POST /admin/asesor/upload
GET  /admin/asesor/documents/{id}/download
DELETE /admin/asesor/documents/{id}
"""
import hashlib
import io
import pytest
from unittest.mock import patch, MagicMock

from app.models.asesor import AsesorCorpusDocument


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


DOC_CONTENT = b"# Test\nContenido del archivo."
DOC_HASH = sha256(DOC_CONTENT)


class TestListDocuments:
    def test_sin_auth_retorna_401(self, client):
        resp = client.get("/admin/asesor/documents")
        assert resp.status_code == 401

    def test_lista_vacia_retorna_lista_vacia(self, client, auth_headers):
        resp = client.get("/admin/asesor/documents", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["documents"] == []
        assert data["total"] == 0

    def test_lista_con_documentos(self, client, auth_headers, db):
        doc = AsesorCorpusDocument(
            object_name="asesor_corpus/test_abc123.md",
            original_filename="test.md",
            content_type="text/markdown",
            size_bytes=1024,
            content_hash="a" * 64,
            title="Test",
            source_type="manual",
            chunks_indexed=2,
            status="active",
        )
        db.add(doc)
        db.commit()

        resp = client.get("/admin/asesor/documents", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["documents"][0]["original_filename"] == "test.md"
        assert data["documents"][0]["chunks_indexed"] == 2


class TestUploadDocument:
    def test_upload_sin_auth_retorna_401(self, client):
        resp = client.post("/admin/asesor/upload")
        assert resp.status_code == 401

    def test_upload_extension_invalida_retorna_422(self, client, auth_headers):
        file_content = b"test content"
        resp = client.post(
            "/admin/asesor/upload",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_upload_excede_tamano_retorna_422(self, client, auth_headers):
        content = b"x" * (6 * 1024 * 1024)
        resp = client.post(
            "/admin/asesor/upload",
            files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_upload_existente_duplicado_retorna_422(
        self, client, auth_headers, db
    ):
        doc = AsesorCorpusDocument(
            object_name="asesor_corpus/existing_abc.md",
            original_filename="test.md",
            content_type="text/markdown",
            size_bytes=100,
            content_hash=DOC_HASH,
            title="Existing",
            source_type="manual",
            chunks_indexed=1,
            status="active",
        )
        db.add(doc)
        db.commit()

        with patch("app.services.asesor_corpus_store.get_storage") as mock_get_storage, \
             patch("app.services.asesor_corpus_store.embed_texts") as mock_embed:
            mock_storage = MagicMock()
            mock_storage.upload.return_value = "asesor_corpus/test.md"
            mock_get_storage.return_value = mock_storage
            mock_embed.return_value = ([0.0] * 3, "Cohere-mock")

            resp = client.post(
                "/admin/asesor/upload",
                files={"file": ("test.md", io.BytesIO(DOC_CONTENT), "text/markdown")},
                headers=auth_headers,
            )
        assert resp.status_code == 422

    def test_upload_exitoso_retorna_200(
        self, client, auth_headers, db
    ):
        with patch("app.services.asesor_corpus_store.get_storage") as mock_get_storage, \
             patch("app.services.asesor_corpus_store.embed_texts") as mock_embed:
            mock_storage = MagicMock()
            mock_storage.upload.return_value = "asesor_corpus/manual_test.md"
            mock_get_storage.return_value = mock_storage
            mock_embed.return_value = ([0.0] * 3, "Cohere-mock")

            resp = client.post(
                "/admin/asesor/upload",
                files={"file": ("manual_test.md", io.BytesIO(DOC_CONTENT), "text/markdown")},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "doc_id" in data
        assert data["original_filename"] == "manual_test.md"
        assert data["source_type"] == "manual"


class TestDownloadDocument:
    def test_sin_auth_retorna_401(self, client):
        resp = client.get("/admin/asesor/documents/1/download")
        assert resp.status_code == 401

    def test_documento_inexistente_retorna_404(self, client, auth_headers):
        resp = client.get("/admin/asesor/documents/99999/download", headers=auth_headers)
        assert resp.status_code == 404

    def test_download_url_exitoso(self, client, auth_headers, db):
        doc = AsesorCorpusDocument(
            object_name="asesor_corpus/test_xyz.md",
            original_filename="test.md",
            content_type="text/markdown",
            size_bytes=512,
            content_hash="c" * 64,
            title="Test Download",
            source_type="manual",
            chunks_indexed=1,
            status="active",
        )
        db.add(doc)
        db.commit()

        with patch("app.routes.admin_asesor.get_asesor_corpus_store") as mock_store_fn:
            mock_store = MagicMock()
            mock_store.get_download_url.return_value = "https://mock.example.com/test_xyz.md"
            mock_store_fn.return_value = mock_store

            resp = client.get(f"/admin/asesor/documents/{doc.id}/download", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert "download_url" in data


class TestDeleteDocument:
    def test_sin_auth_retorna_401(self, client):
        resp = client.delete("/admin/asesor/documents/1")
        assert resp.status_code == 401

    def test_documento_inexistente_retorna_404(self, client, auth_headers):
        resp = client.delete("/admin/asesor/documents/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_exitoso_soft_delete(self, client, auth_headers, db):
        doc = AsesorCorpusDocument(
            object_name="asesor_corpus/del_xyz.md",
            original_filename="delete_me.md",
            content_type="text/markdown",
            size_bytes=256,
            content_hash="d" * 64,
            title="Delete Me",
            source_type="manual",
            chunks_indexed=1,
            status="active",
        )
        db.add(doc)
        db.commit()

        with patch("app.routes.admin_asesor.get_asesor_corpus_store") as mock_store_fn:
            mock_store = MagicMock()
            mock_store.delete_document.return_value = doc
            mock_store_fn.return_value = mock_store

            resp = client.delete(f"/admin/asesor/documents/{doc.id}", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["original_filename"] == "delete_me.md"
