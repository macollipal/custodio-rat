from pydantic import BaseModel
from typing import Optional


class FeriadoItem(BaseModel):
    id: int
    mes: int
    dia: int
    nombre: str
    tipo: str


class FeriadoListResponse(BaseModel):
    anio: int
    feriados: list[FeriadoItem]
    total: int


class FeriadoYearsResponse(BaseModel):
    anios: list[int]


class FeriadoUploadResponse(BaseModel):
    mensaje: str
    total_cargados: int
    errores: list[str]