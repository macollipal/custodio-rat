"""
Tests para B-04: Portabilidad per-titular (Art. 9 — REC-04).
"""

import pytest
from datetime import datetime, timezone


class TestPortabilidad:
    def test_crear_solicitud_portabilidad(self, client, empresa):
        resp = client.get("/solicitudes-derecho/token")
        token = resp.json()["token"]

        payload = {
            "company_id": empresa["id"],
            "tipo": "portabilidad",
            "nombre_titular": "Pedro Sánchez",
            "rut_titular": "11.111.111-1",
            "email_titular": "pedro@test.cl",
            "descripcion": "Solicito copia de todos mis datos personales.",
        }
        resp = client.post("/solicitudes-derecho/", json={**payload, "token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "portabilidad"

    def test_export_portabilidad_json(self, client, auth_headers, empresa):
        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "portabilidad",
            "titular_nombre": "Lucía Fernández",
            "titular_email": "lucia@test.cl",
            "rut_titular": "22.222.222-2",
            "descripcion": "Quiero portabilidad de mis datos.",
        }, headers=auth_headers)
        assert resp.status_code == 200
        ticket_id = resp.json()["id"]

        resp = client.get(
            f"/tkt-solicitud-derecho/{ticket_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "portabilidad"
        assert data["titular_nombre"] == "Lucía Fernández"
        assert data["titular_rut"] is not None
        assert data["titular_email"] == "lucia@test.cl"
        assert "exportado_en" in data
        assert "id" in data

    def test_export_portabilidad_solo_para_tipo_portabilidad(self, client, auth_headers, empresa):
        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Pedro Sánchez",
            "titular_email": "pedro@test.cl",
        }, headers=auth_headers)
        assert resp.status_code == 200
        ticket_id = resp.json()["id"]

        resp = client.get(
            f"/tkt-solicitud-derecho/{ticket_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "portabilidad" in resp.json()["detail"].lower()
