"""
CRUD para Contratos de Encargado del Tratamiento (Art. 14 quater Ley 21.719 — REC-03).
"""

import base64
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.encargado_contrato import EncargadoContrato
from app.schemas.encargado_contrato import (
    EncargadoContratoCreate, EncargadoContratoUpdate, EncargadoContratoOut,
    EncargadoContratoListResponse,
)
from app.schemas.common import MessageResponse
from app.routes.deps import get_current_user, check_company_access

router = APIRouter(prefix="/encargados-contrato", tags=["Contratos de Encargado"])


def _procesar_archivo(data: dict) -> dict:
    base64_str = data.get("archivo_pdf_base64")
    if not base64_str:
        return {}
    try:
        datos = base64.b64decode(base64_str)
    except Exception:
        return {}
    from app.core.crypto import encrypt
    datos_cifrados = encrypt(datos)
    hash_val = hashlib.sha256(datos).hexdigest()
    return {
        "archivo_pdf_datos": datos_cifrados,
        "archivo_pdf_hash": hash_val,
        "archivo_pdf_nombre": data.get("archivo_pdf_nombre"),
        "archivo_pdf_tipo": data.get("archivo_pdf_tipo"),
    }


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
    q = db.query(EncargadoContrato).filter(EncargadoContrato.company_id == company_id)
    if rat_id is not None:
        q = q.filter(EncargadoContrato.rat_id == rat_id)
    total = q.count()
    contratos = q.offset(skip).limit(limit).all()
    return EncargadoContratoListResponse(
        contratos=[_out(c) for c in contratos],
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
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)
    return _out(c)


@router.post("/", response_model=EncargadoContratoOut, status_code=201, summary="Crear contrato de encargado (REC-03)")
async def crear(
    data: EncargadoContratoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    check_company_access(current_user, data.company_id, db)
    datos = data.model_dump()
    archivo_fields = _procesar_archivo(datos)
    datos.update(archivo_fields)
    datos.pop("archivo_pdf_base64", None)

    from datetime import timedelta, datetime, timezone
    duracion_fin = datos.get("duracion_fin")
    fecha_alerta = None
    if duracion_fin:
        if isinstance(duracion_fin, str):
            duracion_fin = datetime.fromisoformat(duracion_fin.replace("Z", "+00:00"))
        if duracion_fin.tzinfo is None:
            duracion_fin = duracion_fin.replace(tzinfo=timezone.utc)
        fecha_alerta = duracion_fin - timedelta(days=60)
        datos["fecha_alerta_vencimiento"] = fecha_alerta

    contrato = EncargadoContrato(
        **datos,
        created_by=current_user.username,
    )
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return _out(contrato)


@router.put("/{contrato_id}", response_model=EncargadoContratoOut, summary="Actualizar contrato de encargado")
async def actualizar(
    contrato_id: int,
    data: EncargadoContratoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)

    cambios = data.model_dump(exclude_none=True)
    archivo_fields = _procesar_archivo(cambios)
    cambios.update(archivo_fields)
    cambios.pop("archivo_pdf_base64", None)

    for field, value in cambios.items():
        setattr(c, field, value)

    db.commit()
    db.refresh(c)
    return _out(c)


@router.delete("/{contrato_id}", response_model=MessageResponse, summary="Eliminar contrato de encargado")
async def eliminar(
    contrato_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contrato no encontrado.")
    check_company_access(current_user, c.company_id, db)
    db.delete(c)
    db.commit()
    return MessageResponse(message="Contrato eliminado correctamente.")


def _out(c: EncargadoContrato) -> EncargadoContratoOut:
    return EncargadoContratoOut(
        id=c.id,
        company_id=c.company_id,
        rat_id=c.rat_id,
        nombre_encargado=c.nombre_encargado,
        objeto=c.objeto,
        duracion_inicio=c.duracion_inicio,
        duracion_fin=c.duracion_fin,
        finalidad=c.finalidad,
        tipo_datos=c.tipo_datos,
        categorias_titulares=c.categorias_titulares,
        derechos_obligaciones=c.derechos_obligaciones,
        tiene_archivo=bool(c.archivo_pdf_datos),
        activo=c.activo,
        fecha_alerta_vencimiento=c.fecha_alerta_vencimiento,
        created_by=c.created_by,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )
