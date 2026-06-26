"""
Tests para cifrado PII en consentimientos (Art. 12, 16 Ley 21.719 + Art. 11 medidas seguridad).

Verifica que:
- nombre_titular_cipher y email_titular_cipher se almacenan cifrados con Fernet
- texto_consentimiento_hash es SHA-256 del texto original
- ip_origen_masked es /16 mask
"""
import hashlib
import pytest
from datetime import datetime, timezone

from app.core.crypto import decrypt
from app.models.consentimiento import Consentimiento


def _crear_rat(client, auth_headers, rat_base):
    resp = client.post("/rats/", json=rat_base, headers=auth_headers)
    assert resp.status_code == 201, f"Error creando RAT: {resp.text}"
    return resp.json()["id"]


class TestConsentimientoPiiCifrado:
    """Tests de integracion que verifican cifrado real en BD."""

    def test_nombre_titular_se_cifra_en_bd(self, client, auth_headers, rat_base, db):
        rat_id = _crear_rat(client, auth_headers, rat_base)
        nombre_original = "Juan Perez Gonzalez"

        payload = {
            "rat_id": rat_id,
            "nombre_titular": nombre_original,
            "email_titular": "juan@test.cl",
            "canal": "web",
            "texto_consentimiento": "Yo otorgo mi consentimiento para el tratamiento.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=payload, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"
        consent_id = resp.json()["id"]

        consent = db.query(Consentimiento).filter(Consentimiento.id == consent_id).first()
        assert consent is not None
        assert consent.nombre_titular_cipher is not None
        assert consent.nombre_titular_cipher != nombre_original.encode()
        assert decrypt(consent.nombre_titular_cipher).decode("utf-8") == nombre_original

    def test_email_titular_se_cifra_en_bd(self, client, auth_headers, rat_base, db):
        rat_id = _crear_rat(client, auth_headers, rat_base)
        email_original = "maria.gonzalez@empresa.cl"

        payload = {
            "rat_id": rat_id,
            "nombre_titular": "Maria",
            "email_titular": email_original,
            "canal": "web",
            "texto_consentimiento": "Consentimiento test.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        consent_id = resp.json()["id"]

        consent = db.query(Consentimiento).filter(Consentimiento.id == consent_id).first()
        assert consent.email_titular_cipher is not None
        assert consent.email_titular_cipher != email_original.encode()
        assert decrypt(consent.email_titular_cipher).decode("utf-8") == email_original

    def test_texto_consentimiento_hash_sha256(self, client, auth_headers, rat_base, db):
        rat_id = _crear_rat(client, auth_headers, rat_base)
        texto = "Texto legal de consentimiento para Art. 12 Ley 21.719."

        payload = {
            "rat_id": rat_id,
            "nombre_titular": "Test",
            "canal": "web",
            "texto_consentimiento": texto,
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        consent_id = resp.json()["id"]

        consent = db.query(Consentimiento).filter(Consentimiento.id == consent_id).first()
        assert consent.texto_consentimiento_hash is not None
        hash_esperado = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        assert consent.texto_consentimiento_hash == hash_esperado
        assert len(consent.texto_consentimiento_hash) == 64

    def test_ip_origen_se_mascara_16(self, client, auth_headers, rat_base, db):
        rat_id = _crear_rat(client, auth_headers, rat_base)

        payload = {
            "rat_id": rat_id,
            "nombre_titular": "Test IP",
            "canal": "web",
            "texto_consentimiento": "Test IP.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
            "ip_origen": "192.168.1.100",
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        consent_id = resp.json()["id"]

        consent = db.query(Consentimiento).filter(Consentimiento.id == consent_id).first()
        assert consent.ip_origen_masked == "192.168.***.***"

    def test_ip_origen_invalida_no_se_mascara(self, client, auth_headers, rat_base, db):
        """Si ip_origen no es valida, _mask_ip retorna el string tal cual."""
        rat_id = _crear_rat(client, auth_headers, rat_base)

        payload = {
            "rat_id": rat_id,
            "nombre_titular": "Test",
            "canal": "web",
            "texto_consentimiento": "Test.",
            "fecha_obtencion": datetime.now(timezone.utc).isoformat(),
            "ip_origen": "not-an-ip",
        }
        resp = client.post(f"/rats/{rat_id}/consentimientos", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        consent_id = resp.json()["id"]

        consent = db.query(Consentimiento).filter(Consentimiento.id == consent_id).first()
        assert consent.ip_origen_masked == "not-an-ip"

    def test_ip_origen_none_no_almacena_mask(self, client, auth_headers, rat_base, db):
        """Si ip_origen es None al crear via service directo, _mask_ip retorna None."""
        from app.schemas.consentimiento import ConsentimientoCreate
        from app.services.consentimiento_service import crear_consentimiento
        from app.models.rat import RAT as RATModel

        rat_id = _crear_rat(client, auth_headers, rat_base)

        data = ConsentimientoCreate(
            rat_id=rat_id,
            nombre_titular="Test",
            email_titular=None,
            canal="verbal",
            texto_consentimiento="Sin IP.",
            fecha_obtencion=datetime.now(timezone.utc),
            ip_origen=None,
        )
        c = crear_consentimiento(db=db, data=data, usuario="admin")
        consent = db.query(Consentimiento).filter(Consentimiento.id == c.id).first()
        assert consent.ip_origen_masked is None