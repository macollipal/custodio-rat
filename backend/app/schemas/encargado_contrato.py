from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EncargadoContratoCreate(BaseModel):
    company_id: int
    rat_id: Optional[int] = None
    nombre_encargado: str
    objeto: str
    duracion_inicio: datetime
    duracion_fin: Optional[datetime] = None
    finalidad: str
    tipo_datos: str
    categorias_titulares: str
    derechos_obligaciones: str
    archivo_pdf_base64: Optional[str] = None
    archivo_pdf_nombre: Optional[str] = None
    archivo_pdf_tipo: Optional[str] = None


class EncargadoContratoUpdate(BaseModel):
    objeto: Optional[str] = None
    duracion_inicio: Optional[datetime] = None
    duracion_fin: Optional[datetime] = None
    finalidad: Optional[str] = None
    tipo_datos: Optional[str] = None
    categorias_titulares: Optional[str] = None
    derechos_obligaciones: Optional[str] = None
    archivo_pdf_base64: Optional[str] = None
    archivo_pdf_nombre: Optional[str] = None
    archivo_pdf_tipo: Optional[str] = None
    activo: Optional[bool] = None


class EncargadoContratoOut(BaseModel):
    id: int
    company_id: int
    rat_id: Optional[int] = None
    nombre_encargado: str
    objeto: str
    duracion_inicio: datetime
    duracion_fin: Optional[datetime] = None
    finalidad: str
    tipo_datos: str
    categorias_titulares: str
    derechos_obligaciones: str
    tiene_archivo: bool = False
    activo: bool
    fecha_alerta_vencimiento: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
