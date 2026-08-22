import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.company import Company
from app.models.encargado_contrato import EncargadoContrato
from app.models.breach import SecurityBreach
from app.models.politica_transparencia import PoliticaTransparencia
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.audit_service import log_audit


def calcular_metricas_empresa(rats: list, now: datetime) -> tuple[int, int]:
    """Retorna (completitud_promedio, rats_vencidos) para una lista de RATs de una empresa."""
    from app.services.rat_calculations import calcular_completitud, rat_to_dict
    if not rats:
        return 0, 0
    completitud_promedio = round(sum(calcular_completitud(rat_to_dict(r)) for r in rats) / len(rats))
    vencidos = 0
    for r in rats:
        plazo = r.plazo_retencion or ""
        match = re.search(r"(\d+)\s*(?:año|años)", plazo, re.IGNORECASE)
        if not match:
            continue
        years = int(match.group(1))
        created = r.created_at
        if created is None:
            continue
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except Exception:
                continue
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created + timedelta(days=years * 365) < now:
            vencidos += 1
    return completitud_promedio, vencidos


def _delete_company_orphans(db: Session, company_id: int) -> None:
    """Elimina registros huérfanos sin cascade antes de borrar la empresa."""
    from sqlalchemy import delete
    db.execute(delete(EncargadoContrato).where(EncargadoContrato.company_id == company_id))
    db.execute(delete(SecurityBreach).where(SecurityBreach.company_id == company_id))
    db.execute(delete(PoliticaTransparencia).where(PoliticaTransparencia.company_id == company_id))


def get_companies(db: Session, skip: int = 0, limit: int = 100, incluir_inactivas: bool = False) -> tuple[list[Company], int]:
    query = db.query(Company)
    if not incluir_inactivas:
        query = query.filter(Company.activa)
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
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
    dump = data.model_dump()
    dump.pop("activa", None)
    company = Company(**dump, activa=True)
    db.add(company)
    db.flush()

    log_audit(db, "company", company.id, "crear", usuario, data.model_dump(), ip_origen)
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company_id: int, data: CompanyUpdate, usuario: str, ip_origen: Optional[str] = None) -> Company:
    company = get_company(db, company_id)
    cambios = data.model_dump(exclude_none=True)
    cambios.pop("activa", None)
    for field, value in cambios.items():
        setattr(company, field, value)

    log_audit(db, "company", company_id, "editar", usuario, cambios, ip_origen)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: int, usuario: str, ip_origen: Optional[str] = None) -> dict:
    company = get_company(db, company_id)
    _delete_company_orphans(db, company_id)
    log_audit(db, "company", company_id, "eliminar", usuario, {"nombre": company.nombre}, ip_origen)
    db.delete(company)
    db.commit()
    return {"message": f"Empresa '{company.nombre}' eliminada correctamente."}


def deactivate_company(db: Session, company_id: int, usuario: str, ip_origen: Optional[str] = None) -> Company:
    company = get_company(db, company_id)
    if not company.activa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La empresa ya está desactivada.",
        )
    company.activa = False
    company.desactivada_at = datetime.now(timezone.utc)
    company.desactivada_por = usuario
    log_audit(db, "company", company_id, "desactivar", usuario, {"nombre": company.nombre}, ip_origen)
    db.commit()
    db.refresh(company)
    return company


def reactivate_company(db: Session, company_id: int, usuario: str, ip_origen: Optional[str] = None) -> Company:
    company = get_company(db, company_id)
    if company.activa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La empresa ya está activa.",
        )
    company.activa = True
    company.desactivada_at = None
    company.desactivada_por = None
    log_audit(db, "company", company_id, "reactivar", usuario, {"nombre": company.nombre}, ip_origen)
    db.commit()
    db.refresh(company)
    return company


def hard_delete_company(
    db: Session,
    company_id: int,
    admin_username: str,
    admin_password: str,
    ip_origen: Optional[str] = None,
) -> dict:
    from app.models.user import User
    from app.core.security import verify_password

    admin = db.query(User).filter(User.username == admin_username).first()
    if not admin or not verify_password(admin_password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contraseña de administrador incorrecta.",
        )

    company = get_company(db, company_id)
    nombre = company.nombre

    _delete_company_orphans(db, company_id)

    log_audit(
        db, "company", company_id, "hard_delete",
        admin_username,
        {"nombre": nombre, "borrado_por": admin_username},
        ip_origen,
    )

    db.delete(company)
    db.commit()
    return {"message": f"Empresa '{nombre}' eliminada permanentemente."}