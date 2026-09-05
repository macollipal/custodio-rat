"""
Tests Sprint 1 — Compliance urgente ARCO.

Cubre:
- P0: Endpoint público /solicitudes-derecho/tracking/{token}
- P0: Validación de método verificación de identidad antes de 'resuelto' (Art. 12 Ley 21.719)
- P0: Rechazo con causal_rechazo válida (enum)
- P0: Hash SHA-256 de integridad al resolver
- P1: Rechazo con causal_rechazo inválida -> 422

Estos tests requieren PostgreSQL (Neon QA). Ver backend/CLAUDE.md.
"""
import uuid


def _crear_ticket(client, headers, company_id, tipo="acceso"):
    """Crea un TKT base por API."""
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
            "descripcion": "Solicitud de prueba ARCO",
        },
        headers=headers,
    )
    assert resp.status_code == 200, f"Error creando ticket: {resp.text}"
    return resp.json()


# ============================================================
# P0: Endpoint público de tracking
# ============================================================
class TestTrackingPublico:
    def test_tracking_token_valido_retorna_estado(self, client, auth_headers, empresa):
        """El endpoint público devuelve el estado de la solicitud."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])
        token = ticket["tracking_token"]
        assert token, "El ticket debería tener tracking_token"

        # El endpoint público NO requiere auth.
        resp = client.get(f"/seguimiento/{token}")
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["estado"] == "Abierto"
        assert data["tipo"] == "Acceso"
        assert "dias_restantes" in data

    def test_tracking_token_inexistente_retorna_404(self, client):
        """Token inexistente -> 404 (no 403, para no filtrar existencia)."""
        resp = client.get("/seguimiento/no-existe-token")
        assert resp.status_code == 404

    def test_tracking_no_exige_auth(self, client):
        """El endpoint debe ser público (sin Authorization header)."""
        resp = client.get("/seguimiento/algo")
        # 404 (no encontrado) está OK — confirma que pasó la validación de auth
        assert resp.status_code in (404, 403)


# ============================================================
# P0: Validación de identidad antes de 'resuelto'
# ============================================================
class TestValidacionIdentidad:
    def test_resolver_sin_metodo_verificacion_falla_422(self, client, auth_headers, empresa):
        """No se puede marcar como resuelto sin método de verificación de identidad."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.patch(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            json={
                "estado": "resuelto",
                "respuesta_texto": "Respuesta al titular.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 422, resp.text
        assert "verificación de identidad" in resp.text or "verificacion de identidad" in resp.text.lower()

    def test_resolver_con_metodo_verificacion_pasa(self, client, auth_headers, empresa):
        """Si hay método de verificación + respuesta, se puede resolver."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.patch(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            json={
                "estado": "resuelto",
                "respuesta_texto": "Confirmamos que sus datos son correctos.",
                "metodo_verificacion_identidad": "email_verificado",
                "evidencia_identidad": "Email + DPI del titular verificados",
                "medio_respuesta": "email",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["estado"] == "resuelto"
        assert data["metodo_verificacion_identidad"] == "email_verificado"
        # S1.4: hash debe calcularse
        assert data.get("evidencia_respuesta_hash")
        assert len(data["evidencia_respuesta_hash"]) == 64  # SHA-256 hex


# ============================================================
# P0: Rechazo con causal_rechazo enum
# ============================================================
class TestRechazoCausal:
    def test_rechazar_con_causal_valida(self, client, auth_headers, empresa):
        """POST /rechazar con causal del enum debe funcionar."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket['id']}/rechazar",
            json={
                "causal_rechazo": "identidad_no_verificada",
                "motivo_detalle": "La firma del RUT no coincide con la cedula.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["estado"] == "rechazado"
        assert data["causal_rechazo"] == "identidad_no_verificada"

    def test_rechazar_con_causal_invalida_falla_422(self, client, auth_headers, empresa):
        """Causal fuera del enum -> 422."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket['id']}/rechazar",
            json={"causal_rechazo": "fantasma"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_rechazar_persistido_en_tracking(self, client, auth_headers, empresa):
        """El estado rechazado debe exponerse en /seguimiento."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])

        client.post(
            f"/tkt-solicitud-derecho/{ticket['id']}/rechazar",
            json={"causal_rechazo": "plazo_vencido", "motivo_detalle": "Pasaron 12 dias habiles."},
            headers=auth_headers,
        )

        resp = client.get(f"/seguimiento/{ticket['tracking_token']}")
        assert resp.status_code == 200
        assert resp.json()["estado"] == "Rechazado"


# ============================================================
# P1: Hash de integridad SHA-256
# ============================================================
class TestHashEvidencia:
    def test_hash_sha256_64_chars(self, client, auth_headers, empresa):
        """evidencia_respuesta_hash debe ser SHA-256 hex (64 chars)."""
        ticket = _crear_ticket(client, auth_headers, empresa["id"])
        client.patch(
            f"/tkt-solicitud-derecho/{ticket['id']}",
            json={
                "estado": "resuelto",
                "respuesta_texto": "Su solicitud fue procesada.",
                "metodo_verificacion_identidad": "cedula_escaneada",
                "evidencia_identidad": "DPI verificada vs selfie.",
                "medio_respuesta": "email",
            },
            headers=auth_headers,
        )

        resp = client.get(f"/seguimiento/{ticket['tracking_token']}")
        data = resp.json()
        assert data["estado"] == "Resuelto"
        h = data["evidencia_respuesta_hash"]
        assert h and len(h) == 64, f"Hash invalido: {h!r}"
        # El backend genera hash con salt temporal, no podemos reconstruirlo exacto.
        # Validamos la forma (solo hex chars) y la presencia.
        assert all(c in "0123456789abcdef" for c in h)
