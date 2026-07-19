"""
Schemas Pydantic para Consentimiento.

C4 fix (2026-07-18): ConsentimientoOut.descifra los campos *_cipher desde
BD on-demand. El modelo SQLAlchemy NO tiene columnas plaintext, por lo que
este schema es responsable de exponer los datos legibles.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_serializer


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
    ip_origen: Optional[str] = None  # siempre será IP enmascarada
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("nombre_titular", when_used="json")
    def _ser_nombre(self, v: str) -> str:
        return v  # ya viene descifrado

    @classmethod
    def from_orm_cifrado(cls, obj) -> "ConsentimientoOut":
        """Construye desde modelo SQLAlchemy, descifrando los *_cipher."""
        from app.services.consentimiento_service import (
            descifrar_nombre, descifrar_email, descifrar_texto
        )
        return cls(
            id=obj.id,
            company_id=obj.company_id,
            rat_id=obj.rat_id,
            nombre_titular=descifrar_nombre(obj),
            email_titular=descifrar_email(obj),
            canal=obj.canal.value if hasattr(obj.canal, "value") else obj.canal,
            texto_consentimiento=descifrar_texto(obj),
            fecha_obtencion=obj.fecha_obtencion,
            fecha_revocacion=obj.fecha_revocacion,
            activo=obj.activo,
            ip_origen=obj.ip_origen_masked,
            created_at=obj.created_at,
        )


class ConsentimientoListResponse(BaseModel):
    consentimientos: list[ConsentimientoOut]
    total: int
    skip: int
    limit: int
