"""
Tests para scheduler de notificacion APDP a las 72h (Art. 14 bis Ley 21.719).

Cubre crear_brecha() en breach_service.py que encola una tarea
NOTIFICAR_BRECHA_DPO con scheduled_for = fecha_deteccion + 72h.
"""
import json
import pytest
from datetime import datetime, timedelta, timezone

from app.models.task import TaskQueue, TaskType


class TestBreachScheduler72h:
    """Tests de integracion - verifican encolado en TaskQueue via BD directa."""

    def test_crear_brecha_encola_tarea_72h(
        self, client, auth_headers, empresa, db, clean_task_queue
    ):
        fecha_deteccion = datetime.now(timezone.utc)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha para test scheduler",
            "fecha_deteccion": fecha_deteccion.isoformat(),
            "nivel_riesgo": "alto",
            "naturaleza": "confidencialidad",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201, f"Error: {resp.text}"
        breach_id = resp.json()["id"]

        task = db.query(TaskQueue).filter(
            TaskQueue.task_type == TaskType.NOTIFICAR_BRECHA_DPO.value
        ).first()
        assert task is not None, "No se encolo tarea NOTIFICAR_BRECHA_DPO"
        assert task.status == "pending"

        scheduled_for = task.scheduled_for
        if scheduled_for.tzinfo is None:
            scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)

        delta = scheduled_for - fecha_deteccion
        assert timedelta(hours=71, minutes=59) < delta < timedelta(hours=72, minutes=1), \
            f"Delta esperado ~72h, obtido {delta}"

        task_payload = json.loads(task.payload)
        assert task_payload["breach_id"] == breach_id
        assert task_payload["company_id"] == empresa["id"]

    def test_crear_brecha_sin_email_dpo_no_falla_encolar(
        self, client, auth_headers, empresa, db, clean_task_queue
    ):
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha sin email DPO",
            "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
            "nivel_riesgo": "bajo",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201

        task = db.query(TaskQueue).filter(
            TaskQueue.task_type == TaskType.NOTIFICAR_BRECHA_DPO.value
        ).first()
        assert task is not None, "El enqueue debe ocurrir independiente del email DPO"

    def test_crear_brecha_fecha_naive_se_interpreta_como_utc(
        self, client, auth_headers, empresa, db, clean_task_queue
    ):
        """fecha_deteccion sin tzinfo debe tratarse como UTC."""
        naive_dt = datetime(2026, 1, 15, 10, 30, 0)
        payload = {
            "company_id": empresa["id"],
            "descripcion": "Brecha con fecha naive",
            "fecha_deteccion": naive_dt.isoformat(),
            "nivel_riesgo": "medio",
        }
        resp = client.post("/brechas/", json=payload, headers=auth_headers)
        assert resp.status_code == 201

        task = db.query(TaskQueue).first()
        assert task is not None
        assert task.scheduled_for.tzinfo is not None, "scheduled_for debe tener tzinfo"

        scheduled_for = task.scheduled_for
        if scheduled_for.tzinfo is None:
            scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)

        expected = naive_dt.replace(tzinfo=timezone.utc) + timedelta(hours=72)
        delta = abs((scheduled_for - expected).total_seconds())
        assert delta < 60, f"scheduled_for deberia ser ~{expected}, obtuve {scheduled_for}"

    def test_crear_multiples_brechas_encola_multiples_tareas(
        self, client, auth_headers, empresa, db, clean_task_queue
    ):
        for i in range(3):
            payload = {
                "company_id": empresa["id"],
                "descripcion": f"Brecha {i}",
                "fecha_deteccion": datetime.now(timezone.utc).isoformat(),
                "nivel_riesgo": "bajo",
            }
            resp = client.post("/brechas/", json=payload, headers=auth_headers)
            assert resp.status_code == 201

        tasks = db.query(TaskQueue).filter(
            TaskQueue.task_type == TaskType.NOTIFICAR_BRECHA_DPO.value
        ).all()
        assert len(tasks) == 3, f"Esperaba 3 tareas, encontre {len(tasks)}"
