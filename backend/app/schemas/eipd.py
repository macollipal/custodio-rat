from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class EIPDOut(BaseModel):
    id: int
    rat_id: int
    metodologia: Optional[str] = None
    objetivos: Optional[str] = None
    necesidad_proporcionalidad: Optional[str] = None
    riesgos_identificados: Optional[str] = None
    medidas_propuestas: Optional[str] = None
    parecer_dpo: Optional[str] = None
    fecha_elaboracion: Optional[date] = None
    fecha_aprobacion: Optional[date] = None
    resultado: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EIPDCreate(BaseModel):
    rat_id: int
    metodologia: Optional[str] = None
    objetivos: Optional[str] = None
    necesidad_proporcionalidad: Optional[str] = None
    riesgos_identificados: Optional[str] = None
    medidas_propuestas: Optional[str] = None
    parecer_dpo: Optional[str] = None
    fecha_elaboracion: Optional[date] = None
    fecha_aprobacion: Optional[date] = None
    resultado: str = "en_proceso"


class EIPDUpdate(BaseModel):
    metodologia: Optional[str] = None
    objetivos: Optional[str] = None
    necesidad_proporcionalidad: Optional[str] = None
    riesgos_identificados: Optional[str] = None
    medidas_propuestas: Optional[str] = None
    parecer_dpo: Optional[str] = None
    fecha_elaboracion: Optional[date] = None
    fecha_aprobacion: Optional[date] = None
    resultado: Optional[str] = None