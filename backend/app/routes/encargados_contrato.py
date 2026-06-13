"""
CRUD para Contratos de Encargado del Tratamiento (Art. 14 quater Ley 21.719 — REC-03).
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.encargado_contrato import (
    EncargadoContratoCreate, EncargadoContratoUpdate, EncargadoContratoOut,
    EncargadoContratoListResponse,
)
from app.schemas.common import MessageResponse
from app.routes.deps import get_current_user, check_company_access
from app.services import encargado_contrato_service as svc

router = APIRouter(prefix="/encargados-contrato", tags=["Contratos de Encargado"])


@router.get("/", response_model=EncargadoContratoListResponse, summary="Listar contratos de encargado")
async def listar(
    company_id: int,
    rat_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    contratos, total = svc.listar_contratos(db, company_id, rat_id, skip, limit)
    return EncargadoContratoListResponse(
        contratos=[svc._transform_to_out(c) for c in contratos],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{contrato_id}", response_model=EncargadoContratoOut, summary="Obtener contrato por ID")
async def obtener(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = svc.obtener_contrato(db, contrato_id)
    except svc.ContratoNotFoundError:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)
    return svc._transform_to_out(c)


@router.post("/", response_model=EncargadoContratoOut, status_code=201, summary="Crear contrato de encargado (REC-03)")
async def crear(
    data: EncargadoContratoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, data.company_id, db)
    contrato = svc.crear_contrato(db, data, current_user.username)
    return svc._transform_to_out(contrato)


@router.put("/{contrato_id}", response_model=EncargadoContratoOut, summary="Actualizar contrato de encargado")
async def actualizar(
    contrato_id: int,
    data: EncargadoContratoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = svc.actualizar_contrato(db, contrato_id, data)
    except svc.ContratoNotFoundError:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)
    return svc._transform_to_out(c)


@router.delete("/{contrato_id}", response_model=MessageResponse, summary="Eliminar contrato de encargado")
async def eliminar(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        c = svc.obtener_contrato(db, contrato_id)
    except svc.ContratoNotFoundError:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)
    svc.eliminar_contrato(db, contrato_id)
    return MessageResponse(message="Contrato eliminado correctamente.")