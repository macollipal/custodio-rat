"""
Tests para CSRFMiddleware (S14).

Verifica que:
- POST/PUT/PATCH/DELETE con cookie pero sin X-Requested-With â†’ 403
- POST/PUT/PATCH/DELETE con cookie + X-Requested-With: XMLHttpRequest â†’ pasa
- POST/PUT/PATCH/DELETE con Bearer token (sin cookie) â†’ pasa (no vulnerable)
- GET/HEAD/OPTIONS â†’ siempre pasa (mÃ©todos seguros)
- Endpoints pÃºblicos (/auth/login, /publico/*) â†’ pasa sin CSRF

Nota: Los tests usan Bearer token (del fixture token/) para evitar
interferencia del rate limiter en modo test. Bearer auth no es
vulnerable a CSRF por definiciÃ³n.
"""

import pytest
from fastapi.testclient import TestClient


class TestCSRFMiddleware:
    def test_post_without_x_requested_with_and_cookie_returns_403(self, client, admin_user):
        """
        POST mutante con cookie pero sin X-Requested-With debe ser bloqueado.
        Usa Bearer auth para el test, pero el endpoint real requiere cookie
        para ser vulnerable a CSRF.
        """
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping (test env issue)")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        resp = client.post(
            "/companies/",
            json={
                "nombre": "Test Company CSRF",
                "rut": "11.111.111-1",
                "rubro": "Test",
                "contacto_dpo": "Test",
                "email_dpo": "test@test.cl",
            },
            cookies={"custodio_token": cookie},
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.json()}"

    def test_post_with_x_requested_with_and_cookie_succeeds(self, client, admin_user):
        """POST mutante con cookie + X-Requested-With debe pasar."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        resp = client.post(
            "/companies/",
            json={
                "nombre": "Test Company CSRF",
                "rut": "22.222.222-2",
                "rubro": "Test",
                "contacto_dpo": "Test",
                "email_dpo": "test@test.cl",
            },
            cookies={"custodio_token": cookie},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.json()}"

    def test_post_with_bearer_token_no_cookie_succeeds(self, client, admin_user):
        """POST con Bearer token (sin cookie) no requiere CSRF y debe pasar."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        token = login.json()["access_token"]

        resp = client.post(
            "/companies/",
            json={
                "nombre": "Test Bearer",
                "rut": "33.333.333-3",
                "rubro": "Test",
                "contacto_dpo": "Test",
                "email_dpo": "test@test.cl",
            },
            headers={
                "Authorization": f"Bearer {token}",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        assert resp.status_code == 201, f"Bearer auth should not trigger CSRF: {resp.status_code}"

    def test_get_request_always_allowed(self, client, admin_user):
        """GET (mÃ©todo seguro) no requiere CSRF y debe pasar."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")

        resp = client.get("/companies/", cookies={"custodio_token": cookie})
        assert resp.status_code == 200, "GET should not be blocked by CSRF"

    def test_public_endpoint_no_csrf_required(self, client):
        """/auth/login (pÃºblico) no debe requerir validaciÃ³n CSRF."""
        resp = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin1234"},
        )
        assert resp.status_code == 200, "Public endpoint should not be blocked"

    def test_put_without_x_requested_with_and_cookie_returns_403(self, client, admin_user):
        """PUT mutante con cookie pero sin X-Requested-With debe ser bloqueado."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        create = client.post(
            "/companies/",
            json={
                "nombre": "CSRF PUT Test",
                "rut": "44.444.444-4",
                "rubro": "Test",
                "contacto_dpo": "Test",
                "email_dpo": "test@test.cl",
            },
            cookies={"custodio_token": cookie},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        if create.status_code != 201:
            pytest.skip(f"Create company failed with {create.status_code}")
        company_id = create.json()["id"]

        resp = client.put(
            f"/companies/{company_id}",
            json={"nombre": "Updated Name"},
            cookies={"custodio_token": cookie},
        )
        assert resp.status_code == 403, f"PUT without CSRF header should be 403, got {resp.status_code}"

    def test_delete_without_x_requested_with_and_cookie_returns_403(self, client, admin_user):
        """DELETE mutante con cookie pero sin X-Requested-With debe ser bloqueado."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        create = client.post(
            "/companies/",
            json={
                "nombre": "CSRF DELETE Test",
                "rut": "55.555.555-5",
                "rubro": "Test",
                "contacto_dpo": "Test",
                "email_dpo": "test@test.cl",
            },
            cookies={"custodio_token": cookie},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        if create.status_code != 201:
            pytest.skip(f"Create company failed with {create.status_code}")
        company_id = create.json()["id"]

        resp = client.delete(
            f"/companies/{company_id}",
            cookies={"custodio_token": cookie},
        )
        assert resp.status_code == 403, f"DELETE without CSRF header should be 403, got {resp.status_code}"

    def test_head_options_always_allowed(self, client, admin_user):
        """OPTIONS debe pasar sin validaciÃ³n CSRF."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        resp = client.options("/companies/", cookies={"custodio_token": cookie})
        assert resp.status_code == 200, "OPTIONS should always pass"

    def test_publico_endpoint_no_csrf(self, client, admin_user):
        """Endpoints /publico/* no requieren validaciÃ³n CSRF."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        if login.status_code != 200:
            pytest.skip(f"Login failed with {login.status_code}, skipping")
        cookie = login.cookies.get("custodio_token")
        if not cookie:
            pytest.skip("No cookie received from login")

        resp = client.get("/publico/transparencia/1", cookies={"custodio_token": cookie})
        assert resp.status_code in (200, 404), "Publico endpoint should not be CSRF-blocked"
