"""
Schemas Pydantic para el módulo TKT Solicitudes ARCO.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


TktTipoEnum = Literal["acceso", "rectificacion", "cancelacion", "oposicion", "bloqueo", "portabilidad"]
TktEstadoEnum = Literal["abierto", "en_proceso", "pendiente", "resuelto", "bloqueado", "rechazado", "subsanacion"]
TktPrioridadEnum = Literal["urgente", "normal", "baja"]
TktOrigenEnum = Literal["web", "email", "telefono", "presencial", "manual"]


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


class TktTicketUpdate(BaseModel):
    estado: Optional[TktEstadoEnum] = None
    prioridad: Optional[TktPrioridadEnum] = None
    responsable_id: Optional[int] = None
    respuesta_texto: Optional[str] = None
    plantilla_id: Optional[int] = None
    subsanacion_detalle: Optional[str] = None


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
    created_by: Optional[str]
    created_at: Optional[datetime]
    dias_restantes: Optional[int] = None
    sla_color: Optional[str] = None
    estado_sla: Optional[str] = None


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


class TktListResponse(BaseModel):
    tickets: list[TktTicketResponse]
    total: int
    skip: int
    limit: int
    stats: Optional[dict] = None
