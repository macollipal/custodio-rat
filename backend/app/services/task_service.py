"""
Servicio de cola de tareas asincronas.

En Vercel serverless, los threads no sobreviven. Por lo tanto, la cola es
persistida en BD y ejecutada por:
1. Un endpoint /admin/tasks/run que un cron externo (Vercel Cron, GitHub Actions, etc.)
   puede llamar periodicamente.
2. Un trigger automatico desde el lifespan de la app (best-effort, solo en local).
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import TaskQueue, TaskStatus, TaskType
from app.models.token_blacklist import TokenBlacklist
from app.models.rat import RAT, EstadoRAT
from app.models.company import Company
from app.models.breach import SecurityBreach
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.services.email_service import (
    notificar_vencimiento_rat, notificar_nueva_brecha, notificar_respuesta_arco, EmailError,
)
from app.services.ticket_service import (
    cambiar_estado_ticket, get_dashboard_stats,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def enqueue_task(
    db: Session,
    task_type: str,
    payload: Optional[dict] = None,
    scheduled_for: Optional[datetime] = None,
    max_attempts: int = 3,
) -> TaskQueue:
    """Encola una tarea para ejecucion asincrona."""
    task = TaskQueue(
        task_type=task_type,
        status=TaskStatus.PENDING,
        payload=json.dumps(payload or {}, ensure_ascii=False, default=str),
        scheduled_for=scheduled_for or datetime.now(timezone.utc),
        max_attempts=max_attempts,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def _run_revisar_rats_vencidos(db: Session) -> int:
    """Revisa RATs con mas de 180 dias sin revision y notifica al DPO."""
    from datetime import timedelta
    DIAS_REVISION = 180
    umbral = datetime.now(timezone.utc) - timedelta(days=DIAS_REVISION)

    rats = (
        db.query(RAT)
        .filter(
            RAT.estado.in_([EstadoRAT.COMPLETO, EstadoRAT.EN_REVISION, EstadoRAT.APROBADO]),
            RAT.updated_at < umbral,
        )
        .all()
    )

    notificados = 0
    for rat in rats:
        empresa = db.query(Company).filter(Company.id == rat.company_id).first()
        if not empresa or not empresa.email_dpo:
            continue
        try:
            notificar_vencimiento_rat(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                rat_nombre=rat.nombre_proceso,
                dias_revision=DIAS_REVISION,
            )
            notificados += 1
        except EmailError as e:
            logger.error(f"RAT vencido {rat.id}: fallo enviando notificación: {e}")

    return notificados


def _run_notificar_brecha_dpo(db: Session, payload: dict) -> bool:
    breach_id = payload.get("breach_id")
    if not breach_id:
        return False
    breach = db.query(SecurityBreach).filter(SecurityBreach.id == breach_id).first()
    if not breach:
        return False
    empresa = db.query(Company).filter(Company.id == breach.company_id).first()
    if not empresa or not empresa.email_dpo:
        return False
    fecha_str = breach.fecha_deteccion.strftime("%d-%m-%Y %H:%M")
    try:
        notificar_nueva_brecha(
            email_dpo=empresa.email_dpo,
            nombre_dpo=empresa.contacto_dpo or "",
            nombre_empresa=empresa.nombre,
            descripcion=breach.descripcion or "Sin descripción",
            fecha_deteccion=fecha_str,
        )
        return True
    except EmailError as e:
        logger.error(f"Task notificar_brecha {breach_id}: {e}")
        return False


def _run_notificar_respuesta_arco(db: Session, payload: dict) -> bool:
    ticket_id = payload.get("ticket_id")
    if not ticket_id:
        return False
    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket or not ticket.titular_email:
        return False
    empresa = db.query(Company).filter(Company.id == ticket.company_id).first()
    try:
        notificar_respuesta_arco(
            email_titular=ticket.titular_email,
            nombre_titular=ticket.titular_nombre,
            tipo_derecho=ticket.tipo,
            respuesta=ticket.respuesta_texto or "Su solicitud ha sido procesada.",
            empresa_nombre=empresa.nombre if empresa else "la empresa",
        )
        return True
    except EmailError as e:
        logger.error(f"Task notificar_respuesta_arco {ticket_id}: {e}")
        return False


def _run_cleanup_tokens(db: Session) -> int:
    """Elimina tokens revocados que ya expiraron."""
    from sqlalchemy import delete
    ahora = datetime.now(timezone.utc)
    result = db.execute(delete(TokenBlacklist).where(TokenBlacklist.expires_at < ahora))
    db.commit()
    return result.rowcount if hasattr(result, 'rowcount') else 0


def run_task(db: Session, task: TaskQueue) -> bool:
    """Ejecuta una tarea individual. Retorna True si fue exitosa."""
    task.status = TaskStatus.RUNNING
    task.attempts += 1
    task.started_at = datetime.now(timezone.utc)
    db.commit()

    try:
        payload = json.loads(task.payload or "{}")
        success = False
        detail = None

        if task.task_type == TaskType.REVISAR_RATS_VENCIDOS.value:
            count = _run_revisar_rats_vencidos(db)
            success = True
            detail = f"{count} RATs notificados"
        elif task.task_type == TaskType.NOTIFICAR_BRECHA_DPO.value:
            success = _run_notificar_brecha_dpo(db, payload)
        elif task.task_type == TaskType.NOTIFICAR_RESPUESTA_ARCO.value:
            success = _run_notificar_respuesta_arco(db, payload)
        elif task.task_type == TaskType.NOTIFICAR_VENCIMIENTO_RAT.value:
            success = _run_revisar_rats_vencidos(db) > 0
        elif task.task_type == TaskType.CLEANUP_TOKENS.value:
            count = _run_cleanup_tokens(db)
            success = True
            detail = f"{count} tokens eliminados"
        else:
            detail = f"Tipo de tarea desconocido: {task.task_type}"
            logger.warning(detail)

        if success:
            task.status = TaskStatus.DONE
            task.completed_at = datetime.now(timezone.utc)
            if detail:
                task.last_error = f"OK: {detail}"
        else:
            if task.attempts >= task.max_attempts:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                task.last_error = detail or "Falló sin detalle"
            else:
                task.status = TaskStatus.RETRYING
                task.last_error = detail or "Falló, se reintentará"

        db.commit()
        return success
    except Exception as e:
        logger.exception(f"Error ejecutando task {task.id}: {e}")
        if task.attempts >= task.max_attempts:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
        else:
            task.status = TaskStatus.RETRYING
        task.last_error = str(e)[:1000]
        db.commit()
        return False


def process_pending_tasks(db: Session, max_tasks: int = 20) -> dict:
    """Procesa todas las tareas pendientes. Llamado por el cron externo o lifespan."""
    ahora = datetime.now(timezone.utc)
    tasks = (
        db.query(TaskQueue)
        .filter(
            TaskQueue.status.in_([TaskStatus.PENDING, TaskStatus.RETRYING]),
            TaskQueue.scheduled_for <= ahora,
        )
        .order_by(TaskQueue.scheduled_for.asc())
        .limit(max_tasks)
        .all()
    )

    results = {"processed": 0, "done": 0, "failed": 0}
    for task in tasks:
        results["processed"] += 1
        if run_task(db, task):
            results["done"] += 1
        else:
            results["failed"] += 1
    return results
