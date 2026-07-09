"""
H5.5 — Tests RBAC admin_empresa para endpoints RAT.

4 escenarios:
1. admin_empresa puede leer RATs de su empresa
2. admin_empresa NO puede leer RATs de otra empresa
3. admin_empresa puede crear RAT en su empresa
4. admin_empresa NO puede eliminar RAT de otra empresa
"""


class TestRBACAdminEmpresaLectura:
    def test_admin_empresa_puede_listar_rats_de_su_empresa(self, client, db, empresa, rat_base):
        """admin_empresa con acceso a la empresa puede listar sus RATs."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="adminemp_rbac",
            email="adminemp_rbac@test.cl",
            full_name="Admin Empresa RBAC",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "adminemp_rbac", "password": "pass1234"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=headers)
        assert resp.status_code == 200

    def test_admin_empresa_no_puede_listar_rats_de_otra_empresa(self, client, db, empresa, rat_base, auth_headers):
        """admin_empresa NO puede listar RATs de empresa a la que no tiene acceso."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        otra_empresa_resp = client.post("/companies/", json={
            "nombre": "Otra Empresa RBAC",
            "rut": "76.555.001-1",
            "rubro": "Test",
            "contacto_dpo": "Otro",
            "email_dpo": "otro@rbac.cl",
        }, headers=auth_headers)
        otra_empresa_id = otra_empresa_resp.json()["id"]

        user = User(
            username="adminemp_rbac2",
            email="adminemp_rbac2@test.cl",
            full_name="Admin Empresa RBAC 2",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "adminemp_rbac2", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get(f"/rats/?company_id={otra_empresa_id}", headers=headers)
        assert resp.status_code == 403


class TestRBACAdminEmpresaEscritura:
    def test_admin_empresa_puede_crear_rat_en_su_empresa(self, client, db, empresa, rat_base):
        """admin_empresa puede crear RAT en su empresa."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="adminemp_create",
            email="adminemp_create@test.cl",
            full_name="Admin Empresa Create",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "adminemp_create", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        payload = {**rat_base, "nombre_proceso": "RAT creado por admin_empresa"}
        resp = client.post("/rats/", json=payload, headers=headers)
        assert resp.status_code == 201

    def test_admin_empresa_no_puede_eliminar_rat_de_otra_empresa(self, client, db, empresa, auth_headers):
        """admin_empresa NO puede eliminar RAT de empresa a la que no tiene acceso."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        otra_empresa_resp = client.post("/companies/", json={
            "nombre": "Otra Empresa Eliminar",
            "rut": "76.666.001-1",
            "rubro": "Test",
            "contacto_dpo": "Otro",
            "email_dpo": "otro@elim.cl",
        }, headers=auth_headers)
        otra_empresa_id = otra_empresa_resp.json()["id"]

        rat_resp = client.post("/rats/", json={
            "company_id": otra_empresa_id,
            "nombre_proceso": "RAT otra empresa",
            "categoria_datos": "Test",
            "categoria_titulares": "Test",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Test",
            "plazo_retencion": "1 año",
        }, headers=auth_headers)
        rat_id = rat_resp.json()["id"]

        user = User(
            username="adminemp_del",
            email="adminemp_del@test.cl",
            full_name="Admin Empresa Del",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "adminemp_del", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.delete(f"/rats/{rat_id}", headers=headers)
        assert resp.status_code == 403
