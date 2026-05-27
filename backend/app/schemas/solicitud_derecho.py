from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SolicitudDerechoBase(BaseModel):
    tipo: str
    nombre_titular: str
    email_titular: str
    rut_titular: Optional[str] = None
    descripcion: str


class SolicitudDerechoCreate(SolicitudDerechoBase):
    company_id: int


class SolicitudDerechoUpdate(BaseModel):
    estado: Optional[str] = None
    respuesta: Optional[str] = None


class SolicitudDerechoOut(SolicitudDerechoBase):
    id: int
    company_id: int
    estado: str
    respuesta: Optional[str] = None
    fecha_respuesta: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
