"""
QW8: Portal público del Titular — Consulta de estado por tracking_token.
No requiere autenticación. Acceso público.

C7 fix (2026-07-18): rate limit 10/minute por IP para prevenir enumeración
de tracking tokens (compliance + seguridad).
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.limiter import limiter
from app.database.database import get_db
from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
from app.models.tkt_historial import TktHistorial


router = APIRouter(prefix="/seguimiento", tags=["Seguimiento Público"])


class SeguimientoEntry(BaseModel):
    estado_anterior: Optional[str]
    estado_nuevo: str
    descripcion: Optional[str]
    fecha: str


class SeguimientoResponse(BaseModel):
    id: int
    tipo: str
    estado: str
    fecha_recepcion: Optional[str]
    fecha_vencimiento: Optional[str]
    dias_restantes: Optional[int]
    company_nombre: Optional[str]
    evidencia_respuesta_hash: Optional[str] = None
    historial: List[SeguimientoEntry]


TIPO_LABELS = {
    "acceso": "Acceso",
    "rectificacion": "Rectificación",
    "cancelacion": "Cancelación",
    "oposicion": "Oposición",
    "bloqueo": "Bloqueo temporal",
    "portabilidad": "Portabilidad",
}

ESTADO_LABELS = {
    "abierto": "Abierto",
    "en_proceso": "En Proceso",
    "pendiente": "Pendiente",
    "resuelto": "Resuelto",
    "bloqueado": "Bloqueado",
    "rechazado": "Rechazado",
    "subsanacion": "Subsanación",
    "prorroga": "Prórroga",
}


@router.get("/{tracking_token}", response_model=SeguimientoResponse, summary="Consultar estado de solicitud ARCO por tracking token")
@limiter.limit("10/minute")
def consultar_seguimiento(
    request: Request,
    tracking_token: str,
    db: Session = Depends(get_db),
):
    """
    Permite al titular consultar el estado de su solicitud usando el tracking_token
    que recibió por email. No requiere autenticación.
    """
    ticket = db.query(TktSolicitudDerecho).filter(
        TktSolicitudDerecho.tracking_token == tracking_token
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="No se encontró ninguna solicitud con ese número de seguimiento. Verificá el número e intentá de nuevo.")

    historial = db.query(TktHistorial).filter(
        TktHistorial.ticket_id == ticket.id
    ).order_by(TktHistorial.created_at.asc()).limit(100).all()

    from datetime import datetime, timezone
    dias_restantes = None
    if ticket.fecha_vencimiento:
        v = ticket.fecha_vencimiento
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        delta = v - datetime.now(timezone.utc)
        dias_restantes = delta.days

    company_nombre = None
    if ticket.company:
        company_nombre = ticket.company.nombre

    return SeguimientoResponse(
        id=ticket.id,
        tipo=TIPO_LABELS.get(ticket.tipo, ticket.tipo),
        estado=ESTADO_LABELS.get(ticket.estado, ticket.estado),
        fecha_recepcion=ticket.fecha_recepcion.isoformat() if ticket.fecha_recepcion else None,
        fecha_vencimiento=ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        dias_restantes=dias_restantes,
        company_nombre=company_nombre,
        evidencia_respuesta_hash=ticket.evidencia_respuesta_hash if hasattr(ticket, "evidencia_respuesta_hash") else None,
        historial=[
            SeguimientoEntry(
                estado_anterior=h.estado_anterior,
                estado_nuevo=ESTADO_LABELS.get(h.estado_nuevo, h.estado_nuevo),
                descripcion=h.descripcion,
                fecha=h.created_at.isoformat() if h.created_at else None,
            )
            for h in historial
        ],
    )
