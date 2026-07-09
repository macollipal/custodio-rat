"""
Tests para los 5 campos nuevos del modelo ARCO/TKT (Iter 10 - Gaps Ley 21.719).
ValidaciÃ³n: metodo_verificacion_identidad, evidencia_identidad, evidencia_respuesta_hash,
causal_rechazo, medio_respuesta.

NOTA: Tests ejecutados contra PostgreSQL (Neon QA).
"""



def _crear_ticket_base(client, headers, empresa, extra_payload=None):
    payload = {
        "company_id": empresa["id"],
        "tipo": "acceso",
        "prioridad": "normal",
        "origen": "web",
        "titular_nombre": "Juan Test",
        "titular_email": "juan@test.cl",
        "descripcion": "Solicitud de acceso a datos personales",
    }
    if extra_payload:
        payload.update(extra_payload)
    resp = client.post("/tkt-solicitud-derecho/", json=payload, headers=headers)
    return resp


class TestARCOMetodoVerificacionIdentidad:
    """Tests para campo metodo_verificacion_identidad."""

    def test_crear_ticket_con_metodo_verificacion(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con metodo_verificacion_identidad vÃ¡lido."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "metodo_verificacion_identidad": "cedula"
        })
        assert resp.status_code == 200
        assert resp.json()["metodo_verificacion_identidad"] == "cedula"

    def test_crear_ticket_firma_digital(self, client, auth_headers, empresa):
        """Caso borde: Ticket con metodo_verificacion_identidad = firma_digital."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "metodo_verificacion_identidad": "firma_digital"
        })
        assert resp.status_code == 200
        assert resp.json()["metodo_verificacion_identidad"] == "firma_digital"

    def test_crear_ticket_sin_metodo_verificacion(self, client, auth_headers, empresa):
        """Caso negativo: Ticket sin metodo_verificacion_identidad (NULL)."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        assert resp.json().get("metodo_verificacion_identidad") is None


class TestARCOEvidenciaIdentidad:
    """Tests para campo evidencia_identidad."""

    def test_crear_ticket_con_evidencia_identidad(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con evidencia_identidad completa."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "evidencia_identidad": "CÃ©dula de identidad Chilean vigente, verificada vÃ­a video call"
        })
        assert resp.status_code == 200
        assert "CÃ©dula" in resp.json()["evidencia_identidad"]

    def test_crear_ticket_evidencia_identidad_larga(self, client, auth_headers, empresa):
        """Caso borde: evidencia_identidad con texto muy largo (>500 chars)."""
        evidencia_larga = "A" * 600
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "evidencia_identidad": evidencia_larga
        })
        assert resp.status_code == 200
        assert len(resp.json()["evidencia_identidad"]) == 600

    def test_crear_ticket_sin_evidencia_identidad(self, client, auth_headers, empresa):
        """Caso negativo: Ticket sin evidencia_identidad (NULL)."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        assert resp.json().get("evidencia_identidad") is None


class TestARCOEvidenciaRespuestaHash:
    """Tests para campo evidencia_respuesta_hash (SHA-256)."""

    def test_crear_ticket_con_hash_valido(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con evidencia_respuesta_hash SHA-256 vÃ¡lido."""
        hash_sha256 = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ab"
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "evidencia_respuesta_hash": hash_sha256
        })
        assert resp.status_code == 200
        assert resp.json()["evidencia_respuesta_hash"] == hash_sha256

    def test_crear_ticket_hash_64_chars(self, client, auth_headers, empresa):
        """Caso borde: hash exactamente 64 caracteres (SHA-256)."""
        hash_64 = "0000000000000000000000000000000000000000000000000000000000000000"
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "evidencia_respuesta_hash": hash_64
        })
        assert resp.status_code == 200
        assert len(resp.json()["evidencia_respuesta_hash"]) == 64

    def test_crear_ticket_sin_hash(self, client, auth_headers, empresa):
        """Caso negativo: Ticket sin evidencia_respuesta_hash (NULL)."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        assert resp.json().get("evidencia_respuesta_hash") is None


class TestARCOCausalRechazo:
    """Tests para campo causal_rechazo."""

    def test_crear_ticket_causal_falta_identidad(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con causal_rechazo = falta_identidad."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "causal_rechazo": "falta_identidad"
        })
        assert resp.status_code == 200
        assert resp.json()["causal_rechazo"] == "falta_identidad"

    def test_crear_ticket_causal_manifiestamente_infundada(self, client, auth_headers, empresa):
        """Caso borde: causal_rechazo = solicitud_manifiestamente_infundada."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "causal_rechazo": "solicitud_manifiestamente_infundada"
        })
        assert resp.status_code == 200
        assert resp.json()["causal_rechazo"] == "solicitud_manifiestamente_infundada"

    def test_crear_ticket_sin_causal_rechazo(self, client, auth_headers, empresa):
        """Caso negativo: Ticket sin causal_rechazo (NULL)."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        assert resp.json().get("causal_rechazo") is None


class TestARCOMedioRespuesta:
    """Tests para campo medio_respuesta."""

    def test_crear_ticket_medio_email(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con medio_respuesta = email."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "medio_respuesta": "email"
        })
        assert resp.status_code == 200
        assert resp.json()["medio_respuesta"] == "email"

    def test_crear_ticket_medio_domicilio(self, client, auth_headers, empresa):
        """Caso borde: medio_respuesta = domicilio."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "medio_respuesta": "domicilio"
        })
        assert resp.status_code == 200
        assert resp.json()["medio_respuesta"] == "domicilio"

    def test_crear_ticket_sin_medio_respuesta(self, client, auth_headers, empresa):
        """Caso negativo: Ticket sin medio_respuesta (NULL)."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        assert resp.json().get("medio_respuesta") is None


class TestARCOTodosLosCamposJuntos:
    """Tests combinando los 5 campos nuevos."""

    def test_crear_ticket_todos_los_campos(self, client, auth_headers, empresa):
        """Caso afirmativo: Ticket con los 5 campos nuevos."""
        resp = _crear_ticket_base(client, auth_headers, empresa, {
            "metodo_verificacion_identidad": "cedula",
            "evidencia_identidad": "CÃ©dula verificada presencialmente",
            "evidencia_respuesta_hash": "abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
            "causal_rechazo": None,
            "medio_respuesta": "email",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["metodo_verificacion_identidad"] == "cedula"
        assert data["evidencia_identidad"] == "CÃ©dula verificada presencialmente"
        assert data["evidencia_respuesta_hash"] == "abc123def456abc123def456abc123def456abc123def456abc123def456abc1"
        assert data["causal_rechazo"] is None
        assert data["medio_respuesta"] == "email"

    def test_actualizar_ticket_nuevos_campos(self, client, auth_headers, empresa):
        """Caso negativo: Actualizar ticket agregando campos nuevos."""
        resp = _crear_ticket_base(client, auth_headers, empresa)
        assert resp.status_code == 200
        ticket_id = resp.json()["id"]

        update_resp = client.patch(
            f"/tkt-solicitud-derecho/{ticket_id}",
            json={
                "evidencia_respuesta_hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "causal_rechazo": "excesiva",
            },
            headers=auth_headers
        )
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["evidencia_respuesta_hash"] == "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        assert data["causal_rechazo"] == "excesiva"
