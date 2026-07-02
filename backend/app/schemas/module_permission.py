"""
Schemas Pydantic para ModulePermission.
"""
from typing import Dict, List
from pydantic import BaseModel, Field


class ModuleStatusOut(BaseModel):
    modulo: str
    enabled: bool


class CompanyModulesOut(BaseModel):
    company_id: int
    modules: Dict[str, bool]


class ActiveModulesOut(BaseModel):
    company_id: int
    active_modules: List[str]


class ModuleToggleIn(BaseModel):
    modulo: str
    enabled: bool


class ModuleBulkUpdateIn(BaseModel):
    modules: Dict[str, bool] = Field(
        ..., description="Dict {modulo: enabled} con modulos a actualizar"
    )