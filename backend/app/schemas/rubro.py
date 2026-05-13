"""
Schemas Pydantic para Rubros.
"""

from typing import Optional
from pydantic import BaseModel


class RubroBase(BaseModel):
    nombre: str
    orden: int = 0


class RubroCreate(RubroBase):
    pass


class RubroUpdate(BaseModel):
    nombre: Optional[str] = None
    orden: Optional[int] = None


class RubroOut(RubroBase):
    id: int
    total_sugerencias: Optional[int] = None

    model_config = {"from_attributes": True}