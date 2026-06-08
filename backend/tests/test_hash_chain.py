"""
Tests P0: Hash Chain — Verificación de integridad de auditoría.
Custodio RAT Manager — Ley 21.719 Art. 12 (Principio de responsabilidad proactiva).

Covers:
- verify_audit_chain() — integrity check
- Hash chain no se rompe con operaciones normales
- Tampering detection (prev_hash mismatch)
- Tampering detection (hash mismatch)
- Genesis record (first record)
- Endpoint /rats/{id}/audit integration
"""

import pytest
from app.models.audit_log import AuditLog, GENESIS_HASH
from app.services.audit_service import log_audit, verify_audit_chain, _compute_hash


class TestHashChainGenesis:
    def test_genesis_hash_es_64_ceros(self):
        """GENESIS_HASH debe ser 64 caracteres '0'."""
        assert GENESIS_HASH == "0" * 64
        assert len(GENESIS_HASH) == 64

    def test_primer_registro_tiene_genesis_como_prev_hash(self, db, admin_user):
        """El primer registro de auditoría debe tener prev_hash = GENESIS_HASH."""
        log_audit(db, "rat", 1, "crear", "admin", {"nombre": "Test"})
        db.commit()

        first = db.query(AuditLog).order_by(AuditLog.id.asc()).first()
        assert first is not None
        assert first.prev_hash == GENESIS_HASH

    def test_primer_registro_tiene_hash_valido(self, db, admin_user):
        """El hash del primer registro debe ser computable y no vacío."""
        log_audit(db, "rat", 1, "crear", "admin", {"nombre": "Test"})
        db.commit()

        first = db.query(AuditLog).order_by(AuditLog.id.asc()).first()
        assert first is not None
        assert len(first.hash) == 64
        assert first.hash != GENESIS_HASH
        assert all(c in '0123456789abcdef' for c in first.hash)


class TestHashChainVerification:
    def test_verify_audit_chain_sin_registros_retorna_true(self, db, admin_user):
        """Si no hay registros, verify debe retornar válido."""
        result = verify_audit_chain(db)
        assert result["valid"] is True
        assert result["total_records"] == 0
        assert result["broken_at"] is None

    def test_verify_audit_chain_con_registros_intactos_retorna_true(self, db, admin_user):
        """Con registros sin tampering, verify debe retornar válido."""
        for i in range(3):
            log_audit(db, "rat", i + 1, "crear", "admin", {"nombre": f"RAT-{i}"})
            db.commit()

        all_logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
        assert len(all_logs) == 3, f"Expected 3 records, found {len(all_logs)}: {[l.id for l in all_logs]}"

        result = verify_audit_chain(db)
        assert result["valid"] is True, f"Chain invalid: {result}"
        assert result["total_records"] == 3
        assert result["broken_at"] is None

    def test_verify_audit_chain_detecta_prev_hash_invalido(self, db, admin_user):
        """Si se modifica prev_hash de un registro, verify debe detectarlo."""
        log_audit(db, "rat", 1, "crear", "admin", {"nombre": "Test"})
        db.commit()

        record = db.query(AuditLog).first()
        record.prev_hash = "X" * 64
        db.commit()

        result = verify_audit_chain(db)
        assert result["valid"] is False
        assert result["broken_at"] == record.id

    def test_verify_audit_chain_detecta_hash_corrupto(self, db, admin_user):
        """Si se modifica el detalle de un registro, el hash ya no calza y verify lo detecta."""
        log_audit(db, "rat", 1, "crear", "admin", {"nombre": "Test"})
        db.commit()

        record = db.query(AuditLog).first()
        record.detalle = '{"nombre": "MANIPULADO"}'
        db.commit()

        result = verify_audit_chain(db)
        assert result["valid"] is False
        assert result["broken_at"] == record.id

    def test_verify_audit_chain_con_limite_solo_verifica_esa_cantidad(self, db, admin_user):
        """verify_audit_chain(limit=N) solo verifica los primeros N registros."""
        for i in range(5):
            log_audit(db, "rat", i + 1, "crear", "admin", {"nombre": f"RAT-{i}"})
            db.commit()

        result = verify_audit_chain(db, limit=3)
        assert result["valid"] is True
        assert result["total_records"] == 3

    def test_verificacion_sin_tampering_segundo_registro(self, db, admin_user):
        """Verificar que el segundo registro tiene prev_hash = hash del primero."""
        log_audit(db, "rat", 1, "crear", "admin", {"nombre": "RAT-1"})
        db.commit()
        first = db.query(AuditLog).order_by(AuditLog.id.asc()).first()

        log_audit(db, "rat", 2, "crear", "admin", {"nombre": "RAT-2"})
        db.commit()
        second = db.query(AuditLog).order_by(AuditLog.id.desc()).first()

        assert second.prev_hash == first.hash
        assert second.prev_hash != GENESIS_HASH


class TestHashChainEndpoint:
    def test_audit_de_rat_retorna_registros(self, client, auth_headers, empresa, rat_base):
        """GET /rats/{id}/auditoria debe retornar los registros de auditoría."""
        rat_resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert rat_resp.status_code == 201
        rat_id = rat_resp.json()["id"]

        audit_resp = client.get(f"/rats/{rat_id}/auditoria", headers=auth_headers)
        assert audit_resp.status_code == 200
        assert isinstance(audit_resp.json(), list)

    def test_audit_de_rat_sin_auth_falla(self, client, empresa, rat_base):
        """GET /rats/{id}/auditoria sin autenticación debe retornar 401."""
        rat_resp = client.post("/rats/", json=rat_base, headers={"Authorization": "Bearer invalid"})
        if rat_resp.status_code == 201:
            rat_id = rat_resp.json()["id"]
            audit_resp = client.get(f"/rats/{rat_id}/auditoria")
            assert audit_resp.status_code == 401


class TestComputeHash:
    def test_compute_hash_deterministic(self):
        """_compute_hash debe ser determinístico: misma entrada = misma salida."""
        from datetime import datetime, timezone
        ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        h1 = _compute_hash(GENESIS_HASH, ts, "crear", "rat", 1, "admin", '{"nombre": "Test"}')
        h2 = _compute_hash(GENESIS_HASH, ts, "crear", "rat", 1, "admin", '{"nombre": "Test"}')
        assert h1 == h2
        assert len(h1) == 64

    def test_compute_hash_diferente_con_datos_distintos(self):
        """Datos distintos deben producir hashes distintos."""
        from datetime import datetime, timezone
        ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        h1 = _compute_hash(GENESIS_HASH, ts, "crear", "rat", 1, "admin", '{"nombre": "A"}')
        h2 = _compute_hash(GENESIS_HASH, ts, "crear", "rat", 1, "admin", '{"nombre": "B"}')
        assert h1 != h2

    def test_compute_hash_diferente_con_timestamp_distinto(self):
        """Timestamps distintos deben producir hashes distintos."""
        from datetime import datetime, timezone
        ts1 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2026, 1, 1, 12, 0, 1, tzinfo=timezone.utc)
        h1 = _compute_hash(GENESIS_HASH, ts1, "crear", "rat", 1, "admin", '{"nombre": "Test"}')
        h2 = _compute_hash(GENESIS_HASH, ts2, "crear", "rat", 1, "admin", '{"nombre": "Test"}')
        assert h1 != h2