"""
Tests para los 5 campos nuevos del modelo RAT (Iter 10 - Gaps Ley 21.719).
ValidaciÃ³n: sistema_almacenamiento, volumen_titulares_estimado, operaciones_tratamiento,
logica_automatizada, responsable_tratamiento_email.

NOTA: Tests ejecutados contra PostgreSQL (Neon QA).
"""

import pytest
from fastapi.testclient import TestClient


class TestRATSistemaAlmacenamiento:
    """Tests para campo sistema_almacenamiento."""

    def test_crear_rat_con_sistema_almacenamiento(self, client: TestClient, auth_headers, empresa):
        """Caso afirmativo: RAT creado con sistema_almacenamiento vÃ¡lido."""
        payload = _rat_payload(empresa)
        payload["sistema_almacenamiento"] = "CRM Salesforce"
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["sistema_almacenamiento"] == "CRM Salesforce"

    def test_crear_rat_sin_sistema_almacenamiento(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT creado sin sistema_almacenamiento (NULL)."""
        payload = _rat_payload(empresa)
        payload.pop("sistema_almacenamiento", None)
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data.get("sistema_almacenamiento") is None

    def test_actualizar_rat_sistema_almacenamiento(self, client: TestClient, auth_headers, empresa):
        """Caso negativo: Actualizar RAT agregando sistema_almacenamiento."""
        rat = _crear_rat(client, auth_headers, empresa)
        response = client.put(
            f"/rats/{rat['id']}", json={"sistema_almacenamiento": "Excel corporativo"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["sistema_almacenamiento"] == "Excel corporativo"


class TestRATVolumenTitulares:
    """Tests para campo volumen_titulares_estimado."""

    def test_crear_rat_con_volumen_valido(self, client: TestClient, auth_headers, empresa):
        """Caso afirmativo: RAT con volumen_titulares_estimado vÃ¡lido."""
        payload = _rat_payload(empresa)
        payload["volumen_titulares_estimado"] = 50000
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["volumen_titulares_estimado"] == 50000

    def test_crear_rat_volumen_cero(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT con volumen_titulares_estimado = 0."""
        payload = _rat_payload(empresa)
        payload["volumen_titulares_estimado"] = 0
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["volumen_titulares_estimado"] == 0

    def test_crear_rat_volumen_muy_grande(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT con volumen_titulares_estimado muy grande (millones)."""
        payload = _rat_payload(empresa)
        payload["volumen_titulares_estimado"] = 15000000
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["volumen_titulares_estimado"] == 15000000


class TestRATOperacionesTratamiento:
    """Tests para campo operaciones_tratamiento (JSONB)."""

    def test_crear_rat_operaciones_array(self, client: TestClient, auth_headers, empresa):
        """Caso afirmativo: RAT con operaciones_tratamiento como array de strings."""
        payload = _rat_payload(empresa)
        payload["operaciones_tratamiento"] = ["recoleccion", "almacenamiento", "consulta"]
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["operaciones_tratamiento"] == ["recoleccion", "almacenamiento", "consulta"]

    def test_crear_rat_operaciones_dict(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT con operaciones_tratamiento como dict (estructura extendida)."""
        payload = _rat_payload(empresa)
        payload["operaciones_tratamiento"] = {
            "recoleccion": {"metodo": "formulario_web", "frecuencia": "diaria"},
            "almacenamiento": {"tipo": "cloud", "ubicacion": "Chile"},
        }
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["operaciones_tratamiento"]["recoleccion"]["metodo"] == "formulario_web"

    def test_crear_rat_sin_operaciones(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT sin operaciones_tratamiento (NULL)."""
        payload = _rat_payload(empresa)
        payload.pop("operaciones_tratamiento", None)
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json().get("operaciones_tratamiento") is None


class TestRATLogicaAutomatizada:
    """Tests para campo logica_automatizada."""

    def test_crear_rat_con_logica_automatizada(self, client: TestClient, auth_headers, empresa):
        """Caso afirmativo: RAT con logica_automatizada completa."""
        payload = _rat_payload(empresa)
        payload["decisiones_automatizadas"] = True
        payload["logica_automatizada"] = "Score crediticio: algoritmo de 5 variables. Consecuencia: aprobaciÃ³n/rechazo automÃ¡tico. RevisiÃ³n humana disponible vÃ­a email."
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert "Score crediticio" in response.json()["logica_automatizada"]

    def test_crear_rat_logica_larga(self, client: TestClient, auth_headers, empresa):
        """Caso borde: logica_automatizada con texto muy largo (>1000 chars)."""
        payload = _rat_payload(empresa)
        payload["decisiones_automatizadas"] = True
        payload["logica_automatizada"] = "A" * 2000
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert len(response.json()["logica_automatizada"]) == 2000

    def test_crear_rat_sin_logica_automatizada(self, client: TestClient, auth_headers, empresa):
        """Caso negativo: RAT con decisiones_automatizadas=True pero sin logica_automatizada."""
        payload = _rat_payload(empresa)
        payload["decisiones_automatizadas"] = True
        payload.pop("logica_automatizada", None)
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json().get("logica_automatizada") is None


class TestRATResponsableTratamientoEmail:
    """Tests para campo responsable_tratamiento_email."""

    def test_crear_rat_con_email_valido(self, client: TestClient, auth_headers, empresa):
        """Caso afirmativo: RAT con responsable_tratamiento_email vÃ¡lido."""
        payload = _rat_payload(empresa)
        payload["responsable_tratamiento_email"] = "responsable@empresa.cl"
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["responsable_tratamiento_email"] == "responsable@empresa.cl"

    def test_crear_rat_email_formato_invalido(self, client: TestClient, auth_headers, empresa):
        """Caso negativo: RAT con email en formato invÃ¡lido (backend lo acepta, validaciÃ³n estricta en frontend)."""
        payload = _rat_payload(empresa)
        payload["responsable_tratamiento_email"] = "no-es-un-email"
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201

    def test_crear_rat_sin_email_responsable(self, client: TestClient, auth_headers, empresa):
        """Caso borde: RAT sin responsable_tratamiento_email (NULL)."""
        payload = _rat_payload(empresa)
        payload.pop("responsable_tratamiento_email", None)
        response = client.post("/rats", json=payload, headers=auth_headers)
        assert response.status_code == 201
        assert response.json().get("responsable_tratamiento_email") is None


def _rat_payload(empresa) -> dict:
    return {
        "company_id": empresa["id"],
        "nombre_proceso": "Test RAT gaps",
        "categoria_datos": "Datos de contacto",
        "finalidad": "GestiÃ³n de clientes",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Formulario web",
        "plazo_retencion": "5 aÃ±os",
    }


def _crear_rat(client: TestClient, auth_headers, empresa) -> dict:
    payload = _rat_payload(empresa)
    response = client.post("/rats", json=payload, headers=auth_headers)
    return response.json()
