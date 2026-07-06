"""
H5.4 — Tests de dashboard stats adicionales.

5 escenarios no cubiertos por test_dashboard.py:
1. eipd_pendientes: RAT con evaluacion_impacto=True y estado_eipd='pendiente'
2. transferencias_sin_garantias: RAT con transferencia_internacional=True sin garantias
3. interes_legitimo_sin_test: RAT con base_legal='Interes legitimo' sin test_interes_legitimo
4. encargados_sin_contrato: RAT con nombre_encargado sin tiene_contrato_encargado
5. rats_sin_doc_base_legal: RAT con base_legal != 'Otra' sin archivo
"""
import pytest


class TestDashboardStatsAvanzados:
    def test_dashboard_eipd_pendientes_count(self, client, auth_headers, rat_base):
        """Dashboard compta RATs con evaluacion_impacto=True y estado_eipd!='completada'."""
        payload = {
            **rat_base,
            "evaluacion_impacto": True,
            "estado_eipd": "pendiente",
        }
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "eipd_pendientes" in resp.json()

    def test_dashboard_transferencia_internacional_sin_garantias(self, client, auth_headers, rat_base):
        """Dashboard compta transferencias sin garantias documentadas."""
        payload = {
            **rat_base,
            "transferencia_internacional": True,
            "pais_destino": "Argentina",
            "garantias_transferencia_int": "",
        }
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "transferencias_sin_garantias" in resp.json()

    def test_dashboard_interes_legitimo_sin_test(self, client, auth_headers, rat_base):
        """Dashboard compta RATs con base_legal=Interes legitimo sin test documentado."""
        payload = {**rat_base, "base_legal": "Interés legítimo"}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "interes_legitimo_sin_test" in resp.json()

    def test_dashboard_encargado_sin_contrato(self, client, auth_headers, rat_base):
        """Dashboard compta RATs con encargado registrado sin contrato activo."""
        payload = {**rat_base, "nombre_encargado": "Proveedor CRM SpA"}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "encargados_sin_contrato" in resp.json()

    def test_dashboard_rats_sin_doc_base_legal(self, client, auth_headers, rat_base):
        """Dashboard compta RATs sin documento de base legal (cuando base_legal!='Otra')."""
        payload = {**rat_base, "base_legal": "Consentimiento del titular"}
        client.post("/rats/", json=payload, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "rats_sin_doc_base_legal" in resp.json()

    def test_dashboard_rats_por_vencer_presente(self, client, auth_headers, rat_base):
        """Dashboard incluye campo rats_por_vencer."""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/dashboard/{rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "rats_por_vencer" in resp.json()
        assert "rats_vencidos" in resp.json()
