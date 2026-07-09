"""
Tests CRUD de empresas: crear, listar, obtener, actualizar, eliminar.
Incluye casos edge: duplicados, campos obligatorios, IDs inexistentes.
"""



PAYLOAD_BASE = {
    "nombre": "Empresa Alpha Ltda.",
    "rut": "76.111.222-3",
    "rubro": "Retail",
    "direccion": "Calle Falsa 123",
    "contacto_dpo": "MarÃ­a GarcÃ­a",
    "email_dpo": "dpo@alpha.cl",
    "descripcion": "Empresa de prueba.",
}


class TestCrearEmpresa:
    def test_crear_empresa_completa(self, client, auth_headers):
        resp = client.post("/companies/", json=PAYLOAD_BASE, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == PAYLOAD_BASE["nombre"]
        assert data["rut"] == PAYLOAD_BASE["rut"]
        assert "id" in data
        assert data["total_rats"] == 0

    def test_crear_empresa_minima(self, client, auth_headers):
        """Solo campos obligatorios: nombre y rut."""
        resp = client.post("/companies/", json={"nombre": "MÃ­nima SpA", "rut": "76.999.000-K"}, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["rubro"] is None

    def test_crear_empresa_sin_nombre_falla(self, client, auth_headers):
        payload = {**PAYLOAD_BASE, "nombre": ""}
        resp = client.post("/companies/", json=payload, headers=auth_headers)
        # Nombre vacÃ­o puede ser 422 (validaciÃ³n Pydantic) o 400 (validaciÃ³n de negocio)
        assert resp.status_code in (400, 422)

    def test_crear_empresa_sin_rut_falla(self, client, auth_headers):
        payload = {k: v for k, v in PAYLOAD_BASE.items() if k != "rut"}
        resp = client.post("/companies/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_empresa_sin_auth_falla(self, client):
        resp = client.post("/companies/", json=PAYLOAD_BASE)
        assert resp.status_code in (401, 403)


class TestListarEmpresas:
    def test_listar_vacio(self, client, auth_headers):
        resp = client.get("/companies/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "empresas" in data
        assert isinstance(data["empresas"], list)

    def test_listar_con_empresa(self, client, auth_headers, empresa):
        resp = client.get("/companies/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        ids = [e["id"] for e in data["empresas"]]
        assert empresa["id"] in ids

    def test_listar_contiene_total_rats(self, client, auth_headers, empresa):
        resp = client.get("/companies/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        found = next((e for e in data["empresas"] if e["id"] == empresa["id"]), None)
        assert found is not None
        assert "total_rats" in found


class TestObtenerEmpresa:
    def test_obtener_existente(self, client, auth_headers, empresa):
        resp = client.get(f"/companies/{empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == empresa["id"]

    def test_obtener_inexistente_404(self, client, auth_headers):
        resp = client.get("/companies/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestActualizarEmpresa:
    def test_actualizar_nombre(self, client, auth_headers, empresa):
        resp = client.put(
            f"/companies/{empresa['id']}",
            json={"nombre": "Empresa Renombrada SpA"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Empresa Renombrada SpA"

    def test_actualizar_dpo(self, client, auth_headers, empresa):
        resp = client.put(
            f"/companies/{empresa['id']}",
            json={"contacto_dpo": "Pedro Nuevo", "email_dpo": "pedro@empresa.cl"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["contacto_dpo"] == "Pedro Nuevo"

    def test_actualizar_inexistente_404(self, client, auth_headers):
        resp = client.put("/companies/99999", json={"nombre": "X"}, headers=auth_headers)
        assert resp.status_code == 404


class TestEliminarEmpresa:
    def test_eliminar_existente(self, client, auth_headers):
        # Crear empresa temporal para eliminar
        r = client.post("/companies/", json={"nombre": "Para Eliminar", "rut": "11.222.333-4"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        resp = client.delete(f"/companies/{eid}", headers=auth_headers)
        assert resp.status_code == 200

        # Verificar que ya no existe
        check = client.get(f"/companies/{eid}", headers=auth_headers)
        assert check.status_code == 404

    def test_eliminar_inexistente_404(self, client, auth_headers):
        resp = client.delete("/companies/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestSoftDeleteEmpresa:
    def test_desactivar_empresa_existente(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Para Desactivar", "rut": "77.888.999-1"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        resp = client.patch(f"/companies/{eid}/desactivar", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["activa"] is False
        assert resp.json()["desactivada_at"] is not None

    def test_desactivar_no_aparece_en_listado(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Para Ocultar", "rut": "77.888.999-2"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        client.patch(f"/companies/{eid}/desactivar", headers=auth_headers)

        listing = client.get("/companies/", headers=auth_headers)
        ids = [e["id"] for e in listing.json()["empresas"]]
        assert eid not in ids

    def test_desactivar_ya_desactivada_409(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Ya Inactiva", "rut": "77.888.999-3"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]
        client.patch(f"/companies/{eid}/desactivar", headers=auth_headers)

        resp = client.patch(f"/companies/{eid}/desactivar", headers=auth_headers)
        assert resp.status_code == 409

    def test_desactivar_inexistente_404(self, client, auth_headers):
        resp = client.patch("/companies/99999/desactivar", headers=auth_headers)
        assert resp.status_code == 404


class TestReactivarEmpresa:
    def test_reactivar_empresa_desactivada(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Para Reactivar", "rut": "77.888.999-4"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]
        client.patch(f"/companies/{eid}/desactivar", headers=auth_headers)

        resp = client.patch(f"/companies/{eid}/reactivar", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["activa"] is True
        assert resp.json()["desactivada_at"] is None

    def test_reactivar_ya_activa_409(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Ya Activa", "rut": "77.888.999-5"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        resp = client.patch(f"/companies/{eid}/reactivar", headers=auth_headers)
        assert resp.status_code == 409

    def test_reactivar_inexistente_404(self, client, auth_headers):
        resp = client.patch("/companies/99999/reactivar", headers=auth_headers)
        assert resp.status_code == 404


class TestHardDeleteEmpresa:
    def test_hard_delete_password_incorrecta_403(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Para Hard Delete", "rut": "77.888.999-6"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        resp = client.post(
            f"/companies/{eid}/hard-delete",
            json={"password": "wrong_password"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_hard_delete_sin_password_422(self, client, auth_headers):
        r = client.post("/companies/", json={"nombre": "Para Hard Delete 2", "rut": "77.888.999-7"}, headers=auth_headers)
        assert r.status_code == 201
        eid = r.json()["id"]

        resp = client.post(
            f"/companies/{eid}/hard-delete",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 422
