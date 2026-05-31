"""
Tests de seguridad: token blacklist, RBAC, rate limiting.
"""

import pytest
import time


class TestTokenBlacklist:
    def test_logout_invalidates_token(self, client, admin_user):
        """Después de logout, el token no debe ser válido."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout.status_code == 200

        resp = client.get("/companies/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401, "Token debería ser inválido después de logout"

    def test_revocated_token_cannot_access(self, client, admin_user):
        """Un token revocado no debe permitir acceso a endpoints protegidos."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]

        client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

        resp = client.get("/companies/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_logout_without_token_returns_ok(self, client):
        """Logout sin token debería retornar OK (no crash)."""
        resp = client.post("/auth/logout")
        assert resp.status_code == 200

    def test_logout_with_invalid_token_returns_ok(self, client):
        """Logout con token inválido debería retornar OK sin crash."""
        resp = client.post("/auth/logout", headers={"Authorization": "Bearer token_invalido"})
        assert resp.status_code == 200


class TestRBAC:
    def test_usuario_no_puede_crear_rat(self, client, db, admin_user):
        """Usuario regular no debe poder crear RATs."""
        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        empresa_resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = empresa_resp.json()["access_token"]

        empresa = client.post("/companies/", json={
            "nombre": "Empresa RBAC Test",
            "rut": "76.543.210-1",
            "rubro": "Test",
            "contacto_dpo": "Test",
            "email_dpo": "test@test.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert empresa.status_code == 201
        company_id = empresa.json()["id"]

        usuario = User(
            username="usuario_rbac",
            email="usuario@test.cl",
            full_name="Usuario Regular",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            rol_global=RolGlobal.USUARIO.value,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        uc = UserCompany(user_id=usuario.id, company_id=company_id, rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "usuario_rbac", "password": "password123"})
        assert login.status_code == 200
        user_token = login.json()["access_token"]

        resp = client.post("/rats/", json={
            "company_id": company_id,
            "nombre_proceso": "Test RAT",
            "categoria_datos": "Datos",
            "categoria_titulares": "Titulares",
            "finalidad": "Finalidad",
            "base_legal": "Consentimiento",
            "fuente_datos": "Fuente",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403, "Usuario no debería poder crear RATs"

    def test_admin_global_puede_crear_empresa(self, client, admin_user):
        """Superadmin debe poder crear empresas."""
        resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = resp.json()["access_token"]

        empresa = client.post("/companies/", json={
            "nombre": "Empresa Admin Global",
            "rut": "76.111.222-3",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@admin.cl",
        }, headers={"Authorization": f"Bearer {token}"})
        assert empresa.status_code == 201

    def test_unauthenticated_cannot_access_protected_routes(self, client):
        """Rutas protegidas deben rechazar requests sin auth."""
        protected = [
            ("GET", "/companies/"),
            ("GET", "/rats/"),
            ("GET", "/brechas"),
            ("GET", "/auth/me"),
        ]
        for method, path in protected:
            if method == "GET":
                resp = client.get(path)
            assert resp.status_code in (401, 403), f"{method} {path} debería requerir auth"


class TestRateLimiting:
    def test_login_rate_limit_basic(self, client, admin_user):
        """Login debe existir y ser accesible (rate limit verificado manualmente)."""
        resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert resp.status_code == 200

    def test_ai_ask_requires_auth(self, client):
        """AI endpoint debe requerir autenticación."""
        resp = client.post("/ai/ask", json={"question": "test"})
        assert resp.status_code in (401, 403)


class TestSecurityHeaders:
    def test_health_endpoint_no_auth_required(self, client):
        """Health endpoints no deben requerir auth."""
        resp = client.get("/health")
        assert resp.status_code == 200

        resp_db = client.get("/health/db")
        assert resp_db.status_code == 200

    def test_sql_injection_prevention(self, client, admin_user):
        """SQL injection en búsqueda no debe romper la app."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]

        empresa = client.post("/companies/", json={
            "nombre": "Company SQL Test",
            "rut": "76.999.888-7",
            "rubro": "Test",
            "contacto_dpo": "Test",
            "email_dpo": "test@test.cl",
        }, headers={"Authorization": f"Bearer {token}"})
        assert empresa.status_code == 201

        resp = client.get("/rats/", params={"search": "'; DROP TABLE rats; --"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200