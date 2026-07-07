from typing import Optional
from sqlalchemy.orm import Session

from app.models.tkt_regla_asignacion import TktReglaAsignacion


def evaluar_reglas_asignacion(
    db: Session,
    company_id: int,
    tipo: Optional[str] = None,
    prioridad: Optional[str] = None,
) -> Optional[int]:
    rules = db.query(TktReglaAsignacion).filter(
        TktReglaAsignacion.activo
    ).all()

    matched = []
    for rule in rules:
        if rule.company_id is not None and rule.company_id != company_id:
            continue
        if rule.tipo is not None and rule.tipo != tipo:
            continue
        if rule.prioridad is not None and rule.prioridad != prioridad:
            continue

        specificity = 0
        if rule.company_id is not None:
            specificity += 4
        if rule.tipo is not None:
            specificity += 2
        if rule.prioridad is not None:
            specificity += 1

        matched.append((specificity, -rule.orden, rule.responsable_id))

    if not matched:
        return None

    matched.sort(reverse=True)
    return matched[0][2]


def asignar_ticket_automatico(
    db: Session,
    ticket,
) -> Optional[int]:
    return evaluar_reglas_asignacion(
        db,
        company_id=ticket.company_id,
        tipo=ticket.tipo,
        prioridad=ticket.prioridad,
    )
