"""
Tests para QW9: Auto-asignaciÃ³n por reglas ARCO.
Custodio RAT Manager â€” Ley 21.719 Art. 12.

Covers:
- CRUD de reglas de asignaciÃ³n (solo admin_empresa y superadmin)
- EvaluaciÃ³n de reglas con distintos niveles de especificidad
- Auto-asignaciÃ³n al crear ticket
- Sin asignaciÃ³n si no hay regla que aplique
"""

import pytest


class TestReglaAsignacionCRUD:
    def test_superadmin_puede_crear_regla(self, client, auth_headers, empresa, admin_user, db):
        """Superadmin puede crear una regla de asignaciÃ³n."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            username="resp_test",
            email="resp@test.cl",
            full_name="Responsable Test",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        resp = client.post("/tkt-reglas-asignacion/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "prioridad": None,
            "responsable_id": user.id,
            "activo": True,
            "orden": 0,
        }, headers=auth_headers)
        assert resp.status_code == 200, f"Error: {resp.status_code} {resp.text}"
        data = resp.json()
        assert data["tipo"] == "acceso"
        assert data["responsable_id"] == user.id
        assert data["activo"] is True

    def test_usuario_no_puede_crear_regla(self, client, db, empresa):
        """Usuario regular no puede crear reglas de asignaciÃ³n."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        user = User(
            username="usr_regla_test",
            email="usr_regla@test.cl",
            full_name="Usuario Regla Test",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="usuario",
        )
        db.add(user)
        db.commit()

        uc = UserCompany(user_id=user.id, company_id=empresa["id"], rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "usr_regla_test", "password": "pass1234"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/tkt-reglas-asignacion/", json={
            "tipo": "acceso",
            "responsable_id": 1,
        }, headers=headers)
        assert resp.status_code == 403

    def test_listar_reglas(self, client, auth_headers, empresa, db, admin_user):
        """GET /tkt-reglas-asignacion/ lista reglas."""
        resp = client.get("/tkt-reglas-asignacion/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_actualizar_regla(self, client, auth_headers, empresa, db, admin_user):
        """PUT /tkt-reglas-asignacion/{id} actualiza regla."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            username="resp_update",
            email="resp_update@test.cl",
            full_name="Responsable Update",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        create = client.post("/tkt-reglas-asignacion/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "responsable_id": user.id,
            "activo": True,
        }, headers=auth_headers)
        regla_id = create.json()["id"]

        resp = client.put(f"/tkt-reglas-asignacion/{regla_id}", json={
            "tipo": "rectificacion",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["tipo"] == "rectificacion"

    def test_eliminar_regla(self, client, auth_headers, empresa, db, admin_user):
        """DELETE /tkt-reglas-asignacion/{id} elimina regla."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            username="resp_del",
            email="resp_del@test.cl",
            full_name="Responsable Del",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        create = client.post("/tkt-reglas-asignacion/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "responsable_id": user.id,
            "activo": True,
        }, headers=auth_headers)
        regla_id = create.json()["id"]

        resp = client.delete(f"/tkt-reglas-asignacion/{regla_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["ok"] is True


class TestAutoAsignacion:
    def test_auto_asignacion_por_tipo(self, client, auth_headers, empresa, db):
        """Un ticket se auto-asigna al responsable de su tipo."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            username="resp_tipo",
            email="resp_tipo@test.cl",
            full_name="Responsable Tipo",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        client.post("/tkt-reglas-asignacion/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "responsable_id": user.id,
            "activo": True,
            "orden": 0,
        }, headers=auth_headers)

        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Juan Perez",
            "titular_email": "juan@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["responsable_id"] == user.id

    def test_sin_asignacion_si_no_hay_regla(self, client, auth_headers, empresa, db):
        """Un ticket no se asigna si no hay regla que aplique."""
        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Juan Perez",
            "titular_email": "juan@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["responsable_id"] is None

    def test_regla_global_sin_filtros(self, client, auth_headers, empresa, db):
        """Una regla global (sin company_id, sin tipo, sin prioridad) asigna a cualquier ticket."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            username="resp_global",
            email="resp_global@test.cl",
            full_name="Responsable Global",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        client.post("/tkt-reglas-asignacion/", json={
            "company_id": None,
            "tipo": None,
            "prioridad": None,
            "responsable_id": user.id,
            "activo": True,
            "orden": 0,
        }, headers=auth_headers)

        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "rectificacion",
            "titular_nombre": "Maria Lopez",
            "titular_email": "maria@test.cl",
            "prioridad": "urgente",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["responsable_id"] == user.id

    def test_regla_mas_especifica_prevalece(self, client, auth_headers, empresa, db):
        """Una regla mÃ¡s especÃ­fica (empresa+tipo) prevalece sobre una global."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user_global = User(
            username="resp_gl",
            email="resp_gl@test.cl",
            full_name="Responsable Global",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user_global)
        db.commit()
        db.refresh(user_global)

        user_especifico = User(
            username="resp_esp",
            email="resp_esp@test.cl",
            full_name="Responsable Especifico",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(user_especifico)
        db.commit()
        db.refresh(user_especifico)

        client.post("/tkt-reglas-asignacion/", json={
            "company_id": None,
            "tipo": None,
            "prioridad": None,
            "responsable_id": user_global.id,
            "activo": True,
            "orden": 0,
        }, headers=auth_headers)

        client.post("/tkt-reglas-asignacion/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "prioridad": None,
            "responsable_id": user_especifico.id,
            "activo": True,
            "orden": 0,
        }, headers=auth_headers)

        resp = client.post("/tkt-solicitud-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "titular_nombre": "Pedro Gomez",
            "titular_email": "pedro@test.cl",
            "prioridad": "normal",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["responsable_id"] == user_especifico.id
