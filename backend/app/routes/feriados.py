"""
Endpoints para gestión de Feriados (cálculo de días hábiles para SLAs).
Los feriados se almacenan en BD y se usan en ticket_service.py para calcular
fecha de vencimiento de tickets ARCO.
"""
import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.feriado import Feriado

router = APIRouter(prefix="/admin/feriados", tags=["Admin Feriados"])


def _require_admin():
    from app.routes.deps import require_admin as _ra
    return _ra()


@router.get("/", summary="Listar feriados de un año")
async def listar_feriados(
    anio: int = Query(..., description="Año"),
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    """Retorna todos los feriados configurados para el año dado."""
    feriados = db.query(Feriado).filter(Feriado.anio == anio).order_by(Feriado.mes, Feriado.dia).all()
    return {
        "anio": anio,
        "feriados": [
            {"id": f.id, "mes": f.mes, "dia": f.dia, "nombre": f.nombre, "tipo": f.tipo}
            for f in feriados
        ],
        "total": len(feriados),
    }


@router.get("/years", summary="Años con feriados configurados")
async def listar_anios(
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    """Retorna lista de años que tienen feriados cargados."""
    from sqlalchemy import func, distinct
    anios = (
        db.query(distinct(Feriado.anio))
        .order_by(distinct(Feriado.anio).desc())
        .all()
    )
    return {"anios": [a[0] for a in anios]}


@router.post("/upload", summary="Subir feriados via CSV")
async def upload_feriados(
    anio: int = Query(..., description="Año a reemplazar"),
    file: UploadFile = File(..., description="Archivo CSV (año,mes,día,nombre[,tipo])"),
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    """
    Reemplaza todos los feriados del año especificado con los del CSV.
    Formato CSV: año,mes,día,nombre[,tipo]
    Ejemplo:
        2025,1,1,Año Nuevo,fijo
        2025,4,17,Jueves Santo,variable
        2025,4,18,Viernes Santo,variable
    """
    raw = await file.read()
    try:
        decoded = raw.decode("utf-8-sig")  # tolera BOM
        reader = csv.DictReader(io.StringIO(decoded))
        rows = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV inválido: {e}")

    if not rows:
        raise HTTPException(status_code=400, detail="El CSV está vacío.")

    errores = []
    feriados_nuevos = []
    for i, row in enumerate(rows, start=2):
        try:
            row_anio = int(row["año"].strip())
            mes = int(row["mes"].strip())
            dia = int(row["día"].strip())
            nombre = row["nombre"].strip()
            tipo = row.get("tipo", "fijo").strip() or "fijo"
        except (KeyError, ValueError) as e:
            errores.append(f"Fila {i}: columna faltante o valor inválido ({e})")
            continue

        if row_anio != anio:
            errores.append(f"Fila {i}: año {row_anio} no coincide con {anio}")
            continue
        if not (1 <= mes <= 12):
            errores.append(f"Fila {i}: mes {mes} fuera de rango")
            continue
        if not (1 <= dia <= 31):
            errores.append(f"Fila {i}: día {dia} fuera de rango")
            continue
        if not nombre:
            errores.append(f"Fila {i}: nombre vacío")
            continue

        feriados_nuevos.append(Feriado(anio=anio, mes=mes, dia=dia, nombre=nombre, tipo=tipo))

    if errores and not feriados_nuevos:
        raise HTTPException(status_code=400, detail="Errores en todas las filas:\n" + "\n".join(errores[:10]))

    db.execute(delete(Feriado).where(Feriado.anio == anio))
    for f in feriados_nuevos:
        db.add(f)
    db.commit()

    return {
        "mensaje": f"Feriados de {anio} actualizados",
        "total_cargados": len(feriados_nuevos),
        "errores": errores[:20] if errores else [],
    }


@router.get("/example", summary="Descargar CSV de ejemplo")
async def download_example():
    """Genera un CSV de ejemplo con el formato requerido."""
    example = """año,mes,día,nombre,tipo
2025,1,1,Año Nuevo,fijo
2025,5,1,Dia del Trabajo,fijo
2025,9,18,Dia de la Independencia,fijo
2025,9,19,Dia de las Glorias del Ejercito,fijo
2025,12,8,Inmaculada Concepcion,fijo
2025,12,25,Navidad,fijo
2025,4,17,Jueves Santo,variable
2025,4,18,Viernes Santo,variable"""

    stream = io.StringIO(example)
    return StreamingResponse(
        iter([example]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feriados_ejemplo.csv"},
    )


@router.delete("/{anio}", summary="Eliminar feriados de un año")
async def eliminar_feriados(
    anio: int,
    db: Session = Depends(get_db),
    current_user=Depends(_require_admin),
):
    """Elimina todos los feriados configurados para el año dado."""
    deleted = db.execute(delete(Feriado).where(Feriado.anio == anio)).rowcount
    db.commit()
    return {"mensaje": f"{deleted} feriados de {anio} eliminados"}