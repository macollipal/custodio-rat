"""
Rutas del módulo Data Discovery & Mapping.
Permite registrar fuentes de datos y escanear sus esquemas en busca de datos personales.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.discovery import DataSource, DiscoveryFinding, DiscoveryRun
from app.routes.deps import get_current_user
from app.services.discovery_service import (
    decrypt_password,
    encrypt_password,
    ejecutar_escaneo,
    generar_sugerencias_rat,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/discovery", tags=["Discovery"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DataSourceCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    tipo: str = Field(..., pattern="^(postgresql|sqlserver)$")
    host: str = Field(..., min_length=1, max_length=300)
    port: int = Field(..., ge=1, le=65535)
    database_name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=500)
    schema_name: Optional[str] = Field(None, max_length=100)


class DataSourceUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    host: Optional[str] = Field(None, min_length=1, max_length=300)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database_name: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, min_length=1, max_length=200)
    password: Optional[str] = Field(None, min_length=1, max_length=500)
    schema_name: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None


class DataSourceOut(BaseModel):
    id: int
    company_id: int
    nombre: str
    tipo: str
    host: str
    port: int
    database_name: str
    username: str
    schema_name: Optional[str]
    activo: bool
    ultimo_run_id: Optional[int] = None
    ultimo_run_estado: Optional[str] = None

    class Config:
        from_attributes = True


class DiscoveryRunOut(BaseModel):
    id: int
    source_id: int
    company_id: int
    estado: str
    started_at: str
    finished_at: Optional[str]
    error_msg: Optional[str]
    total_tablas: Optional[int]
    total_columnas: Optional[int]
    total_hallazgos: Optional[int]
    total_gaps: Optional[int]
    ejecutado_por: Optional[str]

    class Config:
        from_attributes = True


class DiscoveryFindingOut(BaseModel):
    id: int
    table_name: str
    column_name: str
    data_type_sql: Optional[str]
    categoria: str
    descripcion: Optional[str]
    confianza: int
    rat_id: Optional[int]
    descartado: bool
    es_gap: bool

    class Config:
        from_attributes = True


class DiscoveryRunDetail(BaseModel):
    run: DiscoveryRunOut
    findings: list[DiscoveryFindingOut]
    sugerencias_rat: list[dict]


# ── Helpers de acceso ─────────────────────────────────────────────────────────

def _get_source_or_404(source_id: int, company_id: int, db: Session) -> DataSource:
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.company_id == company_id,
        DataSource.activo == True,
    ).first()
    if not source:
        raise HTTPException(status_code=404, detail="Fuente de datos no encontrada")
    return source


def _get_company_ids(user, db: Session) -> list[int]:
    from app.models.user import RolGlobal
    from app.models.user_company import UserCompany
    if user.rol_global == RolGlobal.SUPERADMIN:
        from app.models.company import Company
        return [c.id for c in db.query(Company.id).all()]
    return [uc.company_id for uc in db.query(UserCompany).filter(UserCompany.user_id == user.id).all()]


# ── Endpoints de fuentes ──────────────────────────────────────────────────────

@router.get("/sources", response_model=list[DataSourceOut])
def listar_sources(
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")

    sources = db.query(DataSource).filter(
        DataSource.company_id == company_id,
        DataSource.activo == True,
    ).all()

    result = []
    for s in sources:
        last_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.source_id == s.id)
            .order_by(DiscoveryRun.started_at.desc())
            .first()
        )
        out = DataSourceOut(
            id=s.id,
            company_id=s.company_id,
            nombre=s.nombre,
            tipo=s.tipo,
            host=s.host,
            port=s.port,
            database_name=s.database_name,
            username=s.username,
            schema_name=s.schema_name,
            activo=s.activo,
            ultimo_run_id=last_run.id if last_run else None,
            ultimo_run_estado=last_run.estado if last_run else None,
        )
        result.append(out)
    return result


@router.post("/sources", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
def crear_source(
    company_id: int,
    payload: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")

    source = DataSource(
        company_id=company_id,
        nombre=payload.nombre,
        tipo=payload.tipo,
        host=payload.host,
        port=payload.port,
        database_name=payload.database_name,
        username=payload.username,
        password_enc=encrypt_password(payload.password),
        schema_name=payload.schema_name,
        created_by=current_user.username,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return DataSourceOut(
        id=source.id, company_id=source.company_id, nombre=source.nombre,
        tipo=source.tipo, host=source.host, port=source.port,
        database_name=source.database_name, username=source.username,
        schema_name=source.schema_name, activo=source.activo,
    )


@router.patch("/sources/{source_id}", response_model=DataSourceOut)
def actualizar_source(
    source_id: int,
    company_id: int,
    payload: DataSourceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")
    source = _get_source_or_404(source_id, company_id, db)

    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "password":
            source.password_enc = encrypt_password(value)
        else:
            setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return DataSourceOut(
        id=source.id, company_id=source.company_id, nombre=source.nombre,
        tipo=source.tipo, host=source.host, port=source.port,
        database_name=source.database_name, username=source.username,
        schema_name=source.schema_name, activo=source.activo,
    )


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_source(
    source_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")
    source = _get_source_or_404(source_id, company_id, db)
    source.activo = False  # soft delete
    db.commit()


# ── Endpoints de escaneo ──────────────────────────────────────────────────────

@router.post("/sources/{source_id}/scan", response_model=DiscoveryRunDetail)
def ejecutar_scan(
    source_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")
    source = _get_source_or_404(source_id, company_id, db)

    try:
        run = ejecutar_escaneo(db, source, ejecutado_por=current_user.username)
    except Exception as exc:
        # El run queda en estado "error" en BD; retornamos el error al cliente
        raise HTTPException(
            status_code=502,
            detail=f"Error al conectar con la fuente de datos: {exc}",
        )

    findings = db.query(DiscoveryFinding).filter(DiscoveryFinding.run_id == run.id).all()
    sugerencias = generar_sugerencias_rat(findings)

    return DiscoveryRunDetail(
        run=_run_to_out(run),
        findings=[_finding_to_out(f) for f in findings],
        sugerencias_rat=sugerencias,
    )


@router.get("/runs/{run_id}", response_model=DiscoveryRunDetail)
def obtener_run(
    run_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")

    run = db.query(DiscoveryRun).filter(
        DiscoveryRun.id == run_id,
        DiscoveryRun.company_id == company_id,
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")

    findings = db.query(DiscoveryFinding).filter(DiscoveryFinding.run_id == run_id).all()
    sugerencias = generar_sugerencias_rat(findings)

    return DiscoveryRunDetail(
        run=_run_to_out(run),
        findings=[_finding_to_out(f) for f in findings],
        sugerencias_rat=sugerencias,
    )


@router.get("/sources/{source_id}/runs", response_model=list[DiscoveryRunOut])
def listar_runs_de_source(
    source_id: int,
    company_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")

    runs = (
        db.query(DiscoveryRun)
        .filter(DiscoveryRun.source_id == source_id, DiscoveryRun.company_id == company_id)
        .order_by(DiscoveryRun.started_at.desc())
        .limit(10)
        .all()
    )
    return [_run_to_out(r) for r in runs]


class ManualColumnRow(BaseModel):
    table_name: str
    column_name: str
    data_type: str = ""


class ManualScanPayload(BaseModel):
    columns: list[ManualColumnRow] = Field(..., min_length=1)


@router.post("/sources/{source_id}/scan/manual", response_model=DiscoveryRunDetail)
def ejecutar_scan_manual(
    source_id: int,
    company_id: int,
    payload: ManualScanPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Escaneo manual: el usuario provee las columnas (resultado de la query SQL)."""
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")
    source = _get_source_or_404(source_id, company_id, db)

    from app.services.discovery_service import _clasificar_columna, _es_gap
    from app.models.rat import RAT
    from datetime import datetime, timezone

    run = DiscoveryRun(
        source_id=source.id,
        company_id=source.company_id,
        estado="completado",
        ejecutado_por=f"{current_user.username} (manual)",
        finished_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.flush()

    rats = db.query(RAT).filter(RAT.company_id == source.company_id).all()
    tablas_vistas: set[str] = set()
    hallazgos = []

    for col in payload.columns:
        tablas_vistas.add(col.table_name)
        clasificacion = _clasificar_columna(col.column_name)
        if not clasificacion:
            continue
        categoria, descripcion, confianza = clasificacion
        es_gap = _es_gap(categoria, rats)
        hallazgos.append(DiscoveryFinding(
            run_id=run.id,
            table_name=col.table_name,
            column_name=col.column_name,
            data_type_sql=col.data_type or None,
            categoria=categoria,
            descripcion=descripcion,
            confianza=confianza,
            es_gap=es_gap,
        ))

    db.bulk_save_objects(hallazgos)
    run.total_tablas = len(tablas_vistas)
    run.total_columnas = len(payload.columns)
    run.total_hallazgos = len(hallazgos)
    run.total_gaps = sum(1 for f in hallazgos if f.es_gap)
    db.commit()
    db.refresh(run)

    saved_findings = db.query(DiscoveryFinding).filter(DiscoveryFinding.run_id == run.id).all()
    sugerencias = generar_sugerencias_rat(saved_findings)

    return DiscoveryRunDetail(
        run=_run_to_out(run),
        findings=[_finding_to_out(f) for f in saved_findings],
        sugerencias_rat=sugerencias,
    )


@router.patch("/findings/{finding_id}/vincular-rat")
def vincular_rat(
    finding_id: int,
    company_id: int,
    rat_id: Optional[int] = None,
    descartado: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Vincula un hallazgo a un RAT existente o lo marca como descartado."""
    company_ids = _get_company_ids(current_user, db)
    if company_id not in company_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a esta empresa")

    finding = db.query(DiscoveryFinding).filter(DiscoveryFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado")

    # Verificar que el run pertenece a la empresa
    run = db.query(DiscoveryRun).filter(
        DiscoveryRun.id == finding.run_id,
        DiscoveryRun.company_id == company_id,
    ).first()
    if not run:
        raise HTTPException(status_code=403, detail="Sin acceso a este hallazgo")

    if rat_id is not None:
        finding.rat_id = rat_id
        finding.es_gap = False
    if descartado is not None:
        finding.descartado = descartado
        if descartado:
            finding.es_gap = False

    db.commit()
    return _finding_to_out(finding)


# ── Serialización ─────────────────────────────────────────────────────────────

def _run_to_out(run: DiscoveryRun) -> DiscoveryRunOut:
    return DiscoveryRunOut(
        id=run.id,
        source_id=run.source_id,
        company_id=run.company_id,
        estado=run.estado,
        started_at=run.started_at.isoformat() if run.started_at else "",
        finished_at=run.finished_at.isoformat() if run.finished_at else None,
        error_msg=run.error_msg,
        total_tablas=run.total_tablas,
        total_columnas=run.total_columnas,
        total_hallazgos=run.total_hallazgos,
        total_gaps=run.total_gaps,
        ejecutado_por=run.ejecutado_por,
    )


def _finding_to_out(f: DiscoveryFinding) -> DiscoveryFindingOut:
    return DiscoveryFindingOut(
        id=f.id,
        table_name=f.table_name,
        column_name=f.column_name,
        data_type_sql=f.data_type_sql,
        categoria=f.categoria,
        descripcion=f.descripcion,
        confianza=f.confianza,
        rat_id=f.rat_id,
        descartado=f.descartado,
        es_gap=f.es_gap,
    )
