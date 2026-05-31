"""
Endpoints para Brechas de Seguridad (Art. 14 bis Ley 21.719).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.breach import BreachCreate, BreachOut, BreachUpdate
from app.services.breach_service import (
    listar_brechas, get_breach, crear_brecha, actualizar_brecha, eliminar_brecha, _enriquecer,
)
from app.services.user_company_service import get_empresas_usuario
from app.routes.deps import get_current_user

router = APIRouter(prefix="/brechas", tags=["Brechas de Seguridad"])


def _check_company_access(current_user, company_id: int, db: Session):
    if current_user.rol_global == "superadmin":
        return
    if company_id not in get_empresas_usuario(db, current_user.id):
        raise HTTPException(status_code=403, detail="No tiene acceso a esta empresa.")


def _out(b) -> BreachOut:
    out = BreachOut.model_validate(b)
    extra = _enriquecer(b)
    out.horas_desde_deteccion = extra["horas_desde_deteccion"]
    out.plazo_apdc_vencido = extra["plazo_apdc_vencido"]
    return out


@router.get("/", summary="Listar brechas de seguridad")
async def listar(
    company_id: int = Query(..., description="ID de la empresa"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_company_access(current_user, company_id, db)
    brechas, total = listar_brechas(db, company_id, skip=skip, limit=limit)
    return {"brechas": [_out(b) for b in brechas], "total": total, "skip": skip, "limit": limit}


@router.get("/{breach_id}", response_model=BreachOut, summary="Obtener brecha por ID")
async def obtener(
    breach_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    b = get_breach(db, breach_id)
    _check_company_access(current_user, b.company_id, db)
    return _out(b)


@router.post("/", response_model=BreachOut, status_code=201, summary="Registrar nueva brecha")
async def crear(
    data: BreachCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _check_company_access(current_user, data.company_id, db)
    b = crear_brecha(db, data, current_user.username)
    return _out(b)


@router.put("/{breach_id}", response_model=BreachOut, summary="Actualizar brecha")
async def actualizar(
    breach_id: int,
    data: BreachUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    b = get_breach(db, breach_id)
    _check_company_access(current_user, b.company_id, db)
    b = actualizar_brecha(db, breach_id, data)
    return _out(b)


@router.delete("/{breach_id}", summary="Eliminar brecha")
async def eliminar(
    breach_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    b = get_breach(db, breach_id)
    _check_company_access(current_user, b.company_id, db)
    eliminar_brecha(db, breach_id)
    return {"message": "Brecha eliminada correctamente."}