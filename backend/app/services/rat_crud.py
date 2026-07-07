"""
CRUD de RAT — operaciones de base de datos (sin validaciones ni alertas).
"""
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.models.rat import RAT, EstadoRAT
from app.models.audit_log import AuditLog
from app.schemas.rat import RATCreate, RATUpdate
from app.services.audit_service import log_audit
from app.services.rat_constants import (
    CAMPOS_COMPLETITUD_EXTENDIDOS,
    CAMPOS_OBLIGATORIOS_COMPLETO,
    UMBRAL_COMPLETITUD_COMPLETO,
)
from app.services.rat_alerts import generar_alertas_auditoria
from app.services.rat_file import procesar_archivo_base_legal
from app.services.rat_validators import (
    tiene_consentimiento_activo,
    tiene_contrato_encargado_activo,
    validar_base_legal_otra_requiere_archivo,
    validar_contrato_encargado,
    validar_consentimiento_sensibles,
    validar_eipd_obligatoria,
)

logger = logging.getLogger(__name__)


def get_rats(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 200) -> list[RAT]:
    query = db.query(RAT).options(
        selectinload(RAT.company),
        selectinload(RAT.consentimientos),
    )
    if company_id:
        query = query.filter(RAT.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def get_rat(db: Session, rat_id: int) -> RAT:
    rat = db.query(RAT).filter(RAT.id == rat_id).first()
    if not rat:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro RAT no encontrado.")
    return rat


def get_rat_for_user(db: Session, rat_id: int, current_user) -> RAT:
    """Version segura de get_rat() con validacion multi-tenant.

    - superadmin: acceso total
    - admin_empresa / usuario: solo RATs de sus empresas asignadas

    Raises 404 (no 403) si el usuario no tiene acceso, para no filtrar
    la existencia del RAT a usuarios no autorizados.
    """
    from app.services.user_company_service import get_empresas_usuario
    rat = get_rat(db, rat_id)
    if current_user.rol_global == "superadmin":
        return rat
    empresas_usuario = get_empresas_usuario(db, current_user.id)
    if rat.company_id not in empresas_usuario:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro RAT no encontrado.")
    return rat


def _calcular_estado(data: dict) -> EstadoRAT:
    """Determina automaticamente el estado del RAT segun completitud."""
    obligatorios_ok = all(
        data.get(campo) and str(data[campo]).strip()
        for campo in CAMPOS_OBLIGATORIOS_COMPLETO
    )
    if not obligatorios_ok:
        return EstadoRAT.BORRADOR

    campos_25 = CAMPOS_OBLIGATORIOS_COMPLETO + CAMPOS_COMPLETITUD_EXTENDIDOS
    completados = sum(
        1 for c in campos_25 if data.get(c) is not None and str(data.get(c) or "").strip()
    )
    completitud_pct = round((completados / len(campos_25)) * 100)

    if completitud_pct >= UMBRAL_COMPLETITUD_COMPLETO:
        return EstadoRAT.COMPLETO
    return EstadoRAT.BORRADOR


def create_rat(db: Session, data: RATCreate, usuario: str, ip_origen: Optional[str] = None) -> RAT:
    from app.models.company import Company
    from fastapi import HTTPException, status

    if not db.query(Company).filter(Company.id == data.company_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    datos = data.model_dump()
    validar_eipd_obligatoria(datos)
    validar_base_legal_otra_requiere_archivo(datos)

    archivo_fields = procesar_archivo_base_legal(datos)
    datos.update(archivo_fields)

    observaciones = generar_alertas_auditoria(datos)
    if datos.get("observaciones_auditoria"):
        obs = datos["observaciones_auditoria"]
        observaciones = (obs + "\n" + observaciones) if observaciones else obs

    rat_data = {k: v for k, v in datos.items() if k not in ("observaciones_auditoria", "archivo_base_legal_base64")}
    rat = RAT(
        **rat_data,
        observaciones_auditoria=observaciones.strip() if observaciones else None,
        created_by=usuario,
        updated_by=usuario,
    )
    rat.estado = _calcular_estado(datos)

    db.add(rat)
    db.flush()
    log_audit(db, "rat", rat.id, "crear", usuario, datos, ip_origen)
    db.commit()
    db.refresh(rat)
    return rat


def update_rat(db: Session, rat_id: int, data: RATUpdate, usuario: str, ip_origen: Optional[str] = None) -> RAT:
    rat = get_rat(db, rat_id)
    cambios = data.model_dump(exclude_unset=True, exclude_none=True)

    archivo_fields = procesar_archivo_base_legal(cambios)
    cambios.update(archivo_fields)

    for field, value in cambios.items():
        setattr(rat, field, value)

    rat.updated_by = usuario

    rat_dict = {c.name: getattr(rat, c.name) for c in rat.__table__.columns}

    if "observaciones_auditoria" not in cambios:
        rat.observaciones_auditoria = generar_alertas_auditoria(rat_dict) or None

    if "estado" not in cambios:
        rat.estado = _calcular_estado(rat_dict)

    if cambios.get("datos_sensibles") and not tiene_consentimiento_activo(db, rat_id):
        validar_consentimiento_sensibles(db, rat)

    if cambios.get("nombre_encargado") and not tiene_contrato_encargado_activo(db, rat_id):
        validar_contrato_encargado(db, rat)

    rat_dict_validacion = {c.name: getattr(rat, c.name) for c in rat.__table__.columns}
    rat_dict_validacion.update(cambios)
    if rat_dict_validacion.get("datos_sensibles") or rat_dict_validacion.get("transferencia_internacional"):
        validar_eipd_obligatoria(rat_dict_validacion, rat_id=rat_id, db=db)
    validar_base_legal_otra_requiere_archivo(rat_dict_validacion)

    log_audit(db, "rat", rat_id, "editar", usuario, cambios, ip_origen)
    db.commit()
    db.refresh(rat)
    return rat


def delete_rat(db: Session, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> dict:
    """Elimina un RAT: mueve archivo a archive bucket antes de borrar de DB."""
    rat = get_rat(db, rat_id)
    nombre = rat.nombre_proceso

    storage_url = rat.archivo_base_legal_storage_url
    if storage_url:
        try:
            from app.core.storage import get_storage_backend
            backend = get_storage_backend()
            if hasattr(backend, 'copy_to_archive'):
                backend.copy_to_archive(storage_url, archive_prefix="rats")
                logger.info(f"Archivo {storage_url} movido a archive bucket")
            else:
                logger.warning(f"Backend no soporta archive, eliminando directamente: {storage_url}")
                backend.delete(storage_url)
        except Exception as e:
            logger.error(f"Error moviendo archivo a archive: {e}")
            try:
                from app.core.storage import get_storage_backend
                get_storage_backend().delete(storage_url)
            except Exception:
                pass

    log_audit(db, "rat", rat_id, "eliminar", usuario, {"nombre_proceso": nombre}, ip_origen)
    db.delete(rat)
    db.commit()
    return {"message": f"Registro '{nombre}' eliminado del RAT."}


def get_audit_logs(db: Session, rat_id: int) -> list[AuditLog]:
    return (
        db.query(AuditLog)
        .filter(AuditLog.entidad == "rat", AuditLog.entidad_id == rat_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


def get_dashboard_stats(db: Session, company_id: int) -> dict:
    from app.models.company import Company
    from fastapi import HTTPException, status

    if not db.query(Company).filter(Company.id == company_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    rats = db.query(RAT).filter(RAT.company_id == company_id).all()
    total = len(rats)
    por_estado = {}
    for r in rats:
        por_estado[r.estado.value] = por_estado.get(r.estado.value, 0) + 1

    sensibles = sum(1 for r in rats if r.datos_sensibles)
    con_transferencia_int = sum(1 for r in rats if r.transferencia_internacional)
    requieren_eipd = sum(1 for r in rats if r.evaluacion_impacto)
    completitud_promedio = round(sum(r.calcular_completitud() for r in rats) / total) if total else 0

    eipd_pendientes = sum(
        1 for r in rats
        if r.evaluacion_impacto and (r.estado_eipd or "pendiente") not in ("completada",)
    )
    transferencias_sin_garantias = sum(
        1 for r in rats if r.transferencia_internacional and not r.garantias_transferencia_int
    )
    interes_legitimo_sin_test = sum(
        1 for r in rats
        if "interés legítimo" in (r.base_legal or "").lower() or "interes legitimo" in (r.base_legal or "").lower()
        if not r.test_interes_legitimo
    )
    encargados_sin_contrato = sum(
        1 for r in rats if r.nombre_encargado and not r.tiene_contrato_encargado
    )

    rats_sin_doc = sum(
        1 for r in rats
        if r.base_legal and r.base_legal.strip().lower() != "otra"
        if not r.archivo_base_legal_datos
    )

    rats_por_vencer = 0
    rats_vencidos = 0
    now = datetime.now(timezone.utc)
    for r in rats:
        plazo = r.plazo_retencion or ""
        total_dias = 0
        for years_m in re.finditer(r"(\d+)\s*(?:año|años?)", plazo, re.IGNORECASE):
            total_dias += int(years_m.group(1)) * 365
        for meses_m in re.finditer(r"(\d+)\s*(?:mes|meses?)", plazo, re.IGNORECASE):
            total_dias += int(meses_m.group(1)) * 30
        for dias_m in re.finditer(r"(\d+)\s*(?:día|días|dia|dias?)", plazo, re.IGNORECASE):
            total_dias += int(dias_m.group(1))
        if total_dias == 0:
            continue
        created = r.created_at
        if created is None:
            continue
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                continue
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        expiry = created + timedelta(days=total_dias)
        if expiry < now:
            rats_vencidos += 1
        elif expiry - timedelta(days=90) < now:
            rats_por_vencer += 1

    return {
        "total_procesos": total,
        "por_estado": por_estado,
        "procesos_con_datos_sensibles": sensibles,
        "transferencias_internacionales": con_transferencia_int,
        "requieren_eipd": requieren_eipd,
        "completitud_promedio": completitud_promedio,
        "eipd_pendientes": eipd_pendientes,
        "transferencias_sin_garantias": transferencias_sin_garantias,
        "interes_legitimo_sin_test": interes_legitimo_sin_test,
        "encargados_sin_contrato": encargados_sin_contrato,
        "rats_por_vencer": rats_por_vencer,
        "rats_vencidos": rats_vencidos,
        "rats_sin_doc_base_legal": rats_sin_doc,
    }


def marcar_revisado(db: Session, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> AuditLog:
    rat = get_rat(db, rat_id)
    rat.updated_at = datetime.now(timezone.utc)
    rat.updated_by = usuario

    log_audit(db, "rat", rat_id, "revisado", usuario, {"nota": "Revision periódica del RAT confirmada"}, ip_origen)
    db.commit()

    log_entry = db.query(AuditLog).filter(
        AuditLog.entidad == "rat",
        AuditLog.entidad_id == rat_id,
        AuditLog.accion == "revisado",
    ).order_by(AuditLog.timestamp.desc()).first()
    return log_entry


def aprobar_rat(db: Session, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> RAT:
    """Aprueba un RAT registrando el DPO que lo aprueba y la fecha.
    El RAT debe tener 100% de completitud (incluyendo documento de base legal si aplica).
    """
    from fastapi import HTTPException, status

    rat = get_rat(db, rat_id)

    completitud = rat.calcular_completitud()
    if completitud < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El RAT debe estar 100% completo para poder aprobarlo. Completitud actual: {completitud}%",
        )

    rat.estado = EstadoRAT.APROBADO
    rat.aprobado_por = usuario
    rat.fecha_aprobacion = datetime.now(timezone.utc)
    rat.updated_at = datetime.now(timezone.utc)
    rat.updated_by = usuario

    log_audit(db, "rat", rat_id, "aprobar", usuario, {
        "nota": f"RAT aprobado por {usuario}",
        "fecha_aprobacion": rat.fecha_aprobacion.isoformat(),
    }, ip_origen)
    db.commit()
    db.refresh(rat)
    return rat
