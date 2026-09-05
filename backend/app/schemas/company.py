from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


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
    rubro_id: Optional[int] = None
    direccion: Optional[str] = None
    contacto_dpo: Optional[str] = None
    email_dpo: Optional[EmailStr] = None
    telefono_dpo: Optional[str] = None
    representante_legal: Optional[str] = None
    descripcion: Optional[str] = None
    canal_ejercicio_derechos: Optional[str] = None
    activa: Optional[bool] = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    rubro_id: Optional[int] = None
    direccion: Optional[str] = None
    contacto_dpo: Optional[str] = None
    email_dpo: Optional[EmailStr] = None

    @field_validator("nombre", mode="before")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not str(v).strip():
            raise ValueError("La razón social no puede estar vacía.")
        return v
    telefono_dpo: Optional[str] = None
    representante_legal: Optional[str] = None
    descripcion: Optional[str] = None
    canal_ejercicio_derechos: Optional[str] = None


class CompanyOut(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_rats: Optional[int] = 0
    mi_rol: Optional[str] = None
    rubro_id: Optional[int] = None
    completitud_promedio: Optional[int] = 0
    rats_vencidos: Optional[int] = 0
    solicitudes_pendientes: Optional[int] = 0
    solicitudes_vencidas_sla: Optional[int] = 0
    activa: Optional[bool] = True
    desactivada_at: Optional[datetime] = None
    desactivada_por: Optional[str] = None
    has_politica_transparencia: Optional[bool] = False
    # True si algún RAT activa el umbral de DPO obligatorio (Art. 14 Ley 21.719)
    requiere_dpo: Optional[bool] = False

    model_config = {"from_attributes": True}


class CompanyPublicOut(BaseModel):
    id: int
    nombre: str
    rut: str
    email_dpo: Optional[str] = None
    contacto_dpo: Optional[str] = None
    canal_ejercicio_derechos: Optional[str] = None

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    empresas: list[CompanyOut]
    total: int
    skip: int
    limit: int
