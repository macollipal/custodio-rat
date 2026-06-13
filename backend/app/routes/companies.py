"""
Endpoints CRUD para empresas (responsables del tratamiento).
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.schemas.company import CompanyCreate, CompanyOut, CompanyPublicOut, CompanyUpdate, CompanyListResponse
from app.services.company_service import (
    create_company, delete_company, get_companies, get_company, update_company
)
from app.services.user_company_service import get_empresas_usuario, get_rol_usuario
from app.routes.deps import get_current_user, require_admin, get_client_ip, check_company_access
from app.models.rat import RAT as RATModel

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.get("/publico", response_model=list[CompanyPublicOut], summary="Listar empresas públicas (requiere autenticación)")
async def listar_publico(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.company import Company
    companies = db.query(Company).order_by(Company.nombre).all()
    return companies


@router.get("/", response_model=CompanyListResponse, summary="Listar empresas")
async def listar(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "superadmin":
        companies, total = get_companies(db, skip, limit)
    else:
        ids = get_empresas_usuario(db, current_user.id)
        from app.models.company import Company as CompanyModel
        count_total = db.query(CompanyModel).filter(CompanyModel.id.in_(ids)).count()
        companies = db.query(CompanyModel).filter(CompanyModel.id.in_(ids)).offset(skip).limit(limit).all()
        total = count_total

    count_q = (
        db.query(RATModel.company_id, func.count(RATModel.id).label("cnt"))
        .group_by(RATModel.company_id)
        .subquery()
    )
    rat_counts = {row.company_id: row.cnt for row in db.query(count_q).all()}

    result = []
    for c in companies:
        out = CompanyOut.model_validate(c)
        out.total_rats = rat_counts.get(c.id, 0)
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
    out.total_rats = len(c.rats)
    if current_user.rol_global != "superadmin":
        rol = get_rol_usuario(db, current_user.id, c.id)
        out.mi_rol = rol.value if rol else None
    return out


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
