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
        resp = client.get("/solicitudes-derecho/token")
        token = resp.json()["token"]

        payload = {
            "company_id": empresa["id"],
            "tipo": "portabilidad",
            "nombre_titular": "Lucía Fernández",
            "rut_titular": "22.222.222-2",
            "email_titular": "lucia@test.cl",
            "descripcion": "Quiero portabilidad de mis datos.",
        }
        resp = client.post("/solicitudes-derecho/", json={**payload, "token": token})
        assert resp.status_code == 200
        solicitud_id = resp.json()["id"]

        resp = client.get(
            f"/solicitudes-derecho/{solicitud_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "portabilidad"
        assert data["nombre_titular"] == "Lucía Fernández"
        assert data["rut_titular"] == "22.222.222-2"
        assert data["email_titular"] == "lucia@test.cl"
        assert "exportado_en" in data
        assert "id" in data

    def test_export_portabilidad_solo_para_tipo_portabilidad(self, client, auth_headers, empresa):
        resp = client.get("/solicitudes-derecho/token")
        token = resp.json()["token"]

        payload = {
            "company_id": empresa["id"],
            "tipo": "acceso",
            "nombre_titular": "Pedro Sánchez",
            "email_titular": "pedro@test.cl",
        }
        resp = client.post("/solicitudes-derecho/", json={**payload, "token": token})
        assert resp.status_code == 200
        solicitud_id = resp.json()["id"]

        resp = client.get(
            f"/solicitudes-derecho/{solicitud_id}/portabilidad/export",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "portabilidad" in resp.json()["detail"].lower()
