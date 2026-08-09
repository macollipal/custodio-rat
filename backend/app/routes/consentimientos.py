"""
Endpoints para gestión de Consentimientos (Art. 12 Ley 21.719).
CRUD completo: listar, crear, ver, revocar.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.consentimiento import (
    ConsentimientoCreate, ConsentimientoOut, ConsentimientoListResponse,
)
from app.routes.deps import get_current_user, check_company_access
from app.services import consentimiento_service

router = APIRouter(prefix="/consentimientos", tags=["Consentimientos"])


@router.get("/", response_model=ConsentimientoListResponse, summary="Listar consentimientos de la empresa")
async def listar_consentimientos(
    company_id: int = Query(..., description="ID de la empresa"),
    rat_id: Optional[int] = None,
    solo_activos: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    items, total = consentimiento_service.listar_consentimientos(
        db, company_id, rat_id, solo_activos, skip, limit
    )
    return ConsentimientoListResponse(
        consentimientos=[ConsentimientoOut.from_orm_cifrado(c) for c in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{consentimiento_id}", response_model=ConsentimientoOut, summary="Detalle de un consentimiento")
async def obtener_consentimiento(
    consentimiento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = consentimiento_service.obtener_consentimiento(db, consentimiento_id)
    except consentimiento_service.ConsentimientoNotFoundError:
        raise HTTPException(status_code=404, detail="Consentimiento no encontrado.")
    check_company_access(current_user, c.company_id, db)
    return ConsentimientoOut.from_orm_cifrado(c)


@router.post("/", response_model=ConsentimientoOut, status_code=201, summary="Crear consentimiento")
async def crear_consentimiento(
    data: ConsentimientoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = consentimiento_service.crear_consentimiento(db, data, current_user.username)
        check_company_access(current_user, c.company_id, db)
        return ConsentimientoOut.from_orm_cifrado(c)
    except consentimiento_service.RATNotFoundError:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")


@router.post("/{consentimiento_id}/revocar", response_model=ConsentimientoOut, summary="Revocar consentimiento")
async def revocar_consentimiento(
    consentimiento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = consentimiento_service.revocar_consentimiento(db, consentimiento_id, current_user.username)
    except consentimiento_service.ConsentimientoNotFoundError:
        raise HTTPException(status_code=404, detail="Consentimiento no encontrado.")
    check_company_access(current_user, c.company_id, db)
    return ConsentimientoOut.from_orm_cifrado(c)