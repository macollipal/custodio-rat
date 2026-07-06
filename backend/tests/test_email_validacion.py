"""
H5.6 — Test validacion de email invalido.

1 escenario:
- Crear usuario con email invalido → 422 Pydantic validation error
"""
import pytest


class TestEmailValidation:
    def test_crear_usuario_email_invalido_retorna_422(self, client, auth_headers):
        """Email sin formato valido es rechazado por Pydantic (EmailStr)."""
        resp = client.post("/users/", json={
            "username": "user_email_inv",
            "email": "no-es-un-email",
            "full_name": "Usuario Email Invalido",
            "password": "Test1234!",
            "rol_global": "usuario",
        }, headers=auth_headers)
        assert resp.status_code == 422, f"Esperado 422, obtuvo {resp.status_code}: {resp.text}"

    def test_crear_usuario_email_sin_aroba_retorna_422(self, client, auth_headers):
        """Email sin @ es rechazado."""
        resp = client.post("/users/", json={
            "username": "user_email_inv2",
            "email": "email-sin-aroba.cl",
            "full_name": "Usuario Sin @",
            "password": "Test1234!",
            "rol_global": "usuario",
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_usuario_email_valido_retorna_201(self, client, auth_headers):
        """Email con formato valido es aceptado."""
        resp = client.post("/users/", json={
            "username": "user_email_ok",
            "email": "valido@test.cl",
            "full_name": "Usuario Email Valido",
            "password": "Test1234!",
            "rol_global": "usuario",
        }, headers=auth_headers)
        assert resp.status_code == 201, f"Esperado 201, obtuvo {resp.status_code}: {resp.text}"
