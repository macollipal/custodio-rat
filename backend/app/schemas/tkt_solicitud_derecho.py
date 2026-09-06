"""
Schemas Pydantic para el módulo TKT Solicitudes ARCO.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, model_validator


TktTipoEnum = Literal["acceso", "rectificacion", "cancelacion", "oposicion", "bloqueo", "portabilidad"]
TktEstadoEnum = Literal["abierto", "en_proceso", "pendiente", "resuelto", "bloqueado", "rechazado", "subsanacion", "prorroga"]
TktPrioridadEnum = Literal["urgente", "normal", "baja"]
TktOrigenEnum = Literal["web", "email", "telefono", "presencial", "manual"]
CausalRechazoEnum = Literal[
    "falta_identidad",
    "solicitud_manifiestamente_infundada",
    "solicitud_excesiva",
    "falta_poder_notorial",
    "plazo_vencido",
    "identidad_no_verificada",
    "otro",
]


class TktTicketCreate(BaseModel):
    company_id: int
    tipo: TktTipoEnum
    prioridad: TktPrioridadEnum = "normal"
    origen: TktOrigenEnum = "web"
    titular_nombre: str
    titular_email: EmailStr
    rut_titular: Optional[str] = None
    descripcion: Optional[str] = None
    rat_id: Optional[int] = None
    telefono: Optional[str] = Field(default=None, max_length=50)
    fecha_nacimiento: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    pais: Optional[str] = Field(default=None, max_length=100)
    representante_nombre: Optional[str] = Field(default=None, max_length=255)
    representante_rut: Optional[str] = Field(default=None, max_length=20)
    representante_poder_notarial_notas: Optional[str] = Field(
        default=None,
        description="Descripción o referencia del poder notarial que acredita la representación (Art. 14 quater)",
    )
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Optional[str] = Field(default=None, max_length=50, description="Enum: cedula, firma_digital, video_call, otro")

    @model_validator(mode="after")
    def validar_poder_notarial_representante(self):
        if self.representante_nombre and not self.representante_poder_notarial_notas:
            raise ValueError(
                "Si hay representante, debe especificarse representante_poder_notarial_notas "
                "con la referencia o descripción del poder notarial (Art. 14 quater)."
            )
        return self
    evidencia_identidad: Optional[str] = Field(default=None, description="Descripción de docs/verificación usada")
    evidencia_respuesta_hash: Optional[str] = Field(default=None, max_length=64, description="SHA-256 de la respuesta enviada")
    causal_rechazo: Optional[CausalRechazoEnum] = Field(default=None, description="Causal de rechazo (Art. 29 RL): falta_identidad, solicitud_manifiestamente_infundada, solicitud_excesiva, falta_poder_notorial, plazo_vencido, identidad_no_verificada, otro")
    medio_respuesta: Optional[str] = Field(default=None, max_length=50, description="Enum: email, domicilio, portal, telefono")


class TktTicketUpdate(BaseModel):
    estado: Optional[TktEstadoEnum] = None
    prioridad: Optional[TktPrioridadEnum] = None
    responsable_id: Optional[int] = None
    respuesta_texto: Optional[str] = None
    plantilla_id: Optional[int] = None
    subsanacion_detalle: Optional[str] = None
    # ARCO-QW10: editar RUT titular y representante post-creación
    titular_rut: Optional[str] = Field(default=None, max_length=20)
    representante_rut: Optional[str] = Field(default=None, max_length=20)
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Optional[str] = None
    evidencia_identidad: Optional[str] = None
    # evidencia_respuesta_hash: calculado server-side, no aceptado como input (Art. 12.5)
    causal_rechazo: Optional[CausalRechazoEnum] = None
    medio_respuesta: Optional[str] = None


class TktSubsanarRequest(BaseModel):
    detalle: str = Field(..., min_length=10, max_length=1000, description="Detalle de la información faltante requerida al titular")


class TktNotaCreate(BaseModel):
    nota: str


class TktNotaResponse(BaseModel):
    id: int
    nota: str
    user_id: int
    created_at: datetime


class TktHistorialResponse(BaseModel):
    id: int
    estado_anterior: Optional[str]
    estado_nuevo: str
    descripcion: Optional[str]
    user_id: int
    created_at: datetime


class TktTicketResponse(BaseModel):
    id: int
    company_id: int
    tipo: str
    estado: str
    prioridad: str
    origen: str
    titular_nombre: str
    titular_email: str
    titular_rut: Optional[str]
    descripcion: Optional[str]
    fecha_recepcion: Optional[datetime]
    fecha_vencimiento: Optional[datetime]
    responsable_id: Optional[int]
    respuesta_texto: Optional[str]
    respuesta_fecha: Optional[datetime]
    rat_id: Optional[int]
    plazo_bloqueo_vencimiento: Optional[datetime]
    portability_data: Optional[str]
    tracking_token: Optional[str]
    acuse_enviado_at: Optional[datetime]
    subsanacion_detalle: Optional[str]
    subsanacion_fecha_pedido: Optional[datetime]
    prorroga_fecha: Optional[datetime]
    prorroga_dias: Optional[int]
    created_by: Optional[str]
    created_at: Optional[datetime]
    representante_nombre: Optional[str] = None
    representante_rut: Optional[str] = None
    representante_poder_notarial_notas: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    pais: Optional[str] = None
    dias_restantes: Optional[int] = None
    sla_color: Optional[str] = None
    estado_sla: Optional[str] = None
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Optional[str] = None
    evidencia_identidad: Optional[str] = None
    evidencia_respuesta_hash: Optional[str] = None
    causal_rechazo: Optional[str] = None
    medio_respuesta: Optional[str] = None


class TktBloquearRequest(BaseModel):
    rat_id: int
    dias_bloqueo: int = 2


class TktExportPortabilidadResponse(BaseModel):
    id: int
    company_id: int
    tipo: str
    titular_nombre: str
    titular_email: str
    titular_rut: Optional[str]
    descripcion: Optional[str]
    estado: str
    fecha_recepcion: Optional[str]
    portability_data: Optional[str]
    exportado_en: Optional[str]


class TktDashboardResponse(BaseModel):
    total: int
    abiertos: int
    en_proceso: int
    pendientes: int
    resueltos: int
    vencidos: int
    cumplimiento_sla: float
    tiempo_promedio_horas: float
    por_tipo: dict = Field(default_factory=dict, description="QW4: derechos más ejercidos, agrupados por tipo (acceso, rectificacion, cancelacion, oposicion, portabilidad, bloqueo)")


class TktListResponse(BaseModel):
    tickets: list[TktTicketResponse]
    total: int
    skip: int
    limit: int
    stats: Optional[dict] = None


class TktProrrogarRequest(BaseModel):
    dias: int = Field(default=10, ge=1, le=10, description="Días de extensión (máximo 10 días hábiles, Art. 12 bis)")
    motivo: Optional[str] = Field(default=None, max_length=500, description="Motivo de la prorroga (opcional)")
