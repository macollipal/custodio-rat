"""
Tests para persistencia de conversaciones del Asesor IA (Arts. 19, 20 Ley 21.719).

Verifica que cada POST /asesor/ask persiste un registro en AsesorConversacion.
"""
import json
import pytest

from app.models.asesor import AsesorConversacion


def _mock_asesor_con_chunks():
    async def fake_ask(db, question, context_extra=""):
        return {
            "answer": "Respuesta mock con informacion valida.",
            "sources": [
                {
                    "source": "test_doc.pdf",
                    "source_type": "pdf",
                    "title": "Documento de prueba",
                    "chunk_index": 0,
                    "score": 0.85,
                    "snippet": "Contenido de prueba del documento.",
                },
            ],
            "provider": "mock",
            "embedding_provider": "fake",
            "latency_ms": 42,
        }

    async def fake_embed_query(text):
        return [0.1, 0.2, 0.3], "fake"

    return fake_ask, fake_embed_query


class TestAsesorConversacionesPersistencia:
    """Tests de integracion con mocks del LLM y embedder."""

    def test_ask_crea_asesor_conversacion(
        self, client, auth_headers, db, monkeypatch
    ):
        fake_ask, fake_embed = _mock_asesor_con_chunks()
        from app.services import asesor_service
        from app.services import asesor_embedder
        import app.routes.asesor

        monkeypatch.setattr(asesor_service, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_embedder, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_service, "ask", fake_ask)
        monkeypatch.setattr(app.routes.asesor, "ask", fake_ask)

        initial_count = db.query(AsesorConversacion).count()

        resp = client.post(
            "/asesor/ask",
            json={"question": "Que es un RAT?", "context": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Error: {resp.text}"
        data = resp.json()
        assert data["answer"] == "Respuesta mock con informacion valida."
        assert data["provider"] == "mock"

        final_count = db.query(AsesorConversacion).count()
        assert final_count == initial_count + 1, f"Esperaba {initial_count + 1} conversaciones"

        conv = db.query(AsesorConversacion).order_by(AsesorConversacion.id.desc()).first()
        assert conv.question == "Que es un RAT?"
        assert conv.answer == "Respuesta mock con informacion valida."
        assert conv.provider == "mock"
        assert conv.embedding_provider == "fake"
        assert conv.latency_ms == 42
        assert conv.sources_json is not None

        sources = json.loads(conv.sources_json)
        assert len(sources) == 1
        assert sources[0]["source"] == "test_doc.pdf"

    def test_ask_conversation_persiste_user_id(
        self, client, auth_headers, db, monkeypatch
    ):
        """La conversacion persistida tiene user_id. company_id puede ser None si el usuario es superadmin."""
        fake_ask, fake_embed = _mock_asesor_con_chunks()
        from app.services import asesor_service
        from app.services import asesor_embedder
        import app.routes.asesor

        monkeypatch.setattr(asesor_service, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_embedder, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_service, "ask", fake_ask)
        monkeypatch.setattr(app.routes.asesor, "ask", fake_ask)

        resp = client.post(
            "/asesor/ask",
            json={"question": "Pregunta trazabilidad"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

        conv = db.query(AsesorConversacion).order_by(AsesorConversacion.id.desc()).first()
        assert conv.user_id is not None
        assert conv.user_id > 0

    def test_multiples_consultas_persisten_cada_una(
        self, client, auth_headers, db, monkeypatch
    ):
        fake_ask, fake_embed = _mock_asesor_con_chunks()
        from app.services import asesor_service
        from app.services import asesor_embedder
        import app.routes.asesor

        monkeypatch.setattr(asesor_service, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_embedder, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_service, "ask", fake_ask)
        monkeypatch.setattr(app.routes.asesor, "ask", fake_ask)

        preguntas = [
            "Que es el Art. 14 bis?",
            "Cuando notificar una brecha?",
            "Que datos requieren EIPD?",
        ]
        for pregunta in preguntas:
            resp = client.post(
                "/asesor/ask",
                json={"question": pregunta, "context": ""},
                headers=auth_headers,
            )
            assert resp.status_code == 200

        conversations = db.query(AsesorConversacion).order_by(AsesorConversacion.id.asc()).all()
        assert len(conversations) >= 3
        questions_persistidas = [c.question for c in conversations[-3:]]
        assert questions_persistidas == preguntas

    def test_ask_sin_persistir_no_explota_si_falla_db(
        self, client, auth_headers, db, monkeypatch
    ):
        """Si la persistencia en BD falla, el endpoint debe responder 200 igualmente."""
        fake_ask, fake_embed = _mock_asesor_con_chunks()
        from app.services import asesor_service
        from app.services import asesor_embedder
        import app.routes.asesor
        from app.models import asesor as asesor_module

        monkeypatch.setattr(asesor_service, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_embedder, "embed_query", fake_embed)
        monkeypatch.setattr(asesor_service, "ask", fake_ask)
        monkeypatch.setattr(app.routes.asesor, "ask", fake_ask)

        original_add = asesor_module.AsesorConversacion.__init__
        call_count = {"n": 0}

        def failing_init(self, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("BD no disponible (test)")
            return original_add(self, *args, **kwargs)

        monkeypatch.setattr(asesor_module.AsesorConversacion, "__init__", failing_init)

        resp = client.post(
            "/asesor/ask",
            json={"question": "Test resiliencia", "context": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Endpoint debio responder 200 a pesar de error de BD"
