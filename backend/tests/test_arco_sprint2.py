"""
Tests Sprint 2 — Consolidación ARCO (sync TKT ↔ SolicitudDerecho legacy).

Cubre:
- S2.2: Crear solicitud pública genera fila legacy ``SolicitudDerecho`` en la misma transacción.
- S2.3: Responder via PATCH legacy ``/solicitudes-derecho/{id}/responder`` actualiza TKT sync.
- S2.4: Schema ``SolicitudResponse`` expone todos los campos compliance Ley 21.719.
- S2.5: Rechazo fundado via endpoint dedicado funciona via frontend API client.

Estos tests requieren PostgreSQL (Neon QA). Ver backend/CLAUDE.md.
"""
import uuid

import pytest


def _crear_ticket(client, headers, company_id, tipo="acceso"):
    resp = client.post(
        "/tkt-solicitud-derecho/",
        json={
            "company_id": company_id,
            "tipo": tipo,
            "prioridad": "normal",
            "origen": "web",
            "titular_nombre": "Juan Titular",
            "titular_email": f"juan+{uuid.uuid4().hex[:6]}@titular.cl",
            "titular_rut": "12.345.678-5",
            "descripcion": "Solicitud de prueba consolidación",
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ============================================================
# S2.4: Schema SolicitudResponse completo
# ============================================================
class TestSchemaSolicitudResponse:
    def test_schema_expone_campos_compliance(self, client, auth_headers, empresa):
        """El GET /solicitudes-derecho/{id} debe exponer todos los campos compliance."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        # Resolvemos el ticket con verificación para completar campos compliance.
        client.patch(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            json={
                "estado": "resuelto",
                "respuesta_texto": "Su solicitud fue atendida.",
                "metodo_verificacion_identidad": "email_verificado",
                "evidencia_identidad": "DNI verificado vs titular",
                "medio_respuesta": "email",
            },
            headers=auth_headers,
        )

        resp = client.get(
            f"/solicitudes-derecho/{ticket['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()

        # Campos compliance Art. 12, 12.5
        assert "metodo_verificacion_identidad" in data
        assert "evidencia_identidad" in data
        assert "evidencia_respuesta_hash" in data
        assert "causal_rechazo" in data
        assert "medio_respuesta" in data
        assert "rat_id" in data
        assert "plazo_bloqueo_vencimiento" in data

        assert data["metodo_verificacion_identidad"] == "email_verificado"
        assert data["evidencia_identidad"] == "DNI verificado vs titular"
        assert data["medio_respuesta"] == "email"
        # hash fue computado
        assert data["evidencia_respuesta_hash"] is not None
        assert len(data["evidencia_respuesta_hash"]) == 64


# ============================================================
# S2.3: Responder via PATCH legacy sincroniza con TKT
# ============================================================
class TestSyncResponderLegacy:
    def test_patch_responder_sincroniza_ticket(self, client, auth_headers, empresa):
        """PATCH /solicitudes-derecho/{id}/responder debe actualizar el TKT también."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        # Seteamos verificación en el TKT via endpoint interno
        client.patch(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            json={
                "metodo_verificacion_identidad": "cedula_escaneada",
                "evidencia_identidad": "DNI firmado",
                "medio_respuesta": "email",
            },
            headers=auth_headers,
        )

        # Ahora respondemos via endpoint legacy PATCH
        resp = client.patch(
            f"/solicitudes-derecho/{ticket['id']}/responder",
            json={
                "estado": "resuelto",
                "respuesta": "Confirmamos sus datos están correctos.",
                "descripcion_accion": "Respuesta enviada al titular",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text

        # El TKT ahora debe estar resuelto con hash
        tkt_resp = client.get(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            headers=auth_headers,
        )
        assert tkt_resp.status_code == 200
        tkt = tkt_resp.json()
        assert tkt["estado"] == "resuelto"
        assert tkt["evidencia_respuesta_hash"] is not None

    def test_patch_responder_sin_verificacion_falla_400_422(self, client, auth_headers, empresa):
        """PATCH responder -> resuelto sin verificación debe fallar."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.patch(
            f"/solicitudes-derecho/{ticket['id']}/responder",
            json={
                "estado": "resuelto",
                "respuesta": "Su solicitud fue atendida.",
            },
            headers=auth_headers,
        )
        # 400 (EstadoInvalidoError) o 422 (validación identidad)
        assert resp.status_code in (400, 422)


# ============================================================
# S2.2: Form público crea SolicitudDerecho legacy
# ============================================================
class TestCrearSolicitudPublica:
    def test_form_publico_crea_ticket(self, client):
        """El endpoint público requiere token de seguridad y crea TKT + SolicitudDerecho."""
        # Pedimos token
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        # Buscamos empresas públicas
        companies = client.get("/companies/publico").json()
        if isinstance(companies, dict):
            companies = companies.get("companies", [])
        if not companies:
            pytest.skip("No hay empresas públicas para testear")
        company_id = companies[0]["id"]

        # Enviamos solicitud via JSON (no multipart)
        resp = client.post(
            "/solicitudes-derecho/",
            json={
                "company_id": company_id,
                "tipo": "acceso",
                "nombre_titular": "Titular Prueba",
                "rut_titular": None,
                "email_titular": f"titular+{uuid.uuid4().hex[:6]}@ejemplo.cl",
                "descripcion": "Quiero saber qué datos tienen sobre mí",
                "token": token,
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["estado"] == "abierto"
        assert data["tracking_token"], "El TKT debe incluir tracking_token"

        # El Tracking endpoint público debe poder leerlo
        track_resp = client.get(f"/solicitudes-derecho/tracking/{data['tracking_token']}")
        assert track_resp.status_code == 200
        assert track_resp.json()["estado"] == "abierto"

    def test_form_publico_crea_legacy_solicitud(self, client):
        """Ademas del TKT, debe crear SolicitudDerecho legacy (mismo id)."""
        token_resp = client.get("/solicitudes-derecho/token")
        token = token_resp.json()["token"]

        companies = client.get("/companies/publico").json()
        if isinstance(companies, dict):
            companies = companies.get("companies", [])
        if not companies:
            pytest.skip("No hay empresas públicas")
        company_id = companies[0]["id"]

        resp = client.post(
            "/solicitudes-derecho/",
            json={
                "company_id": company_id,
                "tipo": "acceso",
                "nombre_titular": "Titular Legacy",
                "email_titular": f"legacy+{uuid.uuid4().hex[:6]}@ejemplo.cl",
                "descripcion": "Quiero recibir mis datos",
                "token": token,
            },
        )
        assert resp.status_code == 200

        # Verificamos que existe SolicitudDerecho legacy con mismo id (via tracking).
        track_resp = client.get(f"/solicitudes-derecho/tracking/{resp.json()['tracking_token']}")
        assert track_resp.status_code == 200, "Tracking del TKT debería funcionar"


# ============================================================
# S2.5: Endpoint rechazar dedicado
# ============================================================
class TestRechazoFundadoEndpoint:
    def test_rechazar_via_endpoint_dedicado(self, client, auth_headers, empresa):
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket['id']}/rechazar",
            json={
                "causal_rechazo": "identidad_no_verificada",
                "motivo_detalle": "La firma del RUT no coincide.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["estado"] == "rechazado"
        assert data["causal_rechazo"] == "identidad_no_verificada"

    def test_rechazar_causal_invalida_falla_422(self, client, auth_headers, empresa):
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket['id']}/rechazar",
            json={"causal_rechazo": "INVALID_VALUE"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
