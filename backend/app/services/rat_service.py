"""
Lógica de negocio para el Registro de Actividades de Tratamiento (RAT).
Incluye validaciones de auditoría conforme a la Ley 21.719.
"""

import json
import base64
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.rat import RAT, EstadoRAT
from app.models.audit_log import AuditLog
from app.schemas.rat import RATCreate, RATUpdate

# Campos obligatorios para marcar un RAT como "completo"
# Debe coincidir con campos_obligatorios en RAT.calcular_completitud()
CAMPOS_OBLIGATORIOS_COMPLETO = [
    "nombre_proceso",
    "categoria_datos",
    "categoria_titulares",
    "finalidad",
    "base_legal",
    "fuente_datos",
    "plazo_retencion",
]

# Alertas de auditoría automáticas
ALERTAS_AUDITORIA = {
    "datos_sensibles": (
        "⚠️ Este proceso trata datos sensibles (Art. 2 letra g Ley 21.719). Verifique que cuenta con base legal "
        "explícita y medidas de seguridad reforzadas. Documente el tipo específico de dato sensible."
    ),
    "datos_sensibles_consentimiento": (
        "⚠️ BASE LEGAL: El tratamiento de datos sensibles basado en consentimiento requiere que sea EXPRESO "
        "(no basta consentimiento implícito). Documente el mecanismo de obtención y revocación del consentimiento."
    ),
    "datos_sensibles_biometria": (
        "🔐 BIOMETRÍA: Los datos biométricos destinados a identificar inequívocamente a una persona se rigen por "
        "el Art. 16 BIS Ley 21.719. Requieren base legal específica y evaluación EIPD. En relaciones laborales, "
        "el consentimiento del empleado NO es base legal válida (relación jerárquica asimétrica)."
    ),
    "evaluacion_impacto": (
        "📋 Se marcó que requiere Evaluación de Impacto en Protección de Datos (EIPD/DPIA). "
        "Asegúrese de completarla y documentarla antes de iniciar el tratamiento (Art. 15 bis Ley 21.719)."
    ),
    "transferencia_internacional": (
        "🌐 Este proceso incluye transferencia internacional de datos. "
        "Verifique que el país destinatario cuenta con nivel adecuado de protección o que se aplican "
        "garantías apropiadas (SCC, BCR u otras). Chile NO está en la lista de adecuación de la UE. "
        "Documente las garantías aplicadas en el campo correspondiente."
    ),
    "transferencia_sin_garantias": (
        "🌐 ATENCIÓN: Se registró transferencia internacional sin especificar las garantías aplicadas. "
        "Documente si aplica nivel adecuado, SCC u otras garantías (Art. 28 Ley 21.719)."
    ),
    "decisiones_automatizadas": (
        "🤖 Este proceso involucra decisiones automatizadas o perfilamiento. Los titulares tienen derecho a "
        "solicitar intervención humana e impugnar la decisión (Art. 8 Ley 21.719). Documente la lógica del sistema "
        "y el mecanismo de revisión humana disponible. Evalúe si requiere EIPD."
    ),
    "interes_legitimo": (
        "⚖️ Base legal: Interés legítimo. Debe documentar el test de 3 pasos: (1) ¿existe interés legítimo real? "
        "(2) ¿el tratamiento es necesario para ese interés? (3) ¿prevalece sobre los derechos del titular? "
        "Sin este test documentado, la base no sirve como defensa ante la APDC."
    ),
    "interes_legitimo_sin_test": (
        "⚖️ PENDIENTE: Base legal Interés legítimo requiere documentar el test de 3 pasos en el campo correspondiente."
    ),
    "encargado_sin_contrato": (
        "📄 ENCARGADO SIN CONTRATO: Se registro un encargado del tratamiento pero no se ha confirmado la existencia "
        "de un contrato de encargo que establezca las instrucciones de tratamiento, confidencialidad y seguridad "
        "(Art. 14 quater Ley 21.719)."
    ),
    "eipd_pendiente": (
        "🔍 EIPD PENDIENTE: Este proceso requiere Evaluación de Impacto en Protección de Datos y aún no está completada. "
        "No puede iniciarse el tratamiento hasta completar la EIPD (Art. 15 bis Ley 21.719)."
    ),
    "falta_doc_base_legal": (
        "📄 SIN DOCUMENTO DE BASE LEGAL: La base legal seleccionada requiere un documento que la respalde "
        "(consentimiento, contrato, norma legal, EIPD, etc.). Adjunte el documento correspondiente para alcanzar el 100% de completitud."
    ),
}


