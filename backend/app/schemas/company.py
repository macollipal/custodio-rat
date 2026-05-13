from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class CompanyBase(BaseModel):
    nombre: str
    rut: str

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La razón social no puede estar vacía.")
        return v.strip()

    @field_validator("rut")
    @classmethod
    def rut_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El RUT no puede estar vacío.")
        return v.strip()
    rubro: Optional[str] = None
    direccion: Optional[str] = None
    contacto_dpo: Optional[str] = None
    email_dpo: Optional[str] = None
    descripcion: Optional[str] = None
    canal_ejercicio_derechos: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    direccion: Optional[str] = None
    contacto_dpo: Optional[str] = None
    email_dpo: Optional[str] = None
    descripcion: Optional[str] = None
    canal_ejercicio_derechos: Optional[str] = None


class CompanyOut(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_rats: Optional[int] = 0
    mi_rol: Optional[str] = None  # rol del usuario actual en esta empresa (None = admin global)

    model_config = {"from_attributes": True}
