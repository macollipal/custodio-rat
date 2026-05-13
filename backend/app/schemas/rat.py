from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator

from app.models.rat import EstadoRAT


class RATBase(BaseModel):
    nombre_proceso: str
    categoria_datos: str
    categoria_titulares: Optional[str] = None
    finalidad: str
    base_legal: str
    fuente_datos: str
    transferencia_datos: Optional[str] = None
    plazo_retencion: str
    medidas_seguridad: Optional[str] = None
    destinatarios: Optional[str] = None
    transferencia_internacional: bool = False
    pais_destino: Optional[str] = None
    garantias_transferencia_int: Optional[str] = None
    datos_sensibles: bool = False
    tipo_dato_sensible: Optional[str] = None
    evaluacion_impacto: bool = False
    estado_eipd: Optional[str] = "no_requerida"
    fecha_eipd: Optional[date] = None
    decisiones_automatizadas: bool = False
    nombre_encargado: Optional[str] = None
    tiene_contrato_encargado: bool = False
    test_interes_legitimo: Optional[str] = None
    observaciones_auditoria: Optional[str] = None

    @field_validator('estado_eipd')
    @classmethod
    def estado_eipd_valido(cls, v: Optional[str]) -> Optional[str]:
        opciones = ["no_requerida", "pendiente", "en_proceso", "completada"]
        if v is not None and v not in opciones:
            raise ValueError(f"estado_eipd debe ser uno de {opciones}")
        return v


class RATCreate(RATBase):
    company_id: int

    @field_validator("nombre_proceso")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del proceso no puede estar vacío.")
        return v.strip()

    @field_validator("base_legal")
    @classmethod
    def base_legal_valida(cls, v: str) -> str:
        opciones_validas = [
            "Consentimiento del titular",
            "Ejecución de contrato",
            "Obligación legal",
            "Interés legítimo",
            "Interés vital del titular",
            "Misión de interés público",
            "Otra",
        ]
        # Validación flexible: si no coincide exactamente, se acepta igual (puede ser texto libre)
        return v.strip()


class RATUpdate(BaseModel):
    nombre_proceso: Optional[str] = None
    categoria_datos: Optional[str] = None
    categoria_titulares: Optional[str] = None
    finalidad: Optional[str] = None
    base_legal: Optional[str] = None
    fuente_datos: Optional[str] = None
    transferencia_datos: Optional[str] = None
    plazo_retencion: Optional[str] = None
    medidas_seguridad: Optional[str] = None
    destinatarios: Optional[str] = None
    transferencia_internacional: Optional[bool] = None
    pais_destino: Optional[str] = None
    garantias_transferencia_int: Optional[str] = None
    datos_sensibles: Optional[bool] = None
    tipo_dato_sensible: Optional[str] = None
    evaluacion_impacto: Optional[bool] = None
    estado_eipd: Optional[str] = None
    fecha_eipd: Optional[date] = None
    decisiones_automatizadas: Optional[bool] = None
    nombre_encargado: Optional[str] = None
    tiene_contrato_encargado: Optional[bool] = None
    test_interes_legitimo: Optional[str] = None
    estado: Optional[EstadoRAT] = None
    observaciones_auditoria: Optional[str] = None


class RATOut(RATBase):
    id: int
    company_id: int
    estado: EstadoRAT
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completitud: Optional[int] = None
    nivel_riesgo: Optional[str] = None

    model_config = {"from_attributes": True}


class RATSugerencia(BaseModel):
    tipo_proceso: str


class RATSugerenciaOut(BaseModel):
    tipo_proceso: str
    categoria_datos: str
    categoria_titulares: str
    finalidad: str
    base_legal: str
    plazo_retencion_sugerido: str
    datos_sensibles: bool
    tipo_dato_sensible: Optional[str] = None
    evaluacion_impacto: Optional[bool] = None
    decisiones_automatizadas: Optional[bool] = None
    observacion: str


class TestInteresLegitimo(BaseModel):
    paso1_interes_legitimo: str
    paso2_necesidad: str
    paso3_balance: str


class ReportesResponse(BaseModel):
    total: int
    skip: int
    limit: int
    sort_by: str
    sort_order: str
    filtros_aplicados: dict
    rats: list[RATOut]
