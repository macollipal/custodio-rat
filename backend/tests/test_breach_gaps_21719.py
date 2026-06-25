"""
Tests para los 5 campos nuevos del modelo SecurityBreach (Iter 10 - Gaps Ley 21.719).
Validación: fecha_ocurrencia_estimada, efectos_probables, causa_raiz,
evidencia_notificacion_apdc_folio, estado_cierre, fecha_cierre.

NOTA: Tests ejecutados contra PostgreSQL (Neon QA).
"""

import pytest
from datetime import datetime, timezone, timedelta


class TestBreachFechaOcurrencia:
    """Tests para campo fecha_ocurrencia_estimada."""

    def test_crear_brecha_con_fecha_ocurrencia(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con fecha_ocurrencia_estimada."""
        ahora = datetime.now(timezone.utc)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con fecha de ocurrencia",
            "fecha_deteccion": ahora.isoformat(),
            "fecha_ocurrencia_estimada": (ahora - timedelta(hours=2)).isoformat(),
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["fecha_ocurrencia_estimada"] is not None

    def test_crear_brecha_fecha_ocurrencia_antes_deteccion(self, client, auth_headers, empresa, clean_task_queue):
        """Caso borde: fecha_ocurrencia_estimada anterior a fecha_deteccion."""
        ahora = datetime.now(timezone.utc)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con fecha ocurrencia anterior",
            "fecha_deteccion": ahora.isoformat(),
            "fecha_ocurrencia_estimada": (ahora - timedelta(days=1)).isoformat(),
            "nivel_riesgo": "alto",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201

    def test_crear_brecha_sin_fecha_ocurrencia(self, client, auth_headers, empresa, clean_task_queue):
        """Caso negativo: Brecha sin fecha_ocurrencia_estimada (NULL)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin fecha ocurrencia",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json().get("fecha_ocurrencia_estimada") is None


class TestBreachEfectosProbables:
    """Tests para campo efectos_probables."""

    def test_crear_brecha_con_efectos_probables(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con efectos_probables completos."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con efectos",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "efectos_probables": "Potencial robo de identidad, fraude financiero, daño reputacional",
            "nivel_riesgo": "alto",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert "robo de identidad" in resp.json()["efectos_probables"]

    def test_crear_brecha_efectos_largos(self, client, auth_headers, empresa, clean_task_queue):
        """Caso borde: efectos_probables con texto muy largo (>500 chars)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha efectos largos",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "efectos_probables": "X" * 600,
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert len(resp.json()["efectos_probables"]) == 600

    def test_crear_brecha_sin_efectos_probables(self, client, auth_headers, empresa, clean_task_queue):
        """Caso negativo: Brecha sin efectos_probables (NULL)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin efectos",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json().get("efectos_probables") is None


class TestBreachCausaRaiz:
    """Tests para campo causa_raiz."""

    def test_crear_brecha_causa_error_humano(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con causa_raiz = error_humano."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha por error humano",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "causa_raiz": "error_humano",
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["causa_raiz"] == "error_humano"

    def test_crear_brecha_causa_malware(self, client, auth_headers, empresa, clean_task_queue):
        """Caso borde: causa_raiz = malware."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha por malware",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "causa_raiz": "malware",
            "nivel_riesgo": "critico",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["causa_raiz"] == "malware"

    def test_crear_brecha_sin_causa_raiz(self, client, auth_headers, empresa, clean_task_queue):
        """Caso negativo: Brecha sin causa_raiz (NULL)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin causa raíz",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json().get("causa_raiz") is None


class TestBreachEvidenciaNotificacionApdc:
    """Tests para campo evidencia_notificacion_apdc_folio."""

    def test_crear_brecha_con_folio_apdc(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con evidencia_notificacion_apdc_folio."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha notificada a APDC",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "evidencia_notificacion_apdc_folio": "APDC-2026-001234",
            "nivel_riesgo": "alto",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["evidencia_notificacion_apdc_folio"] == "APDC-2026-001234"

    def test_crear_brecha_folio_largo(self, client, auth_headers, empresa, clean_task_queue):
        """Caso borde: folio con 100 caracteres exactos."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con folio largo",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "evidencia_notificacion_apdc_folio": "A" * 100,
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert len(resp.json()["evidencia_notificacion_apdc_folio"]) == 100

    def test_crear_brecha_sin_folio_apdc(self, client, auth_headers, empresa, clean_task_queue):
        """Caso negativo: Brecha sin evidencia_notificacion_apdc_folio (NULL)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin folio APDC",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json().get("evidencia_notificacion_apdc_folio") is None


class TestBreachEstadoCierre:
    """Tests para campos estado_cierre y fecha_cierre."""

    def test_crear_brecha_estado_abierta(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con estado_cierre = abierta."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha abierta",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "estado_cierre": "abierta",
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["estado_cierre"] == "abierta"

    def test_crear_brecha_estado_cerrada_con_fecha(self, client, auth_headers, empresa, clean_task_queue):
        """Caso borde: Brecha con estado_cierre = cerrada y fecha_cierre."""
        ahora = datetime.now(timezone.utc)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha cerrada",
            "fecha_deteccion": ahora.isoformat(),
            "estado_cierre": "cerrada",
            "fecha_cierre": ahora.isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["estado_cierre"] == "cerrada"
        assert data["fecha_cierre"] is not None

    def test_crear_brecha_sin_estado_cierre(self, client, auth_headers, empresa, clean_task_queue):
        """Caso negativo: Brecha sin estado_cierre ni fecha_cierre (NULL)."""
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin estado de cierre",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data.get("estado_cierre") is None
        assert data.get("fecha_cierre") is None


class TestBreachTodosLosCamposJuntos:
    """Tests combinando los 6 campos nuevos."""

    def test_crear_brecha_todos_los_campos(self, client, auth_headers, empresa, clean_task_queue):
        """Caso afirmativo: Brecha con los 6 campos nuevos."""
        ahora = datetime.now(timezone.utc)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha completa con todos los campos",
            "fecha_deteccion": ahora.isoformat(),
            "fecha_ocurrencia_estimada": (ahora - timedelta(hours=5)).isoformat(),
            "efectos_probables": "Robo de datos personales de clientes",
            "causa_raiz": "error_humano",
            "evidencia_notificacion_apdc_folio": "APDC-2026-005678",
            "estado_cierre": "notificada",
            "nivel_riesgo": "alto",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["fecha_ocurrencia_estimada"] is not None
        assert "Robo de datos" in data["efectos_probables"]
        assert data["causa_raiz"] == "error_humano"
        assert data["evidencia_notificacion_apdc_folio"] == "APDC-2026-005678"
        assert data["estado_cierre"] == "notificada"
