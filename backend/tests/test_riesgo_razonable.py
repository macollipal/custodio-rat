"""
Tests para B-05: Filtro de riesgo razonable en Brechas (Art. 14 sexies — REC-05).
"""

import pytest
from datetime import datetime, timezone
from app.models.breach import SecurityBreach, NivelRiesgo
from app.services.breach_service import _calcular_reportable, evaluar_riesgo_brecha


class TestCalcularReportable:
    def test_bajo_no_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.BAJO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=False,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is False

    def test_medio_no_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.MEDIO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=False,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is False

    def test_alto_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.ALTO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=False,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is True

    def test_critico_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.CRITICO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=False,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is True

    def test_datos_sensibles_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.BAJO,
            incluye_datos_sensibles=True,
            incluye_datos_nna=False,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is True

    def test_datos_nna_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.BAJO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=True,
            incluye_datos_financieros=False,
        )
        assert _calcular_reportable(breach) is True

    def test_datos_financieros_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.BAJO,
            incluye_datos_sensibles=False,
            incluye_datos_nna=False,
            incluye_datos_financieros=True,
        )
        assert _calcular_reportable(breach) is True

    def test_multiple_flags_reportable(self):
        breach = SecurityBreach(
            nivel_riesgo=NivelRiesgo.MEDIO,
            incluye_datos_sensibles=True,
            incluye_datos_nna=True,
            incluye_datos_financieros=True,
        )
        assert _calcular_reportable(breach) is True


class TestBreachCrud:
    def test_crear_brecha_con_nivel_riesgo(self, client, auth_headers, empresa):
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha de prueba",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "alto",
            "volumen_titulares_afectados": 150,
            "incluye_datos_sensibles": True,
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"
        data = resp.json()
        assert data["nivel_riesgo"] == "alto"
        assert data["volumen_titulares_afectados"] == 150
        assert data["incluye_datos_sensibles"] is True
        assert data["reportable_apdc_calculado"] is True

    def test_evaluar_riesgo_endpoint(self, client, auth_headers, empresa):
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha para evaluar",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        breach_id = resp.json()["id"]

        resp = client.post(f"/brechas/{breach_id}/evaluar-riesgo", headers=auth_headers)
        assert resp.status_code == 200
        assert "reportable_apdc_calculado" in resp.json()

    def test_listar_brechas_con_campos_riesgo(self, client, auth_headers, empresa):
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con riesgo",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "critico",
            "incluye_datos_financieros": True,
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201

        resp = client.get(f"/brechas/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        brechas = resp.json()["brechas"]
        assert any(b["nivel_riesgo"] == "critico" for b in brechas)
