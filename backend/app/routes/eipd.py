"""
Endpoints para Evaluación de Impacto en Protección de Datos (EIPD / DPIA).
Art. 15 bis Ley 21.719.
"""
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.eipd import EIPD, ResultadoEIPD
from app.models.rat import RAT as RATModel
from app.schemas.eipd import EIPDCreate, EIPDOut, EIPDUpdate
from app.services.audit_service import log_audit

router = APIRouter(prefix="/eipd", tags=["EIPD"])


def _get_user():
    from app.routes.deps import get_current_user as _u
    return _u()


def _check_access(user, company_id, db):
    from app.routes.deps import _check_access as _ca
    return _ca(user, company_id, db)


@router.get("/", summary="Listar EIPDs de la empresa")
async def listar_eipds(
    company_id: int = Query(..., description="ID de la empresa"),
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Lista todos los EIPDs registrados para RATs de la empresa."""
    _check_access(current_user, company_id, db)

    q = (
        db.query(EIPD)
        .join(RATModel, EIPD.rat_id == RATModel.id)
        .filter(RATModel.company_id == company_id)
    )
    if estado:
        q = q.filter(EIPD.resultado == estado)

    total = q.count()
    items = q.order_by(EIPD.updated_at.desc()).offset(skip).limit(limit).all()

    return {
        "eipds": [EIPDOut.model_validate(e).model_dump() for e in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/rat/{rat_id}", response_model=EIPDOut, summary="Obtener EIPD de un RAT")
async def obtener_eipd_por_rat(
    rat_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    __check_access(current_user, rat.company_id, db)

    eipd = db.query(EIPD).filter(EIPD.rat_id == rat_id).first()
    if not eipd:
        raise HTTPException(status_code=404, detail="EIPD no encontrado para este RAT.")
    return eipd


@router.post("/", response_model=EIPDOut, status_code=201, summary="Crear EIPD para un RAT")
async def crear_eipd(
    data: EIPDCreate,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    __check_access(current_user, rat.company_id, db)

    existing = db.query(EIPD).filter(EIPD.rat_id == data.rat_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un EIPD para este RAT. Use PUT para actualizar.")

    try:
        resultado = ResultadoEIPD(data.resultado)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Resultado inválido. Valores permitidos: {[r.value for r in ResultadoEIPD]}")

    eipd = EIPD(
        rat_id=data.rat_id,
        metodologia=data.metodologia,
        objetivos=data.objetivos,
        necesidad_proporcionalidad=data.necesidad_proporcionalidad,
        riesgos_identificados=data.riesgos_identificados,
        medidas_propuestas=data.medidas_propuestas,
        parecer_dpo=data.parecer_dpo,
        fecha_elaboracion=data.fecha_elaboracion,
        fecha_aprobacion=data.fecha_aprobacion,
        resultado=resultado,
        created_by=current_user.username,
    )
    db.add(eipd)
    db.flush()
    log_audit(
        db=db,
        entidad="eipd",
        entidad_id=eipd.id,
        accion="create",
        usuario=current_user.username,
        detalle={"rat_id": data.rat_id, "resultado": data.resultado},
    )
    db.commit()
    db.refresh(eipd)
    return eipd


@router.put("/{eipd_id}", response_model=EIPDOut, summary="Actualizar EIPD")
async def actualizar_eipd(
    eipd_id: int,
    data: EIPDUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    eipd = db.query(EIPD).filter(EIPD.id == eipd_id).first()
    if not eipd:
        raise HTTPException(status_code=404, detail="EIPD no encontrado.")

    rat = db.query(RATModel).filter(RATModel.id == eipd.rat_id).first()
    if rat:
        __check_access(current_user, rat.company_id, db)

    cambios = data.model_dump(exclude_none=True)
    if "resultado" in cambios:
        try:
            cambios["resultado"] = ResultadoEIPD(cambios["resultado"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Resultado inválido")

    for field, value in cambios.items():
        setattr(eipd, field, value)

    log_audit(
        db=db,
        entidad="eipd",
        entidad_id=eipd.id,
        accion="update",
        usuario=current_user.username,
        detalle={"rat_id": eipd.rat_id, "campos": list(cambios.keys())},
    )
    db.commit()
    db.refresh(eipd)
    return eipd
