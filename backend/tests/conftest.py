"""
Fixtures compartidas para toda la suite de tests.
- BD en memoria (aislada por test)
- TestClient con autenticación JWT real
- Helpers para crear entidades de prueba
"""

import os
os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

TEST_DB_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db():
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(db):
    from app.models import company, rat, user, audit_log, token_blacklist
    Base.metadata.create_all(bind=engine_test)
    existing = db.query(User).filter(User.username == "admin").first()
    if existing:
        return existing
    user = User(
        username="admin",
        email="admin@test.cl",
        full_name="Administrador del Sistema",
        hashed_password=get_password_hash("admin1234"),
        is_active=True,
        is_admin=True,
        rol_global="superadmin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def token(client, admin_user):
    resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
    if resp.status_code != 200:
        raise RuntimeError(f"Login fallido: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def empresa(client, auth_headers):
    from app.models import company, rat, user, audit_log, token_blacklist
    Base.metadata.create_all(bind=engine_test)
    payload = {
        "nombre": "Empresa Test SpA",
        "rut": "76.000.001-1",
        "rubro": "Tecnología",
        "direccion": "Av. Providencia 1234",
        "contacto_dpo": "Juan Test",
        "email_dpo": "dpo@test.cl",
        "descripcion": "Empresa de prueba para tests.",
    }
    resp = client.post("/companies/", json=payload, headers=auth_headers)
    if resp.status_code != 201:
        raise RuntimeError(f"No se pudo crear empresa: {resp.status_code} {resp.text}")
    return resp.json()


@pytest.fixture(scope="function")
def rat_base(empresa):
    return {
        "company_id": empresa["id"],
        "nombre_proceso": "Gestión de Clientes Web",
        "categoria_datos": "Nombre, email, teléfono",
        "categoria_titulares": "Clientes y usuarios del servicio",
        "finalidad": "Gestión comercial y soporte al cliente",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "El propio titular a través del formulario web",
        "plazo_retencion": "5 años desde la última interacción",
        "medidas_seguridad": "Cifrado en tránsito y reposo, acceso restringido",
        "destinatarios": "Equipo comercial interno",
        "transferencia_internacional": False,
        "datos_sensibles": False,
        "evaluacion_impacto": False,
        "decisiones_automatizadas": False,
    }