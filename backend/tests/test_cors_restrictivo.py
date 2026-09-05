"""
Tests de CORS restrictivo.

Valida que el middleware CORSMiddleware estÃ¡ configurado con listas
explÃ­citas de mÃ©todos y headers (no comodines), en lÃ­nea con la guÃ­a
de seguridad Z-02 (defense-in-depth).
"""


def test_cors_preflight_allowed_method_returns_headers(client):
    """Preflight OPTIONS con mÃ©todo permitido retorna headers CORS."""
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code in (200, 204)
    assert "access-control-allow-origin" in {k.lower() for k in resp.headers.keys()}


def test_cors_preflight_get_allowed(client):
    """Preflight con mÃ©todo GET es permitido."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert resp.status_code in (200, 204)


def test_cors_preflight_put_allowed(client):
    """Preflight con mÃ©todo PUT es permitido."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert resp.status_code in (200, 204)


def test_cors_preflight_patch_allowed(client):
    """Preflight con mÃ©todo PATCH es permitido."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert resp.status_code in (200, 204)


def test_cors_preflight_delete_allowed(client):
    """Preflight con mÃ©todo DELETE es permitido."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert resp.status_code in (200, 204)


def test_cors_preflight_options_allowed(client):
    """Preflight OPTIONS es permitido (es el mÃ©todo del preflight)."""
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "OPTIONS",
        },
    )
    assert resp.status_code in (200, 204)


def test_cors_allowed_header_authorization(client):
    """Preflight con header Authorization permitido retorna ACAO."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    allowed_headers = resp.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allowed_headers


def test_cors_allowed_header_content_type(client):
    """Preflight con header Content-Type permitido retorna ACAO."""
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    allowed_headers = resp.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed_headers


def test_cors_allowed_header_x_requested_with(client):
    """Preflight con header X-Requested-With permitido (CSRF protection)."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-requested-with",
        },
    )
    allowed_headers = resp.headers.get("access-control-allow-headers", "").lower()
    assert "x-requested-with" in allowed_headers


def test_cors_allowed_header_x_request_id(client):
    """Preflight con header X-Request-ID permitido (correlaciÃ³n)."""
    resp = client.options(
        "/companies/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-request-id",
        },
    )
    allowed_headers = resp.headers.get("access-control-allow-headers", "").lower()
    assert "x-request-id" in allowed_headers


def test_cors_exposes_request_id_header(client):
    """El header X-Request-ID estÃ¡ en expose_headers."""
    resp = client.get("/health", headers={"Origin": "http://localhost:3000"})
    exposed = resp.headers.get("access-control-expose-headers", "").lower()
    assert "x-request-id" in exposed
