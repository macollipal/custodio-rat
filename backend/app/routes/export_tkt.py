"""
Endpoints de exportación ARCO-QW1: CSV, Excel, PDF.
Ruta: /export/tkt/
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.routes.deps import get_current_user
from app.services.export_tkt_service import generar_csv, generar_excel, generar_pdf
from app.services.user_company_service import get_empresas_usuario

router = APIRouter(prefix="/export/tkt", tags=["Exportación ARCO"])


@router.get("/csv")
async def exportar_csv(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Exporta tickets ARCO a CSV."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            raise PermissionError("Sin acceso a ninguna empresa")
        if company_id and company_id not in empresas:
            raise PermissionError("Acceso denegado a esta empresa")
        if not company_id:
            company_id = empresas[0]

    data = generar_csv(db, company_id, estado, prioridad, fecha_desde, fecha_hasta)
    return StreamingResponse(
        iter([data]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=custodio_arco_tickets.csv"},
    )


@router.get("/excel")
async def exportar_excel(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Exporta tickets ARCO a Excel (.xlsx)."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            raise PermissionError("Sin acceso a ninguna empresa")
        if company_id and company_id not in empresas:
            raise PermissionError("Acceso denegado a esta empresa")
        if not company_id:
            company_id = empresas[0]

    data = generar_excel(db, company_id, estado, prioridad, fecha_desde, fecha_hasta)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=custodio_arco_tickets.xlsx"},
    )


@router.get("/pdf")
async def exportar_pdf(
    company_id: Optional[int] = None,
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Exporta tickets ARCO a PDF."""
    if current_user.rol_global != "superadmin":
        empresas = get_empresas_usuario(db, current_user.id)
        if not empresas:
            raise PermissionError("Sin acceso a ninguna empresa")
        if company_id and company_id not in empresas:
            raise PermissionError("Acceso denegado a esta empresa")
        if not company_id:
            company_id = empresas[0]

    data = generar_pdf(db, company_id, estado, prioridad, fecha_desde, fecha_hasta)
    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=custodio_arco_tickets.pdf"},
    )