def get_rats(db: Session, company_id: Optional[int] = None, skip: int = 0, limit: int = 200) -> list[RAT]:
    query = db.query(RAT)
    if company_id:
        query = query.filter(RAT.company_id == company_id)
    return query.offset(skip).limit(limit).all()


def get_rat(db: Session, rat_id: int) -> RAT:
    rat = db.query(RAT).filter(RAT.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro RAT no encontrado.")
    return rat


def _procesar_archivo_base_legal(data: dict) -> dict:
    """Convierte archivo_base_legal_base64 (string) a binario y hash. Retorna campos a escribir en el modelo."""
    base64_str = data.get("archivo_base_legal_base64")
    if not base64_str:
        return {}
    try:
        datos = base64.b64decode(base64_str)
    except Exception:
        return {}
    hash_val = hashlib.sha256(datos).hexdigest()
    return {
        "archivo_base_legal_datos": datos,
        "archivo_base_legal_hash": hash_val,
        "archivo_base_legal_nombre": data.get("archivo_base_legal_nombre"),
        "archivo_base_legal_tipo": data.get("archivo_base_legal_tipo"),
    }


def create_rat(db: Session, data: RATCreate, usuario: str) -> RAT:
    from app.models.company import Company
    if not db.query(Company).filter(Company.id == data.company_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    datos = data.model_dump()
    archivo_fields = _procesar_archivo_base_legal(datos)
    datos.update(archivo_fields)

    observaciones = _generar_alertas_auditoria(datos)
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
    _log_audit(db, rat.id, "crear", usuario, datos)
    db.commit()
    db.refresh(rat)
    return rat


def update_rat(db: Session, rat_id: int, data: RATUpdate, usuario: str) -> RAT:
    rat = get_rat(db, rat_id)
    cambios = data.model_dump(exclude_none=True)

    archivo_fields = _procesar_archivo_base_legal(cambios)
    cambios.update(archivo_fields)

    for field, value in cambios.items():
        setattr(rat, field, value)

    rat.updated_by = usuario

    rat_dict = {c.name: getattr(rat, c.name) for c in rat.__table__.columns}

    if "observaciones_auditoria" not in cambios:
        rat.observaciones_auditoria = _generar_alertas_auditoria(rat_dict) or None

    if "estado" not in cambios:
        rat.estado = _calcular_estado(rat_dict)

    _log_audit(db, rat_id, "editar", usuario, cambios)
    db.commit()
    db.refresh(rat)
    return rat


def delete_rat(db: Session, rat_id: int, usuario: str) -> dict:
    rat = get_rat(db, rat_id)
    nombre = rat.nombre_proceso
    _log_audit(db, rat_id, "eliminar", usuario, {"nombre_proceso": nombre})
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

    # RATs sin documento de base legal (cuando base legal != "Otra")
    rats_sin_doc = sum(
        1 for r in rats
        if r.base_legal and r.base_legal.strip().lower() != "otra"
        if not r.archivo_base_legal_datos
    )

    rats_por_vencer = 0
    rats_vencidos = 0
    from datetime import datetime, timezone, timedelta
    import re
    now = datetime.now(timezone.utc)
    for r in rats:
        plazo = r.plazo_retencion or ""
        match = re.search(r"(\d+)\s*(?:año|años)", plazo, re.IGNORECASE)
        if not match:
            continue
        years = int(match.group(1))
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
        expiry = created + timedelta(days=years * 365)
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


# ── Funciones internas ──────────────────────────────────────────────────────

def _calcular_estado(data: dict) -> EstadoRAT:
    """Determina automáticamente el estado del RAT según completitud."""
    todos_completos = all(data.get(campo) and str(data[campo]).strip() for campo in CAMPOS_OBLIGATORIOS_COMPLETO)
    if todos_completos:
        return EstadoRAT.COMPLETO
    return EstadoRAT.BORRADOR


def _generar_alertas_auditoria(data: dict) -> str:
    """Genera observaciones automáticas de auditoría según flags activados."""
    alertas = []
    base_legal = (data.get("base_legal") or "").lower()
    tipo_sensible = (data.get("tipo_dato_sensible") or "").lower()

    if data.get("datos_sensibles"):
        alertas.append(ALERTAS_AUDITORIA["datos_sensibles"])
        if "consentimiento" in base_legal:
            alertas.append(ALERTAS_AUDITORIA["datos_sensibles_consentimiento"])
        if "biométrico" in tipo_sensible or "biometrico" in tipo_sensible:
            alertas.append(ALERTAS_AUDITORIA["datos_sensibles_biometria"])

    if data.get("evaluacion_impacto"):
        alertas.append(ALERTAS_AUDITORIA["evaluacion_impacto"])

    if data.get("transferencia_internacional"):
        alertas.append(ALERTAS_AUDITORIA["transferencia_internacional"])
        if not data.get("garantias_transferencia_int"):
            alertas.append(ALERTAS_AUDITORIA["transferencia_sin_garantias"])

    if data.get("decisiones_automatizadas"):
        alertas.append(ALERTAS_AUDITORIA["decisiones_automatizadas"])

    if "interés legítimo" in base_legal or "interes legitimo" in base_legal:
        alertas.append(ALERTAS_AUDITORIA["interes_legitimo"])
        if not data.get("test_interes_legitimo"):
            alertas.append(ALERTAS_AUDITORIA["interes_legitimo_sin_test"])

    if data.get("nombre_encargado") and not data.get("tiene_contrato_encargado"):
        alertas.append(ALERTAS_AUDITORIA["encargado_sin_contrato"])

    if data.get("evaluacion_impacto") and (data.get("estado_eipd") or "pendiente") not in ("completada",):
        alertas.append(ALERTAS_AUDITORIA["eipd_pendiente"])

    # Alerta si falta documento de base legal (pero no bloquea)
    base_legal_raw = data.get("base_legal") or ""
    if base_legal_raw.strip().lower() != "otra" and not data.get("archivo_base_legal_datos"):
        alertas.append(ALERTAS_AUDITORIA["falta_doc_base_legal"])

    return "\n".join(alertas)


def marcar_revisado(db: Session, rat_id: int, usuario: str) -> AuditLog:
    rat = get_rat(db, rat_id)
    from datetime import datetime, timezone
    rat.updated_at = datetime.now(timezone.utc)
    rat.updated_by = usuario
    log = AuditLog(
        entidad="rat",
        entidad_id=rat_id,
        accion="revisado",
        usuario=usuario,
        detalle=json.dumps({"nota": "Revisión periódica del RAT confirmada"}, ensure_ascii=False),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def aprobar_rat(db: Session, rat_id: int, usuario: str) -> RAT:
    """
    Aprueba un RAT registrando el DPO que lo aprueba y la fecha.
    El RAT debe tener 100% de completitud (incluyendo documento de base legal si aplica).
    """
    from datetime import datetime, timezone
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

    log = AuditLog(
        entidad="rat",
        entidad_id=rat_id,
        accion="aprobar",
        usuario=usuario,
        detalle=json.dumps({
            "nota": f"RAT aprobado por {usuario}",
            "fecha_aprobacion": rat.fecha_aprobacion.isoformat(),
        }, ensure_ascii=False),
    )
    db.add(log)
    db.commit()
    db.refresh(rat)
    return rat


def _log_audit(db: Session, rat_id: int, accion: str, usuario: str, detalle: dict):
    log = AuditLog(
        entidad="rat",
        entidad_id=rat_id,
        accion=accion,
        usuario=usuario,
        detalle=json.dumps(detalle, ensure_ascii=False, default=str),
    )
    db.add(log)
    db.flush()
    db.commit()
