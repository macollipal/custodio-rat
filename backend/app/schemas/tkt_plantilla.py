"""
Schemas Pydantic para el módulo de Plantillas de respuesta ARCO.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


TktPlantillaTipoEnum = str


class TktPlantillaCreate(BaseModel):
    company_id: Optional[int] = None
    tipo: str
    nombre: str
    contenido: str
    activo: bool = True


class TktPlantillaUpdate(BaseModel):
    tipo: Optional[str] = None
    nombre: Optional[str] = None
    contenido: Optional[str] = None
    activo: Optional[bool] = None


class TktPlantillaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    company_id: Optional[int]
    tipo: str
    nombre: str
    contenido: str
    activo: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
