"""
Lógica de negocio para Brechas de Seguridad (Art. 14 bis Ley 21.719).
Plazos legales: notificación APDC en 72 horas; titulares sin dilación en datos sensibles/menores/financieros.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.breach import SecurityBreach
from app.schemas.breach import BreachCreate, BreachUpdate

logger = logging.getLogger(__name__)


def listar_brechas(db: Session, company_id: int, skip: int = 0, limit: int = 100) -> tuple[list[SecurityBreach], int]:
    total = db.query(SecurityBreach).filter(SecurityBreach.company_id == company_id).count()
    breaches = (
        db.query(SecurityBreach)
        .filter(SecurityBreach.company_id == company_id)
        .order_by(SecurityBreach.fecha_deteccion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return breaches, total


def get_breach(db: Session, breach_id: int) -> SecurityBreach:
    b = db.query(SecurityBreach).filter(SecurityBreach.id == breach_id).first()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brecha no encontrada.")
    return b


def crear_brecha(db: Session, data: BreachCreate, usuario: str) -> SecurityBreach:
    from app.models.company import Company
    empresa = db.query(Company).filter(Company.id == data.company_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

    breach = SecurityBreach(**data.model_dump(), creado_por=usuario)
    db.add(breach)
    db.commit()
    db.refresh(breach)

    if empresa.email_dpo:
        from app.services.email_service import notificar_nueva_brecha, EmailError
        fecha_str = breach.fecha_deteccion.strftime("%d-%m-%Y %H:%M")
        try:
            notificar_nueva_brecha(
                email_dpo=empresa.email_dpo,
                nombre_dpo=empresa.contacto_dpo or "",
                nombre_empresa=empresa.nombre,
                descripcion=breach.descripcion or "Sin descripción",
                fecha_deteccion=fecha_str,
            )
        except EmailError as e:
            logger.error(f"Brecha {breach.id}: fallo enviando notificación al DPO {empresa.email_dpo}: {e}")

    return breach


def actualizar_brecha(db: Session, breach_id: int, data: BreachUpdate) -> SecurityBreach:
    breach = get_breach(db, breach_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(breach, field, value)
    db.commit()
    db.refresh(breach)
    return breach


def eliminar_brecha(db: Session, breach_id: int) -> dict:
    breach = get_breach(db, breach_id)
    db.delete(breach)
    db.commit()
    return {"message": "Brecha eliminada."}


def _enriquecer(breach: SecurityBreach) -> dict:
    """Calcula campos derivados: horas desde detección y si el plazo APDC (72h) está vencido."""
    ahora = datetime.now(timezone.utc)
    det = breach.fecha_deteccion
    if det.tzinfo is None:
        det = det.replace(tzinfo=timezone.utc)
    horas = (ahora - det).total_seconds() / 3600
    return {
        "horas_desde_deteccion": round(horas, 1),
        "plazo_apdc_vencido": horas > 72 and not breach.notificado_apdc,
    }
