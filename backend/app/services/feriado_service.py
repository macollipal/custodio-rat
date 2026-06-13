"""
Lógica de negocio para gestión de feriados.
Se usan en ticket_service.py para calcular fechas de vencimiento de tickets ARCO.
"""
import csv
import io
from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy import delete, func, distinct
from sqlalchemy.orm import Session

from app.models.feriado import Feriado


@dataclass
class FeriadoRowError:
    fila: int
    mensaje: str


@dataclass
class FeriadoUploadResult:
    total_cargados: int
    errores: List[str]


def listar_feriados(db: Session, anio: int) -> List[Feriado]:
    return db.query(Feriado).filter(Feriado.anio == anio).order_by(Feriado.mes, Feriado.dia).all()


def listar_anios(db: Session) -> List[int]:
    anios = (
        db.query(distinct(Feriado.anio))
        .order_by(distinct(Feriado.anio).desc())
        .all()
    )
    return [a[0] for a in anios]


def _parsear_csv(raw: bytes, anio: int) -> Tuple[List[Feriado], List[FeriadoRowError]]:
    try:
        decoded = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        rows = list(reader)
    except Exception as e:
        raise ValueError(f"CSV inválido: {e}")

    if not rows:
        raise ValueError("El CSV está vacío.")

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
            errores.append(FeriadoRowError(fila=i, mensaje=f"columna faltante o valor inválido ({e})"))
            continue

        if row_anio != anio:
            errores.append(FeriadoRowError(fila=i, mensaje=f"año {row_anio} no coincide con {anio}"))
            continue
        if not (1 <= mes <= 12):
            errores.append(FeriadoRowError(fila=i, mensaje=f"mes {mes} fuera de rango"))
            continue
        if not (1 <= dia <= 31):
            errores.append(FeriadoRowError(fila=i, mensaje=f"día {dia} fuera de rango"))
            continue
        if not nombre:
            errores.append(FeriadoRowError(fila=i, mensaje="nombre vacío"))
            continue

        feriados_nuevos.append(Feriado(anio=anio, mes=mes, dia=dia, nombre=nombre, tipo=tipo))

    return feriados_nuevos, errores


def upload_feriados(db: Session, anio: int, raw: bytes) -> FeriadoUploadResult:
    feriados_nuevos, errores = _parsear_csv(raw, anio)

    if errores and not feriados_nuevos:
        raise ValueError("Errores en todas las filas:\n" + "\n".join(f"Fila {e.fila}: {e.mensaje}" for e in errores[:10]))

    db.execute(delete(Feriado).where(Feriado.anio == anio))
    for f in feriados_nuevos:
        db.add(f)
    db.commit()

    return FeriadoUploadResult(
        total_cargados=len(feriados_nuevos),
        errores=[f"Fila {e.fila}: {e.mensaje}" for e in errores[:20]] if errores else [],
    )


def eliminar_feriados(db: Session, anio: int) -> int:
    deleted = db.execute(delete(Feriado).where(Feriado.anio == anio)).rowcount
    db.commit()
    return deleted