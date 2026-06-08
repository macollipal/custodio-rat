"""
Scheduler ligero (basado en threading) para tareas periódicas en background.

En Vercel serverless, este scheduler NO se ejecuta (los threads daemon mueren
con el proceso). Por eso las tareas se encolan en task_queue y se procesan
desde el endpoint /admin/tasks/run que un cron externo (Vercel Cron, etc.)
debe llamar periódicamente.

Aqui solo encolamos la tarea; el procesamiento lo hace el worker.
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Callable

from app.core.config import settings
from app.database.database import SessionLocal

logger = logging.getLogger(__name__)


DIAS_REVISION = 180  # debe coincidir con frontend/lib/constants.ts


def _job_enqueue_revisar_rats_vencidos() -> None:
    """Encola la tarea de revisión de RATs vencidos en la cola persistente."""
    from app.services.task_service import enqueue_task
    db = SessionLocal()
    try:
        enqueue_task(db, "revisar_rats_vencidos")
        logger.info("Scheduler: tarea 'revisar_rats_vencidos' encolada")
    finally:
        db.close()


def _job_enqueue_cleanup_tokens() -> None:
    """Encola limpieza de tokens expirados."""
    from app.services.task_service import enqueue_task
    db = SessionLocal()
    try:
        enqueue_task(db, "cleanup_tokens")
        logger.info("Scheduler: tarea 'cleanup_tokens' encolada")
    finally:
        db.close()


_JOBS = [
    (_job_enqueue_revisar_rats_vencidos, 24 * 60 * 60),  # cada 24h
    (_job_enqueue_cleanup_tokens, 6 * 60 * 60),  # cada 6h
]  # type: ignore


_scheduler_thread = None  # type: ignore
_stop_event = threading.Event()


def _run_scheduler() -> None:
    logger.info("Scheduler iniciado (modo enqueue)")
    next_runs = {job: time.time() + interval for job, interval in _JOBS}
    while not _stop_event.is_set():
        now = time.time()
        for job, interval in _JOBS:
            if now >= next_runs[job]:
                try:
                    job()
                except Exception as e:
                    logger.exception(f"Scheduler: error en job {job.__name__}: {e}")
                next_runs[job] = now + interval
        _stop_event.wait(timeout=60)
    logger.info("Scheduler detenido")


def start_scheduler() -> None:
    """Arranca el scheduler en un thread daemon. Idempotente."""
    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return
    if settings.ENVIRONMENT == "test":
        logger.info("Scheduler omitido (ENVIRONMENT=test)")
        return
    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_run_scheduler, name="custodio-scheduler", daemon=True
    )
    _scheduler_thread.start()


def stop_scheduler() -> None:
    _stop_event.set()
