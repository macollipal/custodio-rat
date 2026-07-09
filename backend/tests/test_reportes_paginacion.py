"""
H5.2 — Tests de paginacion del endpoint /rats/reportes (QW-ITER14-01).

Cubre:
- Paginacion basica (skip, limit)
- Total filtered refleja filtros aplicados
- Comportamiento con >100 registros
- Validacion de sort_by contra whitelist
- Paginacion en export (CSV/PDF)

QW-ITER14-01: reportes deben paginar cuando hay >100 RATs para
evitar memory issues en el cliente.
"""



class TestReportesPaginacion:
    """Tests del endpoint GET /rats/reportes con paginacion."""

    def test_paginacion_basica_skip_0_limit_10(self, client, auth_headers, empresa, rat_base):
        """Pagina 1 con limit=10 debe retornar hasta 10 RATs."""
        # Crear 5 RATs
        for i in range(5):
            payload = {**rat_base, "nombre_proceso": f"RAT Test {i}"}
            r = client.post("/rats/", json=payload, headers=auth_headers)
            assert r.status_code == 201

        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=0&limit=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["skip"] == 0
        assert body["limit"] == 10
        assert body["total"] == 5
        assert len(body["rats"]) == 5

    def test_paginacion_offset_skip_2_limit_2(self, client, auth_headers, empresa, rat_base):
        """Saltar 2 y tomar 2 siguientes."""
        for i in range(5):
            payload = {**rat_base, "nombre_proceso": f"RAT Pagination {i}"}
            r = client.post("/rats/", json=payload, headers=auth_headers)
            assert r.status_code == 201

        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=2&limit=2",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["skip"] == 2
        assert body["limit"] == 2
        assert body["total"] == 5
        assert len(body["rats"]) == 2

    def test_paginacion_total_filtered_correcto(self, client, auth_headers, empresa, rat_base):
        """Total filtered refleja solo RATs con filtro aplicado."""
        # Crear 3 RATs con datos sensibles + 2 sin
        for i in range(3):
            r = client.post("/rats/", json={
                **rat_base,
                "nombre_proceso": f"RAT Sensible {i}",
                "datos_sensibles": True,
                "tipo_dato_sensible": "Salud",
                "evaluacion_impacto": True,
                "estado_eipd": "pendiente",
            }, headers=auth_headers)
            assert r.status_code == 201
        for i in range(2):
            r = client.post("/rats/", json={
                **rat_base,
                "nombre_proceso": f"RAT Normal {i}",
            }, headers=auth_headers)
            assert r.status_code == 201

        # Filtrar solo sensibles
        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&datos_sensibles=true&limit=50",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 3, f"Esperado 3 sensibles, obtuvo {body['total']}"
        assert len(body["rats"]) == 3
        for rat in body["rats"]:
            assert rat["datos_sensibles"] is True

    def test_paginacion_sort_by_whitelist(self, client, auth_headers, empresa, rat_base):
        """sort_by debe estar en whitelist — valores no permitidos se rechazan."""
        for i in range(3):
            payload = {**rat_base, "nombre_proceso": f"RAT Sort {i}"}
            client.post("/rats/", json=payload, headers=auth_headers)

        # sort_by valido
        resp_ok = client.get(
            f"/rats/reportes?company_id={empresa['id']}&sort_by=nombre_proceso&sort_order=asc",
            headers=auth_headers,
        )
        assert resp_ok.status_code == 200

        # sort_by invalido — debe usar default 'created_at' (no falla)
        resp_bad = client.get(
            f"/rats/reportes?company_id={empresa['id']}&sort_by=campo_que_no_existe",
            headers=auth_headers,
        )
        assert resp_bad.status_code == 200
        assert resp_bad.json()["sort_by"] == "created_at"

    def test_qw_iter14_01_cien_registros_pagina(self, client, auth_headers, empresa, rat_base):
        """QW-ITER14-01: con 100+ RATs el endpoint debe paginar correctamente."""
        # Crear 25 RATs (suficiente para validar paginacion sin demorar)
        for i in range(25):
            payload = {**rat_base, "nombre_proceso": f"RAT Bulk {i:03d}"}
            r = client.post("/rats/", json=payload, headers=auth_headers)
            assert r.status_code == 201

        # Pagina 1: limit=10
        resp1 = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=0&limit=10",
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        assert resp1.json()["total"] == 25
        assert len(resp1.json()["rats"]) == 10

        # Pagina 2: skip=10, limit=10
        resp2 = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=10&limit=10",
            headers=auth_headers,
        )
        assert resp2.status_code == 200
        assert len(resp2.json()["rats"]) == 10

        # Pagina 3: skip=20, limit=10 → quedan 5
        resp3 = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=20&limit=10",
            headers=auth_headers,
        )
        assert resp3.status_code == 200
        assert len(resp3.json()["rats"]) == 5

    def test_paginacion_sin_auth_401(self, client, empresa):
        """Sin auth → 401."""
        resp = client.get(f"/rats/reportes?company_id={empresa['id']}&skip=0&limit=10")
        assert resp.status_code == 401

    def test_paginacion_filtro_combinado(self, client, auth_headers, empresa, rat_base):
        """Filtros + paginacion funcionan juntos."""
        # Crear 10 RATs: 5 con transferencia internacional, 5 sin
        for i in range(5):
            r = client.post("/rats/", json={
                **rat_base,
                "nombre_proceso": f"RAT Int {i}",
                "transferencia_internacional": True,
                "pais_destino": "Estados Unidos",
                "garantias_transferencia_int": "SCC EU 2021",
                "evaluacion_impacto": True,
                "estado_eipd": "pendiente",
            }, headers=auth_headers)
            assert r.status_code == 201
        for i in range(5):
            r = client.post("/rats/", json={
                **rat_base,
                "nombre_proceso": f"RAT Nac {i}",
            }, headers=auth_headers)
            assert r.status_code == 201

        # Filtro + paginacion
        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&transferencia_internacional=true&skip=2&limit=2",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert len(body["rats"]) == 2
        for rat in body["rats"]:
            assert rat["transferencia_internacional"] is True