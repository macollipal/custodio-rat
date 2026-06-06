"""
Tests para B-03: Contrato formal de Encargado (Art. 14 quater — REC-03).
"""

import pytest
from datetime import datetime, timezone, timedelta


class TestContratoEncargado:
    def test_crear_contrato_encargado(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        contrato = {
            "company_id": empresa["id"],
            "rat_id": rat_id,
            "nombre_encargado": "Encargado Test SpA",
            "objeto": "Tratamiento de datos personales de clientes por cuenta del responsable.",
            "duracion_inicio": datetime.now(timezone.utc).isoformat(),
            "duracion_fin": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            "finalidad": "Gestión de clientes y soporte.",
            "tipo_datos": "Datos identificativos, datos de contacto.",
            "categorias_titulares": "Clientes, usuarios.",
            "derechos_obligaciones": "El encargado se obliga a tratar los datos solo según instrucciones del responsable.",
        }
        resp = client.post("/encargados-contrato/", json=contrato, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"
        data = resp.json()
        assert data["nombre_encargado"] == "Encargado Test SpA"
        assert data["activo"] is True
        assert data["rat_id"] == rat_id

    def test_listar_contratos(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        contrato = {
            "company_id": empresa["id"],
            "rat_id": rat_id,
            "nombre_encargado": "Encargado Listado",
            "objeto": "Test",
            "duracion_inicio": datetime.now(timezone.utc).isoformat(),
            "finalidad": "Test",
            "tipo_datos": "Test",
            "categorias_titulares": "Test",
            "derechos_obligaciones": "Test",
        }
        client.post("/encargados-contrato/", json=contrato, headers=auth_headers)

        resp = client.get(f"/encargados-contrato/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert any(c["nombre_encargado"] == "Encargado Listado" for c in data["contratos"])

    def test_actualizar_contrato(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        contrato = {
            "company_id": empresa["id"],
            "rat_id": rat_id,
            "nombre_encargado": "Encargado Original",
            "objeto": "Test original",
            "duracion_inicio": datetime.now(timezone.utc).isoformat(),
            "finalidad": "Test",
            "tipo_datos": "Test",
            "categorias_titulares": "Test",
            "derechos_obligaciones": "Test",
        }
        resp = client.post("/encargados-contrato/", json=contrato, headers=auth_headers)
        contrato_id = resp.json()["id"]

        resp = client.put(
            f"/encargados-contrato/{contrato_id}",
            json={"objeto": "Test actualizado"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["objeto"] == "Test actualizado"

    def test_eliminar_contrato(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        contrato = {
            "company_id": empresa["id"],
            "rat_id": rat_id,
            "nombre_encargado": "Encargado a eliminar",
            "objeto": "Test",
            "duracion_inicio": datetime.now(timezone.utc).isoformat(),
            "finalidad": "Test",
            "tipo_datos": "Test",
            "categorias_titulares": "Test",
            "derechos_obligaciones": "Test",
        }
        resp = client.post("/encargados-contrato/", json=contrato, headers=auth_headers)
        contrato_id = resp.json()["id"]

        resp = client.delete(f"/encargados-contrato/{contrato_id}", headers=auth_headers)
        assert resp.status_code == 200

        resp = client.get(f"/encargados-contrato/{contrato_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_rat_con_encargado_sin_contrato_falla(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        resp = client.put(
            f"/rats/{rat_id}",
            json={"nombre_encargado": "Encargado Sin Contrato SpA"},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        assert "contrato" in resp.json()["detail"].lower()

    def test_rat_con_encargado_y_contrato_ok(self, client, auth_headers, empresa, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        contrato = {
            "company_id": empresa["id"],
            "rat_id": rat_id,
            "nombre_encargado": "Encargado Con Contrato SpA",
            "objeto": "Tratamiento de datos.",
            "duracion_inicio": datetime.now(timezone.utc).isoformat(),
            "finalidad": "Gestión.",
            "tipo_datos": "Datos identificativos.",
            "categorias_titulares": "Clientes.",
            "derechos_obligaciones": "Solo según instrucciones.",
        }
        client.post("/encargados-contrato/", json=contrato, headers=auth_headers)

        resp = client.put(
            f"/rats/{rat_id}",
            json={"nombre_encargado": "Encargado Con Contrato SpA"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, f"Error: {resp.text}"
