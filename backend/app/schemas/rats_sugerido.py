"""
Schemas Pydantic para RATs Sugeridos por rubro.
"""

from typing import Optional
from pydantic import BaseModel


class RATSugeridoBase(BaseModel):
    rubro_id: int
    nombre_proceso: str
    categoria_datos: str
    categoria_titulares: Optional[str] = None
    finalidad: Optional[str] = None
    base_legal: Optional[str] = None
    plazo_retencion: Optional[str] = None
    datos_sensibles: bool = False
    evaluacion_impacto: bool = False
    decisiones_automatizadas: bool = False


class RATSugeridoCreate(RATSugeridoBase):
    pass


class RATSugeridoUpdate(BaseModel):
    rubro_id: Optional[int] = None
    nombre_proceso: Optional[str] = None
    categoria_datos: Optional[str] = None
    categoria_titulares: Optional[str] = None
    finalidad: Optional[str] = None
    base_legal: Optional[str] = None
    plazo_retencion: Optional[str] = None
    datos_sensibles: Optional[bool] = None
    evaluacion_impacto: Optional[bool] = None
    decisiones_automatizadas: Optional[bool] = None


class RATSugeridoOut(RATSugeridoBase):
    id: int

    model_config = {"from_attributes": True}