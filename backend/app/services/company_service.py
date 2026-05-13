"""
Lógica de negocio para empresas.
"""

import json
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.company import Company
from app.models.audit_log import AuditLog
from app.schemas.company import CompanyCreate, CompanyUpdate


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> list[Company]:
    return db.query(Company).offset(skip).limit(limit).all()


def get_company(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    return company


def create_company(db: Session, data: CompanyCreate, usuario: str) -> Company:
    existing = db.query(Company).filter(Company.rut == data.rut).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una empresa con el RUT {data.rut}.",
        )
    company = Company(**data.model_dump())
    db.add(company)
    db.flush()

    _log_audit(db, "company", company.id, "crear", usuario, data.model_dump())
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company_id: int, data: CompanyUpdate, usuario: str) -> Company:
    company = get_company(db, company_id)
    cambios = data.model_dump(exclude_none=True)
    for field, value in cambios.items():
        setattr(company, field, value)

    _log_audit(db, "company", company_id, "editar", usuario, cambios)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: int, usuario: str) -> dict:
    company = get_company(db, company_id)
    _log_audit(db, "company", company_id, "eliminar", usuario, {"nombre": company.nombre})
    db.delete(company)
    db.commit()
    return {"message": f"Empresa '{company.nombre}' eliminada correctamente."}


def _log_audit(db: Session, entidad: str, entidad_id: int, accion: str, usuario: str, detalle: dict):
    log = AuditLog(
        entidad=entidad,
        entidad_id=entidad_id,
        accion=accion,
        usuario=usuario,
        detalle=json.dumps(detalle, ensure_ascii=False, default=str),
    )
    db.add(log)
