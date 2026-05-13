from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BreachBase(BaseModel):
    descripcion: str
    fecha_deteccion: datetime
    rats_afectados: Optional[str] = None
    datos_comprometidos: Optional[str] = None
    medidas_adoptadas: Optional[str] = None
    notificado_apdc: bool = False
    fecha_notificacion_apdc: Optional[datetime] = None
    notificado_titulares: bool = False
    fecha_notificacion_titulares: Optional[datetime] = None


class BreachCreate(BreachBase):
    company_id: int


class BreachUpdate(BaseModel):
    descripcion: Optional[str] = None
    fecha_deteccion: Optional[datetime] = None
    rats_afectados: Optional[str] = None
    datos_comprometidos: Optional[str] = None
    medidas_adoptadas: Optional[str] = None
    notificado_apdc: Optional[bool] = None
    fecha_notificacion_apdc: Optional[datetime] = None
    notificado_titulares: Optional[bool] = None
    fecha_notificacion_titulares: Optional[datetime] = None


class BreachOut(BreachBase):
    id: int
    company_id: int
    creado_por: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    horas_desde_deteccion: Optional[float] = None
    plazo_apdc_vencido: Optional[bool] = None

    model_config = {"from_attributes": True}
