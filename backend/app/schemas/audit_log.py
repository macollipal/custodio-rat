from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    entidad: str
    entidad_id: int
    accion: str
    usuario: Optional[str]
    detalle: Optional[str]
    ip_origen: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}
