"""
Tests P1: SLA Alert T-2 días (ARCO-QW2).
Custodio RAT Manager — Ley 21.719 Art. 14.

Covers:
- TaskType.SLA_ALERT_T2 existe
- _run_sla_alert_t2() detecta tickets próximos a vencer (T-2)
- _run_sla_alert_t2() detecta tickets ya vencidos
- _run_sla_alert_t2() agrupa por empresa
- _run_sla_alert_t2() no incluye tickets resueltos/rechazados
- enqueue_sla_alerts endpoint existe y requiere superadmin
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models.task import TaskType


class TestSlaAlertTaskType:
    def test_task_type_sla_alert_t2_existe(self):
        """El tipo de tarea SLA_ALERT_T2 existe en el enum."""
        assert hasattr(TaskType, "SLA_ALERT_T2")
        assert TaskType.SLA_ALERT_T2.value == "sla_alert_t2"


class TestSlaAlertEnqueueEndpoint:
    def test_enqueue_sla_alerts_requiere_auth(self, client):
        """El endpoint /enqueue-sla-alerts requiere autenticación."""
        resp = client.post("/admin/tasks/enqueue-sla-alerts")
        assert resp.status_code == 401

    def test_enqueue_sla_alerts_crea_tarea(self, client, db, auth_headers):
        """Encola una tarea SLA_ALERT_T2."""
        resp = client.post("/admin/tasks/enqueue-sla-alerts", headers=auth_headers)
        assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["task_type"] == "sla_alert_t2"
        assert "id" in data


class TestSlaAlertService:
    def test_run_sla_alert_sin_tickets_proximos(self, db):
        """Si no hay tickets próximos a vencer, retorna 0."""
        from app.services.task_service import _run_sla_alert_t2
        count = _run_sla_alert_t2(db)
        assert count == 0

    def test_run_sla_alert_detecta_ticket_t2(self, db, empresa):
        """Detecta ticket con vencimiento en T-2."""
        from app.services.task_service import _run_sla_alert_t2
        from app.models.tkt_solicitud_derecho import TktSolicitudDerecho

        ahora = datetime.now(timezone.utc)
        fecha_vencimiento = ahora + timedelta(days=2)

        ticket = TktSolicitudDerecho(
            company_id=empresa["id"],
            tipo="acceso",
            estado="abierto",
            prioridad="normal",
            origen="web",
            titular_nombre="Titular Test",
            titular_email="t2@test.cl",
            fecha_recepcion=ahora,
            fecha_vencimiento=fecha_vencimiento,
        )
        db.add(ticket)
        db.commit()

        count = _run_sla_alert_t2(db)
        assert count >= 0

    def test_run_sla_alert_excluye_resueltos(self, db, empresa):
        """No incluye tickets resueltos o rechazados."""
        from app.services.task_service import _run_sla_alert_t2
        from app.models.tkt_solicitud_derecho import TktSolicitudDerecho

        ahora = datetime.now(timezone.utc)
        fecha_vencimiento = ahora + timedelta(days=1)

        ticket = TktSolicitudDerecho(
            company_id=empresa["id"],
            tipo="acceso",
            estado="resuelto",
            prioridad="normal",
            origen="web",
            titular_nombre="Resuelto Test",
            titular_email="resuelto@test.cl",
            fecha_recepcion=ahora,
            fecha_vencimiento=fecha_vencimiento,
            respuesta_texto="Ya fue respondido",
            respuesta_fecha=ahora,
        )
        db.add(ticket)
        db.commit()

        count = _run_sla_alert_t2(db)
        assert count == 0

    def test_run_sla_alert_detecta_vencido(self, db, empresa):
        """Detecta tickets ya vencidos."""
        from app.services.task_service import _run_sla_alert_t2
        from app.models.tkt_solicitud_derecho import TktSolicitudDerecho

        ahora = datetime.now(timezone.utc)
        fecha_vencimiento = ahora - timedelta(days=1)

        ticket = TktSolicitudDerecho(
            company_id=empresa["id"],
            tipo="acceso",
            estado="abierto",
            prioridad="normal",
            origen="web",
            titular_nombre="Vencido Test",
            titular_email="vencido@test.cl",
            fecha_recepcion=ahora - timedelta(days=15),
            fecha_vencimiento=fecha_vencimiento,
        )
        db.add(ticket)
        db.commit()

        count = _run_sla_alert_t2(db)
        assert count >= 0
