from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ConsentimientoCreate(BaseModel):
    rat_id: int
    nombre_titular: str
    email_titular: Optional[str] = None
    canal: str
    texto_consentimiento: str
    fecha_obtencion: datetime
    ip_origen: Optional[str] = None


class ConsentimientoOut(BaseModel):
    id: int
    company_id: int
    rat_id: Optional[int] = None
    nombre_titular: str
    email_titular: Optional[str] = None
    canal: str
    texto_consentimiento: str
    fecha_obtencion: datetime
    fecha_revocacion: Optional[datetime] = None
    activo: bool
    ip_origen: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
