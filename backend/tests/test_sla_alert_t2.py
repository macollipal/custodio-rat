"""
Tests para QW5 SLA alert T-2 días (Art. 14 Ley 21.719).

Cubre:
- ARCO tickets próximos a vencer (T-2 días hábiles)
- ARCO tickets ya vencidos
- RATs próximos a cumplir 180 días desde último update
- RATs ya vencidos (>180 días)
- Agrupación por empresa + email al DPO
- No notifica si no hay deadlines próximos
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.models.company import Company
from app.models.rat import RAT
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.services.task_service import _run_sla_alert_t2


class TestSLAAlertT2:
    """Tests para el job _run_sla_alert_t2 del scheduler."""

    def test_no_notifica_si_no_hay_deadlines(self, db, monkeypatch):
        """Si no hay tickets ni RATs próximos, retorna 0 sin enviar email."""
        # No hay datos en la BD
        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 0
        mock_send.assert_not_called()

    def test_detecta_arco_ticket_T2_dias(
        self, db, monkeypatch, empresa, rat_base
    ):
        """ARCO ticket con vencimiento en 1 día debe ser detectado."""
        # Crear ticket con vencimiento en 1 día
        ahora = datetime.now(timezone.utc)
        ticket = TktSolicitudDerecho(
            company_id=rat_base["company_id"],
            tipo="acceso",
            prioridad="alta",
            origen="web",
            titular_nombre="Test User",
            titular_email="test@test.cl",
            descripcion="Test ARCO",
            fecha_recepcion=ahora,
            fecha_vencimiento=ahora + timedelta(days=1),
            estado="abierto",
            tracking_token="test-token-001",
        )
        db.add(ticket)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 1
        mock_send.assert_called_once()
        # Verificar subject del email
        args, kwargs = mock_send.call_args
        assert "Alerta SLA" in args[1]
        assert "1 deadlines" in args[1]

    def test_detecta_arco_ticket_vencido(
        self, db, monkeypatch, empresa, rat_base
    ):
        """ARCO ticket ya vencido debe ser detectado (dias_restantes < 0)."""
        ahora = datetime.now(timezone.utc)
        ticket = TktSolicitudDerecho(
            company_id=rat_base["company_id"],
            tipo="rectificacion",
            prioridad="normal",
            origen="web",
            titular_nombre="Test User 2",
            titular_email="test2@test.cl",
            descripcion="Test vencido",
            fecha_recepcion=ahora - timedelta(days=15),
            fecha_vencimiento=ahora - timedelta(days=2),  # VENCIDO
            estado="abierto",
            tracking_token="test-vencido-001",
        )
        db.add(ticket)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 1
        mock_send.assert_called_once()

    def test_detecta_rat_T2_revision_180d(
        self, db, monkeypatch, empresa, rat_base
    ):
        """RAT con updated_at = hace 178 días debe ser detectado (T-2 de 180)."""
        ahora = datetime.now(timezone.utc)
        # Crear RAT con updated_at = hace 178 días (T-2 antes de vencer 180)
        rat = RAT(
            company_id=rat_base["company_id"],
            nombre_proceso="RAT próximo a vencer",
            categoria_datos="Test",
            categoria_titulares="Test",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Test",
            plazo_retencion="1 año",
            medidas_seguridad="Test",
            destinatarios="Test",
            estado="borrador",
            created_at=ahora - timedelta(days=200),
            updated_at=ahora - timedelta(days=178),  # T-2
        )
        db.add(rat)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 1
        mock_send.assert_called_once()

    def test_detecta_rat_vencido_180d(
        self, db, monkeypatch, empresa, rat_base
    ):
        """RAT con updated_at = hace 185 días debe ser detectado como vencido."""
        ahora = datetime.now(timezone.utc)
        rat = RAT(
            company_id=rat_base["company_id"],
            nombre_proceso="RAT vencido",
            categoria_datos="Test",
            categoria_titulares="Test",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Test",
            plazo_retencion="1 año",
            medidas_seguridad="Test",
            destinatarios="Test",
            estado="borrador",
            created_at=ahora - timedelta(days=200),
            updated_at=ahora - timedelta(days=185),  # VENCIDO
        )
        db.add(rat)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 1

    def test_no_detecta_rat_reciente(
        self, db, monkeypatch, empresa, rat_base
    ):
        """RAT con updated_at reciente (< 175 días) no debe ser detectado."""
        ahora = datetime.now(timezone.utc)
        rat = RAT(
            company_id=rat_base["company_id"],
            nombre_proceso="RAT reciente",
            categoria_datos="Test",
            categoria_titulares="Test",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Test",
            plazo_retencion="1 año",
            medidas_seguridad="Test",
            destinatarios="Test",
            estado="borrador",
            created_at=ahora - timedelta(days=10),
            updated_at=ahora - timedelta(days=10),  # Reciente
        )
        db.add(rat)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 0
        mock_send.assert_not_called()

    def test_agrupa_multiples_empresas_en_un_email_cada_una(
        self, db, monkeypatch, empresa, rat_base
    ):
        """Cada empresa recibe UN email con sus tickets/RATs (no se mezclan)."""
        # Crear segunda empresa
        otra_empresa = Company(
            nombre="Otra Empresa SpA",
            rut="88.888.888-8",
            email_dpo="dpo2@test.cl",
            contacto_dpo="Otro DPO",
        )
        db.add(otra_empresa)
        db.commit()
        db.refresh(otra_empresa)

        ahora = datetime.now(timezone.utc)
        # Ticket en empresa 1
        t1 = TktSolicitudDerecho(
            company_id=empresa["id"],
            tipo="acceso",
            prioridad="normal",
            origen="web",
            titular_nombre="T1",
            titular_email="t1@test.cl",
            descripcion="Ticket 1",
            fecha_recepcion=ahora,
            fecha_vencimiento=ahora + timedelta(days=1),
            estado="abierto",
            tracking_token="t1-token",
        )
        # Ticket en empresa 2
        t2 = TktSolicitudDerecho(
            company_id=otra_empresa.id,
            tipo="cancelacion",
            prioridad="normal",
            origen="web",
            titular_nombre="T2",
            titular_email="t2@test.cl",
            descripcion="Ticket 2",
            fecha_recepcion=ahora,
            fecha_vencimiento=ahora + timedelta(days=1),
            estado="abierto",
            tracking_token="t2-token",
        )
        db.add_all([t1, t2])
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        # 2 emails (uno por empresa)
        assert count == 2
        assert mock_send.call_count == 2

        # Verificar que cada email va a su empresa correcta
        emails_enviados = [call.args[0] for call in mock_send.call_args_list]
        assert empresa["email_dpo"] in emails_enviados
        assert "dpo2@test.cl" in emails_enviados

    def test_no_notifica_empresa_sin_email_dpo(
        self, db, monkeypatch, empresa
    ):
        """Si empresa no tiene email_dpo, no se intenta enviar (skip silencioso)."""
        from app.models.company import Company
        obj = db.query(Company).filter(Company.id == empresa["id"]).first()
        obj.email_dpo = None
        db.commit()

        ahora = datetime.now(timezone.utc)
        ticket = TktSolicitudDerecho(
            company_id=empresa["id"],
            tipo="acceso",
            prioridad="normal",
            origen="web",
            titular_nombre="Test",
            titular_email="test@test.cl",
            descripcion="Test",
            fecha_recepcion=ahora,
            fecha_vencimiento=ahora + timedelta(days=1),
            estado="abierto",
            tracking_token="no-dpo-token",
        )
        db.add(ticket)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 0  # No se contó
        mock_send.assert_not_called()

    def test_excluye_rats_soft_deleted(
        self, db, monkeypatch, empresa, rat_base
    ):
        """RATs con deleted_at != NULL no deben ser notificados (F3.2)."""
        ahora = datetime.now(timezone.utc)
        rat = RAT(
            company_id=rat_base["company_id"],
            nombre_proceso="RAT eliminado",
            categoria_datos="Test",
            categoria_titulares="Test",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Test",
            plazo_retencion="1 año",
            medidas_seguridad="Test",
            destinatarios="Test",
            estado="borrador",
            created_at=ahora - timedelta(days=200),
            updated_at=ahora - timedelta(days=185),
            deleted_at=ahora - timedelta(days=10),  # soft-deleted
        )
        db.add(rat)
        db.commit()

        with patch("app.services.email_service._send_raw") as mock_send:
            count = _run_sla_alert_t2(db)

        assert count == 0
        mock_send.assert_not_called()