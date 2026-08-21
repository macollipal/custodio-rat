"""
Endpoints CRUD para el RAT, más exportación y sugerencias automáticas.
"""

import logging
import unicodedata
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_client_ip, get_current_user, require_editor_or_admin_empresa, check_company_access
from app.schemas.rat import RATCreate, RATOut, RATSugerencia, RATSugerenciaOut, RATUpdate, ReportesResponse, SugerenciasTiposOut, BaseLegalOptionsOut, BASE_LEGAL_OPTIONS
from app.schemas.audit_log import AuditLogOut
from app.schemas.consentimiento import ConsentimientoCreate, ConsentimientoOut
from app.services.rat_service import (
    create_rat, delete_rat, download_rat_file, get_audit_logs, get_dashboard_stats,
    get_rat_for_user, get_rats, update_rat, marcar_revisado, aprobar_rat,
)
from app.services.rat_crud import clone_rat
from app.services.export_service import exportar_csv, exportar_pdf, exportar_pdf_apdp
from app.services.suggestion_service import sugerir_rat, listar_tipos_proceso
from app.services.company_service import get_company
from app.services.user_company_service import get_empresas_usuario
from app.services.rat_calculations import calcular_completitud, calcular_nivel_riesgo, rat_to_dict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rats", tags=["Registro RAT"])


