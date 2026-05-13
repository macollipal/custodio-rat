"""
Tests de exportación CSV y PDF.
Valida: content-type, headers de descarga, contenido mínimo, empresa sin RATs.
"""

import pytest


class TestExportCSV:
    def test_csv_retorna_200(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/csv?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_csv_content_type_correcto(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/csv?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "text/csv" in resp.headers["content-type"]

    def test_csv_header_descarga_presente(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/csv?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "content-disposition" in resp.headers
        assert "attachment" in resp.headers["content-disposition"]
        assert ".csv" in resp.headers["content-disposition"]

    def test_csv_contiene_cabecera_columnas(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/csv?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        content = resp.content.decode("utf-8-sig")
        # Debe contener al menos una columna del schema RAT
        assert "nombre_proceso" in content or "Nombre" in content

    def test_csv_contiene_dato_del_rat(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/csv?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        content = resp.content.decode("utf-8-sig")
        assert "Gestión de Clientes Web" in content

    def test_csv_empresa_sin_rats_no_falla(self, client, auth_headers, empresa):
        resp = client.get(
            f"/rats/export/csv?company_id={empresa['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_csv_sin_company_id_falla(self, client, auth_headers):
        resp = client.get("/rats/export/csv", headers=auth_headers)
        assert resp.status_code == 422

    def test_csv_empresa_inexistente_falla(self, client, auth_headers):
        resp = client.get("/rats/export/csv?company_id=99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_csv_sin_auth_falla(self, client, empresa):
        resp = client.get(f"/rats/export/csv?company_id={empresa['id']}")
        assert resp.status_code in (401, 403)


class TestExportPDF:
    def test_pdf_retorna_200(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/pdf?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_pdf_content_type_correcto(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/pdf?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "application/pdf" in resp.headers["content-type"]

    def test_pdf_header_descarga_presente(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/pdf?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert "content-disposition" in resp.headers
        assert "attachment" in resp.headers["content-disposition"]
        assert ".pdf" in resp.headers["content-disposition"]

    def test_pdf_firma_magica_correcta(self, client, auth_headers, rat_base):
        """Los primeros bytes deben ser la firma PDF: %PDF"""
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/pdf?company_id={rat_base['company_id']}",
            headers=auth_headers,
        )
        assert resp.content[:4] == b"%PDF"

    def test_pdf_empresa_sin_rats_no_falla(self, client, auth_headers, empresa):
        resp = client.get(
            f"/rats/export/pdf?company_id={empresa['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_pdf_empresa_inexistente_falla(self, client, auth_headers):
        resp = client.get("/rats/export/pdf?company_id=99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_pdf_sin_auth_falla(self, client, empresa):
        resp = client.get(f"/rats/export/pdf?company_id={empresa['id']}")
        assert resp.status_code in (401, 403)

    def test_pdf_nombre_archivo_contiene_rut(self, client, auth_headers, rat_base, empresa):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(
            f"/rats/export/pdf?company_id={empresa['id']}",
            headers=auth_headers,
        )
        disposition = resp.headers.get("content-disposition", "")
        # El RUT de la empresa fixture es "76.000.001-1"
        assert "76" in disposition or "Empresa" in disposition
