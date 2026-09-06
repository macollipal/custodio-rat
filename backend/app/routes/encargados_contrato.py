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


def _notificar_si_cerca_vencer(db: Session, contrato) -> None:
    """Si el contrato vence en <= 30 días o ya venció, notifica al DPO."""
    from datetime import datetime, timedelta, timezone
    from app.models.company import Company
    from app.services.email_service import notificar_vencimiento_encargado, EmailError

    if not contrato.duracion_fin:
        return
    ahora = datetime.now(timezone.utc)
    umbral = ahora + timedelta(days=30)
    if contrato.duracion_fin > umbral:
        return
    empresa = db.query(Company).filter(Company.id == contrato.company_id).first()
    if not empresa or not empresa.email_dpo:
        return
    dias = (contrato.duracion_fin - ahora).days
    try:
        notificar_vencimiento_encargado(
            email_dpo=empresa.email_dpo,
            nombre_dpo=empresa.contacto_dpo or "",
            nombre_empresa=empresa.nombre,
            nombre_encargado=contrato.nombre_encargado,
            finalidad=contrato.finalidad or "",
            dias_restantes=dias,
        )
    except EmailError as e:
        import logging
        logging.getLogger(__name__).error(f"Encargado contrato {contrato.id}: fallo enviando notificación: {e}")


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
    from app.routes.deps import require_editor_or_admin_empresa
    require_editor_or_admin_empresa(data.company_id, db, current_user)
    contrato = svc.crear_contrato(db, data, current_user.username)
    _notificar_si_cerca_vencer(db, contrato)
    return svc._transform_to_out(contrato)


@router.put("/{contrato_id}", response_model=EncargadoContratoOut, summary="Actualizar contrato de encargado")
async def actualizar(
    contrato_id: int,
    data: EncargadoContratoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        existing = svc.obtener_contrato(db, contrato_id)
    except svc.ContratoNotFoundError:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, existing.company_id, db)
    from app.routes.deps import require_editor_or_admin_empresa
    require_editor_or_admin_empresa(existing.company_id, db, current_user)
    try:
        c = svc.actualizar_contrato(db, contrato_id, data)
    except svc.ContratoNotFoundError:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    _notificar_si_cerca_vencer(db, c)
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
    from app.routes.deps import require_editor_or_admin_empresa
    require_editor_or_admin_empresa(c.company_id, db, current_user)
    svc.eliminar_contrato(db, contrato_id)
    return MessageResponse(message="Contrato eliminado correctamente.")