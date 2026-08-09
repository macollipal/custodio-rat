from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class BreachBase(BaseModel):
    descripcion: str
    fecha_deteccion: datetime
    rats_afectados: Optional[str] = None
    datos_comprometidos: Optional[str] = None
    medidas_adoptadas: Optional[str] = None
    notificado_apdc: bool = False
    fecha_notificacion_apdc: Optional[datetime] = None
    notificado_titulares: bool = False
    fecha_notificacion_titulares: Optional[datetime] = None
    nivel_riesgo: Literal["bajo", "medio", "alto", "critico"] = "bajo"
    volumen_titulares_afectados: Optional[int] = 0
    incluye_datos_sensibles: Optional[bool] = False
    incluye_datos_nna: Optional[bool] = False
    incluye_datos_financieros: Optional[bool] = False
    naturaleza: Optional[Literal["confidencialidad", "integridad", "disponibilidad"]] = None
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    fecha_ocurrencia_estimada: Optional[datetime] = None
    efectos_probables: Optional[str] = None
    causa_raiz: Optional[Literal["error_humano", "malware", "acceso_no_autorizado", "proveedor", "perdida_equipo", "otro"]] = None
    evidencia_notificacion_apdc_folio: Optional[str] = Field(default=None, max_length=100, description="Folio/ID de la notificación a APDC")
    estado_cierre: Optional[Literal["abierta", "investigando", "contenida", "notificada", "cerrada"]] = None
    fecha_cierre: Optional[datetime] = None


class BreachCreate(BreachBase):
    company_id: int


class BreachUpdate(BaseModel):
    descripcion: Optional[str] = Field(default=None, min_length=1)
    fecha_deteccion: Optional[datetime] = None
    rats_afectados: Optional[str] = None
    datos_comprometidos: Optional[str] = None
    medidas_adoptadas: Optional[str] = None
    notificado_apdc: Optional[bool] = None
    fecha_notificacion_apdc: Optional[datetime] = None
    notificado_titulares: Optional[bool] = None
    fecha_notificacion_titulares: Optional[datetime] = None
    nivel_riesgo: Optional[Literal["bajo", "medio", "alto", "critico"]] = None
    volumen_titulares_afectados: Optional[int] = None
    incluye_datos_sensibles: Optional[bool] = None
    incluye_datos_nna: Optional[bool] = None
    incluye_datos_financieros: Optional[bool] = None
    naturaleza: Optional[Literal["confidencialidad", "integridad", "disponibilidad"]] = None
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    fecha_ocurrencia_estimada: Optional[datetime] = None
    efectos_probables: Optional[str] = None
    causa_raiz: Optional[Literal["error_humano", "malware", "acceso_no_autorizado", "proveedor", "perdida_equipo", "otro"]] = None
    evidencia_notificacion_apdc_folio: Optional[str] = None
    estado_cierre: Optional[Literal["abierta", "investigando", "contenida", "notificada", "cerrada"]] = None
    fecha_cierre: Optional[datetime] = None

    @model_validator(mode="after")
    def set_fecha_notificacion_defaults(self) -> "BreachUpdate":
        ahora = datetime.now(timezone.utc)
        if self.notificado_apdc and not self.fecha_notificacion_apdc:
            self.fecha_notificacion_apdc = ahora
        if self.notificado_titulares and not self.fecha_notificacion_titulares:
            self.fecha_notificacion_titulares = ahora
        return self


class BreachOut(BreachBase):
    id: int
    company_id: int
    creado_por: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    horas_desde_deteccion: Optional[float] = None
    plazo_apdc_vencido: Optional[bool] = None
    reportable_apdc_calculado: Optional[bool] = None
    naturaleza: Optional[str] = None
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    fecha_ocurrencia_estimada: Optional[datetime] = None
    efectos_probables: Optional[str] = None
    causa_raiz: Optional[str] = None
    evidencia_notificacion_apdc_folio: Optional[str] = None
    estado_cierre: Optional[str] = None
    fecha_cierre: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BreachListResponse(BaseModel):
    brechas: list[BreachOut]
    total: int
    skip: int
    limit: int
