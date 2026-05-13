"""
Endpoints CRUD para empresas (responsables del tratamiento).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate
from app.services.company_service import (
    create_company, delete_company, get_companies, get_company, update_company
)
from app.services.user_company_service import get_empresas_usuario, get_rol_usuario
from app.routes.deps import get_current_user, require_admin
from app.models.rat import RAT as RATModel

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.get("/", response_model=list[CompanyOut], summary="Listar empresas")
async def listar(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.rol_global == "superadmin":
        companies = get_companies(db, skip, limit)
    else:
        ids = get_empresas_usuario(db, current_user.id)
        from app.models.company import Company as CompanyModel
        companies = db.query(CompanyModel).filter(CompanyModel.id.in_(ids)).offset(skip).limit(limit).all()

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
    return result


@router.get("/{company_id}", response_model=CompanyOut, summary="Obtener empresa por ID")
async def obtener(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    c = get_company(db, company_id)
    out = CompanyOut.model_validate(c)
    out.total_rats = len(c.rats)
    if current_user.rol_global != "superadmin":
        rol = get_rol_usuario(db, current_user.id, c.id)
        out.mi_rol = rol.value if rol else None
    return out


@router.post("/", response_model=CompanyOut, status_code=201, summary="Crear empresa")
async def crear(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return create_company(db, data, current_user.username)


@router.put("/{company_id}", response_model=CompanyOut, summary="Actualizar empresa")
async def actualizar(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Permite: admin global o admin_empresa con rol admin en la empresa
    if current_user.rol_global not in ("superadmin", "admin_empresa"):
        from app.models.user_company import RolEmpresa
        rol = get_rol_usuario(db, current_user.id, company_id)
        if rol != RolEmpresa.ADMIN:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Se requiere rol administrador en esta empresa.")
    return update_company(db, company_id, data, current_user.username)


@router.delete("/{company_id}", summary="Eliminar empresa")
async def eliminar(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return delete_company(db, company_id, current_user.username)
