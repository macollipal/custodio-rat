"""
Fixtures compartidas para toda la suite de tests.
- BD en memoria (aislada por sesión de test)
- TestClient con autenticación JWT real
- Helpers para crear entidades de prueba
"""

import os
os.environ["ENV"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

# ── BD en memoria ─────────────────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Crea todas las tablas en la BD de test una sola vez por sesión."""
    from app.models import company, rat, user, audit_log, token_blacklist  # noqa
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db():
    """Sesión de BD aislada: hace rollback al terminar cada test."""
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """TestClient con override de get_db → BD en memoria."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Crea el usuario admin en la BD de test."""
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


@pytest.fixture
def token(client, admin_user):
    """Obtiene JWT para el usuario admin."""
    resp = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
    assert resp.status_code == 200, f"Login fallido: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    """Headers de autorización listos para usar."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def empresa(client, auth_headers):
    """Crea una empresa de prueba y retorna su JSON."""
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
    assert resp.status_code == 201, f"No se pudo crear empresa: {resp.text}"
    return resp.json()


@pytest.fixture
def rat_base(empresa):
    """Payload base para crear un RAT."""
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