@router.get("/reportes", response_model=ReportesResponse, summary="Reporte filtrado de RATs")
async def reportes(
    company_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    search: Optional[str] = Query(None, description="Buscar por nombre de proceso"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    base_legal: Optional[str] = Query(None, description="Filtrar por base legal"),
    categoria_titulares: Optional[str] = Query(None, description="Filtrar por categor�a de titulares"),
    datos_sensibles: Optional[bool] = Query(None, description="Solo procesos con datos sensibles"),
    evaluacion_impacto: Optional[bool] = Query(None, description="Solo procesos que requieren EIPD"),
    transferencia_internacional: Optional[bool] = Query(None, description="Solo con transferencia internacional"),
    created_by: Optional[str] = Query(None, description="Filtrar por creador (username)"),
    categoria_datos: Optional[str] = Query(None, description="Filtrar por categor�a de datos"),
    datos_nna: Optional[str] = Query(None, description="Filtrar por datos NNA"),
    transferencia_nacional: Optional[bool] = Query(None, description="Solo con transferencia nacional"),
    nivel_confidencialidad: Optional[str] = Query(None, description="Filtrar por nivel de confidencialidad"),
    decisiones_automatizadas: Optional[bool] = Query(None, description="Solo con decisiones automatizadas"),
    sort_by: Optional[str] = Query("created_at", description="Campo de ordenamiento"),
    sort_order: Optional[str] = Query("desc", description="Direccion: asc o desc"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Endpoint de reportes con filtros avanzados para m+�ltiples RATs.
    Soporta: b+�squeda por texto, estado, base legal, categor+�a de titulares,
    flags de datos sensibles, EIPD, transferencia internacional, creador,
    ordenamiento y paginaci+�n.
    """
    from app.models.rat import RAT as RATModel

    SORTABLE_FIELDS = {
        "created_at", "updated_at", "nombre_proceso", "estado",
        "completitud", "nivel_riesgo", "base_legal", "datos_sensibles",
        "evaluacion_impacto", "transferencia_internacional",
        "categoria_datos", "categoria_titulares", "plazo_retencion",
        "datos_nna", "transferencia_nacional", "nivel_confidencialidad",
        "decisiones_automatizadas", "evaluacion_impacto",
    }

    def escape_like(s: str) -> str:
        return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    sort_col = sort_by if sort_by in SORTABLE_FIELDS else "created_at"
    sort_dir = "desc" if sort_order == "desc" else "asc"

    query = db.query(RATModel)

    if company_id is not None:
        query = query.filter(RATModel.company_id == company_id)
    elif not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        query = query.filter(RATModel.company_id.in_(ids))

    if search:
        query = query.filter(RATModel.nombre_proceso.ilike(f"%{escape_like(search)}%"))

    if estado:
        query = query.filter(RATModel.estado == estado)

    if base_legal:
        query = query.filter(RATModel.base_legal.ilike(f"%{escape_like(base_legal)}%"))

    if categoria_titulares:
        query = query.filter(RATModel.categoria_titulares.ilike(f"%{escape_like(categoria_titulares)}%"))

    if datos_sensibles is not None:
        query = query.filter(RATModel.datos_sensibles == datos_sensibles)

    if evaluacion_impacto is not None:
        query = query.filter(RATModel.evaluacion_impacto == evaluacion_impacto)

    if transferencia_internacional is not None:
        query = query.filter(RATModel.transferencia_internacional == transferencia_internacional)

    if created_by:
        query = query.filter(RATModel.created_by == created_by)

    if categoria_datos:
        query = query.filter(RATModel.categoria_datos.ilike(f"%{escape_like(categoria_datos)}%"))

    if datos_nna:
        query = query.filter(RATModel.datos_nna.ilike(f"%{escape_like(datos_nna)}%"))

    if transferencia_nacional is not None:
        query = query.filter(RATModel.transferencia_nacional == transferencia_nacional)

    if nivel_confidencialidad:
        query = query.filter(RATModel.nivel_confidencialidad.ilike(f"%{escape_like(nivel_confidencialidad)}%"))

    if decisiones_automatizadas is not None:
        query = query.filter(RATModel.decisiones_automatizadas == decisiones_automatizadas)

    total_filtered = query.count()

    sort_column = getattr(RATModel, sort_col, RATModel.created_at)
    if sort_dir == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    rats_list = query.offset(skip).limit(limit).all()

    result = []
    for r in rats_list:
        out = RATOut.model_validate(r)
        out.completitud = calcular_completitud(rat_to_dict(r))
        out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
        out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
        result.append(out)

    return {
        "total": total_filtered,
        "skip": skip,
        "limit": limit,
        "sort_by": sort_col,
        "sort_order": sort_dir,
        "filtros_aplicados": {
            "company_id": company_id,
            "search": search,
            "estado": estado,
            "base_legal": base_legal,
            "categoria_titulares": categoria_titulares,
            "datos_sensibles": datos_sensibles,
            "evaluacion_impacto": evaluacion_impacto,
            "transferencia_internacional": transferencia_internacional,
            "created_by": created_by,
            "categoria_datos": categoria_datos,
            "datos_nna": datos_nna,
            "transferencia_nacional": transferencia_nacional,
            "nivel_confidencialidad": nivel_confidencialidad,
            "decisiones_automatizadas": decisiones_automatizadas,
        },
        "rats": result,
    }


@router.get("/", response_model=list[RATOut], summary="Listar registros RAT")
async def listar(
    company_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Feature gate N-02: modulo RAT debe estar habilitado
    if company_id is not None:
        from app.services.module_permission_service import require_module_enabled
        require_module_enabled(db, company_id, "RAT")
    # No-admin: solo puede ver RATs de sus empresas
    if not current_user.rol_global == "superadmin" and company_id is None:
        ids = get_empresas_usuario(db, current_user.id)
        from app.models.rat import RAT as RATModel
        rats_list = db.query(RATModel).filter(RATModel.company_id.in_(ids)).offset(skip).limit(limit).all()
    else:
        if company_id is not None and current_user.rol_global != "superadmin":
            check_company_access(current_user, company_id, db)
        rats_list = get_rats(db, company_id, skip, limit)

    result = []
    for r in rats_list:
        out = RATOut.model_validate(r)
        out.completitud = calcular_completitud(rat_to_dict(r))
        out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
        out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
        result.append(out)
    return result


@router.get("/dashboard/{company_id}", summary="Estad+�sticas del dashboard")
async def dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # H2.4 — feature gate N-02: modulo RAT debe estar habilitado
    from app.services.module_permission_service import require_module_enabled
    require_module_enabled(db, company_id, "RAT")

    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")
    return get_dashboard_stats(db, company_id)


@router.get("/sugerencias/base-legal", summary="Sugerencia de base legal según rubro")
async def sugerencia_base_legal(
    rubro_id: int = Query(..., description="ID del rubro de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dado un rubro_id, retorna la base legal más frecuente en RATs de empresas del mismo rubro."""
    from app.services.rat_crud import get_base_legal_sugerida
    base_legal = get_base_legal_sugerida(db, rubro_id)
    return {"base_legal": base_legal}


@router.get("/sugerencias/tipos", response_model=SugerenciasTiposOut, summary="Listar tipos de proceso disponibles para sugerencias")
async def tipos_proceso(current_user=Depends(get_current_user)):
    return SugerenciasTiposOut(tipos=listar_tipos_proceso())


BASE_LEGAL_DESCRIPCIONES: dict[str, str] = {
    "Consentimiento del titular": "Art. 12 - Debe ser libre, previo, expreso, informado, específico, revocable y sin condición negocial. Para datos sensibles, el consentimiento debe ser EXPRESO.",
    "Ejecución de contrato": "Art. 13 b) - El tratamiento es necesario para ejecutar un contrato en que el titular es parte.",
    "Obligación legal": "Art. 13 a) - El tratamiento es requerido por una norma legal vigente.",
    "Interés legítimo": "Art. 16 - Requiere test de 3 pasos documentado: (1) ¿Existe interés legítimo real? (2) ¿El tratamiento es necesario? (3) ¿Prevalece sobre los derechos del titular?",
    "Interés vital del titular": "Art. 13 c) - El tratamiento es necesario para proteger la vida o integridad física del titular o de otra persona.",
    "Misión de interés público": "Art. 13 d) - El tratamiento se encuentra previstos en una norma legal para el cumplimiento de una misión realizada en interés público.",
    "Datos biométricos de identificación (Art. 16 BIS)": "Art. 16 BIS - Datos biométricos para identificación inequívoca. Requiere EIPD obligatoria.",
    "Otra": "Base legal distinta a las anteriores. Documentar específicamente en el campo correspondiente.",
}


@router.get("/base-legal-opciones", response_model=BaseLegalOptionsOut, summary="Lista de bases legales válidas (Art. 13 Ley 21.719)")
async def base_legal_opciones(current_user=Depends(get_current_user)):
    return BaseLegalOptionsOut(opciones=BASE_LEGAL_OPTIONS, descripciones=BASE_LEGAL_DESCRIPCIONES)


@router.post("/sugerencias", response_model=RATSugerenciaOut, summary="Obtener sugerencias autom+�ticas para un proceso")
async def sugerencias(data: RATSugerencia, current_user=Depends(get_current_user)):
    """
    Dado un tipo de proceso (ej: 'clientes web', 'empleados'),
    retorna sugerencias precompletadas para el RAT basadas en la Ley 21.719.
    """
    return sugerir_rat(data.tipo_proceso)


@router.get("/{rat_id}", response_model=RATOut, summary="Obtener registro RAT por ID")
async def obtener(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    r = get_rat_for_user(db, rat_id, current_user)
    out = RATOut.model_validate(r)
    out.completitud = calcular_completitud(rat_to_dict(r))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out


@router.post("/", response_model=RATOut, status_code=201, summary="Crear registro RAT")
async def crear(
    request: Request,
    data: RATCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "admin_empresa":
        from app.services.user_company_service import get_empresas_usuario
        empresas = get_empresas_usuario(db, current_user.id)
        if data.company_id not in empresas:
            raise HTTPException(status_code=403, detail="No puede crear RATs en empresas que no gestiona.")
    else:
        require_editor_or_admin_empresa(data.company_id, db, current_user)
    r = create_rat(db, data, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = calcular_completitud(rat_to_dict(r))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out

@router.post("/{rat_id}/consentimientos", response_model=ConsentimientoOut, status_code=201, summary="Registrar consentimiento expreso para datos sensibles (REC-06)")
async def crear_consentimiento(
    request: Request,
    rat_id: int,
    data: ConsentimientoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Registra un consentimiento expreso del titular para un RAT que trata datos sensibles (Art. 16 Ley 21.719).

    Delega en consentimiento_service.crear_consentimiento() para aplicar el cifrado
    PII (Fernet) y hash SHA-256 de texto_consentimiento (Arts. 11, 12, 19 Ley 21.719).
    """
    from app.models.rat import RAT as RATModel
    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    require_editor_or_admin_empresa(rat.company_id, db, current_user)

    from app.services.consentimiento_service import crear_consentimiento as crear_consentimiento_service
    from app.services.consentimiento_service import RATNotFoundError

    if not data.ip_origen:
        data.ip_origen = get_client_ip(request)

    try:
        consentimiento = crear_consentimiento_service(db=db, data=data, usuario=current_user.username)
    except RATNotFoundError:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    return ConsentimientoOut.from_orm_cifrado(consentimiento)


@router.put("/{rat_id}", response_model=RATOut, summary="Actualizar registro RAT")
async def actualizar(
    request: Request,
    rat_id: int,
    data: RATUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rat = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    r = update_rat(db, rat_id, data, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = calcular_completitud(rat_to_dict(r))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out


@router.patch("/{rat_id}/archivar", response_model=RATOut, summary="Archivar un RAT")
async def archivar_rat(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cambia el estado del RAT a 'archivado'."""
    from app.models.rat import EstadoRAT as EstadoRATModel

    rat = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    rat.estado = EstadoRATModel.ARCHIVADO
    rat.updated_by = current_user.username
    from app.services.audit_service import log_audit
    log_audit(db, "rat", rat_id, "archivar", current_user.username, {"estado": "archivado"}, get_client_ip(request))
    db.commit()
    db.refresh(rat)
    out = RATOut.model_validate(rat)
    out.completitud = calcular_completitud(rat_to_dict(rat))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(rat))
    out.tiene_archivo_base_legal = bool(rat.archivo_base_legal_datos)
    return out


@router.post("/{rat_id}/clone", response_model=RATOut, status_code=201, summary="Clonar un RAT existente")
async def clonar_rat(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Crea una copia del RAT en estado borrador.

    No se clonan: archivo de base legal, estados de aprobación,
    observaciones de auditoría, ni tracking token.
    El RAT clonado pertenece a la misma empresa.
    """
    rat_original = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat_original.company_id, db, current_user)
    r = clone_rat(db, rat_id, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = calcular_completitud(rat_to_dict(r))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out


@router.delete("/{rat_id}", summary="Eliminar registro RAT")
async def eliminar(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.rat import RAT as RATModel
    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    if current_user.rol_global != "superadmin":
        check_company_access(current_user, rat.company_id, db)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    return delete_rat(db, rat_id, current_user.username, get_client_ip(request))


@router.post("/{rat_id}/revision", response_model=AuditLogOut, summary="Registrar revisi+�n peri+�dica del RAT")
async def registrar_revision(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Marca el proceso como revisado peri+�dicamente y registra el evento en la auditor+�a."""
    rat = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    return marcar_revisado(db, rat_id, current_user.username, get_client_ip(request))


@router.post("/{rat_id}/aprobar", response_model=RATOut, summary="Aprobar un RAT (solo admin/empresa)")
async def approve_rat(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Aprueba un RAT. Solo admin_empresa o superadmin pueden aprobar.
    Registra qui+�n aprob+� y la fecha de aprobaci+�n.
    """
    rat = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    r = aprobar_rat(db, rat_id, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = calcular_completitud(rat_to_dict(r))
    out.nivel_riesgo = calcular_nivel_riesgo(rat_to_dict(r))
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out


@router.get("/{rat_id}/archivo", summary="Descargar documento de base legal del RAT")
async def descargar_archivo(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retorna el documento que respalda la base legal del RAT.
    Si existe storage_url (OCI), genera pre-signed URL (5 min) para descarga directa.
    Si est� en BYTEA, retorna los bytes directamente.
    Requiere autenticaci�n. Descarga en nueva pesta�a del navegador.
    """

    rat = get_rat_for_user(db, rat_id, current_user)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)

    try:
        result = download_rat_file(
            db, rat_id,
            usuario=current_user.username,
            ip_origen=None
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener el archivo")

    if result["type"] == "presigned_url":
        return {
            "url": result["url"],
            "nombre": result["nombre"],
            "content_type": result["content_type"],
            "expires_in_seconds": 300,
        }

    elif result["type"] == "bytes":
        import base64
        datos = base64.b64decode(result["content"])
        return Response(
            content=datos,
            media_type=result["content_type"],
            headers={
                "Content-Disposition": f'inline; filename="{result["nombre"]}"',
            },
        )

    raise HTTPException(status_code=404, detail="Archivo no encontrado")


@router.get("/{rat_id}/auditoria", response_model=list[AuditLogOut], summary="Ver historial de auditor+�a de un RAT")
async def auditoria(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Validar acceso multi-tenant antes de retornar audit log
    get_rat_for_user(db, rat_id, current_user)
    return get_audit_logs(db, rat_id)


@router.get("/auditoria/{company_id}", summary="Historial de auditor+�a global de la empresa")
async def auditoria_global(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retorna todos los eventos de auditor+�a de los RATs de una empresa,
    ordenados por timestamp descendente, para que el DPO pueda ver
    toda la actividad reciente de un vistazo.
    Solo usuarios con acceso a la empresa pueden consultar.
    """
    from app.models.audit_log import AuditLog
    from app.models.rat import RAT as RATModel

    ids = get_empresas_usuario(db, current_user.id)
    if company_id not in ids:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta empresa")

    rat_ids = [r.id for r in db.query(RATModel.id).filter(RATModel.company_id == company_id).all()]
    if not rat_ids:
        return []
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.entidad == "rat", AuditLog.entidad_id.in_(rat_ids))
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [{"id": log.id, "rat_id": log.entidad_id, "accion": log.accion, "usuario": log.usuario, "timestamp": log.timestamp, "detalle": log.detalle} for log in logs]


@router.get("/auditoria/verify-chain", summary="Verificar integridad de la cadena de auditor+�a")
async def verificar_cadena_auditoria(
    limit: int = Query(1000, description="L+�mite de registros a verificar"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verifica la integridad de la cadena de hashes de auditor+�a.
    Retorna estado de validaci+�n y el ID del primer registro roto (si hay).
    Solo SUPERADMIN puede verificar la cadena global (H2.2 — auditor+�a 2026-07-07).
    """
    from app.services.audit_service import verify_audit_chain

    if current_user.rol_global != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Solo SUPERADMIN puede verificar la cadena de auditor+�a global.",
        )

    result = verify_audit_chain(db, limit=limit)
    return result


# ������ Exportaci+�n ���������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������

@router.get("/export/csv", summary="Exportar RAT a CSV")
async def exportar_a_csv(
    company_id: int = Query(..., description="ID de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    check_company_access(current_user, company_id, db)
    rats = get_rats(db, company_id)
    company = get_company(db, company_id)
    contenido = exportar_csv(rats)
    filename = _safe_filename(f"RAT_{company.nombre}_{company.rut}.csv")
    return Response(
        content=contenido,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf", summary="Exportar RAT a PDF")
async def exportar_a_pdf(
    company_id: int = Query(..., description="ID de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    check_company_access(current_user, company_id, db)
    rats = get_rats(db, company_id)
    company = get_company(db, company_id)
    contenido = exportar_pdf(rats, company)
    filename = _safe_filename(f"RAT_{company.nombre}_{company.rut}.pdf")
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/apdp", summary="Exportar Reporte APDP (Art. 16 Ley 21.719)")
async def exportar_reporte_apdp(
    company_id: int = Query(..., description="ID de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    """Genera el informe formal para la Agencia de Protección de Datos Personales."""
    check_company_access(current_user, company_id, db)
    rats = get_rats(db, company_id)
    company = get_company(db, company_id)
    contenido = exportar_pdf_apdp(rats, company)
    filename = _safe_filename(f"APDP_{company.nombre}_{company.rut}.pdf")
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{rat_id}/export/pdf", summary="Exportar un RAT individual a PDF")
async def exportar_rat_individual_pdf(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    from app.models.rat import RAT as RATModel

    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    check_company_access(current_user, rat.company_id, db)
    company = get_company(db, rat.company_id)
    contenido = exportar_pdf([rat], company)
    filename = _safe_filename(f"RAT_{rat.nombre_proceso}_{company.rut}.pdf")
    return Response(
        content=contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/cni", summary="Exportar RAT en formato para APDC (Ley 21.719)")
async def exportar_cni(
    company_id: int = Query(..., description="ID de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    check_company_access(current_user, company_id, db)
    rats = get_rats(db, company_id)
    company = get_company(db, company_id)
    from app.services.export_cni_service import exportar_rat_cni
    contenido = exportar_rat_cni(rats, company)
    filename = _safe_filename(f"RAT_CNI_{company.nombre}_{company.rut}.txt")
    return Response(
        content=contenido,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _safe_filename(name: str) -> str:
    """Convierte un nombre a ASCII seguro para headers HTTP."""
    normalized = unicodedata.normalize("NFD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_name.replace(" ", "_")
