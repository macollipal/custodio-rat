"""
CRUD de RAT — operaciones de base de datos (sin validaciones ni alertas).
"""
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import func
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
    validar_datos_nna_base_legal,
    validar_eipd_obligatoria,
    validar_test_interes_legitimo,
)
from app.services.rat_calculations import calcular_completitud, rat_to_dict

CAMPOS_CLONE_EXCLUIDOS = {
    "id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "estado",
    "aprobado_por",
    "fecha_aprobacion",
    "observaciones_auditoria",
    "archivo_base_legal_nombre",
    "archivo_base_legal_tipo",
    "archivo_base_legal_datos",
    "archivo_base_legal_hash",
    "archivo_base_legal_storage_url",
    "tracking_token",
}


def clone_rat(db: Session, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> RAT:
    """Clona un RAT existente creando uno nuevo en estado borrador.

    Campos que no se clonan: id, created_at, updated_at, created_by, updated_by,
    estado (fijado a borrador), archivo_base_legal_*, aprobado_por, fecha_aprobacion,
    observaciones_auditoria, tracking_token.
    El RAT clonado mantiene el mismo company_id.
    """
    rat_original = get_rat(db, rat_id)

    datos_originales = {
        c.name: getattr(rat_original, c.name)
        for c in rat_original.__table__.columns
    }

    datos_clon = {
        k: v for k, v in datos_originales.items()
        if k not in CAMPOS_CLONE_EXCLUIDOS
    }

    rat_clonado = RAT(
        **datos_clon,
        estado=EstadoRAT.BORRADOR,
        created_by=usuario,
        updated_by=usuario,
    )

    db.add(rat_clonado)
    db.flush()

    log_audit(
        db, "rat", rat_clonado.id, "clone",
        usuario,
        {"rat_original_id": rat_id, "nombre_proceso": datos_originales.get("nombre_proceso")},
        ip_origen,
    )

    db.commit()
    db.refresh(rat_clonado)
    return rat_clonado

logger = logging.getLogger(__name__)


def get_rats(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 200) -> list[RAT]:
    query = db.query(RAT).options(
        selectinload(RAT.company),
        selectinload(RAT.consentimientos),
    ).filter(RAT.deleted_at.is_(None))
    if company_id:
        query = query.filter(RAT.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def get_rat(db: Session, rat_id: int) -> RAT:
    rat = db.query(RAT).filter(RAT.id == rat_id, RAT.deleted_at.is_(None)).first()
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
    validar_test_interes_legitimo(datos)
    validar_datos_nna_base_legal(datos)

    archivo_fields = procesar_archivo_base_legal(datos)
    datos.update(archivo_fields)

    observaciones = generar_alertas_auditoria(datos)
    if datos.get("observaciones_auditoria"):
        obs = datos["observaciones_auditoria"]
        observaciones = (obs + "\n" + observaciones) if observaciones else obs

    rat_data = {k: v for k, v in datos.items() if k not in ("observaciones_auditoria", "archivo_base_legal_base64", "justificacion_no_aplica")}
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


_REQUIRED_RAT_FIELDS = frozenset({
    'nombre_proceso', 'categoria_datos', 'categoria_titulares',
    'finalidad', 'base_legal', 'fuente_datos', 'plazo_retencion',
})
_PLACEHOLDER_RE = re.compile(r'^\.*$')


def update_rat(db: Session, rat_id: int, data: RATUpdate, usuario: str, ip_origen: Optional[str] = None) -> RAT:
    rat = get_rat(db, rat_id)
    _raw = data.model_dump(exclude_unset=True, exclude_none=True)
    # _strip_unset_required_fields inyecta "." / "..." como placeholders para los campos
    # obligatorios de RATBase que no están en el payload del PATCH/PUT. Esos valores
    # no deben sobreescribir los datos reales en BD; se filtran aquí.
    cambios = {
        k: v for k, v in _raw.items()
        if not (k in _REQUIRED_RAT_FIELDS and isinstance(v, str) and _PLACEHOLDER_RE.match(v))
    }

    archivo_fields = procesar_archivo_base_legal(cambios)
    cambios.update(archivo_fields)

    # Capturar estado anterior para diff granular en audit log
    _campos_binarios = {"archivo_base_legal_datos"}
    _antes = {
        k: getattr(rat, k, None)
        for k in cambios
        if k not in _campos_binarios and hasattr(rat, k)
    }

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
    validar_test_interes_legitimo(rat_dict_validacion)
    validar_datos_nna_base_legal(rat_dict_validacion)

    _campos_omitir_log = {"archivo_base_legal_base64", "archivo_base_legal_datos"}
    _despues = {k: v for k, v in cambios.items() if k not in _campos_omitir_log}
    _diff = {
        k: {"antes": _antes.get(k), "despues": _despues[k]}
        for k in _despues
        if _antes.get(k) != _despues[k]
    }
    log_audit(db, "rat", rat_id, "editar", usuario, {"diff": _diff}, ip_origen)
    db.commit()
    db.refresh(rat)
    return rat


def delete_rat(db: Session, rat_id: int, usuario: str, ip_origen: Optional[str] = None) -> dict:
    """Soft delete de RAT con archivo a bucket archive (Art. 19 + 28 Ley 21.719).

    C-01: usa deleted_at en lugar de db.delete para preservar cadena de custodia.
    C-07: bloquea si hay consentimientos activos — los datos siguen siendo tratados legalmente.
    """
    from fastapi import HTTPException, status as http_status

    rat = get_rat(db, rat_id)

    if rat.estado == EstadoRAT.APROBADO:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar un RAT en estado 'aprobado'. "
                "Revise el Art. 19 Ley 21.719: los registros aprobados forman parte de la cadena de custodia."
            ),
        )

    if tiene_consentimiento_activo(db, rat_id):
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar un RAT que tiene consentimientos activos. "
                "Revoque todos los consentimientos antes de eliminar el registro (Art. 16 Ley 21.719)."
            ),
        )

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

    now = datetime.now(timezone.utc)
    rat.deleted_at = now
    rat.updated_at = now
    log_audit(db, "rat", rat_id, "eliminar", usuario, {"nombre_proceso": nombre}, ip_origen)
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
    """Calcula estadísticas de RATs para dashboard.

    Optimizado: usa SQL GROUP BY/COUNT para agregados simples.
    Solo carga columnas necesarias para cómputos complejos.
    """
    from app.models.company import Company
    from fastapi import HTTPException, status
    from sqlalchemy import func

    if not db.query(Company).filter(Company.id == company_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    # SQL aggregations para stats simples
    total = db.query(func.count(RAT.id)).filter(RAT.company_id == company_id).scalar() or 0

    # por_estado via GROUP BY
    estado_rows = (
        db.query(RAT.estado, func.count(RAT.id).label("count"))
        .filter(RAT.company_id == company_id)
        .group_by(RAT.estado)
        .all()
    )
    por_estado = {row.estado.value: row.count for row in estado_rows}

    # Agregados booleanos via SQL
    sensibles = (
        db.query(func.count(RAT.id))
        .filter(RAT.company_id == company_id, RAT.datos_sensibles)
        .scalar()
    ) or 0
    con_transferencia_int = (
        db.query(func.count(RAT.id))
        .filter(RAT.company_id == company_id, RAT.transferencia_internacional)
        .scalar()
    ) or 0
    requieren_eipd = (
        db.query(func.count(RAT.id))
        .filter(RAT.company_id == company_id, RAT.evaluacion_impacto)
        .scalar()
    ) or 0

    # Cómputos que requieren lógica Python compleja: cargar instancias completas.
    # Se llama RAT.calcular_completitud() y se accede a atributos simples.
    # Historia: originalmente hacia db.query(RAT.col1, RAT.col2, ...) — eso devolvia
    # Row (named tuple) sin acceso a metodos de instancia. El bug rompia GET
    # /rats/dashboard/{id} en produccion con 'AttributeError: calcular_completitud'.
    # Workaround H3.1 (auditoria): extraer esta logica a un servicio.
    rats_complex = (
        db.query(RAT)
        .filter(RAT.company_id == company_id)
        .all()
    )
    # Un solo loop sobre rats_complex para todos los cómputos Python (C5).
    completitud_sum = 0
    eipd_pendientes = 0
    transferencias_sin_garantias = 0
    interes_legitimo_sin_test = 0
    encargados_sin_contrato = 0
    rats_sin_doc = 0
    rats_por_vencer = 0
    rats_vencidos = 0
    now = datetime.now(timezone.utc)

    for r in rats_complex:
        completitud_sum += calcular_completitud(rat_to_dict(r))

        if r.evaluacion_impacto and (r.estado_eipd or "pendiente") not in ("completada",):
            eipd_pendientes += 1
        if r.transferencia_internacional and not r.garantias_transferencia_int:
            transferencias_sin_garantias += 1
        base = (r.base_legal or "").lower()
        if ("interés legítimo" in base or "interes legitimo" in base) and not r.test_interes_legitimo:
            interes_legitimo_sin_test += 1
        if r.nombre_encargado and not r.tiene_contrato_encargado:
            encargados_sin_contrato += 1
        if r.base_legal and r.base_legal.strip().lower() != "otra" and not r.archivo_base_legal_datos:
            rats_sin_doc += 1

        plazo = r.plazo_retencion or ""
        total_dias = 0
        for years_m in re.finditer(r"(\d+)\s*(?:año|años?)", plazo, re.IGNORECASE):
            total_dias += int(years_m.group(1)) * 365
        for meses_m in re.finditer(r"(\d+)\s*(?:mes|meses?)", plazo, re.IGNORECASE):
            total_dias += int(meses_m.group(1)) * 30
        for dias_m in re.finditer(r"(\d+)\s*(?:día|días|dia|dias?)", plazo, re.IGNORECASE):
            total_dias += int(dias_m.group(1))
        if total_dias > 0 and r.created_at is not None:
            created = r.created_at
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except Exception:
                    created = None
            if created is not None:
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                expiry = created + timedelta(days=total_dias)
                if expiry < now:
                    rats_vencidos += 1
                elif expiry - timedelta(days=90) < now:
                    rats_por_vencer += 1

    completitud_promedio = round(completitud_sum / total, 1) if total else 0

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

    completitud = calcular_completitud(rat_to_dict(rat))
    if completitud < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El RAT debe estar 100% completo para poder aprobarlo. Completitud actual: {completitud}%",
        )

    # C-05: validar EIPD obligatoria antes de aprobar (Art. 15 bis Ley 21.719)
    rat_dict = {c.name: getattr(rat, c.name) for c in rat.__table__.columns}
    if rat_dict.get("datos_sensibles") or rat_dict.get("transferencia_internacional"):
        validar_eipd_obligatoria(rat_dict, rat_id=rat_id, db=db)

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


def get_base_legal_sugerida(db: Session, rubro_id: int) -> Optional[str]:
    """Devuelve la base legal más usada en RATs de empresas del mismo rubro.

    Args:
        db: sesión de BD
        rubro_id: ID del rubro a consultar

    Returns:
        Nombre de la base legal más frecuente, o None si no hay datos.
    """
    from app.models.company import Company

    result = (
        db.query(RAT.base_legal, func.count(RAT.id).label("cnt"))
        .join(Company, RAT.company_id == Company.id)
        .filter(
            Company.rubro_id == rubro_id,
            RAT.base_legal.isnot(None),
            RAT.base_legal != "",
        )
        .group_by(RAT.base_legal)
        .order_by(func.count(RAT.id).desc())
        .first()
    )
    return result.base_legal if result else None
