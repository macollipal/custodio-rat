"""
Tests para app.core.crypto — cifrado simétrico Fernet de datos en reposo.
Cumple Ley 21.719 Art. 16.
"""

import base64
import os
import pytest


class TestFernetCrypto:
    def test_encrypt_decrypt_round_trip(self):
        """Datos cifrados y descifrados deben ser idénticos al original."""
        from app.core.crypto import encrypt, decrypt, generate_key
        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        import app.core.crypto
        reload(app.core.crypto)

        original = b"Contenido confidencial del PDF del RAT"
        cifrado = app.core.crypto.encrypt(original)
        descifrado = app.core.crypto.decrypt(cifrado)

        assert descifrado == original
        assert cifrado != original

    def test_encrypt_produces_different_output(self):
        """El mismo contenido cifrado dos veces debe producir outputs distintos (salts diferentes)."""
        from app.core.crypto import encrypt, decrypt, generate_key
        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        import app.core.crypto
        reload(app.core.crypto)

        data = b"Test data"
        enc1 = app.core.crypto.encrypt(data)
        enc2 = app.core.crypto.encrypt(data)

        assert enc1 != enc2
        assert app.core.crypto.decrypt(enc1) == data
        assert app.core.crypto.decrypt(enc2) == data

    def test_encrypt_empty_data(self):
        """Datos vacíos deben retornar sin cambios."""
        from app.core.crypto import encrypt, decrypt
        assert encrypt(b"") == b""
        assert decrypt(b"") == b""

    def test_generate_key_produces_valid_fernet_key(self):
        """La clave generada debe ser válida para Fernet."""
        from cryptography.fernet import Fernet
        from app.core.crypto import generate_key
        key = generate_key()
        fernet = Fernet(key.encode())
        data = b"test"
        enc = fernet.encrypt(data)
        dec = fernet.decrypt(enc)
        assert dec == data

    def test_decrypt_with_wrong_key_fails_safely(self):
        """Descifrar con key equivocada debe retornar datos cifrados sin modificar (fail safe, no crash)."""
        from app.core.crypto import encrypt, decrypt, generate_key
        key1 = generate_key()
        key2 = generate_key()
        os.environ["encryption_key"] = key1
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        import app.core.crypto
        reload(app.core.crypto)

        data = b"secret data"
        enc = app.core.crypto.encrypt(data)

        os.environ["encryption_key"] = key2
        reload(app.core.config)
        reload(app.core.crypto)

        result = app.core.crypto.decrypt(enc)
        assert result == enc

    def test_encrypt_decrypt_pdf_bytes(self):
        """PDF binario real debe cifrarse y descifrarse correctamente."""
        from app.core.crypto import encrypt, decrypt, generate_key
        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        import app.core.config
        reload(app.core.config)
        import app.core.crypto
        reload(app.core.crypto)

        pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
        cifrado = app.core.crypto.encrypt(pdf_bytes)
        descifrado = app.core.crypto.decrypt(cifrado)

        assert descifrado == pdf_bytes
        assert cifrado != pdf_bytes


class TestEncryptIntegrationWithBYTEA:
    def test_rat_file_procesar_archivo_base_legal_with_encryption(self, client, auth_headers, empresa, db):
        """Al subir archivo RAT (BYTEA fallback), los datos deben estar cifrados en BD."""
        from app.core.crypto import encrypt, generate_key
        from app.core.config import settings
        import app.core.crypto

        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        reload(app.core.config)
        reload(app.core.crypto)

        pdf_content = b"%PDF-1.4 mock pdf content for encryption test"
        pdf_b64 = base64.b64encode(pdf_content).decode()

        rat_payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "Test RAT with encrypted file",
            "categoria_datos": "Nombre, email",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento",
            "fuente_datos": "Titular",
            "plazo_retencion": "1 año",
            "archivo_base_legal_base64": pdf_b64,
            "archivo_base_legal_nombre": "test.pdf",
            "archivo_base_legal_tipo": "application/pdf",
        }

        resp = client.post("/rats/", json=rat_payload, headers=auth_headers)
        assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
        rat_id = resp.json()["id"]

        from app.models.rat import RAT
        rat = db.query(RAT).filter(RAT.id == rat_id).first()
        assert rat is not None
        assert rat.archivo_base_legal_datos is not None

        descifrado = app.core.crypto.decrypt(rat.archivo_base_legal_datos)
        assert descifrado == pdf_content

    def test_download_rat_file_returns_decrypted_content(self, client, auth_headers, empresa):
        """Al descargar archivo RAT (BYTEA), el contenido debe estar descifrado."""
        from app.core.crypto import encrypt, generate_key
        import app.core.crypto

        key = generate_key()
        os.environ["encryption_key"] = key
        from importlib import reload
        reload(app.core.config)
        reload(app.core.crypto)

        pdf_content = b"%PDF-1.4 download decryption test"
        pdf_b64 = base64.b64encode(pdf_content).decode()

        rat_payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "Test RAT download decrypt",
            "categoria_datos": "Nombre, email",
            "categoria_titulares": "Clientes",
            "finalidad": "Test",
            "base_legal": "Consentimiento",
            "fuente_datos": "Titular",
            "plazo_retencion": "1 año",
            "archivo_base_legal_base64": pdf_b64,
            "archivo_base_legal_nombre": "download_test.pdf",
            "archivo_base_legal_tipo": "application/pdf",
        }

        resp = client.post("/rats/", json=rat_payload, headers=auth_headers)
        assert resp.status_code == 201
        rat_id = resp.json()["id"]

        download_resp = client.get(f"/rats/{rat_id}/archivo", headers=auth_headers)
        assert download_resp.status_code == 200
        data = download_resp.json()
        assert data["type"] == "bytes"
        downloaded_content = base64.b64decode(data["content"])
        assert downloaded_content == pdf_content


class TestSettings:
    def test_encryption_key_mandatory_in_production(self):
        """En ENVIRONMENT=production sin ENCRYPTION_KEY debe lanzar ValueError."""
        os.environ["environment"] = "production"
        os.environ["encryption_key"] = ""
        from importlib import reload
        import app.core.config
        reload(app.core.config)

        with pytest.raises(ValueError, match="ENCRYPTION_KEY"):
            _ = app.core.config.settings.resolved_encryption_key

    def test_encryption_key_optional_in_development(self):
        """En ENVIRONMENT=development sin ENCRYPTION_KEY debe usar dev fallback (sin crash)."""
        os.environ["environment"] = "development"
        os.environ["encryption_key"] = ""
        from importlib import reload
        import app.core.config
        reload(app.core.config)

        key = app.core.config.settings.resolved_encryption_key
        assert key is not None

    def test_encryption_key_used_in_development_when_set(self):
        """En ENVIRONMENT=development con ENCRYPTION_KEY configurada, debe usarla."""
        key = "TestKey12345678901234567890123456789012=="
        os.environ["environment"] = "development"
        os.environ["encryption_key"] = key
        from importlib import reload
        import app.core.config
        reload(app.core.config)

        assert app.core.config.settings.resolved_encryption_key == key