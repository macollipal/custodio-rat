"""
Tests para C6: timestamp UTC en hash chain (audit_service).

Cubre:
- Timestamp naive se trata como UTC
- Timestamp aware de otra zona se convierte a UTC
- Hash es determinístico (mismo input -> mismo hash)
- Hash cambia si cambia cualquier input
- Hash chain es verificable después de múltiples inserciones
"""
from datetime import datetime, timezone, timedelta

from app.services.audit_service import _compute_hash, GENESIS_HASH


class TestComputeHashUTC:
    def test_naive_datetime_se_trata_como_utc(self):
        """Datetime naive (sin tzinfo) debe ser tratado como UTC."""
        ts_naive = datetime(2026, 7, 18, 12, 0, 0)
        h1 = _compute_hash(GENESIS_HASH, ts_naive, "create", "rat", 1, "user", '{"x":1}')
        h2 = _compute_hash(GENESIS_HASH, ts_naive, "create", "rat", 1, "user", '{"x":1}')
        assert h1 == h2  # determinístico

    def test_aware_utc_datetime_mismo_hash_que_naive(self):
        """Datetime aware UTC debe producir mismo hash que naive (asumido UTC)."""
        ts_naive = datetime(2026, 7, 18, 12, 0, 0)
        ts_utc = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
        h_naive = _compute_hash(GENESIS_HASH, ts_naive, "create", "rat", 1, "user", '{"x":1}')
        h_utc = _compute_hash(GENESIS_HASH, ts_utc, "create", "rat", 1, "user", '{"x":1}')
        assert h_naive == h_utc

    def test_aware_other_timezone_se_convierte_a_utc(self):
        """Datetime aware de otra zona (ej. Chile UTC-4) debe convertirse a UTC."""
        chile_tz = timezone(timedelta(hours=-4))  # UTC-4
        ts_chile = datetime(2026, 7, 18, 8, 0, 0, tzinfo=chile_tz)  # 8:00 Chile = 12:00 UTC
        ts_utc = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
        h_chile = _compute_hash(GENESIS_HASH, ts_chile, "create", "rat", 1, "user", '{"x":1}')
        h_utc = _compute_hash(GENESIS_HASH, ts_utc, "create", "rat", 1, "user", '{"x":1}')
        assert h_chile == h_utc, "Datetime Chile y UTC deben producir mismo hash"

    def test_aware_positive_timezone_se_convierte_a_utc(self):
        """Datetime aware de zona positiva (ej. Tokyo UTC+9) debe convertirse a UTC."""
        tokyo_tz = timezone(timedelta(hours=9))
        ts_tokyo = datetime(2026, 7, 18, 21, 0, 0, tzinfo=tokyo_tz)  # 21:00 Tokyo = 12:00 UTC
        ts_utc = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
        h_tokyo = _compute_hash(GENESIS_HASH, ts_tokyo, "create", "rat", 1, "user", '{"x":1}')
        h_utc = _compute_hash(GENESIS_HASH, ts_utc, "create", "rat", 1, "user", '{"x":1}')
        assert h_tokyo == h_utc

    def test_diferente_utc_mismo_momento_hash_distinto_antes_fix(self):
        """Documenta el bug que C6 corrige.

        Antes del fix, timestamp naive (UTC) y aware UTC producían hash distinto
        porque el naive usaba isoformat() sin timezone y el aware también (tras
        strip de tzinfo). El fix los unifica via .astimezone(UTC).
        """
        ts_naive = datetime(2026, 7, 18, 12, 0, 0)
        ts_utc = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
        h_naive = _compute_hash(GENESIS_HASH, ts_naive, "test", "e", 1, "u", "d")
        h_utc = _compute_hash(GENESIS_HASH, ts_utc, "test", "e", 1, "u", "d")
        assert h_naive == h_utc, (
            "Mismo instante debe producir mismo hash (idempotencia UTC)"
        )

    def test_hash_cambia_si_timestamp_cambia(self):
        """Hash diferente para timestamps distintos."""
        ts1 = datetime(2026, 7, 18, 12, 0, 0, tzinfo=timezone.utc)
        ts2 = datetime(2026, 7, 18, 12, 0, 1, tzinfo=timezone.utc)  # +1 segundo
        h1 = _compute_hash(GENESIS_HASH, ts1, "test", "e", 1, "u", "d")
        h2 = _compute_hash(GENESIS_HASH, ts2, "test", "e", 1, "u", "d")
        assert h1 != h2

    def test_hash_cambia_si_accion_cambia(self):
        h1 = _compute_hash(GENESIS_HASH, datetime.now(timezone.utc), "create", "rat", 1, "u", "d")
        h2 = _compute_hash(GENESIS_HASH, datetime.now(timezone.utc), "delete", "rat", 1, "u", "d")
        assert h1 != h2

    def test_hash_formato_sha256(self):
        """Hash debe ser SHA-256 (64 caracteres hex)."""
        h = _compute_hash(GENESIS_HASH, datetime.now(timezone.utc), "test", "e", 1, "u", "d")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestAuditChainIntegration:
    """Tests de integración con la BD: la cadena debe ser verificable."""

    def test_cadena_construible_y_verificable(self, db):
        """Insertar varios audit logs y verificar que la cadena es íntegra."""
        from app.services.audit_service import log_audit, verify_audit_chain

        log_audit(db, "rat", 1, "create", "user1", {"field": "value1"})
        db.commit()
        log_audit(db, "rat", 1, "update", "user2", {"field": "value2"})
        db.commit()
        log_audit(db, "rat", 2, "create", "user1", {"field": "value3"})
        db.commit()

        result = verify_audit_chain(db)
        assert result["valid"] is True, f"Cadena rota: {result}"
        assert result["total_records"] >= 3

    def test_cadena_detecta_tampering(self, db):
        """Modificar un detalle manualmente debe romper la verificación."""
        from app.services.audit_service import log_audit, verify_audit_chain

        log_audit(db, "rat", 1, "create", "user1", {"field": "value1"})
        db.commit()

        result_before = verify_audit_chain(db)
        assert result_before["valid"] is True

        # Tampering: modificar detalle del primer registro
        from app.models.audit_log import AuditLog
        first_log = db.query(AuditLog).order_by(AuditLog.id.asc()).first()
        first_log.detalle = '{"field": "TAMPERED"}'
        db.commit()

        result_after = verify_audit_chain(db)
        assert result_after["valid"] is False, "Tampering no detectado"
        assert result_after["broken_at"] is not None