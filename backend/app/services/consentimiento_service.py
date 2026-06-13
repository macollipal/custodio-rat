"""
Lógica de negocio para Consentimientos (Art. 12 Ley 21.719).
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.consentimiento import Consentimiento
from app.models.rat import RAT as RATModel
from app.schemas.consentimiento import ConsentimientoCreate
from app.services.audit_service import log_audit


class ConsentimientoNotFoundError(Exception):
    pass


class RATNotFoundError(Exception):
    pass


class ConsentimientoYaRevocadoError(Exception):
    pass


def listar_consentimientos(
    db: Session,
    company_id: int,
    rat_id: Optional[int] = None,
    solo_activos: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Consentimiento], int]:
    q = db.query(Consentimiento).filter(Consentimiento.company_id == company_id)
    if rat_id is not None:
        q = q.filter(Consentimiento.rat_id == rat_id)
    if solo_activos:
        q = q.filter(Consentimiento.activo == True)

    total = q.count()
    items = q.order_by(Consentimiento.fecha_obtencion.desc()).offset(skip).limit(limit).all()
    return items, total


def obtener_consentimiento(db: Session, consentimiento_id: int) -> Consentimiento:
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise ConsentimientoNotFoundError("Consentimiento no encontrado.")
    return c


def crear_consentimiento(db: Session, data: ConsentimientoCreate, usuario: str) -> Consentimiento:
    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise RATNotFoundError("RAT no encontrado.")

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
        usuario=usuario,
        detalle={"rat_id": data.rat_id, "titular": data.nombre_titular, "canal": data.canal},
    )
    db.commit()
    db.refresh(c)
    return c


def revocar_consentimiento(db: Session, consentimiento_id: int, usuario: str) -> Consentimiento:
    c = db.query(Consentimiento).filter(Consentimiento.id == consentimiento_id).first()
    if not c:
        raise ConsentimientoNotFoundError("Consentimiento no encontrado.")
    if c.fecha_revocacion:
        raise ConsentimientoYaRevocadoError("El consentimiento ya fue revocado.")

    c.activo = False
    c.fecha_revocacion = datetime.now(timezone.utc)
    log_audit(
        db=db,
        entidad="consentimiento",
        entidad_id=c.id,
        accion="revocar",
        usuario=usuario,
        detalle={"rat_id": c.rat_id, "titular": c.nombre_titular},
    )
    db.commit()
    db.refresh(c)
    return c