"""
Lógica de negocio para EIPD (Evaluación de Impacto en Protección de Datos).
Art. 15 bis Ley 21.719.
"""

from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from app.models.eipd import EIPD, ResultadoEIPD
from app.models.rat import RAT as RATModel
from app.schemas.eipd import EIPDCreate, EIPDUpdate
from app.services.audit_service import log_audit


class EIPDNotFoundError(Exception):
    pass


class RATNotFoundError(Exception):
    pass


class EIPDJaExisteError(Exception):
    pass


class ResultadoInvalidoError(Exception):
    def __init__(self, valores_permitidos: List[str]):
        self.valores_permitidos = valores_permitidos
        super().__init__(f"Resultado inválido. Valores permitidos: {valores_permitidos}")


def listar_eipds(
    db: Session,
    company_id: int,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[EIPD], int]:
    q = (
        db.query(EIPD)
        .join(RATModel, EIPD.rat_id == RATModel.id)
        .filter(RATModel.company_id == company_id)
    )
    if estado:
        q = q.filter(EIPD.resultado == estado)

    total = q.count()
    items = q.order_by(EIPD.updated_at.desc()).offset(skip).limit(limit).all()
    return items, total


def obtener_eipd_por_rat(db: Session, rat_id: int) -> EIPD:
    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        raise RATNotFoundError("RAT no encontrado.")

    eipd = db.query(EIPD).filter(EIPD.rat_id == rat_id).first()
    if not eipd:
        raise EIPDNotFoundError("EIPD no encontrado para este RAT.")
    return eipd


def crear_eipd(db: Session, data: EIPDCreate, usuario: str) -> EIPD:
    rat = db.query(RATModel).filter(RATModel.id == data.rat_id).first()
    if not rat:
        raise RATNotFoundError("RAT no encontrado.")

    existing = db.query(EIPD).filter(EIPD.rat_id == data.rat_id).first()
    if existing:
        raise EIPDJaExisteError("Ya existe un EIPD para este RAT. Use PUT para actualizar.")

    try:
        resultado = ResultadoEIPD(data.resultado)
    except ValueError:
        valores = [r.value for r in ResultadoEIPD]
        raise ResultadoInvalidoError(valores)

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
        created_by=usuario,
    )
    db.add(eipd)
    db.flush()
    log_audit(
        db=db,
        entidad="eipd",
        entidad_id=eipd.id,
        accion="create",
        usuario=usuario,
        detalle={"rat_id": data.rat_id, "resultado": data.resultado},
    )
    db.commit()
    db.refresh(eipd)
    return eipd


def actualizar_eipd(db: Session, eipd_id: int, data: EIPDUpdate, usuario: str) -> EIPD:
    eipd = db.query(EIPD).filter(EIPD.id == eipd_id).first()
    if not eipd:
        raise EIPDNotFoundError("EIPD no encontrado.")

    cambios = data.model_dump(exclude_none=True)
    if "resultado" in cambios:
        try:
            cambios["resultado"] = ResultadoEIPD(cambios["resultado"])
        except ValueError:
            valores = [r.value for r in ResultadoEIPD]
            raise ResultadoInvalidoError(valores)

    for field, value in cambios.items():
        setattr(eipd, field, value)

    log_audit(
        db=db,
        entidad="eipd",
        entidad_id=eipd.id,
        accion="update",
        usuario=usuario,
        detalle={"rat_id": eipd.rat_id, "campos": list(cambios.keys())},
    )
    db.commit()
    db.refresh(eipd)
    return eipd


def get_eipd_by_id(db: Session, eipd_id: int) -> EIPD:
    eipd = db.query(EIPD).filter(EIPD.id == eipd_id).first()
    if not eipd:
        raise EIPDNotFoundError("EIPD no encontrado.")
    return eipd