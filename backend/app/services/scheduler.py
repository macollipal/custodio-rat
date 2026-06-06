"""
Scheduler ligero (basado en threading) para tareas periódicas en background.

Por qué no APScheduler: para mantener el bundle de Vercel liviano y no
agregar dependencias. Este scheduler corre en un thread daemon dentro del
proceso del backend; suficiente para periodicidades diarias/horarias.

Tareas registradas:
  - revisión de RATs vencidos: cada 24h
  - (se pueden agregar más en _JOBS)
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


def _job_revisar_rats_vencidos() -> None:
    """
    Revisa todos los RATs de todas las empresas y notifica al DPO
    cuando un RAT supera el umbral de revisión periódica.
    """
    from app.models.rat import RAT
    from app.models.company import Company
    from app.services.email_service import notificar_vencimiento_rat

    db = SessionLocal()
    try:
        umbral = datetime.now(timezone.utc) - timedelta(days=DIAS_REVISION)
        rats = (
            db.query(RAT)
            .filter(RAT.updated_at < umbral)
            .filter(RAT.estado.in_(["completo", "en_revision", "aprobado"]))
            .all()
        )
        logger.info(f"Scheduler: {len(rats)} RAT(s) requieren revisión")

        for rat in rats:
            empresa = db.query(Company).filter(Company.id == rat.company_id).first()
            if not empresa or not empresa.email_dpo:
                continue
            dias_remanente = int(
                (datetime.now(timezone.utc) - rat.updated_at).total_seconds() / 86400
            ) - DIAS_REVISION
            try:
                notificar_vencimiento_rat(
                    email_dpo=empresa.email_dpo,
                    nombre_dpo=empresa.contacto_dpo or "",
                    nombre_empresa=empresa.nombre,
                    nombre_proceso=rat.nombre_proceso or f"RAT #{rat.id}",
                    rat_id=rat.id,
                    dias_remanente=-dias_remanente,  # negativo = vencido
                )
            except Exception as e:
                logger.error(
                    f"Scheduler: fallo enviando notificación RAT #{rat.id} "
                    f"a {empresa.email_dpo}: {e}"
                )
    finally:
        db.close()


_JOBS: list[tuple[Callable[[], None], int]] = [
    (_job_revisar_rats_vencidos, 24 * 60 * 60),  # cada 24h
]


_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _run_scheduler() -> None:
    logger.info("Scheduler iniciado")
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
    if _scheduler_thread and _scheduler_thread.is_alive():
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
