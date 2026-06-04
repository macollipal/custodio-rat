"""
Schemas Pydantic para el módulo TKT Solicitudes ARCO.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr


TktTipoEnum = Literal["acceso", "rectificacion", "cancelacion", "oposicion"]
TktEstadoEnum = Literal["abierto", "en_proceso", "pendiente", "resuelto"]
TktPrioridadEnum = Literal["alta", "normal", "baja"]
TktOrigenEnum = Literal["web", "email", "telefono", "presencial", "manual"]


class TktTicketCreate(BaseModel):
    company_id: int
    tipo: TktTipoEnum
    prioridad: TktPrioridadEnum = "normal"
    origen: TktOrigenEnum = "web"
    titular_nombre: str
    titular_email: EmailStr
    titular_rut: Optional[str] = None
    descripcion: Optional[str] = None


class TktTicketUpdate(BaseModel):
    estado: Optional[TktEstadoEnum] = None
    prioridad: Optional[TktPrioridadEnum] = None
    responsable_id: Optional[int] = None
    respuesta_texto: Optional[str] = None


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
    created_by: Optional[str]
    created_at: Optional[datetime]
    dias_restantes: Optional[int] = None
    sla_color: Optional[str] = None
    estado_sla: Optional[str] = None


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
