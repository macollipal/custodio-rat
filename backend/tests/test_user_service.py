"""
Tests unitarios para user_service.py.
Usa el fixture db con transaction rollback (aislamiento de tests).
"""

import pytest
from fastapi import HTTPException

from app.services.user_service import (
    create_user,
    authenticate_user,
    is_admin,
    is_admin_empresa,
    can_access_company,
)
from app.models.user import User, RolGlobal


class TestCreateUser:
    def test_create_user_superadmin_ok(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="testadmin",
            email="testadmin@test.cl",
            full_name="Test Admin",
            password="TestPass123!",
            rol_global="superadmin",
        )
        user = create_user(db, data)

        assert user.username == "testadmin"
        assert user.email == "testadmin@test.cl"
        assert user.rol_global == "superadmin"
        assert user.is_admin is True
        assert user.is_active is True

    def test_create_user_admin_empresa_ok(self, db):
        from app.schemas.user import UserCreate
        from app.models.company import Company

        company = Company(nombre="Test Company", rut="76.123.456-7", rubro="Tech")
        db.add(company)
        db.commit()

        data = UserCreate(
            username="testadminemp",
            email="testadminemp@test.cl",
            full_name="Test Admin Emp",
            password="TestPass123!",
            rol_global="admin_empresa",
            company_id=company.id,
        )
        user = create_user(db, data)

        assert user.rol_global == "admin_empresa"
        assert user.is_admin is False

    def test_create_user_duplicate_username(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="dupuser",
            email="dup1@test.cl",
            full_name="Dup User",
            password="TestPass123!",
            rol_global="superadmin",
        )
        create_user(db, data)

        data2 = UserCreate(
            username="dupuser",
            email="dup2@test.cl",
            full_name="Dup User 2",
            password="TestPass123!",
            rol_global="superadmin",
        )
        with pytest.raises(HTTPException) as exc:
            create_user(db, data2)
        assert exc.value.status_code == 409
        assert "nombre de usuario ya está en uso" in exc.value.detail

    def test_create_user_duplicate_email(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="user1",
            email="same@email.cl",
            full_name="User One",
            password="TestPass123!",
            rol_global="superadmin",
        )
        create_user(db, data)

        data2 = UserCreate(
            username="user2",
            email="same@email.cl",
            full_name="User Two",
            password="TestPass123!",
            rol_global="superadmin",
        )
        with pytest.raises(HTTPException) as exc:
            create_user(db, data2)
        assert exc.value.status_code == 409
        assert "email ya está registrado" in exc.value.detail

    def test_create_user_invalid_rol(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="badrol",
            email="badrol@test.cl",
            full_name="Bad Rol",
            password="TestPass123!",
            rol_global="invalid_rol",
        )
        with pytest.raises(HTTPException) as exc:
            create_user(db, data)
        assert exc.value.status_code == 400
        assert "Rol global inválido" in exc.value.detail

    def test_create_user_admin_empresa_without_company(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="no_company_admin",
            email="no_company@test.cl",
            full_name="No Company Admin",
            password="TestPass123!",
            rol_global="admin_empresa",
            company_id=None,
        )
        with pytest.raises(HTTPException) as exc:
            create_user(db, data)
        assert exc.value.status_code == 400
        assert "Debes asignar al menos una empresa" in exc.value.detail


