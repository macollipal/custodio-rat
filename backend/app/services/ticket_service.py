"""
Servicio de negocio para módulos TKT (ticketing).
Maneja lógica de SLA, estados, y estadísticas.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session


def calcular_dias_habiles(fecha_inicio: datetime, dias: int) -> datetime:
    """Calcula fecha de vencimiento sumando días hábiles (lunes a viernes, excluye feriados Chile)."""
    dias_restantes = dias
    fecha_actual = fecha_inicio.replace(hour=23, minute=59, second=59)

    # Feriados fijos Chile (año, mes, día)
    feriados = [
        (1, 1),   # Año Nuevo
        (4, 11),  # Viernes Santo
        (4, 12),  # Sábado Santo
        (5, 1),   # Día del Trabajo
        (5, 21),  # Glorias Navales
        (6, 29),  # San Pedro y San Pablo
        (7, 16),  # Virgen del Carmen
        (8, 15),  # Asunción
        (9, 18),  # Independencia
        (9, 19),  # Día de las Glorias del Ejército
        (9, 20),  # Plebiscito (adjustable)
        (10, 12), # Encuentro de Dos Mundos
        (10, 31), # Día de las Iglesias Evangélicas
        (11, 1),  # Día de Todos los Santos
        (12, 8),  # Inmaculada Concepción
        (12, 25), # Navidad
    ]

    def es_feriado(dt: datetime) -> bool:
        for mes, dia in feriados:
            if dt.month == mes and dt.day == dia:
                return True
        return False

    while dias_restantes > 0:
        fecha_actual += timedelta(days=1)
        # Normalize to midnight for comparison
        check_date = fecha_actual.replace(hour=0, minute=0, second=0, microsecond=0)
        dia_semana = check_date.weekday()
        if dia_semana < 5 and not es_feriado(check_date):
            dias_restantes -= 1

    return fecha_actual.replace(hour=23, minute=59, second=59)


def calcular_dias_restantes(fecha_vencimiento: datetime) -> int:
    """Calcula días restantes hasta vencimiento (negativo si vencido)."""
    ahora = datetime.now(timezone.utc)
    if fecha_vencimiento.tzinfo is None:
        fecha_vencimiento = fecha_vencimiento.replace(tzinfo=timezone.utc)
    delta = fecha_vencimiento - ahora
    return delta.days


def get_sla_color(dias_restantes: int) -> str:
    """Retorna color según días restantes."""
    if dias_restantes < 0:
        return "rojo"  # Vencido
    elif dias_restantes <= 2:
        return "rojo"  # < 3 días
    elif dias_restantes <= 5:
        return "amarillo"  # 3-5 días
    else:
        return "verde"  # > 5 días


def get_estado_sla(dias_restantes: int, estado: str) -> str:
    """Retorna estado SLA considerando también estado del ticket."""
    if estado == "resuelto":
        return "cumplido"
    if dias_restantes < 0:
        return "vencido"
    return "activo"


def crear_ticket_desde_solicitud(
    db: Session,
    company_id: int,
    tipo: str,
    titular_nombre: str,
    titular_email: str,
    descripcion: Optional[str] = None,
    titular_rut: Optional[str] = None,
    origen: str = "web",
) -> "TktSolicitudDerecho":
    """Crea un ticket TKT desde el formulario público de solicitudes."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ahora = datetime.now(timezone.utc)
    fecha_vencimiento = calcular_dias_habiles(ahora, 10)

    ticket = TktSolicitudDerecho(
        company_id=company_id,
        tipo=tipo,
        estado="abierto",
        prioridad="normal",
        origen=origen,
        titular_nombre=titular_nombre,
        titular_email=titular_email,
        titular_rut=titular_rut,
        descripcion=descripcion,
        fecha_recepcion=ahora,
        fecha_vencimiento=fecha_vencimiento,
    )
    db.add(ticket)
    db.flush()

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=None,
        estado_nuevo="abierto",
        descripcion="Ticket creado desde formulario público",
    )
    db.add(historial)
    db.commit()
    db.refresh(ticket)
    return ticket


def cambiar_estado_ticket(
    db: Session,
    ticket_id: int,
    nuevo_estado: str,
    user_id: Optional[int] = None,
    descripcion: Optional[str] = None,
) -> tuple:
    """Cambia estado de ticket y registra historial."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    estado_anterior = ticket.estado
    ticket.estado = nuevo_estado

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        user_id=user_id,
        descripcion=descripcion or f"Estado cambiado a {nuevo_estado}",
    )
    db.add(historial)
    db.commit()
    db.refresh(ticket)
    return ticket, None


def get_dashboard_stats(db: Session, company_id: Optional[int] = None) -> dict:
    """Calcula estadísticas de tickets para dashboard."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from sqlalchemy import func

    query = db.query(TktSolicitudDerecho)
    if company_id:
        query = query.filter(TktSolicitudDerecho.company_id == company_id)

    total = query.count()
    abiertos = query.filter(TktSolicitudDerecho.estado == "abierto").count()
    en_proceso = query.filter(TktSolicitudDerecho.estado == "en_proceso").count()
    pendientes = query.filter(TktSolicitudDerecho.estado == "pendiente").count()
    resueltos = query.filter(TktSolicitudDerecho.estado == "resuelto").count()

    ahora = datetime.now(timezone.utc)
    vencidos = query.filter(
        TktSolicitudDerecho.estado.in_(["abierto", "en_proceso", "pendiente"]),
        TktSolicitudDerecho.fecha_vencimiento < ahora,
    ).count()

    # Cumplimiento SLA
    total_con_sla = query.filter(TktSolicitudDerecho.estado == "resuelto").count()
    resueltos_en_tiempo = query.filter(
        TktSolicitudDerecho.estado == "resuelto",
        TktSolicitudDerecho.respuesta_fecha <= TktSolicitudDerecho.fecha_vencimiento,
    ).count()
    cumplimiento = round((resueltos_en_tiempo / total_con_sla) * 100, 1) if total_con_sla > 0 else 100.0

    # Tiempo promedio primera respuesta
    avg_query = db.query(
        func.avg(
            func.extract('epoch', TktSolicitudDerecho.respuesta_fecha) -
            func.extract('epoch', TktSolicitudDerecho.fecha_recepcion)
        )
    ).filter(
        TktSolicitudDerecho.estado == "resuelto",
        TktSolicitudDerecho.respuesta_fecha.isnot(None),
    )
    if company_id:
        avg_query = avg_query.filter(TktSolicitudDerecho.company_id == company_id)
    avg_seconds = avg_query.scalar()
    tiempo_promedio = round(avg_seconds / 3600, 1) if avg_seconds else 0

    return {
        "total": total,
        "abiertos": abiertos,
        "en_proceso": en_proceso,
        "pendientes": pendientes,
        "resueltos": resueltos,
        "vencidos": vencidos,
        "cumplimiento_sla": cumplimiento,
        "tiempo_promedio_horas": tiempo_promedio,
    }