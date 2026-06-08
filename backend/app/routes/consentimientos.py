"""
Endpoints para gestión de Consentimientos (Art. 12 Ley 21.719).
CRUD completo: listar, crear, ver, revocar.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.consentimiento import Consentimiento
from app.models.rat import RAT as RATModel
from app.schemas.consentimiento import (
    ConsentimientoCreate, ConsentimientoOut,
)
from app.services.audit_service import log_audit

router = APIRouter(prefix="/consentimientos", tags=["Consentimientos"])


def _get_user():
    from app.routes.deps import get_current_user as _u
    return _u()


def _check_access(user, company_id, db):
    from app.routes.deps import _check_access as _ca
    return _ca(user, company_id, db)





@router.get("/", summary="Listar consentimientos de la empresa")
async def listar_consentimientos(
    company_id: int = Query(..., description="ID de la empresa"),
    rat_id: Optional[int] = None,
    solo_activos: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Lista todos los consentimientos registrados para una empresa."""
    _check_access(current_user, company_id, db)

    q = db.query(Consentimiento).filter(Consentimiento.company_id == company_id)
    if rat_id is not None:
        q = q.filter(Consentimiento.rat_id == rat_id)
    if solo_activos:
        q = q.filter(Consentimiento.activo == True)

    total = q.count()
    items = q.order_by(Consentimiento.fecha_obtencion.desc()).offset(skip).limit(limit).all()

    return {
        "consentimientos": [ConsentimientoOut.model_validate(c).model_dump() for c in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{consentimiento_id}", response_model=ConsentimientoOut, summary="Detalle de un consentimiento")
async def obtener_consentimiento(
    consentimiento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consentimiento no encontrado.")
    _check_access(current_user, c.company_id, db)
    return c


@router.post("/", response_model=ConsentimientoOut, status_code=201, summary="Crear consentimiento")
async def crear_consentimiento(
    data: ConsentimientoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Crea un nuevo consentimiento. Valida que el RAT exista y pertenezca a la empresa del usuario."""
    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise HTTPException(status_code=404, detail="RAT no encontrado.")
    _check_access(current_user, rat.company_id, db)

    c = Consentimiento(
        company_id=rat.company_id,
        rat_id=data.rat_id,
        nombre_titular=data.nombre_titular,
        email_titular=data.email_titular,
        canal=data.canal,
        texto_consentimiento=data.texto_consentimiento,
        fecha_obtencion=data.fecha_obtencion,
        ip_origen=data.ip_origen,
        activo=True,
    )
    db.add(c)
    db.flush()
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="create",
        usuario=current_user.username,
        detalle={"rat_id": data.rat_id, "titular": data.nombre_titular, "canal": data.canal},
    )
    db.commit()
    db.refresh(c)
    return c


@router.post("/{consentimiento_id}/revocar", response_model=ConsentimientoOut, summary="Revocar consentimiento")
async def revocar_consentimiento(
    consentimiento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(_get_user),
):
    """Marca un consentimiento como revocado (Art. 12 Ley 21.719)."""
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Consentimiento no encontrado.")
    _check_access(current_user, c.company_id, db)
    if c.fecha_revocacion:
        raise HTTPException(status_code=400, detail="El consentimiento ya fue revocado.")

    c.activo = False
    c.fecha_revocacion = datetime.now(timezone.utc)
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="revocar",
        usuario=current_user.username,
        detalle={"rat_id": c.rat_id, "titular": c.nombre_titular},
    )
    db.commit()
    db.refresh(c)
    return c
