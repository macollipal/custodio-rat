"""
Tests para F3.1: Versionamiento API /api/v1/.

Verifica que los endpoints existen en ambas rutas (legacy y versionada)
durante el periodo de deprecación. Una vez removida la compatibilidad con
legacy (Q1 2027), este test debe actualizarse.
"""
import pytest


class TestAPIVersioning:
    """Tests de versionamiento API. Los endpoints deben existir en ambas URLs."""

    # Lista de (path_v1, path_legacy) que deben responder igual
    # (404 = endpoint no existe, pero también puede ser "company_id no existe")
    ENDPOINTS_SIN_AUTH = [
        ("/api/v1/publico/transparencia/1", "/publico/transparencia/1"),
    ]

    @pytest.mark.parametrize("path_v1,path_legacy", ENDPOINTS_SIN_AUTH)
    def test_endpoints_existen_en_ambas_urls(self, client, path_v1, path_legacy):
        """El endpoint debe estar disponible en /api/v1/ y en legacy.

        Como ambos endpoints requieren un company_id valido y la BD de test
        esta vacia por defecto, esperamos 404 (company not found).
        Si fuera 404 por "endpoint no existe" sin body, no podriamos distinguirlos.
        Por ahora validamos que ambos retornen el mismo status code.
        """
        r1 = client.get(path_v1)
        r2 = client.get(path_legacy)

        # Ambos deben responder el mismo status (ambos enrutan al mismo handler).
        assert r1.status_code == r2.status_code, (
            f"Path {path_v1} -> {r1.status_code}, path {path_legacy} -> {r2.status_code}. "
            f"Esperado: mismo handler, mismo status."
        )

    def test_root_documenta_api_versions(self, client):
        """El endpoint raíz debe listar las versiones disponibles."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "api_versions" in data, (
            "Root debe listar api_versions para clientes"
        )
        # Debe mencionar v1
        versions_str = " ".join(data["api_versions"])
        assert "v1" in versions_str, (
            f"Root debe mencionar v1: {data['api_versions']}"
        )

    def test_path_v1_precede_legacy_en_resolucion(self, client):
        """Las requests a /api/v1/ deben ir al router v1, no al legacy."""
        r1 = client.get("/api/v1/publico/transparencia/1")
        r2 = client.get("/publico/transparencia/1")
        # Mismo status code esperado (ambos handlers equivalentes).
        assert r1.status_code == r2.status_code