"""
Endpoints CRUD para empresas (responsables del tratamiento).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.schemas.company import CompanyCreate, CompanyOut, CompanyPublicOut, CompanyUpdate, CompanyListResponse
from app.services.company_service import (
    create_company, delete_company, deactivate_company, get_companies, get_company,
    reactivate_company, update_company,
)
from app.services.user_company_service import get_empresas_usuario, get_rol_usuario
from app.routes.deps import get_current_user, require_admin, get_client_ip, check_company_access
from app.models.rat import RAT as RATModel
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho, EstadoTicket
from app.models.politica_transparencia import PoliticaTransparencia
from app.services.rat_calculations import calcular_completitud, rat_to_dict

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.get("/publico", response_model=list[CompanyPublicOut], summary="Listar empresas públicas (requiere autenticación)")
async def listar_publico(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.company import Company
    companies = db.query(Company).filter(Company.activa).order_by(Company.nombre).all()
    return companies


@router.get("/", response_model=CompanyListResponse, summary="Listar empresas")
async def listar(
    skip: int = 0,
    limit: int = 200,
    incluir_inactivas: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "superadmin":
        companies, total = get_companies(db, skip, limit, incluir_inactivas=incluir_inactivas)
    else:
        ids = get_empresas_usuario(db, current_user.id)
        from app.models.company import Company as CompanyModel
        query = db.query(CompanyModel).filter(CompanyModel.id.in_(ids))
        if not incluir_inactivas:
            query = query.filter(CompanyModel.activa)
        count_total = query.count()
        companies = query.offset(skip).limit(limit).all()
        total = count_total

    count_q = (
        db.query(RATModel.company_id, func.count(RATModel.id).label("cnt"))
        .group_by(RATModel.company_id)
        .subquery()
    )
    rat_counts = {row.company_id: row.cnt for row in db.query(count_q).all()}

    rats_by_company = {}
    for rat in db.query(RATModel).filter(RATModel.company_id.in_([c.id for c in companies])).all():
        rats_by_company.setdefault(rat.company_id, []).append(rat)

    from datetime import datetime, timezone, timedelta
    import re

    company_ids = [c.id for c in companies]
    now = datetime.now(timezone.utc)
    estados_pendientes = [EstadoTicket.ABIERTO.value, EstadoTicket.EN_PROCESO.value, EstadoTicket.PENDIENTE.value]
    all_pending = (
        db.query(TktSolicitudDerecho.company_id, func.count(TktSolicitudDerecho.id))
        .filter(
            TktSolicitudDerecho.company_id.in_(company_ids),
            TktSolicitudDerecho.estado.in_(estados_pendientes),
        )
        .group_by(TktSolicitudDerecho.company_id)
        .all()
    )
    pending_by_company = {cid: cnt for cid, cnt in all_pending}
    all_vencidas = (
        db.query(TktSolicitudDerecho.company_id, func.count(TktSolicitudDerecho.id))
        .filter(
            TktSolicitudDerecho.company_id.in_(company_ids),
            TktSolicitudDerecho.fecha_vencimiento < now,
            TktSolicitudDerecho.estado != EstadoTicket.RESUELTO.value,
        )
        .group_by(TktSolicitudDerecho.company_id)
        .all()
    )
    vencidas_by_company = {cid: cnt for cid, cnt in all_vencidas}

    politicas_exists = {
        row.company_id for row in
        db.query(PoliticaTransparencia.company_id).filter(
            PoliticaTransparencia.company_id.in_(company_ids)
        ).all()
    }

    result = []
    for c in companies:
        out = CompanyOut.model_validate(c)
        out.total_rats = rat_counts.get(c.id, 0)
        rats = rats_by_company.get(c.id, [])

        if rats:
            out.completitud_promedio = round(sum(calcular_completitud(rat_to_dict(r)) for r in rats) / len(rats))
            vencidos = 0
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
                    vencidos += 1
            out.rats_vencidos = vencidos
        else:
            out.completitud_promedio = 0
            out.rats_vencidos = 0

        out.solicitudes_pendientes = pending_by_company.get(c.id, 0)
        out.solicitudes_vencidas_sla = vencidas_by_company.get(c.id, 0)
        out.has_politica_transparencia = c.id in politicas_exists
        if current_user.rol_global != "superadmin":
            rol = get_rol_usuario(db, current_user.id, c.id)
            out.mi_rol = rol.value if rol else None
        result.append(out)
    return CompanyListResponse(empresas=result, total=total, skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyOut, summary="Obtener empresa por ID")
async def obtener(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    c = get_company(db, company_id)
    out = CompanyOut.model_validate(c)
    rats = c.rats
    out.total_rats = len(rats)

    if rats:
        out.completitud_promedio = round(sum(calcular_completitud(rat_to_dict(r)) for r in rats) / len(rats))
        from datetime import datetime, timezone, timedelta
        import re
        vencidos = 0
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
                vencidos += 1
        out.rats_vencidos = vencidos
    else:
        out.completitud_promedio = 0
        out.rats_vencidos = 0

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    estados_pendientes = [EstadoTicket.ABIERTO.value, EstadoTicket.EN_PROCESO.value, EstadoTicket.PENDIENTE.value]
    tickets = db.query(TktSolicitudDerecho).filter(
        TktSolicitudDerecho.company_id == company_id,
        TktSolicitudDerecho.estado.in_(estados_pendientes),
    ).all()
    out.solicitudes_pendientes = len(tickets)
    out.solicitudes_vencidas_sla = db.query(TktSolicitudDerecho).filter(
        TktSolicitudDerecho.company_id == company_id,
        TktSolicitudDerecho.fecha_vencimiento < now,
        TktSolicitudDerecho.estado != EstadoTicket.RESUELTO.value,
    ).count()

    out.has_politica_transparencia = db.query(PoliticaTransparencia).filter(
        PoliticaTransparencia.company_id == company_id
    ).first() is not None

    if current_user.rol_global != "superadmin":
        rol = get_rol_usuario(db, current_user.id, c.id)
        out.mi_rol = rol.value if rol else None
    return out


@router.patch("/{company_id}/desactivar", response_model=CompanyOut, summary="Desactivar empresa (soft delete)")
async def desactivar(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    return deactivate_company(db, company_id, current_user.username, get_client_ip(request))


@router.patch("/{company_id}/reactivar", response_model=CompanyOut, summary="Reactivar empresa desactivada")
async def reactivar(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.user import RolGlobal
    if current_user.rol_global != RolGlobal.SUPERADMIN.value:
        raise HTTPException(status_code=403, detail="Solo superadmin puede reactivar empresas.")
    return reactivate_company(db, company_id, current_user.username, get_client_ip(request))


@router.post("/", response_model=CompanyOut, status_code=201, summary="Crear empresa")
async def crear(
    request: Request,
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return create_company(db, data, current_user.username, get_client_ip(request))


@router.put("/{company_id}", response_model=CompanyOut, summary="Actualizar empresa")
async def actualizar(
    request: Request,
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    return update_company(db, company_id, data, current_user.username, get_client_ip(request))


@router.delete("/{company_id}", summary="Eliminar empresa")
async def eliminar(
    request: Request,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    check_company_access(current_user, company_id, db)
    return delete_company(db, company_id, current_user.username, get_client_ip(request))
