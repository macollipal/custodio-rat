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

from app.models.task import TaskQueue, TaskStatus, TaskType
from app.models.token_blacklist import TokenBlacklist
from app.models.rat import RAT, EstadoRAT
from app.models.company import Company
from app.models.breach import SecurityBreach
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.services.email_service import (
    notificar_vencimiento_rat, notificar_nueva_brecha, notificar_respuesta_arco,
    notificar_eipd_vencida, notificar_consentimiento_por_vencer, EmailError,
)

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


def _run_revisar_encargados_vencidos(db: Session) -> int:
    """Revisa contratos de encargado próximos a vencer (≤30 días) y notifica al DPO."""
    from datetime import timedelta
    from app.models.encargado_contrato import EncargadoContrato
    from app.models.company import Company
    from app.services.email_service import notificar_vencimiento_encargado, EmailError

    DIAS_UMBRAL = 30
    ahora = datetime.now(timezone.utc)
    umbral = ahora + timedelta(days=DIAS_UMBRAL)

    contratos = (
        db.query(EncargadoContrato)
        .filter(
            EncargadoContrato.activo,
            EncargadoContrato.duracion_fin.isnot(None),
            EncargadoContrato.duracion_fin <= umbral,
        )
        .all()
    )

    notificados = 0
    for contrato in contratos:
        empresa = db.query(Company).filter(Company.id == contrato.company_id).first()
        if not empresa or not empresa.email_dpo:
            continue
        dias_restantes = (contrato.duracion_fin - ahora).days
        try:
            notificar_vencimiento_encargado(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                nombre_encargado=contrato.nombre_encargado,
                finalidad=contrato.finalidad,
                dias_restantes=dias_restantes,
            )
            notificados += 1
        except EmailError as e:
            logger.error(f"Encargado contrato {contrato.id}: fallo enviando notificación: {e}")

    return notificados


def _run_sla_alert_t2(db: Session) -> int:
    """
    Revisa tickets ARCO con vencimiento en T-2 días hábiles (o menos)
    y envía alerta grupal al DPO de cada empresa.
    """
    from datetime import timedelta
    from app.models.company import Company
    from app.models.user import User
    from app.services.email_service import notificar_sla_alert_t2, EmailError
    from app.services.ticket_service import calcular_dias_restantes

    ahora = datetime.now(timezone.utc)
    umbral_t2 = ahora + timedelta(days=2)

    estados_activos = ["abierto", "en_proceso", "pendiente", "subsanacion", "prorroga"]
    tickets = (
        db.query(TktSolicitudDerecho)
        .filter(
            TktSolicitudDerecho.estado.in_(estados_activos),
            TktSolicitudDerecho.fecha_vencimiento <= umbral_t2,
            TktSolicitudDerecho.fecha_vencimiento >= ahora,
        )
        .all()
    )

    vencidos = (
        db.query(TktSolicitudDerecho)
        .filter(
            TktSolicitudDerecho.estado.in_(estados_activos),
            TktSolicitudDerecho.fecha_vencimiento < ahora,
        )
        .all()
    )

    tickets_vencidos = tickets + vencidos
    if not tickets_vencidos:
        return 0

    por_empresa: dict[int, list] = {}
    for t in tickets_vencidos:
        por_empresa.setdefault(t.company_id, []).append(t)

    notificados = 0
    for company_id, tkt_list in por_empresa.items():
        empresa = db.query(Company).filter(Company.id == company_id).first()
        if not empresa or not empresa.email_dpo:
            continue

        tickets_data = []
        for t in tkt_list:
            dias = calcular_dias_restantes(t.fecha_vencimiento)
            responsable_nombre = None
            if t.responsable_id:
                user = db.query(User).filter(User.id == t.responsable_id).first()
                if user:
                    responsable_nombre = user.full_name or user.username
            tickets_data.append({
                "id": t.id,
                "tipo": t.tipo,
                "titular_nombre": t.titular_nombre,
                "prioridad": t.prioridad,
                "dias_restantes": dias,
                "responsable_nombre": responsable_nombre,
            })

        try:
            notificar_sla_alert_t2(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                tickets=tickets_data,
            )
            notificados += 1
        except EmailError as e:
            logger.error(f"SLA Alert T2 empresa {company_id}: fallo: {e}")

    return notificados


