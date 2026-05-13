"""
Tests CRUD de registros RAT.
Cubre: creación, listado, obtención, actualización de estado, eliminación,
completitud, flags de riesgo y casos edge.
"""

import pytest


class TestCrearRAT:
    def test_crear_rat_completo(self, client, auth_headers, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre_proceso"] == rat_base["nombre_proceso"]
        # El servicio marca automáticamente como "completo" si todos los campos
        # obligatorios están presentes (comportamiento por diseño)
        assert data["estado"] in ("borrador", "completo")
        assert "id" in data
        assert "completitud" in data
        assert isinstance(data["completitud"], int)

    def test_crear_rat_sin_nombre_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "nombre_proceso": ""}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_rat_sin_company_falla(self, client, auth_headers, rat_base):
        payload = {k: v for k, v in rat_base.items() if k != "company_id"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_rat_company_inexistente_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "company_id": 99999}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code in (404, 400)

    def test_crear_rat_con_datos_sensibles(self, client, auth_headers, rat_base):
        payload = {**rat_base, "datos_sensibles": True, "evaluacion_impacto": True}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["datos_sensibles"] is True
        assert data["evaluacion_impacto"] is True

    def test_crear_rat_con_transferencia_internacional(self, client, auth_headers, rat_base):
        payload = {**rat_base, "transferencia_internacional": True, "pais_destino": "Estados Unidos"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["pais_destino"] == "Estados Unidos"

    def test_crear_rat_sin_auth_falla(self, client, rat_base):
        resp = client.post("/rats/", json=rat_base)
        assert resp.status_code in (401, 403)

    def test_nombre_proceso_espacios_vacios_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "nombre_proceso": "   "}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422


class TestListarRATs:
    def test_listar_por_empresa(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/?company_id={rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(r["company_id"] == rat_base["company_id"] for r in data)

    def test_listar_sin_filtro(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get("/rats/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_listar_empresa_sin_rats(self, client, auth_headers, empresa):
        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_todos_tienen_completitud(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get("/rats/", headers=auth_headers)
        assert resp.status_code == 200
        for r in resp.json():
            assert "completitud" in r
            assert 0 <= r["completitud"] <= 100


class TestObtenerRAT:
    def test_obtener_existente(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.get(f"/rats/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_obtener_inexistente_404(self, client, auth_headers):
        resp = client.get("/rats/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestActualizarRAT:
    def test_actualizar_nombre_proceso(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"nombre_proceso": "Proceso Actualizado"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["nombre_proceso"] == "Proceso Actualizado"

    def test_cambiar_estado_a_en_revision(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"estado": "en_revision"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "en_revision"

    def test_cambiar_estado_a_aprobado(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"estado": "aprobado"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "aprobado"

    def test_estado_invalido_falla(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"estado": "estado_inventado"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_actualizar_inexistente_404(self, client, auth_headers):
        resp = client.put("/rats/99999", json={"nombre_proceso": "X"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_completitud_aumenta_al_completar(self, client, auth_headers, rat_base):
        """Un RAT con más campos completos debe tener mayor completitud."""
        # RAT base (sin medidas_seguridad ni algunos campos)
        payload_incompleto = {**rat_base}
        payload_incompleto.pop("medidas_seguridad", None)

        created = client.post("/rats/", json=payload_incompleto, headers=auth_headers).json()
        completitud_inicial = created["completitud"]

        resp = client.put(
            f"/rats/{created['id']}",
            json={"medidas_seguridad": "Cifrado AES-256", "observaciones_auditoria": "Sin observaciones"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["completitud"] >= completitud_inicial


class TestEliminarRAT:
    def test_eliminar_existente(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.delete(f"/rats/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200

        check = client.get(f"/rats/{created['id']}", headers=auth_headers)
        assert check.status_code == 404

    def test_eliminar_inexistente_404(self, client, auth_headers):
        resp = client.delete("/rats/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_empresa_eliminada_borra_rats(self, client, auth_headers, rat_base, empresa):
        """Eliminación en cascada: al borrar empresa, sus RATs desaparecen."""
        rat = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        rat_id = rat["id"]

        client.delete(f"/companies/{empresa['id']}", headers=auth_headers)

        check = client.get(f"/rats/{rat_id}", headers=auth_headers)
        assert check.status_code == 404


class TestCompletitud:
    def test_completitud_entre_0_y_100(self, client, auth_headers, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        pct = resp.json()["completitud"]
        assert 0 <= pct <= 100

    def test_rat_con_todos_los_campos_alta_completitud(self, client, auth_headers, rat_base):
        payload = {
            **rat_base,
            "categoria_titulares": "Clientes del servicio web",
            "medidas_seguridad": "Cifrado AES-256",
            "destinatarios": "Equipo comercial",
            "transferencia_internacional": True,
            "pais_destino": "España",
            "garantias_transferencia_int": "Cláusulas Contractuales Tipo (SCC)",
            "datos_sensibles": False,
            "evaluacion_impacto": False,
            "decisiones_automatizadas": False,
            "observaciones_auditoria": "Proceso auditado y aprobado",
            "transferencia_datos": "Proveedor de email marketing",
        }
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["completitud"] >= 70
