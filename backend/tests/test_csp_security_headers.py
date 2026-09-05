"""
Tests de Z-01: Content-Security-Policy + headers de seguridad.

Valida que el middleware SecurityHeadersMiddleware setea:
- Content-Security-Policy restrictiva
- Strict-Transport-Security (HSTS)
- Y que el resto de headers sigue presente
"""


class TestContentSecurityPolicy:
    def test_csp_header_present(self, client):
        """CSP header presente en respuestas."""
        resp = client.get("/health")
        csp = resp.headers.get("content-security-policy")
        assert csp is not None
        assert "default-src" in csp
        assert "frame-ancestors 'none'" in csp
        assert "base-uri 'none'" in csp

    def test_csp_disallows_unsafe_inline_for_scripts(self, client):
        """API no necesita scripts â€” default-src 'none' bloquea todo por default."""
        resp = client.get("/health")
        csp = resp.headers.get("content-security-policy")
        assert "default-src 'none'" in csp

    def test_csp_on_different_endpoints(self, client):
        """CSP presente en multiples endpoints."""
        endpoints = ["/health", "/auth/me", "/companies/"]
        for ep in endpoints:
            resp = client.get(ep)
            assert "content-security-policy" in {k.lower() for k in resp.headers.keys()}, (
                f"CSP missing in {ep}"
            )


class TestStrictTransportSecurity:
    def test_hsts_header_present(self, client):
        """HSTS header presente con max-age >= 1 year."""
        resp = client.get("/health")
        hsts = resp.headers.get("strict-transport-security")
        assert hsts is not None
        assert "max-age=" in hsts
        max_age = int(hsts.split("max-age=")[1].split(";")[0])
        assert max_age >= 31536000, "HSTS max-age debe ser >= 1 year"
        assert "includeSubDomains" in hsts


class TestAllSecurityHeaders:
    """Verifica que TODOS los headers de seguridad estan presentes."""

    EXPECTED_HEADERS = {
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
        "x-xss-protection": "1; mode=block",
        "referrer-policy": "strict-origin-when-cross-origin",
        "permissions-policy": "geolocation=(), microphone=(), camera=()",
        "content-security-policy": "default-src 'none'",
        "strict-transport-security": "max-age=31536000",
    }

    def test_all_headers_in_response(self, client):
        resp = client.get("/health")
        for header, expected_value_prefix in self.EXPECTED_HEADERS.items():
            value = resp.headers.get(header)
            assert value is not None, f"Header {header} no presente"
            assert expected_value_prefix in value, (
                f"Header {header} = {value!r}, esperaba prefijo {expected_value_prefix!r}"
            )

    def test_headers_consistent_across_endpoints(self, client):
        """Mismos headers en todos los endpoints (no solo en /health)."""
        endpoints = ["/health", "/auth/me"]
        first_resp = client.get(endpoints[0])
        first_headers = {
            k: v for k, v in first_resp.headers.items()
            if k.lower() in self.EXPECTED_HEADERS
        }
        for ep in endpoints[1:]:
            resp = client.get(ep)
            for k, v in first_headers.items():
                assert k in resp.headers
                assert resp.headers.get(k) == v, f"Inconsistencia en {ep} header {k}"
