"""
Tests para B-06: Consentimiento expreso para datos sensibles (Art. 16 — REC-06).
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.rat_service import _tiene_consentimiento_activo, _validar_consentimiento_sensibles
from app.models.rat import RAT
from fastapi import HTTPException


class TestConsentimientoExpreso:
    def test_crear_rat_sin_consentimiento_y_sin_datos_sensibles(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"

    def test_crear_consentimiento_inline(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        consentimiento = {
            "rat_id": rat_id,
            "nombre_titular": "Juan Pérez",
            "email_titular": "juan@test.cl",
            "canal": "web",
            "texto_consentimiento": "Yo, Juan Pérez, otorgo mi consentimiento expreso para el tratamiento de mis datos.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=consentimiento, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"
        data = resp.json()
        assert data["nombre_titular"] == "Juan Pérez"
        assert data["activo"] is True

    def test_tiene_consentimiento_activo_false(self, db):
        assert _tiene_consentimiento_activo(db, rat_id=99999) is False

    def test_actualizar_rat_a_datos_sensibles_sin_consentimiento_falla(
        self, client, auth_headers, empresa, rat_base
    ):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        resp = client.put(f"/rats/{rat_id}", json={"datos_sensibles": True}, headers=auth_headers)
        assert resp.status_code == 422
        assert "consentimiento" in resp.json()["detail"].lower()

    def test_actualizar_rat_a_datos_sensibles_con_consentimiento_ok(
        self, client, auth_headers, empresa, rat_base
    ):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        consentimiento = {
            "rat_id": rat_id,
            "nombre_titular": "Ana López",
            "email_titular": "ana@test.cl",
            "canal": "papel",
            "texto_consentimiento": "Consentimiento expreso para datos sensibles.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=consentimiento, headers=auth_headers)
        assert resp.status_code == 201

        resp = client.put(f"/rats/{rat_id}", json={"datos_sensibles": True}, headers=auth_headers)
        assert resp.status_code == 200, f"Error: {resp.text}"
        assert resp.json()["datos_sensibles"] is True
