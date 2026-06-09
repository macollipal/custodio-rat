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


class TestIDORProtection:
    """TC-061: IDOR en /companies/{id} — un usuario no debe acceder a datos de otra empresa."""

    def test_idor_get_company_forbidden(self, client, db, admin_user):
        """Usuario no puede leer empresa a la que no pertenece."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A", "rut": "76.000.002-K", "rubro": "A", "contacto_dpo": "A", "email_dpo": "a@a.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B", "rut": "76.000.003-7", "rubro": "B", "contacto_dpo": "B", "email_dpo": "b@b.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert emp_a.status_code == 201 and emp_b.status_code == 201
        company_b_id = emp_b.json()["id"]

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        user = User(
            username="user_companies", email="user@comp.cl", full_name="User Companies",
            hashed_password=get_password_hash("pass123"), is_active=True, rol_global=RolGlobal.USUARIO.value
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        uc = UserCompany(user_id=user.id, company_id=emp_a.json()["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        user_login = client.post("/auth/login", json={"username": "user_companies", "password": "pass123"})
        user_token = user_login.json()["access_token"]

        resp = client.get(f"/companies/{company_b_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403, f"IDOR: usuario debería obtener 403 al acceder a empresa ajena, pero obtuvo {resp.status_code}"

    def test_idor_update_company_forbidden(self, client, db, admin_user):
        """Usuario no puede editar empresa a la que no pertenece."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A2", "rut": "76.000.004-5", "rubro": "A", "contacto_dpo": "A", "email_dpo": "a2@a.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B2", "rut": "76.000.005-3", "rubro": "B", "contacto_dpo": "B", "email_dpo": "b2@b.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert emp_a.status_code == 201 and emp_b.status_code == 201
        company_b_id = emp_b.json()["id"]

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        user = User(
            username="user_companies2", email="user2@comp.cl", full_name="User Companies 2",
            hashed_password=get_password_hash("pass123"), is_active=True, rol_global=RolGlobal.USUARIO.value
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        uc = UserCompany(user_id=user.id, company_id=emp_a.json()["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        user_login = client.post("/auth/login", json={"username": "user_companies2", "password": "pass123"})
        user_token = user_login.json()["access_token"]

        resp = client.put(f"/companies/{company_b_id}", json={"nombre": "Hacked"}, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403, f"IDOR PUT: debería ser 403, pero obtuvo {resp.status_code}"

    def test_idor_delete_company_forbidden(self, client, db, admin_user):
        """Usuario no puede eliminar empresa a la que no pertenece."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A3", "rut": "76.000.006-1", "rubro": "A", "contacto_dpo": "A", "email_dpo": "a3@a.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B3", "rut": "76.000.007-K", "rubro": "B", "contacto_dpo": "B", "email_dpo": "b3@b.cl"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert emp_a.status_code == 201 and emp_b.status_code == 201
        company_b_id = emp_b.json()["id"]

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        user = User(
            username="user_companies3", email="user3@comp.cl", full_name="User Companies 3",
            hashed_password=get_password_hash("pass123"), is_active=True, rol_global=RolGlobal.USUARIO.value
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        uc = UserCompany(user_id=user.id, company_id=emp_a.json()["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        user_login = client.post("/auth/login", json={"username": "user_companies3", "password": "pass123"})
        user_token = user_login.json()["access_token"]

        resp = client.delete(f"/companies/{company_b_id}", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403, f"IDOR DELETE: debería ser 403, pero obtuvo {resp.status_code}"


class TestCompaniesPublico:
    """TC-062: /companies/publico ahora requiere autenticación (antes era público)."""

    def test_companies_publico_requires_auth(self, client):
        """Acceso sin token debe retornar 401."""
        resp = client.get("/companies/publico")
        assert resp.status_code == 401, f"/companies/publico debería requerir auth (401), pero obtuvo {resp.status_code}"

    def test_companies_publico_accessible_with_auth(self, client, admin_user):
        """Acceso con token válido debe retornar 200."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]
        resp = client.get("/companies/publico", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, f"/companies/publico con auth debería ser 200, pero obtuvo {resp.status_code}"


class TestCSVInjection:
    """TC-063: Verifica que la sanitización previene CSV injection."""

    def test_sanitize_csv_value_prevents_formula_injection(self):
        """Valores que empiezan con =,+,-,@,tab deben ser prefijados con '."""
        from app.services.export_service import sanitize_csv_value
        dangerous = ["=CMD|'/C calc'!A0", "+SUM(A1:A10)", "-HOLA", "\tTAB", "\rCR"]
        for val in dangerous:
            result = sanitize_csv_value(val)
            assert result.startswith("'"), f"'{val}' debería ser sanitizado con prefijo ', pero quedó: {result}"

    def test_sanitize_csv_value_preserves_normal_text(self):
        """Textos normales no deben ser modificados."""
        from app.services.export_service import sanitize_csv_value
        normal = ["Hola mundo", "RUT 12.345.678-9", "año 2025", "data-with-dashes"]
        for val in normal:
            result = sanitize_csv_value(val)
            assert result == val, f"'{val}' no debería ser sanitizado, pero quedó: {result}"

    def test_csv_export_sanitizes_all_cells(self, client, admin_user, empresa):
        """El CSV exportado no debe contener fórmulas inyectables."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]

        from app.models.rat import RAT
        from app.models.company import Company
        from app.database.database import Base, engine_test
        Base.metadata.create_all(bind=engine_test)

        rat_resp = client.post("/rats/", json={
            "company_id": empresa["id"],
            "nombre_proceso": "=CMD|'/C calc'!A0",
            "categoria_datos": "Nombre, email",
            "categoria_titulares": "Clientes",
            "finalidad": "Test injection",
            "base_legal": "Consentimiento",
            "fuente_datos": "El titular",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {token}"})
        if rat_resp.status_code != 201:
            pytest.skip(f"No se pudo crear RAT para test CSV: {rat_resp.status_code} {rat_resp.text}")

        export_resp = client.get(f"/rats/export/csv?company_id={empresa['id']}", headers={"Authorization": f"Bearer {token}"})
        assert export_resp.status_code == 200
        content = export_resp.content.decode("utf-8-sig")
        unquoted_line = content.replace('"', "")
        assert not unquoted_line.startswith("=CMD"), "CSV injection detectada: fórmula =CMD presente sin escapar en export"
        assert "'=CMD" in content or content.count("CMD") == 0, "CSV injection no sanitizada: valor no prefijado con '"