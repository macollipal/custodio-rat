from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TktReglaAsignacionCreate(BaseModel):
    company_id: Optional[int] = None
    tipo: Optional[str] = None
    prioridad: Optional[str] = None
    responsable_id: int
    activo: bool = True
    orden: int = 0


class TktReglaAsignacionUpdate(BaseModel):
    company_id: Optional[int] = None
    tipo: Optional[str] = None
    prioridad: Optional[str] = None
    responsable_id: Optional[int] = None
    activo: Optional[bool] = None
    orden: Optional[int] = None


class TktReglaAsignacionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    company_id: Optional[int]
    tipo: Optional[str]
    prioridad: Optional[str]
    responsable_id: int
    activo: bool
    orden: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