class TestAuthenticateUser:
    def test_authenticate_user_ok(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="logintest",
            email="logintest@test.cl",
            full_name="Login Test",
            password="SecretPass99!",
            rol_global="superadmin",
        )
        create_user(db, data)

        token = authenticate_user(db, "logintest", "SecretPass99!")

        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.token_type == "bearer"
        assert token.expires_in == 480 * 60
        assert token.user.username == "logintest"

    def test_authenticate_user_wrong_password(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="wrongpw",
            email="wrongpw@test.cl",
            full_name="Wrong Password",
            password="CorrectPass!",
            rol_global="superadmin",
        )
        create_user(db, data)

        with pytest.raises(HTTPException) as exc:
            authenticate_user(db, "wrongpw", "WrongPass!")
        assert exc.value.status_code == 401
        assert "Credenciales incorrectas" in exc.value.detail

    def test_authenticate_user_not_found(self, db):
        with pytest.raises(HTTPException) as exc:
            authenticate_user(db, "nonexistent", "anypass")
        assert exc.value.status_code == 401

    def test_authenticate_user_inactive(self, db):
        from app.schemas.user import UserCreate

        data = UserCreate(
            username="inactiveuser",
            email="inactive@test.cl",
            full_name="Inactive User",
            password="TestPass123!",
            rol_global="superadmin",
        )
        user = create_user(db, data)
        user.is_active = False
        db.commit()

        with pytest.raises(HTTPException) as exc:
            authenticate_user(db, "inactiveuser", "TestPass123!")
        assert exc.value.status_code == 403
        assert "inactivo" in exc.value.detail


class TestRoleHelpers:
    def test_is_admin_true_for_superadmin(self, db):
        user = User(
            username="admin_test",
            email="admin_test@test.cl",
            full_name="Admin Test",
            hashed_password="fake",
            rol_global=RolGlobal.SUPERADMIN.value,
            is_admin=True,
            is_active=True,
        )
        assert is_admin(user) is True

    def test_is_admin_false_for_admin_empresa(self, db):
        user = User(
            username="adminemp_test",
            email="adminemp_test@test.cl",
            full_name="Admin Emp Test",
            hashed_password="fake",
            rol_global=RolGlobal.ADMIN_EMPRESA.value,
            is_admin=False,
            is_active=True,
        )
        assert is_admin(user) is False

    def test_is_admin_empresa_true(self, db):
        user = User(
            username="adminemp2",
            email="adminemp2@test.cl",
            full_name="Admin Emp 2",
            hashed_password="fake",
            rol_global=RolGlobal.ADMIN_EMPRESA.value,
            is_admin=False,
            is_active=True,
        )
        assert is_admin_empresa(user) is True

    def test_is_admin_empresa_false_for_usuario(self, db):
        user = User(
            username="usuario_test",
            email="usuario_test@test.cl",
            full_name="Usuario Test",
            hashed_password="fake",
            rol_global=RolGlobal.USUARIO.value,
            is_admin=False,
            is_active=True,
        )
        assert is_admin_empresa(user) is False


class TestCanAccessCompany:
    def test_superadmin_accesses_any_company(self, db):
        user = User(
            username="superany",
            email="superany@test.cl",
            full_name="Super Any",
            hashed_password="fake",
            rol_global=RolGlobal.SUPERADMIN.value,
            is_admin=True,
            is_active=True,
        )
        assert can_access_company(user, 999, db) is True
        assert can_access_company(user, 1, db) is True

    def test_admin_empresa_accesses_own_company(self, db):
        from app.models.company import Company
        from app.models.user_company import UserCompany, RolEmpresa

        company = Company(nombre="My Company", rut="76.999.999-1", rubro="Tech")
        db.add(company)
        db.commit()

        user = User(
            username="myadmin",
            email="myadmin@test.cl",
            full_name="My Admin",
            hashed_password="fake",
            rol_global=RolGlobal.ADMIN_EMPRESA.value,
            is_admin=False,
            is_active=True,
        )
        db.add(user)
        db.commit()

        uc = UserCompany(user_id=user.id, company_id=company.id, rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        assert can_access_company(user, company.id, db) is True
        assert can_access_company(user, 99999, db) is False

    def test_usuario_accesses_own_company(self, db):
        from app.models.company import Company
        from app.models.user_company import UserCompany, RolEmpresa

        company = Company(nombre="User Company", rut="77.000.000-1", rubro="Retail")
        db.add(company)
        db.commit()

        user = User(
            username="myuser",
            email="myuser@test.cl",
            full_name="My User",
            hashed_password="fake",
            rol_global=RolGlobal.USUARIO.value,
            is_admin=False,
            is_active=True,
        )
        db.add(user)
        db.commit()

        uc = UserCompany(user_id=user.id, company_id=company.id, rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        assert can_access_company(user, company.id, db) is True