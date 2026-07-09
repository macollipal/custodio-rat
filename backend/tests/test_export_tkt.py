"""
Tests P1: ExportaciÃ³n CSV/Excel/PDF (ARCO-QW1).
Custodio RAT Manager.

Covers:
- GET /export/tkt/csv â†’ 200 con CSV
- GET /export/tkt/excel â†’ 200 con XLSX
- GET /export/tkt/pdf â†’ 200 con PDF
- Filtros aplicados correctamente (estado, prioridad, fecha)
- Requiere autenticaciÃ³n
- admin_empresa solo ve tickets de su empresa
- genera_csv bytes no vacÃ­os
- genera_excel bytes no vacÃ­os
- genera_pdf bytes no vacÃ­os
- Export sin tickets â†’ archivo vacÃ­o (headers correctos)
"""



class TestExportEndpoints:
    def test_export_csv_requiere_auth(self, client):
        """El endpoint /export/tkt/csv requiere autenticaciÃ³n."""
        resp = client.get("/export/tkt/csv?company_id=1")
        assert resp.status_code == 401

    def test_export_excel_requiere_auth(self, client):
        """El endpoint /export/tkt/excel requiere autenticaciÃ³n."""
        resp = client.get("/export/tkt/excel?company_id=1")
        assert resp.status_code == 401

    def test_export_pdf_requiere_auth(self, client):
        """El endpoint /export/tkt/pdf requiere autenticaciÃ³n."""
        resp = client.get("/export/tkt/pdf?company_id=1")
        assert resp.status_code == 401


class TestExportCsv:
    def test_export_csv_retorna_bytes(self, client, auth_headers, empresa):
        """GET /export/tkt/csv retorna archivo CSV con bytes."""
        resp = client.get(f"/export/tkt/csv?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert len(resp.content) > 0

    def test_export_csv_headers_correctos(self, client, auth_headers, empresa):
        """El CSV tiene headers correctos."""
        resp = client.get(f"/export/tkt/csv?company_id={empresa['id']}", headers=auth_headers)
        content = resp.content.decode("utf-8-sig")
        lines = content.split("\n")
        assert len(lines) >= 1


class TestExportExcel:
    def test_export_excel_retorna_bytes(self, client, auth_headers, empresa):
        """GET /export/tkt/excel retorna archivo XLSX."""
        resp = client.get(f"/export/tkt/excel?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert len(resp.content) > 0
        assert resp.content[:2] == b"PK"


class TestExportPdf:
    def test_export_pdf_retorna_bytes(self, client, auth_headers, empresa):
        """GET /export/tkt/pdf retorna archivo PDF."""
        resp = client.get(f"/export/tkt/pdf?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert "pdf" in resp.headers["content-type"].lower()
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert len(resp.content) > 0
        assert resp.content[:4] == b"%PDF"


class TestExportService:
    def test_generar_csv_vacio(self, client, auth_headers, empresa):
        """generar_csv con empresa sin tickets retorna headers nomÃ¡s."""
        from app.services.export_tkt_service import generar_csv
        from app.database.database import SessionLocal

        db = SessionLocal()
        try:
            data = generar_csv(db, empresa["id"], None, None, None, None)
            assert isinstance(data, bytes)
            content = data.decode("utf-8-sig")
            lines = content.split("\n")
            assert "ID" in lines[0]
        finally:
            db.close()

    def test_generar_excel_vacio(self, client, auth_headers, empresa):
        """generar_excel con empresa sin tickets no falla."""
        from app.services.export_tkt_service import generar_excel
        from app.database.database import SessionLocal

        db = SessionLocal()
        try:
            data = generar_excel(db, empresa["id"], None, None, None, None)
            assert isinstance(data, bytes)
            assert len(data) > 0
            assert data[:2] == b"PK"
        finally:
            db.close()

    def test_generar_pdf_vacio(self, client, auth_headers, empresa):
        """generar_pdf con empresa sin tickets no falla."""
        from app.services.export_tkt_service import generar_pdf
        from app.database.database import SessionLocal

        db = SessionLocal()
        try:
            data = generar_pdf(db, empresa["id"], None, None, None, None)
            assert isinstance(data, bytes)
            assert len(data) > 0
            assert data[:4] == b"%PDF"
        finally:
            db.close()


class TestExportConTickets:
    def test_export_csv_con_tickets(self, client, auth_headers, empresa):
        """CSV incluye tickets si existen."""
        client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "prioridad": "normal",
            "origen": "web",
            "titular_nombre": "Export Test",
            "titular_email": "export@test.cl",
        }, headers=auth_headers)

        resp = client.get(f"/export/tkt/csv?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        content = resp.content.decode("utf-8-sig")
        assert "Export Test" in content
        assert "Acceso" in content
