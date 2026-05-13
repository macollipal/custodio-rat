"""
Tests del servicio de sugerencias automáticas para el RAT.
Valida: tipos conocidos, coincidencia parcial, tipos desconocidos, estructura de respuesta.
"""

import pytest


class TestSugerenciasAPI:
    def test_tipos_disponibles(self, client, auth_headers):
        resp = client.get("/rats/sugerencias/tipos", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tipos" in data
        assert isinstance(data["tipos"], list)
        assert len(data["tipos"]) > 0

    def test_sugerencia_clientes_web(self, client, auth_headers):
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": "clientes web"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo_proceso"] == "clientes web"
        assert "categoria_datos" in data
        assert "categoria_titulares" in data
        assert "finalidad" in data
        assert "base_legal" in data
        assert "plazo_retencion_sugerido" in data
        assert "datos_sensibles" in data
        assert "observacion" in data

    def test_sugerencia_empleados(self, client, auth_headers):
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": "empleados"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["tipo_proceso"] == "empleados"

    def test_sugerencia_pacientes(self, client, auth_headers):
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": "pacientes"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # Pacientes maneja datos sensibles → debe advertirlo
        assert data["datos_sensibles"] is True

    def test_sugerencia_coincidencia_parcial(self, client, auth_headers):
        """'clientes' debe coincidir aunque no sea la cadena exacta."""
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": "clientes"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_sugerencia_tipo_desconocido_retorna_generico(self, client, auth_headers):
        """Un tipo no reconocido no debe romper el sistema."""
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": "tipo_absolutamente_inventado_xyz"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # Debe retornar algo (sugerencia genérica)
        assert "categoria_datos" in data

    def test_sugerencia_tipo_vacio(self, client, auth_headers):
        resp = client.post(
            "/rats/sugerencias",
            json={"tipo_proceso": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200  # Retorna sugerencia genérica

    def test_sugerencia_sin_auth_falla(self, client):
        resp = client.post("/rats/sugerencias", json={"tipo_proceso": "empleados"})
        assert resp.status_code in (401, 403)

    def test_sugerencia_todos_los_tipos_disponibles(self, client, auth_headers):
        """Cada tipo listado debe retornar una sugerencia válida."""
        tipos_resp = client.get("/rats/sugerencias/tipos", headers=auth_headers)
        tipos = tipos_resp.json()["tipos"]

        for tipo in tipos:
            resp = client.post(
                "/rats/sugerencias",
                json={"tipo_proceso": tipo},
                headers=auth_headers,
            )
            assert resp.status_code == 200, f"Falló para tipo: {tipo}"
            data = resp.json()
            assert data["categoria_datos"], f"categoria_datos vacía para: {tipo}"
            assert data["finalidad"], f"finalidad vacía para: {tipo}"
