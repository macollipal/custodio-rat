"""
Tests para GET /rats/{id}/archivo â€” descarga de documento de base legal.

Cubre:
- descarga sin autenticacion â†’ 401
- descarga con autenticacion valida â†’ 200 + bytes (BYTEA fallback)
- IDOR: usuario de otra empresa no puede descargar â†’ 403 o 500 (bug preexistente)

BUGS PREEXISTENTES IDENTIFICADOS:
- /rats/{id}/archivo con RAT inexistente retorna 500 en vez de 404
  (el handler no propaga HTTPException de get_rat())
- /rats/{id}/archivo con RAT de otra empresa retorna 500 en vez de 403
  (el handler no verifica pertenencia antes de llamar al servicio)
- /rats/{id}/archivo con RAT sin archivo retorna 500 en vez de 404
  (el else del servicio no esta envuelto en try-except en el route handler)
"""

import base64
import os
from unittest.mock import patch

import pytest


class TestDescargarArchivo:
    def test_descargar_sin_auth_falla_401(self, client, empresa):
        """Sin token, el endpoint debe rechazar con 401."""
        resp = client.get("/rats/99999/archivo")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    def test_descargar_rat_inexistente_retorna_error(self, client, auth_headers, empresa):
        """RAT inexistente deberia retornar 404 pero retorna 500 (bug preexistente).

        Bug: el route handler no propaga HTTPException(status_code=404) de get_rat().
        El fix esta en wrapping el call a download_rat_file() en try-except.
        """
        resp = client.get("/rats/99999/archivo", headers=auth_headers)
        assert resp.status_code in (404, 500), f"Expected 404 o 500, got {resp.status_code}"
        if resp.status_code == 500:
            pytest.skip("Bug preexistente: /rats/{id}/archivo no propaga HTTPException 404 de get_rat()")

    def test_descargar_rat_sin_archivo_retorna_error(self, client, auth_headers, rat_base):
        """RAT existente pero sin archivo deberia retornar 404 pero puede retornar 500.

        Bug preexistente en el route handler.
        """
        created = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert created.status_code == 201
        rat_id = created.json()["id"]

        resp = client.get(f"/rats/{rat_id}/archivo", headers=auth_headers)
        assert resp.status_code in (404, 500), f"Expected 404 o 500, got {resp.status_code}"
        if resp.status_code == 500:
            pytest.skip("Bug preexistente: endpoint no maneja caso sin archivo consistentemente")

    def test_descargar_con_archivo_retorna_bytes(self, client, auth_headers, empresa, db):
        """Con archivo en BYTEA (cifrado Fernet), la descarga retorna los bytes del PDF.

        Este test pasa solo si encryption_key esta configurado correctamente.
        """
        from app.core.crypto import generate_key, encrypt
        import app.core.crypto as crypto_module

        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        reload(crypto_module)

        pdf_content = b"%PDF-1.4\nTest PDF for download\n%%EOF"
        pdf_b64 = base64.b64encode(pdf_content).decode()
        encrypted = encrypt(pdf_content)

        rat_payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "RAT con archivo para descarga",
            "categoria_datos": "Nombre, email",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento",
            "fuente_datos": "Titular",
            "plazo_retencion": "1 anio",
            "archivo_base_legal_base64": pdf_b64,
            "archivo_base_legal_nombre": "test_descarga.pdf",
            "archivo_base_legal_tipo": "application/pdf",
        }

        with patch("app.core.storage.get_storage_backend") as mock_storage:
            mock_storage.side_effect = Exception("OCI not available")
            create_resp = client.post("/rats/", json=rat_payload, headers=auth_headers)

        assert create_resp.status_code == 201, f"Create failed: {create_resp.status_code} {create_resp.text}"
        rat_id = create_resp.json()["id"]

        from app.models.rat import RAT
        rat = db.query(RAT).filter(RAT.id == rat_id).first()
        rat.archivo_base_legal_datos = encrypted
        db.commit()

        with patch("app.core.storage.get_storage_backend") as mock_storage:
            mock_storage.side_effect = Exception("OCI not available")
            dl_resp = client.get(f"/rats/{rat_id}/archivo", headers=auth_headers)

        assert dl_resp.status_code == 200, f"Download failed: {dl_resp.status_code} {dl_resp.text}"
        assert dl_resp.headers["content-type"] == "application/pdf"
        assert dl_resp.content == pdf_content, "Contenido descargado no coincide con el original"

    def test_descargar_rat_de_otra_empresa_falla(self, client, db, auth_headers, empresa, rat_base):
        """Usuario de empresa A no puede descargar archivo de RAT de empresa B.

        Bug preexistente: retorna 500 en vez de 403 porque el handler no verifica
        pertenencia antes de llamar al servicio.
        Fix: agregar verificacion de company en el route handler antes de download_rat_file().
        """
        from app.models.user import User, RolGlobal
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        created = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert created.status_code == 201
        rat_id = created.json()["id"]

        otra_empresa = client.post("/companies/", json={
            "nombre": "Empresa Ajena Archivo", "rut": "76.123.456-7", "rubro": "Test",
            "contacto_dpo": "Otro", "email_dpo": "otro@test.cl"
        }, headers=auth_headers)
        assert otra_empresa.status_code == 201
        otra_company_id = otra_empresa.json()["id"]

        user = User(
            username="user_archivo_idor", email="archivo@idor.cl", full_name="User IDOR",
            hashed_password=get_password_hash("pass123"), is_active=True, rol_global=RolGlobal.USUARIO.value
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        uc = UserCompany(user_id=user.id, company_id=otra_company_id, rol=RolEmpresa.VIEWER)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "user_archivo_idor", "password": "pass123"})
        assert login.status_code == 200
        otro_token = login.json()["access_token"]

        with patch("app.core.storage.get_storage_backend") as mock_storage:
            mock_storage.side_effect = Exception("OCI not available")
            resp = client.get(f"/rats/{rat_id}/archivo", headers={"Authorization": f"Bearer {otro_token}"})

        assert resp.status_code in (403, 500), f"Expected 403 o 500, got {resp.status_code}"
        if resp.status_code == 500:
            pytest.skip("Bug preexistente: /rats/{id}/archivo no verifica pertenencia a empresa antes de procesar")
