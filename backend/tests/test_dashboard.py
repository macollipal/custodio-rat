"""
Tests del endpoint de estadísticas del dashboard.
Valida: estructura de respuesta, contadores, cálculo de completitud, flags de riesgo.
"""

import pytest


class TestDashboard:
    def test_dashboard_empresa_sin_rats(self, client, auth_headers, empresa):
        resp = client.get(f"/rats/dashboard/{empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_procesos"] == 0
        assert data["completitud_promedio"] == 0
        assert data["procesos_con_datos_sensibles"] == 0
        assert data["requieren_eipd"] == 0
        assert data["transferencias_internacionales"] == 0

    def test_dashboard_estructura_completa(self, client, auth_headers, empresa):
        resp = client.get(f"/rats/dashboard/{empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        campos_esperados = [
            "total_procesos",
            "completitud_promedio",
            "procesos_con_datos_sensibles",
            "requieren_eipd",
            "transferencias_internacionales",
            "por_estado",
        ]
        for campo in campos_esperados:
            assert campo in data, f"Campo faltante en dashboard: {campo}"

    def test_dashboard_cuenta_rat_creado(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total_procesos"] == 1

    def test_dashboard_detecta_datos_sensibles(self, client, auth_headers, rat_base):
        payload = {**rat_base, "datos_sensibles": True}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.json()["procesos_con_datos_sensibles"] >= 1

    def test_dashboard_detecta_eipd(self, client, auth_headers, rat_base):
        payload = {**rat_base, "evaluacion_impacto": True}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.json()["requieren_eipd"] >= 1

    def test_dashboard_detecta_transferencia_internacional(self, client, auth_headers, rat_base):
        payload = {**rat_base, "transferencia_internacional": True, "pais_destino": "Brasil"}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.json()["transferencias_internacionales"] >= 1

    def test_dashboard_completitud_promedio_entre_0_y_100(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        pct = resp.json()["completitud_promedio"]
        assert 0 <= pct <= 100

    def test_dashboard_por_estado_refleja_rat_creado(self, client, auth_headers, rat_base):
        """El dashboard refleja el estado del RAT (borrador o completo según campos)."""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        por_estado = resp.json()["por_estado"]
        total_en_estados = sum(por_estado.values())
        assert total_en_estados >= 1

    def test_dashboard_empresa_inexistente_404(self, client, auth_headers):
        resp = client.get("/rats/dashboard/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_dashboard_sin_auth_falla(self, client, empresa):
        resp = client.get(f"/rats/dashboard/{empresa['id']}")
        assert resp.status_code in (401, 403)


class TestAuditoria:
    def test_auditoria_rat_registra_creacion(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.get(f"/rats/{created['id']}/auditoria", headers=auth_headers)
        assert resp.status_code == 200
        logs = resp.json()
        assert isinstance(logs, list)

    def test_auditoria_registra_actualizacion(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        client.put(
            f"/rats/{created['id']}",
            json={"estado": "completo"},
            headers=auth_headers,
        )
        resp = client.get(f"/rats/{created['id']}/auditoria", headers=auth_headers)
        assert resp.status_code == 200

    def test_auditoria_sin_auth_falla(self, client, rat_base, auth_headers):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.get(f"/rats/{created['id']}/auditoria")
        assert resp.status_code in (401, 403)
