"""
Tests para B-02: Módulo de Transparencia Pública (Art. 14 ter — REC-02).
"""

import pytest
from datetime import datetime, timezone


class TestTransparenciaPublica:
    def test_obtener_politica_sin_auth(self, client, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers={"Authorization": f"Bearer {client.cookies.get('session') or ''}"})
        if resp.status_code != 201:
            pass

        resp = client.get(f"/publico/transparencia/{empresa['id']}")
        assert resp.status_code == 200, f"Error: {resp.text}"
        data = resp.json()
        assert data["company_id"] == empresa["id"]
        assert data["nombre_empresa"] == empresa["nombre"]
        assert data["version"] is not None
        assert data["fecha_generacion"] is not None

    def test_politica_incluye_12_items(self, client, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base)
        if resp.status_code == 201:
            pass

        resp = client.get(f"/publico/transparencia/{empresa['id']}")
        assert resp.status_code == 200
        data = resp.json()
        for item in ["item_a_politica", "item_b_responsable", "item_c_domicilio", "item_d_categorias",
                     "item_e_medidas", "item_f_derechos_arco", "item_g_recurir_apdc", "item_h_transferencias",
                     "item_i_conservacion", "item_j_fuente", "item_k_retirar_consentimiento",
                     "item_l_decisiones_automatizadas"]:
            assert item in data, f"Falta {item} en la política"

    def test_politica_empresa_inexistente_404(self, client):
        resp = client.get("/publico/transparencia/99999")
        assert resp.status_code == 404

    def test_politica_con_rats_agregados(self, client, auth_headers, empresa, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)

        resp = client.get(f"/publico/transparencia/{empresa['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["item_d_categorias"] is not None
        assert data["item_i_conservacion"] is not None

    def test_hash_sha256_generado(self, client, empresa):
        resp = client.get(f"/publico/transparencia/{empresa['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["hash_sha256"] is not None
        assert len(data["hash_sha256"]) == 64