def _run_notificar_eipd_vencida(db: Session) -> int:
    """Revisa RATs con EIPD pendiente >90 días sin completarse y notifica al DPO."""
    from app.models.eipd import EIPD

    DIAS_UMBRAL = 90
    ahora = datetime.now(timezone.utc)

    rats_con_eipd = (
        db.query(RAT)
        .filter(
            RAT.evaluacion_impacto == True,  # noqa: E712
            RAT.estado_eipd.in_(["pendiente", "en_proceso", "no_requerida"]),
        )
        .all()
    )

    notificados = 0
    for rat in rats_con_eipd:
        eipd = db.query(EIPD).filter(EIPD.rat_id == rat.id).first()
        if not eipd or eipd.estado == "completada":
            continue
        inicio = eipd.fecha_inicio
        if inicio is None:
            continue
        if isinstance(inicio, str):
            try:
                inicio = datetime.fromisoformat(inicio.replace("Z", "+00:00"))
            except Exception:
                continue
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=timezone.utc)
        dias_abierta = (ahora - inicio).days
        if dias_abierta < DIAS_UMBRAL:
            continue

        empresa = db.query(Company).filter(Company.id == rat.company_id).first()
        if not empresa or not empresa.email_dpo:
            continue
        try:
            notificar_eipd_vencida(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                rat_nombre=rat.nombre_proceso,
                rat_id=rat.id,
                dias_abierta=dias_abierta,
            )
            notificados += 1
        except EmailError as e:
            logger.error(f"EIPD vencida RAT {rat.id}: fallo: {e}")

    return notificados


def _run_solicitar_renovacion_consentimiento(db: Session) -> int:
    """Revisa consentimientos activos >2 años y notifica al DPO."""
    from datetime import timedelta
    from app.models.consentimiento import Consentimiento

    DIAS_UMBRAL = 730
    ahora = datetime.now(timezone.utc)
    umbral = ahora - timedelta(days=DIAS_UMBRAL)

    consentimientos = (
        db.query(Consentimiento)
        .filter(
            Consentimiento.activo == True,  # noqa: E712
            Consentimiento.fecha_obtencion < umbral,
        )
        .all()
    )

    notificados = 0
    seen_companies = set()
    for consentimiento in consentimientos:
        rat = db.query(RAT).filter(RAT.id == consentimiento.rat_id).first()
        if not rat:
            continue
        empresa = db.query(Company).filter(Company.id == rat.company_id).first()
        if not empresa or not empresa.email_dpo:
            continue
        if empresa.id in seen_companies:
            continue
        seen_companies.add(empresa.id)
        dias_activo = (ahora - consentimiento.fecha_obtencion.replace(tzinfo=timezone.utc)).days
        try:
            notificar_consentimiento_por_vencer(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                rat_nombre=rat.nombre_proceso,
                rat_id=rat.id,
                dias_activo=dias_activo,
            )
            notificados += 1
        except EmailError as e:
            logger.error(f"Consentimiento por vencer empresa {empresa.id}: fallo: {e}")

    return notificados


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
        elif task.task_type == TaskType.REVISAR_ENCARGADOS_VENCIDOS.value:
            count = _run_revisar_encargados_vencidos(db)
            success = True
            detail = f"{count} encargados notificados"
        elif task.task_type == TaskType.SLA_ALERT_T2.value:
            count = _run_sla_alert_t2(db)
            success = True
            detail = f"{count} empresas notificadas (SLA T-2)"
        elif task.task_type == TaskType.NOTIFICAR_EIPD_VENCIDA.value:
            count = _run_notificar_eipd_vencida(db)
            success = True
            detail = f"{count} EIPDs vencidas notificadas"
        elif task.task_type == TaskType.SOLICITAR_RENOVACION_CONSENTIMIENTO.value:
            count = _run_solicitar_renovacion_consentimiento(db)
            success = True
            detail = f"{count} empresas notificadas (consentimientos >2 años)"
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
