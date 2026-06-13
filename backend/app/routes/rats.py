"""
Endpoints CRUD para el RAT, m├ís exportaci├│n y sugerencias autom├íticas.
"""

import logging
import unicodedata
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request

logger = logging.getLogger(__name__)
from app.routes.deps import get_client_ip
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routes.deps import get_current_user, require_editor_or_admin_empresa
from app.schemas.rat import RATCreate, RATOut, RATSugerencia, RATSugerenciaOut, RATUpdate, ReportesResponse
from app.schemas.audit_log import AuditLogOut
from app.schemas.consentimiento import ConsentimientoCreate, ConsentimientoOut
from app.services.rat_service import (
    create_rat, delete_rat, get_audit_logs, get_dashboard_stats,
    get_rat, get_rats, update_rat, marcar_revisado, aprobar_rat,
)
from app.services.export_service import exportar_csv, exportar_pdf
from app.services.suggestion_service import sugerir_rat, listar_tipos_proceso
from app.services.company_service import get_company
from app.services.user_company_service import get_empresas_usuario

router = APIRouter(prefix="/rats", tags=["Registro RAT"])


@router.get("/reportes", response_model=ReportesResponse, summary="Reporte filtrado de RATs")
async def reportes(
    company_id: Optional[int] = Query(None, description="Filtrar por empresa"),
    search: Optional[str] = Query(None, description="Buscar por nombre de proceso"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    base_legal: Optional[str] = Query(None, description="Filtrar por base legal"),
    categoria_titulares: Optional[str] = Query(None, description="Filtrar por categor├¡a de titulares"),
    datos_sensibles: Optional[bool] = Query(None, description="Solo procesos con datos sensibles"),
    evaluacion_impacto: Optional[bool] = Query(None, description="Solo procesos que requieren EIPD"),
    transferencia_internacional: Optional[bool] = Query(None, description="Solo con transferencia internacional"),
    created_by: Optional[str] = Query(None, description="Filtrar por creador (username)"),
    sort_by: Optional[str] = Query("created_at", description="Campo de ordenamiento"),
    sort_order: Optional[str] = Query("desc", description="Direcci├│n: asc o desc"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Endpoint de reportes con filtros avanzados para m├║ltiples RATs.
    Soporta: b├║squeda por texto, estado, base legal, categor├¡a de titulares,
    flags de datos sensibles, EIPD, transferencia internacional, creador,
    ordenamiento y paginaci├│n.
    """
    from app.models.rat import RAT as RATModel

    SORTABLE_FIELDS = {
        "created_at", "updated_at", "nombre_proceso", "estado",
        "completitud", "nivel_riesgo", "base_legal", "datos_sensibles",
        "evaluacion_impacto", "transferencia_internacional",
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
        out.completitud = r.calcular_completitud()
        out.nivel_riesgo = r.calcular_nivel_riesgo()
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
    # No-admin: solo puede ver RATs de sus empresas
    if not current_user.rol_global == "superadmin" and company_id is None:
        ids = get_empresas_usuario(db, current_user.id)
        from app.models.rat import RAT as RATModel
        rats_list = db.query(RATModel).filter(RATModel.company_id.in_(ids)).offset(skip).limit(limit).all()
    else:
        rats_list = get_rats(db, company_id, skip, limit)

    result = []
    for r in rats_list:
        out = RATOut.model_validate(r)
        out.completitud = r.calcular_completitud()
        out.nivel_riesgo = r.calcular_nivel_riesgo()
        out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
        result.append(out)
    return result


@router.get("/dashboard/{company_id}", summary="Estad├¡sticas del dashboard")
async def dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")
    return get_dashboard_stats(db, company_id)


@router.get("/sugerencias/tipos", summary="Listar tipos de proceso disponibles para sugerencias")
async def tipos_proceso(current_user=Depends(get_current_user)):
    return {"tipos": listar_tipos_proceso()}


@router.post("/sugerencias", response_model=RATSugerenciaOut, summary="Obtener sugerencias autom├íticas para un proceso")
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
    r = get_rat(db, rat_id)
    out = RATOut.model_validate(r)
    out.completitud = r.calcular_completitud()
    out.nivel_riesgo = r.calcular_nivel_riesgo()
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
    out.completitud = r.calcular_completitud()
    out.nivel_riesgo = r.calcular_nivel_riesgo()
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
    """Registra un consentimiento expreso del titular para un RAT que trata datos sensibles (Art. 16 Ley 21.719)."""
    from app.models.rat import RAT as RATModel
    from app.models.consentimiento import Consentimiento

    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    require_editor_or_admin_empresa(rat.company_id, db, current_user)

    if data.rat_id != rat_id:
        raise HTTPException(status_code=400, detail="El rat_id del consentimiento no coincide con la URL.")

    consentimiento = Consentimiento(
        company_id=rat.company_id,
        rat_id=rat_id,
        nombre_titular=data.nombre_titular,
        email_titular=data.email_titular,
        canal=data.canal,
        texto_consentimiento=data.texto_consentimiento,
        fecha_obtencion=data.fecha_obtencion,
        ip_origen=data.ip_origen or get_client_ip(request),
        activo=True,
    )
    db.add(consentimiento)
    db.flush()
    from app.services.audit_service import log_audit
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=consentimiento.id,
        accion="create",
        usuario=current_user.username,
        detalle={"rat_id": rat_id, "titular": data.nombre_titular, "canal": data.canal},
    )
    db.commit()
    db.refresh(consentimiento)
    return consentimiento


@router.put("/{rat_id}", response_model=RATOut, summary="Actualizar registro RAT")
async def actualizar(
    request: Request,
    rat_id: int,
    data: RATUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rat = get_rat(db, rat_id)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    r = update_rat(db, rat_id, data, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = r.calcular_completitud()
    out.nivel_riesgo = r.calcular_nivel_riesgo()
    out.tiene_archivo_base_legal = bool(r.archivo_base_legal_datos)
    return out


@router.delete("/{rat_id}", summary="Eliminar registro RAT")
async def eliminar(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rat = get_rat(db, rat_id)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    return delete_rat(db, rat_id, current_user.username, get_client_ip(request))


@router.post("/{rat_id}/revision", response_model=AuditLogOut, summary="Registrar revisi├│n peri├│dica del RAT")
async def registrar_revision(
    request: Request,
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Marca el proceso como revisado peri├│dicamente y registra el evento en la auditor├¡a."""
    rat = get_rat(db, rat_id)
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
    Registra qui├®n aprob├│ y la fecha de aprobaci├│n.
    """
    rat = get_rat(db, rat_id)
    require_editor_or_admin_empresa(rat.company_id, db, current_user)
    r = aprobar_rat(db, rat_id, current_user.username, get_client_ip(request))
    out = RATOut.model_validate(r)
    out.completitud = r.calcular_completitud()
    out.nivel_riesgo = r.calcular_nivel_riesgo()
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
    Si está en BYTEA, retorna los bytes directamente.
    Requiere autenticación. Descarga en nueva pestaña del navegador.
    """
    from app.services.rat_service import download_rat_file
    from app.core.deps import get_current_user

    result = download_rat_file(
        db, rat_id,
        usuario=current_user.username,
        ip_origen=None
    )

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


@router.get("/{rat_id}/auditoria", response_model=list[AuditLogOut], summary="Ver historial de auditor├¡a de un RAT")
async def auditoria(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_audit_logs(db, rat_id)


@router.get("/auditoria/{company_id}", summary="Historial de auditor├¡a global de la empresa")
async def auditoria_global(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retorna todos los eventos de auditor├¡a de los RATs de una empresa,
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


@router.get("/auditoria/verify-chain", summary="Verificar integridad de la cadena de auditor├¡a")
async def verificar_cadena_auditoria(
    limit: int = Query(1000, description="L├¡mite de registros a verificar"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Verifica la integridad de la cadena de hashes de auditor├¡a.
    Retorna estado de validaci├│n y el ID del primer registro roto (si hay).
    """
    from app.services.audit_service import verify_audit_chain

    result = verify_audit_chain(db, limit=limit)
    return result


# ÔöÇÔöÇ Exportaci├│n ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ

@router.get("/export/csv", summary="Exportar RAT a CSV")
async def exportar_a_csv(
    company_id: int = Query(..., description="ID de la empresa"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")
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
    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")
    rats = get_rats(db, company_id)
    company = get_company(db, company_id)
    contenido = exportar_pdf(rats, company)
    filename = _safe_filename(f"RAT_{company.nombre}_{company.rut}.pdf")
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
    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if rat.company_id not in ids:
            raise HTTPException(status_code=403, detail="No tiene acceso a este RAT.")
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
    if not current_user.rol_global == "superadmin":
        ids = get_empresas_usuario(db, current_user.id)
        if company_id not in ids:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")
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
