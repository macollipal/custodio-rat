"""
Tests para CORSByPathMiddleware (Z-02).
Verifica que las rutas públicas acepten cualquier origen
y que las privadas solo acepten orígenes autorizados.
"""

import pytest
from app.middleware.cors_by_path import _is_public, _cors_response_headers, _preflight_headers

ALLOWED = {"https://custodio-qa.vercel.app", "http://localhost:3000"}


class TestIsPublic:
    def test_root_es_publico(self):
        assert _is_public("/") is True

    def test_health_es_publico(self):
        assert _is_public("/health") is True

    def test_publico_arco_es_publico(self):
        assert _is_public("/publico/arco/empresa/1") is True

    def test_transparencia_es_publico(self):
        assert _is_public("/publico/transparencia/1") is True

    def test_rats_no_es_publico(self):
        assert _is_public("/rats/") is False

    def test_auth_no_es_publico(self):
        assert _is_public("/auth/login") is False

    def test_companies_no_es_publico(self):
        assert _is_public("/companies/1") is False

    def test_brechas_no_es_publico(self):
        assert _is_public("/brechas/") is False


class TestCORSResponseHeaders:
    def test_ruta_publica_devuelve_wildcard(self):
        hdrs = dict(_cors_response_headers("https://cualquier.dominio.com", "/publico/arco/1", ALLOWED))
        assert hdrs.get(b"access-control-allow-origin") == b"*"
        assert b"access-control-allow-credentials" not in hdrs

    def test_ruta_privada_origen_permitido(self):
        origin = "https://custodio-qa.vercel.app"
        hdrs = dict(_cors_response_headers(origin, "/rats/", ALLOWED))
        assert hdrs.get(b"access-control-allow-origin") == origin.encode()
        assert hdrs.get(b"access-control-allow-credentials") == b"true"

    def test_ruta_privada_origen_no_permitido(self):
        hdrs = dict(_cors_response_headers("https://evil.com", "/rats/", ALLOWED))
        assert b"access-control-allow-origin" not in hdrs

    def test_sin_origin_no_devuelve_cors(self):
        hdrs = _cors_response_headers("", "/rats/", ALLOWED)
        assert hdrs == []


class TestPreflightHeaders:
    def test_preflight_publico_acepta_cualquier_origen(self):
        hdrs = dict(_preflight_headers("https://evil.com", "/publico/arco/1", ALLOWED))
        assert hdrs.get(b"access-control-allow-origin") == b"*"
        assert b"access-control-allow-credentials" not in hdrs

    def test_preflight_privado_origen_permitido(self):
        origin = "http://localhost:3000"
        hdrs = dict(_preflight_headers(origin, "/companies/1", ALLOWED))
        assert hdrs.get(b"access-control-allow-origin") == origin.encode()
        assert hdrs.get(b"access-control-allow-credentials") == b"true"
        assert b"access-control-max-age" in hdrs

    def test_preflight_privado_origen_no_permitido(self):
        hdrs = dict(_preflight_headers("https://evil.com", "/companies/1", ALLOWED))
        assert b"access-control-allow-origin" not in hdrs

    def test_health_es_publico_en_preflight(self):
        hdrs = dict(_preflight_headers("https://monitor.example.com", "/health", ALLOWED))
        assert hdrs.get(b"access-control-allow-origin") == b"*"
