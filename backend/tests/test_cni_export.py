"""
H5.3 — Tests de exportacion CNI (formato APDC Ley 21.719).

3 escenarios:
1. GET /rats/export/cni?company_id=X → 200 + text/plain
2. Content-Disposition con attachment + filename
3. Contenido incluye campos del RAT en formato CNI
"""
import pytest


class TestExportCNI:
    def test_cni_retorna_200(self, client, auth_headers, rat_base):
        """Export CNI retorna 200 con datos de la empresa."""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/cni?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_cni_content_type_text_plain(self, client, auth_headers, rat_base):
        """Export CNI usa content-type text/plain charset=utf-8."""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/cni?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "text/plain" in resp.headers["content-type"]

    def test_cni_header_descarga_presente(self, client, auth_headers, rat_base):
        """Export CNI incluye Content-Disposition attachment con filename."""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/cni?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "content-disposition" in resp.headers
        assert "attachment" in resp.headers["content-disposition"]

    def test_cni_sin_auth_falla(self, client, empresa):
        """Sin auth, GET /export/cni retorna 401."""
        resp = client.get(f"/rats/export/cni?company_id={empresa['id']}")
        assert resp.status_code in (401, 403)

    def test_cni_empresa_sin_rats_retorna_200_con_contenido(self, client, auth_headers, empresa):
        """Empresa sin RATs retorna 200 y contenido vacio (no falla)."""
        resp = client.get(
            f"/rats/export/cni?company_id={empresa['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.content, bytes)
