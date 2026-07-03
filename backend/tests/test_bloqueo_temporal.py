"""
Tests para B-01: Workflow de Bloqueo Temporal (Art. 8 ter â€” REC-01).
"""

import pytest
from datetime import datetime, timezone
from app.models.solicitud_derecho import TipoSolicitud, EstadoSolicitud


class TestBloqueoTemporal:
    def test_crear_solicitud_bloqueo_token(self, client):
        resp = client.get("/solicitudes-derecho/token")
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_crear_solicitud_bloqueo(self, client, empresa):
        resp = client.get("/solicitudes-derecho/token")
        token = resp.json()["token"]

        payload = {
            "company_id": empresa["id"],
            "tipo": "bloqueo",
            "nombre_titular": "MarÃ­a GarcÃ­a",
            "email_titular": "maria@test.cl",
            "descripcion": "Solicito bloqueo temporal de mis datos.",
        }
        resp = client.post("/solicitudes-derecho/", json={**payload, "token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "bloqueo"
        assert data["estado"] == "abierto"

    def test_bloquear_rat(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "bloqueo",
            "titular_nombre": "Carlos Ruiz",
            "titular_email": "carlos@test.cl",
        }, headers=auth_headers)
        assert resp.status_code == 200
        ticket_id = resp.json()["id"]

        resp = client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": rat_id, "dias_bloqueo": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "bloqueado"
        assert data["rat_id"] == rat_id
        assert data["plazo_bloqueo_vencimiento"] is not None

    def test_desbloquear_rat(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "bloqueo",
            "titular_nombre": "Laura Torres",
            "titular_email": "laura@test.cl",
        }, headers=auth_headers)
        ticket_id = resp.json()["id"]

        client.post(
            f"/tkt-solicitud-derecho/{ticket_id}/bloquear",
            json={"rat_id": rat_id, "dias_bloqueo": 2},
            headers=auth_headers,
        )

        resp = client.post(f"/tkt-solicitud-derecho/{ticket_id}/desbloquear", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["estado"] == "resuelto"

    def test_tipos_solicitud_incluyen_bloqueo_y_portabilidad(self):
        tipos = [e.value for e in TipoSolicitud]
        assert "bloqueo" in tipos
        assert "portabilidad" in tipos

    def test_estado_solicitud_incluye_bloqueado(self):
        estados = [e.value for e in EstadoSolicitud]
        assert "bloqueado" in estados
