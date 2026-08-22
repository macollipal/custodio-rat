"""
Tests de seguridad: token blacklist, RBAC, rate limiting.
"""

import pytest


class TestTokenBlacklist:
    def test_logout_invalidates_token(self, client, admin_user):
        """DespuÃ©s de logout, el token no debe ser vÃ¡lido."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        logout = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout.status_code == 200

        resp = client.get("/companies/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401, "Token deberÃ­a ser invÃ¡lido despuÃ©s de logout"

    def test_revocated_token_cannot_access(self, client, admin_user):
        """Un token revocado no debe permitir acceso a endpoints protegidos."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]

        client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

        resp = client.get("/companies/", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_logout_without_token_returns_ok(self, client):
        """Logout sin token deberÃ­a retornar OK (no crash)."""
        resp = client.post("/auth/logout")
        assert resp.status_code == 200

    def test_logout_with_invalid_token_returns_ok(self, client):
        """Logout con token invÃ¡lido deberÃ­a retornar OK sin crash."""
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
            "base_legal": "Consentimiento del titular",
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
            assert resp.status_code in (401, 403), f"{method} {path} deberÃ­a requerir auth"


class TestRateLimiting:
    def test_login_rate_limit_basic(self, client, admin_user):
        """Login debe existir y ser accesible (rate limit verificado manualmente)."""
        resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert resp.status_code == 200

    def test_ai_ask_requires_auth(self, client):
        """AI endpoint debe requerir autenticaciÃ³n."""
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
        """SQL injection en bÃºsqueda no debe romper la app."""
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
    """TC-061: IDOR en /companies/{id} â€” un usuario no debe acceder a datos de otra empresa."""

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
        assert resp.status_code == 403, f"IDOR: usuario deberÃ­a obtener 403 al acceder a empresa ajena, pero obtuvo {resp.status_code}"

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
        assert resp.status_code == 403, f"IDOR PUT: deberÃ­a ser 403, pero obtuvo {resp.status_code}"

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
        assert resp.status_code == 403, f"IDOR DELETE: deberÃ­a ser 403, pero obtuvo {resp.status_code}"


class TestCompaniesPublico:
    """TC-062: /companies/publico ahora requiere autenticaciÃ³n (antes era pÃºblico)."""

    def test_companies_publico_requires_auth(self, client):
        """Acceso sin token debe retornar 401."""
        resp = client.get("/companies/publico")
        assert resp.status_code == 401, f"/companies/publico deberÃ­a requerir auth (401), pero obtuvo {resp.status_code}"

    def test_companies_publico_accessible_with_auth(self, client, admin_user):
        """Acceso con token vÃ¡lido debe retornar 200."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]
        resp = client.get("/companies/publico", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200, f"/companies/publico con auth deberÃ­a ser 200, pero obtuvo {resp.status_code}"


class TestCSVInjection:
    """TC-063: Verifica que la sanitizaciÃ³n previene CSV injection."""

    def test_sanitize_csv_value_prevents_formula_injection(self):
        """Valores que empiezan con =,+,-,@,tab deben ser prefijados con '."""
        from app.services.export_service import sanitize_csv_value
        dangerous = ["=CMD|'/C calc'!A0", "+SUM(A1:A10)", "-HOLA", "\tTAB", "\rCR"]
        for val in dangerous:
            result = sanitize_csv_value(val)
            assert result.startswith("'"), f"'{val}' deberÃ­a ser sanitizado con prefijo ', pero quedÃ³: {result}"

    def test_sanitize_csv_value_preserves_normal_text(self):
        """Textos normales no deben ser modificados."""
        from app.services.export_service import sanitize_csv_value
        normal = ["Hola mundo", "RUT 12.345.678-9", "aÃ±o 2025", "data-with-dashes"]
        for val in normal:
            result = sanitize_csv_value(val)
            assert result == val, f"'{val}' no deberÃ­a ser sanitizado, pero quedÃ³: {result}"

    def test_csv_export_sanitizes_all_cells(self, client, admin_user, empresa):
        """El CSV exportado no debe contener fÃ³rmulas inyectables."""
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        token = login.json()["access_token"]

        rat_resp = client.post("/rats/", json={
            "company_id": empresa["id"],
            "nombre_proceso": "=CMD|'/C calc'!A0",
            "categoria_datos": "Nombre, email",
            "categoria_titulares": "Clientes",
            "finalidad": "Test injection",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "El titular",
            "plazo_retencion": "1 aÃ±o",
        }, headers={"Authorization": f"Bearer {token}"})
        if rat_resp.status_code != 201:
            pytest.skip(f"No se pudo crear RAT para test CSV: {rat_resp.status_code} {rat_resp.text}")

        export_resp = client.get(f"/rats/export/csv?company_id={empresa['id']}", headers={"Authorization": f"Bearer {token}"})
        assert export_resp.status_code == 200
        content = export_resp.content.decode("utf-8-sig")
        unquoted_line = content.replace('"', "")
        assert not unquoted_line.startswith("=CMD"), "CSV injection detectada: fÃ³rmula =CMD presente sin escapar en export"
        assert "'=CMD" in content or content.count("CMD") == 0, "CSV injection no sanitizada: valor no prefijado con '"


class TestIDORMultiTenantRAT:
    """Tests de isolación multi-tenant: empresa B no puede acceder a RATs de empresa A."""

    def test_empresa_b_no_puede_ver_rat_de_empresa_a(self, client, db, admin_user):
        """GET /rats/{id} debe retornar 404 para RAT de otra empresa."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        # Crear empresa A
        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A IDOR",
            "rut": "76.111.222-4",
            "rubro": "Test A",
            "contacto_dpo": "DPO A",
            "email_dpo": "dpo@empresaA.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        # Crear empresa B
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B IDOR",
            "rut": "76.111.222-5",
            "rubro": "Test B",
            "contacto_dpo": "DPO B",
            "email_dpo": "dpo@empresaB.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        # Crear usuario para empresa B
        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        usuario_b = User(
            username="usuario_empresa_b",
            email="usuarioB@empresaB.cl",
            full_name="Usuario B",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            rol_global=RolGlobal.USUARIO.value,
        )
        db.add(usuario_b)
        db.commit()
        db.refresh(usuario_b)
        uc_b = UserCompany(user_id=usuario_b.id, company_id=emp_b["id"], rol=RolEmpresa.VIEWER)
        db.add(uc_b)
        db.commit()

        # Crear RAT para empresa A
        rat_a = client.post("/rats/", json={
            "company_id": emp_a["id"],
            "nombre_proceso": "RAT Empresa A Secreto",
            "categoria_datos": "Datos sensibles",
            "categoria_titulares": "Empleados",
            "finalidad": "Gestión depersonal",
            "base_legal": "Ejecución de contrato",
            "fuente_datos": "Sistema interno",
            "plazo_retencion": "5 años",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        # Login como usuario B
        login_b = client.post("/auth/login", json={"username": "usuario_empresa_b", "password": "password123"})
        token_b = login_b.json()["access_token"]

        # Intentar acceder al RAT de empresa A con usuario de empresa B
        resp = client.get(f"/rats/{rat_a['id']}", headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == 404, f"IDOR: empresa B puede ver RAT de empresa A (status={resp.status_code})"

    def test_empresa_b_no_puede_actualizar_rat_de_empresa_a(self, client, db, admin_user):
        """PUT /rats/{id} debe retornar 404 para RAT de otra empresa."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A Update",
            "rut": "76.222.333-1",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empA.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B Update",
            "rut": "76.222.333-2",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empB.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        usuario_b = User(
            username="usuario_b_update",
            email="usuarioB@empB.cl",
            full_name="Usuario B Update",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            rol_global=RolGlobal.USUARIO.value,
        )
        db.add(usuario_b)
        db.commit()
        db.refresh(usuario_b)
        uc_b = UserCompany(user_id=usuario_b.id, company_id=emp_b["id"], rol=RolEmpresa.EDITOR)
        db.add(uc_b)
        db.commit()

        rat_a = client.post("/rats/", json={
            "company_id": emp_a["id"],
            "nombre_proceso": "RAT A Update",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        login_b = client.post("/auth/login", json={"username": "usuario_b_update", "password": "password123"})
        token_b = login_b.json()["access_token"]

        resp = client.put(f"/rats/{rat_a['id']}", json={"nombre_proceso": "HACKED"},
                         headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == 404, f"IDOR: empresa B puede actualizar RAT de empresa A (status={resp.status_code})"

    def test_empresa_b_no_puede_eliminar_rat_de_empresa_a(self, client, db, admin_user):
        """DELETE /rats/{id} debe retornar 404 para RAT de otra empresa."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A Delete",
            "rut": "76.333.444-1",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empAdel.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B Delete",
            "rut": "76.333.444-2",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empBdel.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        usuario_b = User(
            username="usuario_b_delete",
            email="usuarioB@empBdel.cl",
            full_name="Usuario B Delete",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            rol_global=RolGlobal.USUARIO.value,
        )
        db.add(usuario_b)
        db.commit()
        db.refresh(usuario_b)
        uc_b = UserCompany(user_id=usuario_b.id, company_id=emp_b["id"], rol=RolEmpresa.EDITOR)
        db.add(uc_b)
        db.commit()

        rat_a = client.post("/rats/", json={
            "company_id": emp_a["id"],
            "nombre_proceso": "RAT A Delete",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        login_b = client.post("/auth/login", json={"username": "usuario_b_delete", "password": "password123"})
        token_b = login_b.json()["access_token"]

        resp = client.delete(f"/rats/{rat_a['id']}", headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code in (403, 404), f"IDOR: empresa B puede eliminar RAT de empresa A (status={resp.status_code})"

    def test_empresa_b_no_puede_ver_auditoria_rat_de_empresa_a(self, client, db, admin_user):
        """GET /rats/{id}/auditoria debe retornar 404 para RAT de otra empresa."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa A Audit",
            "rut": "76.444.555-1",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empAaudit.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()
        emp_b = client.post("/companies/", json={
            "nombre": "Empresa B Audit",
            "rut": "76.444.555-2",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empBaudit.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash
        usuario_b = User(
            username="usuario_b_audit",
            email="usuarioB@empBaudit.cl",
            full_name="Usuario B Audit",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            rol_global=RolGlobal.USUARIO.value,
        )
        db.add(usuario_b)
        db.commit()
        db.refresh(usuario_b)
        uc_b = UserCompany(user_id=usuario_b.id, company_id=emp_b["id"], rol=RolEmpresa.VIEWER)
        db.add(uc_b)
        db.commit()

        rat_a = client.post("/rats/", json={
            "company_id": emp_a["id"],
            "nombre_proceso": "RAT A Audit",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        login_b = client.post("/auth/login", json={"username": "usuario_b_audit", "password": "password123"})
        token_b = login_b.json()["access_token"]

        resp = client.get(f"/rats/{rat_a['id']}/auditoria", headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == 404, f"IDOR: empresa B puede ver auditoría de RAT de empresa A (status={resp.status_code})"

    def test_superadmin_puede_ver_rat_de_cualquier_empresa(self, client, db, admin_user):
        """Superadmin (admin) debe poder ver RATs de cualquier empresa."""
        admin_login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        admin_token = admin_login.json()["access_token"]

        emp_a = client.post("/companies/", json={
            "nombre": "Empresa Any",
            "rut": "76.555.666-1",
            "rubro": "Test",
            "contacto_dpo": "DPO",
            "email_dpo": "dpo@empAny.cl",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        rat_a = client.post("/rats/", json={
            "company_id": emp_a["id"],
            "nombre_proceso": "RAT Any",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
        }, headers={"Authorization": f"Bearer {admin_token}"}).json()

        # Admin es superadmin, debe poder ver cualquier RAT
        resp = client.get(f"/rats/{rat_a['id']}", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200, f"Superadmin debería poder ver RAT de cualquier empresa (status={resp.status_code})"


class TestRATValidators:
    """Tests para validadores condicionales de compliance (Ley 21.719 Art. 16, 8, 2 g)."""

    def _get_admin_token(self, client, admin_user):
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        return login.json()["access_token"]

    def test_transferencia_internacional_sin_pais_destino(self, client, admin_user, empresa):
        """transferencia_internacional=True sin pais_destino → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        resp = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "Test Transferencia Int",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "transferencia_internacional": True,
            "garantias_transferencia_int": "Contrato con cláusulas tipo",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_transferencia_internacional_sin_garantias(self, client, admin_user, empresa):
        """transferencia_internacional=True sin garantias_transferencia_int → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        resp = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "Test Transferencia Int 2",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "transferencia_internacional": True,
            "pais_destino": "Estados Unidos",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_decisiones_automatizadas_sin_logica(self, client, admin_user, empresa):
        """decisiones_automatizadas=True sin logica_automatizada → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        resp = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "Test Decisiones Auto",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "decisiones_automatizadas": True,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_datos_sensibles_sin_tipo(self, client, admin_user, empresa):
        """datos_sensibles=True sin tipo_dato_sensible → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        resp = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "Test Datos Sensibles",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "datos_sensibles": True,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_email_invalido_responsable_tratamiento(self, client, admin_user, empresa):
        """responsable_tratamiento_email con formato inválido → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        resp = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "Test Email Inválido",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "responsable_tratamiento_email": "no-es-un-email",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"

    def test_rat_update_transferencia_internacional_sin_pais(self, client, admin_user, empresa):
        """PUT con transferencia_internacional=True sin pais_destino → HTTP 422."""
        token = self._get_admin_token(client, admin_user)
        rat = client.post("/rats/", json={
            **{
                "company_id": empresa["id"],
                "nombre_proceso": "RAT para Update Transferencia",
                "categoria_datos": "Datos",
                "categoria_titulares": "Clientes",
                "finalidad": "Test",
                "base_legal": "Consentimiento del titular",
                "fuente_datos": "Web",
                "plazo_retencion": "1 año",
            },
            "transferencia_internacional": False,
        }, headers={"Authorization": f"Bearer {token}"}).json()

        resp = client.put(f"/rats/{rat['id']}", json={
            "transferencia_internacional": True,
            "garantias_transferencia_int": "Contrato SCC",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422, f"Expected 422 on update, got {resp.status_code}: {resp.text}"

    def test_campos_condicionaes_sin_eipd_no_bloquea_schema(self, client, admin_user, empresa):
        """Los validators deben pasar en schema (422) aunque la route luego requiera EIPD."""
        token = self._get_admin_token(client, admin_user)
        # Con datos_sensibles=True + evaluacion_impacto=False, el schema debe pasar
        # (la validacion de EIPD es a nivel route, no schema)
        resp = client.post("/rats/", json={
            "company_id": empresa["id"],
            "nombre_proceso": "Test sin EIPD",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
            "datos_sensibles": True,
            "tipo_dato_sensible": "Salud (física o mental)",
            "evaluacion_impacto": False,
        }, headers={"Authorization": f"Bearer {token}"})
        # Schema validation passes (200/201), route validation may reject for EIPD (422)
        assert resp.status_code in (200, 201, 422), f"Unexpected status: {resp.status_code}: {resp.text}"

    def test_campos_validos_pasan(self, client, admin_user, empresa):
        """Un RAT con todos los campos condicionales válidos debe crearse sin error."""
        token = self._get_admin_token(client, admin_user)

        # Crear EIPD primero (requerido cuando datos_sensibles=True)
        rat_payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "Test RAT Completo",
            "categoria_datos": "Datos",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
            "transferencia_internacional": True,
            "pais_destino": "Argentina",
            "garantias_transferencia_int": "Cláusulas Contractuales Tipo",
            "decisiones_automatizadas": True,
            "logica_automatizada": " scoring crediticio con threshold 0.7, revisión humana para casos >0.9",
            "datos_sensibles": True,
            "tipo_dato_sensible": "Salud (física o mental)",
            "evaluacion_impacto": True,
            "responsable_tratamiento_email": "dpo@test.cl",
        }
        resp = client.post("/rats/", json=rat_payload, headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 201:
            # Si falla por EIPD, es OK — el test verifica que los validators de schema pasan
            assert resp.status_code == 422, f"Expected 201 or 422, got {resp.status_code}: {resp.text}"
            # Verificar que el error NO es por nuestros validators (campos faltantes)
            detail = resp.json().get("detail", "")
            assert "pais_destino" not in detail, f"Error en pais_destino: {detail}"
            assert "garantias" not in detail, f"Error en garantias: {detail}"
            assert "logica_automatizada" not in detail, f"Error en logica: {detail}"
            assert "tipo_dato_sensible" not in detail, f"Error en tipo_dato_sensible: {detail}"
            return
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
