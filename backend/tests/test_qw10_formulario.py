"""
Tests para QW10: Mejorar Formulario PÃºblico
- Campos representante_nombre y representante_rut
- Upload de archivos adjuntos
- Respuesta incluye tracking_token

Estrategia de envÃ­o:
- Sin archivos: json={} (Pydantic validation)
- Con archivos: data={} con JSON serializado como string en campo "data"
  (esto reproduce cÃ³mo el browser envÃ­a multipart/form-data cuando hay files + campos)
"""

import json
import pytest
from fastapi.testclient import TestClient


class TestQW10Representante:
    def test_crear_solicitud_con_representante(self, client, empresa):
        """El formulario pÃºblico acepta representante_nombre y representante_rut."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "nombre_titular": "Juan PÃ©rez",
            "rut_titular": "12.345.678-5",
            "email_titular": "juan@perez.cl",
            "descripcion": "Quiero acceder a mis datos",
            "token": token,
            "representante_nombre": "MarÃ­a LÃ³pez",
            "representante_rut": "98.765.432-1",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["representante_nombre"] == "MarÃ­a LÃ³pez"
        assert data["representante_rut"] == "98.765.432-1"
        assert "tracking_token" in data
        assert data["tracking_token"] is not None

    def test_crear_solicitud_sin_representante(self, client, empresa):
        """El formulario funciona sin campos de representante (compatibilidad)."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "rectificacion",
            "nombre_titular": "Carlos MÃ©ndez",
            "email_titular": "carlos@mendez.cl",
            "descripcion": "Quiero corregir mis datos",
            "token": token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["representante_nombre"] is None
        assert data["representante_rut"] is None
        assert "tracking_token" in data

    def test_crear_solicitud_solo_representante_nombre(self, client, empresa):
        """Se puede enviar solo representante_nombre sin rut."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "cancelacion",
            "nombre_titular": "Pedro Ruiz",
            "email_titular": "pedro@ruiz.cl",
            "token": token,
            "representante_nombre": "Ana Torres",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["representante_nombre"] == "Ana Torres"
        assert data["representante_rut"] is None

    def test_representante_rut_sin_nombre_se_guarda(self, client, empresa):
        """representante_rut sin nombre se guarda igualmente (el frontend valida que nombre vaya primero)."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "nombre_titular": "Pedro Ruiz",
            "email_titular": "pedro@ruiz.cl",
            "token": token,
            "representante_rut": "11.111.111-1",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("representante_rut") == "11.111.111-1"


class TestQW10Archivos:
    def test_crear_solicitud_con_archivo_pdf(self, client, empresa):
        """El formulario acepta archivos PDF como adjuntos."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post(
            "/solicitudes-derecho/",
            data={
                "company_id": str(empresa["id"]),
                "tipo": "acceso",
                "nombre_titular": "Test File",
                "email_titular": "test@file.cl",
                "token": token,
            },
            files={"files": ("carta.pdf", b"%PDF-1.4 test content", "application/pdf")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tracking_token" in data

    def test_crear_solicitud_con_imagen_jpeg(self, client, empresa):
        """El formulario acepta imÃ¡genes JPEG como adjuntos."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post(
            "/solicitudes-derecho/",
            data={
                "company_id": str(empresa["id"]),
                "tipo": "acceso",
                "nombre_titular": "Test Image",
                "email_titular": "test@image.cl",
                "token": token,
            },
            files={"files": ("cedula.jpg", b"\xff\xd8\xff\xe0 test jpeg", "image/jpeg")},
        )
        assert resp.status_code == 200

    def test_archivo_tipo_no_permitido_rechazado(self, client, empresa):
        """Archivos con tipo no permitido (ej: .exe) son rechazados."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post(
            "/solicitudes-derecho/",
            data={
                "company_id": str(empresa["id"]),
                "tipo": "acceso",
                "nombre_titular": "Test Bad File",
                "email_titular": "test@badfile.cl",
                "token": token,
            },
            files={"files": ("virus.exe", b"MZ test", "application/x-msdownload")},
        )
        assert resp.status_code == 400
        assert "tipo no permitido" in resp.json()["detail"]

    def test_multiple_archivos(self, client, empresa):
        """Se pueden adjuntar mÃºltiples archivos hasta 5."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post(
            "/solicitudes-derecho/",
            data={
                "company_id": str(empresa["id"]),
                "tipo": "acceso",
                "nombre_titular": "Test Multi",
                "email_titular": "test@multi.cl",
                "token": token,
            },
            files=[
                ("files", ("a.pdf", b"content a", "application/pdf")),
                ("files", ("b.jpg", b"content b", "image/jpeg")),
            ],
        )
        assert resp.status_code == 200

    def test_representante_y_archivos_juntos(self, client, empresa):
        """Se pueden enviar representante y archivos en la misma solicitud."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post(
            "/solicitudes-derecho/",
            data={
                "company_id": str(empresa["id"]),
                "tipo": "rectificacion",
                "nombre_titular": "Titular Final",
                "email_titular": "titular@final.cl",
                "token": token,
                "representante_nombre": "Rep Legal",
                "representante_rut": "77.777.777-7",
            },
            files={"files": ("poder.pdf", b"%PDF-1.4 poder", "application/pdf")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["representante_nombre"] == "Rep Legal"
        assert data["representante_rut"] == "77.777.777-7"


class TestQW10TrackingToken:
    def test_respuesta_incluye_tracking_token(self, client, empresa):
        """La respuesta del POST incluye tracking_token para seguimiento."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "nombre_titular": "Track Me",
            "email_titular": "track@me.cl",
            "token": token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "tracking_token" in data
        assert data["tracking_token"] is not None
        assert len(data["tracking_token"]) == 36

    def test_tracking_token_es_uuid_unico(self, client, empresa):
        """Cada solicitud recibe un tracking_token Ãºnico."""
        token_resp = client.get("/solicitudes-derecho/token")
        assert token_resp.status_code == 200
        token = token_resp.json()["token"]

        resp1 = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "acceso",
            "nombre_titular": "Uno",
            "email_titular": "uno@track.cl",
            "token": token,
        })
        assert resp1.status_code == 200
        tk1 = resp1.json()["tracking_token"]

        token_resp2 = client.get("/solicitudes-derecho/token")
        token2 = token_resp2.json()["token"]

        resp2 = client.post("/solicitudes-derecho/", json={
            "company_id": empresa["id"],
            "tipo": "rectificacion",
            "nombre_titular": "Dos",
            "email_titular": "dos@track.cl",
            "token": token2,
        })
        assert resp2.status_code == 200
        tk2 = resp2.json()["tracking_token"]

        assert tk1 != tk2
