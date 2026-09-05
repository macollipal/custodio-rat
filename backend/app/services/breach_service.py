"""
Lógica de negocio para Brechas de Seguridad (Art. 14 bis Ley 21.719).
Plazos legales: notificación APDP en 72 horas desde el conocimiento formal; titulares sin dilación en datos sensibles/menores/financieros.
Filtro de riesgo razonable (Art. 14 sexies — REC-05).
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.breach import SecurityBreach, NivelRiesgo
from app.models.task import TaskType
from app.schemas.breach import BreachCreate, BreachUpdate
from app.services.task_service import enqueue_task

logger = logging.getLogger(__name__)


def listar_brechas(db: Session, company_id: int, skip: int = 0, limit: int = 100) -> tuple[list[SecurityBreach], int]:
    total = db.query(SecurityBreach).filter(SecurityBreach.company_id == company_id).count()
    breaches = (
        db.query(SecurityBreach)
        .options(joinedload(SecurityBreach.company))
        .filter(SecurityBreach.company_id == company_id)
        .order_by(SecurityBreach.fecha_deteccion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return breaches, total


def get_breach(db: Session, breach_id: int) -> SecurityBreach:
    b = db.query(SecurityBreach).filter(SecurityBreach.id == breach_id).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brecha no encontrada.")
    return b


def crear_brecha(db: Session, data: BreachCreate, usuario: str) -> SecurityBreach:
    from app.models.company import Company
    from app.services.audit_service import log_audit
    empresa = db.query(Company).filter(Company.id == data.company_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    breach = SecurityBreach(**data.model_dump(), creado_por=usuario)
    # BUG-01: Auto-calcular nivel de riesgo con los flags reales (Art. 14 bis)
    breach.nivel_riesgo = _calcular_nivel_riesgo(breach)
    breach.reportable_apdp_calculado = _calcular_reportable(breach)
    db.add(breach)
    db.flush()
    log_audit(
        db=db,
        entidad="brecha",
        entidad_id=breach.id,
        accion="create",
        usuario=usuario,
        detalle={"company_id": data.company_id, "nivel_riesgo": str(getattr(breach, "nivel_riesgo", ""))},
    )

    # Las 72h corren desde el conocimiento formal (Art. 14 bis); fallback a detección si no informado.
    _base_72h = breach.fecha_conocimiento or breach.fecha_deteccion
    if _base_72h.tzinfo is None:
        _base_72h = _base_72h.replace(tzinfo=timezone.utc)
    scheduled_for = _base_72h + timedelta(hours=72)
    try:
        enqueue_task(
            db=db,
            task_type=TaskType.NOTIFICAR_BRECHA_DPO.value,
            payload={"breach_id": breach.id, "company_id": breach.company_id},
            scheduled_for=scheduled_for,
        )
    except Exception as e:
        logger.error(f"Brecha {breach.id}: fallo encolando notificación 72h: {e}")

    db.commit()
    db.refresh(breach)

    if empresa.email_dpo:
        from app.services.email_service import notificar_nueva_brecha, EmailError
        try:
            notificar_nueva_brecha(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                descripcion=breach.descripcion or "Sin descripción",
                fecha_deteccion=breach.fecha_deteccion.strftime("%d-%m-%Y %H:%M"),
            )
        except EmailError as e:
            logger.error(f"Brecha {breach.id}: fallo enviando notificación email: {e}")

    return breach


def actualizar_brecha(db: Session, breach_id: int, data: BreachUpdate, usuario: Optional[str] = None) -> SecurityBreach:
    from app.services.audit_service import log_audit
    from app.models.company import Company
    breach = get_breach(db, breach_id)
    empresa = db.query(Company).filter(Company.id == breach.company_id).first()
    cambios = data.model_dump(exclude_none=True)

    _notificado_apdp_prev = breach.notificado_apdp
    _notificado_titulares_prev = breach.notificado_titulares

    for field, value in cambios.items():
        setattr(breach, field, value)

    # Recalcular riesgo si cambió algún factor determinante
    _risk_factors = {"incluye_datos_sensibles", "incluye_datos_nna", "incluye_datos_financieros", "volumen_titulares_afectados"}
    if cambios.keys() & _risk_factors:
        breach.nivel_riesgo = _calcular_nivel_riesgo(breach)
        breach.reportable_apdp_calculado = _calcular_reportable(breach)

    if data.notificado_apdp and not _notificado_apdp_prev and empresa and empresa.email_dpo:
        from app.services.email_service import notificar_nueva_brecha, EmailError
        try:
            notificar_nueva_brecha(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                descripcion=breach.descripcion or "Sin descripción",
                fecha_deteccion=breach.fecha_deteccion.strftime("%d-%m-%Y %H:%M"),
            )
        except EmailError as e:
            logger.error(f"Brecha {breach_id}: fallo enviando notificación APDP: {e}")

    # QW13 (Art. 14 bis): notificar a titulares afectados sin dilación indebida.
    if data.notificado_titulares and not _notificado_titulares_prev and empresa:
        from app.services.email_service import notificar_titulares_brecha
        emails_titulares = _obtener_emails_titulares_afectados(db, empresa.id, breach)
        if emails_titulares:
            enviados = notificar_titulares_brecha(
                emails_titulares=emails_titulares,
                nombre_empresa=empresa.nombre,
                descripcion=breach.descripcion or "Sin descripción",
                fecha_deteccion=breach.fecha_deteccion.strftime("%d-%m-%Y %H:%M"),
                tipo_datos_afectados=breach.datos_comprometidos or "",
            )
            logger.info(
                f"Brecha {breach_id}: notificación a titulares enviada a {enviados} destinatarios"
            )
        else:
            logger.info(
                f"Brecha {breach_id}: notificación a titulares activada pero sin emails registrados"
            )

    log_audit(
        db=db,
        entidad="brecha",
        entidad_id=breach_id,
        accion="update",
        usuario=usuario or "system",
        detalle={"campos_modificados": list(cambios.keys())},
    )
    db.commit()
    db.refresh(breach)
    return breach


def eliminar_brecha(db: Session, breach_id: int, usuario: Optional[str] = None) -> dict:
    from app.services.audit_service import log_audit
    breach = get_breach(db, breach_id)
    log_audit(
        db=db,
        entidad="brecha",
        entidad_id=breach_id,
        accion="delete",
        usuario=usuario or "system",
        detalle={"company_id": breach.company_id},
    )
    db.delete(breach)
    db.commit()
    return {"message": "Brecha eliminada."}


def _enriquecer(breach: SecurityBreach) -> dict:
    """Calcula campos derivados: horas desde detección/conocimiento y si el plazo APDP (72h) está vencido."""
    ahora = datetime.now(timezone.utc)
    det = breach.fecha_deteccion
    if det.tzinfo is None:
        det = det.replace(tzinfo=timezone.utc)
    horas_det = (ahora - det).total_seconds() / 3600

    # Las 72h para APDP corren desde el conocimiento formal (Art. 14 bis).
    base_conocimiento = breach.fecha_conocimiento or breach.fecha_deteccion
    if base_conocimiento.tzinfo is None:
        base_conocimiento = base_conocimiento.replace(tzinfo=timezone.utc)
    horas_con = (ahora - base_conocimiento).total_seconds() / 3600

    return {
        "horas_desde_deteccion": round(horas_det, 1),
        "horas_desde_conocimiento": round(horas_con, 1),
        "plazo_apdp_vencido": horas_con > 72 and not breach.notificado_apdp,
        "reportable_apdp_calculado": _calcular_reportable(breach),
    }


def _calcular_reportable(breach: SecurityBreach) -> bool:
    """Calcula si la brecha debe ser notificada a APDP según Art. 14 sexies (REC-05).

    Es reportable si:
    - nivel_riesgo es ALTO o CRÍTICO, O
    - incluye datos sensibles, O
    - incluye datos de menores de edad, O
    - incluye datos financieros.
    """
    if breach.nivel_riesgo in (NivelRiesgo.ALTO, NivelRiesgo.CRITICO):
        return True
    if breach.incluye_datos_sensibles or breach.incluye_datos_nna or breach.incluye_datos_financieros:
        return True
    return False


def _calcular_nivel_riesgo(breach: SecurityBreach) -> NivelRiesgo:
    """Calcula el nivel de riesgo razonable (Art. 14 sexies Ley 21.719).

    Score basado en tipo de datos comprometidos y volumen de titulares afectados.
    - Datos sensibles (Art. 2 g): +3
    - Datos de NNA: +3
    - Datos financieros: +2
    - >= 10.000 titulares: +3 | >= 1.000: +2 | >= 100: +1
    """
    score = 0

    if breach.incluye_datos_sensibles:
        score += 3
    if breach.incluye_datos_nna:
        score += 3
    if breach.incluye_datos_financieros:
        score += 2

    vol = breach.volumen_titulares_afectados or 0
    if vol >= 10000:
        score += 3
    elif vol >= 1000:
        score += 2
    elif vol >= 100:
        score += 1

    if score >= 6:
        return NivelRiesgo.CRITICO
    if score >= 4:
        return NivelRiesgo.ALTO
    if score >= 2:
        return NivelRiesgo.MEDIO
    return NivelRiesgo.BAJO


def evaluar_riesgo_brecha(db: Session, breach_id: int) -> SecurityBreach:
    """Recalcula nivel de riesgo y reportabilidad de una brecha existente."""
    breach = get_breach(db, breach_id)
    breach.nivel_riesgo = _calcular_nivel_riesgo(breach)
    breach.reportable_apdp_calculado = _calcular_reportable(breach)
    db.commit()
    db.refresh(breach)
    return breach


def _obtener_emails_titulares_afectados(
    db: Session, company_id: int, breach: SecurityBreach
) -> list:
    """
    QW13: Obtiene los emails de los titulares afectados por una brecha.

    Estrategia:
    1. Si breach.rats_afectados tiene RAT IDs, obtener consentimientos activos
       de esos RATs (los titulares dieron consentimiento y tenemos su email).
    2. Si breach.datos_comprometidos menciona emails explícitamente, parsear.
    3. Fallback: lista vacía (no podemos contactar sin emails).

    Por compliance, no obtenemos emails de la BD de usuarios empresa
    (esos son DPO/empleados, no titulares afectados).
    """
    emails: set = set()

    # 1. Consentimientos de RATs afectados
    if breach.rats_afectados:
        try:
            rat_ids = [int(x.strip()) for x in breach.rats_afectados.split(",") if x.strip().isdigit()]
        except (ValueError, AttributeError):
            rat_ids = []
        if rat_ids:
            from app.models.consentimiento import Consentimiento
            consentimientos = (
                db.query(Consentimiento)
                .filter(
                    Consentimiento.rat_id.in_(rat_ids),
                    Consentimiento.company_id == company_id,
                    Consentimiento.activo.is_(True),
                )
                .all()
            )
            for c in consentimientos:
                # nombre_titular_cipher es BYTEA; usamos el placeholder
                # que escribe el service (no es PII real).
                # Para email usamos un campo diferente si existe.
                pass  # El email está en email_titular_cipher (cifrado)

    # 2. Por ahora, no tenemos acceso a emails cifrados sin descifrar
    # cada uno. Eso requiere una clave de descifrado a nivel de servicio.
    # En producción, se debe:
    # - Descifrar email_titular_cipher de cada consentimiento
    # - O tener un canal alternativo (ej. email en otra tabla no cifrada)
    # - O enviar via DPO con CSV
    #
    # Por ahora retornamos lista vacia y loggeamos. El flujo de notificacion
    # queda implementado en email_service.notificar_titulares_brecha para
    # cuando se obtengan los emails (ej. via canal DPO con CSV).
    logger.info(
        f"Brecha {breach.id}: _obtener_emails_titulares_afectados no implementado "
        f"completamente. Emails se obtendran via DPO en produccion."
    )
    return list(emails)
