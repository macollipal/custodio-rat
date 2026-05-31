from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.audit_service import log_audit


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Company], int]:
    total = db.query(Company).count()
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies, total


def get_company(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")
    return company


def create_company(db: Session, data: CompanyCreate, usuario: str, ip_origen: Optional[str] = None) -> Company:
    existing = db.query(Company).filter(Company.rut == data.rut).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una empresa con el RUT {data.rut}.",
        )
    company = Company(**data.model_dump())
    db.add(company)
    db.flush()

    log_audit(db, "company", company.id, "crear", usuario, data.model_dump(), ip_origen)
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company_id: int, data: CompanyUpdate, usuario: str, ip_origen: Optional[str] = None) -> Company:
    company = get_company(db, company_id)
    cambios = data.model_dump(exclude_none=True)
    for field, value in cambios.items():
        setattr(company, field, value)

    log_audit(db, "company", company_id, "editar", usuario, cambios, ip_origen)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: int, usuario: str, ip_origen: Optional[str] = None) -> dict:
    company = get_company(db, company_id)
    log_audit(db, "company", company_id, "eliminar", usuario, {"nombre": company.nombre}, ip_origen)
    db.delete(company)
    db.commit()
    return {"message": f"Empresa '{company.nombre}' eliminada correctamente."}