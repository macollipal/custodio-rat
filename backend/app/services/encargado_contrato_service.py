"""
Lógica de negocio para Contratos de Encargado del Tratamiento (Art. 14 quater Ley 21.719 — REC-03).
"""
import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.encargado_contrato import EncargadoContrato
from app.schemas.encargado_contrato import EncargadoContratoCreate, EncargadoContratoUpdate


class ContratoNotFoundError(Exception):
    pass


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


def _calcular_fecha_alerta(duracion_fin: datetime) -> Optional[datetime]:
    if duracion_fin.tzinfo is None:
        duracion_fin = duracion_fin.replace(tzinfo=timezone.utc)
    return duracion_fin - timedelta(days=60)


def _transform_to_out(c: EncargadoContrato):
    from app.schemas.encargado_contrato import EncargadoContratoOut
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


def listar_contratos(
    db: Session,
    company_id: int,
    rat_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[EncargadoContrato], int]:
    q = db.query(EncargadoContrato).filter(EncargadoContrato.company_id == company_id)
    if rat_id is not None:
        q = q.filter(EncargadoContrato.rat_id == rat_id)
    total = q.count()
    contratos = q.offset(skip).limit(limit).all()
    return contratos, total


def obtener_contrato(db: Session, contrato_id: int) -> EncargadoContrato:
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise ContratoNotFoundError("Contrato no encontrado.")
    return c


def crear_contrato(db: Session, data: EncargadoContratoCreate, usuario: str):
    datos = data.model_dump()
    archivo_fields = _procesar_archivo(datos)
    datos.update(archivo_fields)
    datos.pop("archivo_pdf_base64", None)

    duracion_fin = datos.get("duracion_fin")
    if duracion_fin:
        if isinstance(duracion_fin, str):
            duracion_fin = datetime.fromisoformat(duracion_fin.replace("Z", "+00:00"))
        datos["fecha_alerta_vencimiento"] = _calcular_fecha_alerta(duracion_fin)

    contrato = EncargadoContrato(**datos, created_by=usuario)
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


def actualizar_contrato(db: Session, contrato_id: int, data: EncargadoContratoUpdate):
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise ContratoNotFoundError("Contrato no encontrado.")

    cambios = data.model_dump(exclude_none=True)
    archivo_fields = _procesar_archivo(cambios)
    cambios.update(archivo_fields)
    cambios.pop("archivo_pdf_base64", None)

    if "duracion_fin" in cambios:
        duracion_fin = cambios["duracion_fin"]
        if isinstance(duracion_fin, str):
            duracion_fin = datetime.fromisoformat(duracion_fin.replace("Z", "+00:00"))
        cambios["fecha_alerta_vencimiento"] = _calcular_fecha_alerta(duracion_fin)

    for field, value in cambios.items():
        setattr(c, field, value)

    db.commit()
    db.refresh(c)
    return c


def eliminar_contrato(db: Session, contrato_id: int) -> None:
    c = db.query(EncargadoContrato).filter(EncargadoContrato.id == contrato_id).first()
    if not c:
        raise ContratoNotFoundError("Contrato no encontrado.")
    db.delete(c)
    db.commit()