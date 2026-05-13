"""
Tests de autenticación: login, token JWT, acceso sin credenciales.

Notas de comportamiento real:
- HTTPBearer retorna 403 cuando no hay cabecera Authorization (no 401).
- Cuando el token existe pero es inválido, el código retorna 401.
"""

import pytest


class TestLogin:
    def test_login_exitoso(self, client, admin_user):
        resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "admin"

    def test_login_password_incorrecta(self, client, admin_user):
        resp = client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_usuario_inexistente(self, client, admin_user):
        resp = client.post("/auth/login", json={"username": "noexiste", "password": "admin1234"})
        assert resp.status_code == 401

    def test_login_campos_vacios(self, client, admin_user):
        resp = client.post("/auth/login", json={"username": "", "password": ""})
        assert resp.status_code in (401, 422)

    def test_login_body_invalido(self, client, admin_user):
        """Body sin campos requeridos debe retornar 422."""
        resp = client.post("/auth/login", json={"foo": "bar"})
        assert resp.status_code == 422

    def test_acceso_sin_token_bloqueado(self, client, admin_user):
        """HTTPBearer retorna 403 cuando no hay cabecera Authorization."""
        resp = client.get("/companies/")
        assert resp.status_code == 403

    def test_acceso_token_invalido_bloqueado(self, client, admin_user):
        """Token presente pero inválido → 401."""
        resp = client.get("/companies/", headers={"Authorization": "Bearer token_inventado_invalido"})
        assert resp.status_code == 401

    def test_health_no_requiere_auth(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_root_no_requiere_auth(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "sistema" in resp.json()

    def test_login_retorna_info_usuario(self, client, admin_user):
        resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        user = resp.json()["user"]
        assert user["is_admin"] is True
        assert user["is_active"] is True
        assert "email" in user
