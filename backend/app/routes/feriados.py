"""
Endpoints para gestión de Feriados (cálculo de días hábiles para SLAs).
Los feriados se almacenan en BD y se usan en ticket_service.py para calcular
fecha de vencimiento de tickets ARCO.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.feriado import FeriadoListResponse, FeriadoYearsResponse, FeriadoUploadResponse
from app.schemas.common import MessageResponse
from app.services import feriado_service

router = APIRouter(prefix="/admin/feriados", tags=["Admin Feriados"])


def _require_admin():
    from app.routes.deps import require_admin as _ra
    return _ra()


@router.get("/", response_model=FeriadoListResponse, summary="Listar feriados de un año")
async def listar_feriados(
    anio: int = Query(..., description="Año"),
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    feriados = feriado_service.listar_feriados(db, anio)
    return FeriadoListResponse(
        anio=anio,
        feriados=[
            {"id": f.id, "mes": f.mes, "dia": f.dia, "nombre": f.nombre, "tipo": f.tipo}
            for f in feriados
        ],
        total=len(feriados),
    )


@router.get("/years", response_model=FeriadoYearsResponse, summary="Años con feriados configurados")
async def listar_anios(
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    anios = feriado_service.listar_anios(db)
    return FeriadoYearsResponse(anios=anios)


@router.post("/upload", summary="Subir feriados via CSV")
async def upload_feriados(
    anio: int = Query(..., description="Año a reemplazar"),
    file: UploadFile = File(..., description="Archivo CSV (año,mes,día,nombre[,tipo])"),
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    from app.services.file_validation import validate_upload
    raw = validate_upload(
        file,
        allowed_extensions=["csv"],
        max_bytes=2 * 1024 * 1024,  # 2MB para CSV de feriados
    )
    try:
        result = feriado_service.upload_feriados(db, anio, raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FeriadoUploadResponse(
        mensaje=f"Feriados de {anio} actualizados",
        total_cargados=result.total_cargados,
        errores=result.errores,
    )


@router.get("/example", summary="Descargar CSV de ejemplo")
async def download_example():
    example = """año,mes,día,nombre,tipo
2025,1,1,Año Nuevo,fijo
2025,5,1,Dia del Trabajo,fijo
2025,9,18,Dia de la Independencia,fijo
2025,9,19,Dia de las Glorias del Ejercito,fijo
2025,12,8,Inmaculada Concepcion,fijo
2025,12,25,Navidad,fijo
2025,4,17,Jueves Santo,variable
2025,4,18,Viernes Santo,variable"""
    return StreamingResponse(
        iter([example]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feriados_ejemplo.csv"},
    )


@router.delete("/{anio}", response_model=MessageResponse, summary="Eliminar feriados de un año")
async def eliminar_feriados(
    anio: int,
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    deleted = feriado_service.eliminar_feriados(db, anio)
    return MessageResponse(message=f"{deleted} feriados de {anio} eliminados")