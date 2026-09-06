"""
Endpoints para Evaluación de Impacto en Protección de Datos (EIPD / DPIA).
Art. 15 bis Ley 21.719.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.eipd import EIPDCreate, EIPDOut, EIPDUpdate, EIPDListResponse
from app.routes.deps import get_current_user, check_company_access
from app.services import eipd_service

router = APIRouter(prefix="/eipd", tags=["EIPD"])


@router.get("/", response_model=EIPDListResponse, summary="Listar EIPDs de la empresa")
async def listar_eipds(
    company_id: int = Query(..., description="ID de la empresa"),
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, company_id, db)
    items, total = eipd_service.listar_eipds(db, company_id, estado, skip, limit)
    return EIPDListResponse(
        eipds=[EIPDOut.model_validate(e) for e in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/rat/{rat_id}", response_model=EIPDOut, summary="Obtener EIPD de un RAT")
async def obtener_eipd_por_rat(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.rat import RAT as RATModel

    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    check_company_access(current_user, rat.company_id, db)
    try:
        return eipd_service.obtener_eipd_por_rat(db, rat_id)
    except eipd_service.EIPDNotFoundError:
        raise HTTPException(status_code=404, detail="EIPD no encontrado para este RAT.")


@router.post("/", response_model=EIPDOut, status_code=201, summary="Crear EIPD para un RAT")
async def crear_eipd(
    data: EIPDCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.rat import RAT as RATModel

    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    check_company_access(current_user, rat.company_id, db)
    try:
        eipd = eipd_service.crear_eipd(db, data, current_user.username)
        return eipd
    except eipd_service.RATNotFoundError:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    except eipd_service.EIPDJaExisteError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except eipd_service.ResultadoInvalidoError as e:
        raise HTTPException(status_code=400, detail=f"Resultado inválido. Valores permitidos: {e.valores_permitidos}")


@router.put("/{eipd_id}", response_model=EIPDOut, summary="Actualizar EIPD")
async def actualizar_eipd(
    eipd_id: int,
    data: EIPDUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.rat import RAT as RATModel
    from app.models.eipd import EIPD

    eipd_existing = db.query(EIPD).filter(EIPD.id == eipd_id).first()
    if not eipd_existing:
        raise HTTPException(status_code=404, detail="EIPD no encontrado.")
    rat = db.query(RATModel).filter(RATModel.id == eipd_existing.rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT asociado a esta EIPD no encontrado.")
    check_company_access(current_user, rat.company_id, db)
    try:
        eipd = eipd_service.actualizar_eipd(db, eipd_id, data, current_user.username)
        return eipd
    except eipd_service.EIPDNotFoundError:
        raise HTTPException(status_code=404, detail="EIPD no encontrado.")
    except eipd_service.ResultadoInvalidoError as e:
        raise HTTPException(status_code=400, detail=f"Resultado inválido. Valores permitidos: {e.valores_permitidos}")