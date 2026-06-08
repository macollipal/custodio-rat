"""
Servicio de negocio para módulos TKT (ticketing).
Maneja lógica de SLA, estados, y estadísticas.
"""
from datetime import datetime, date, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session


def calcular_dias_habiles(fecha_inicio: datetime, dias: int, anio: Optional[int] = None) -> datetime:
    """Calcula fecha de vencimiento sumando días hábiles (lunes a viernes, excluye feriados Chile)."""
    if anio is None:
        anio = fecha_inicio.year

    dias_restantes = dias
    fecha_actual = fecha_inicio.replace(hour=23, minute=59, second=59)

    # Feriados fijos Chile (mes, día) - sin año
    feriados_fijos = [
        (1, 1),   # Año Nuevo
        (5, 1),   # Día del Trabajo
        (5, 21),  # Glorias Navales
        (6, 29),  # San Pedro y San Pablo
        (7, 16),  # Virgen del Carmen
        (8, 15),  # Asunción
        (9, 18),  # Independencia
        (9, 19),  # Día de las Glorias del Ejército
        (10, 12), # Encuentro de Dos Mundos
        (10, 31), # Día de las Iglesias Evangélicas
        (11, 1),  # Día de Todos los Santos
        (12, 8),  # Inmaculada Concepción
        (12, 25), # Navidad
    ]

    # Semana Santa 2025-2040 (algoritmo de Gauss simplificado)
    # 2025: Abril 17-18 | 2026: Abril 3-4 | 2027: Marzo 26-27 | 2028: Abril 14-15
    # 2029: Marzo 30-31 | 2030: Abril 18-19 | 2031: Abril 10-11 | 2032: Marzo 26-27
    # 2033: Abril 15-16 | 2034: Abril 7-8 | 2035: Marzo 23-24 | 2036: Abril 12-13
    # 2037: Abril 3-4 | 2038: Abril 16-17 | 2039: Abril 8-9 | 2040: Marzo 30-31
    feriados_semana_santa = {
        2025: [(4, 17), (4, 18)],
        2026: [(4, 3), (4, 4)],
        2027: [(3, 26), (3, 27)],
        2028: [(4, 14), (4, 15)],
        2029: [(3, 30), (3, 31)],
        2030: [(4, 18), (4, 19)],
        2031: [(4, 10), (4, 11)],
        2032: [(3, 26), (3, 27)],
        2033: [(4, 15), (4, 16)],
        2034: [(4, 7), (4, 8)],
        2035: [(3, 23), (3, 24)],
        2036: [(4, 12), (4, 13)],
        2037: [(4, 3), (4, 4)],
        2038: [(4, 16), (4, 17)],
        2039: [(4, 8), (4, 9)],
        2040: [(3, 30), (3, 31)],
    }

    feriados = feriados_fijos.copy()
    if anio in feriados_semana_santa:
        feriados.extend(feriados_semana_santa[anio])

    def es_feriado(dt: datetime) -> bool:
        for mes, dia in feriados:
            if dt.month == mes and dt.day == dia:
                return True
        return False

    while dias_restantes > 0:
        fecha_actual += timedelta(days=1)
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


def crear_ticket(
    db: Session,
    company_id: int,
    tipo: str,
    titular_nombre: str,
    titular_email: str,
    prioridad: str = "normal",
    origen: str = "web",
    titular_rut: Optional[str] = None,
    descripcion: Optional[str] = None,
    created_by: Optional[str] = None,
) -> "TktSolicitudDerecho":
    """Crea un ticket TKT (para uso interno/admin)."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ahora = datetime.now(timezone.utc)
    fecha_vencimiento = calcular_dias_habiles(ahora, 10)

    ticket = TktSolicitudDerecho(
        company_id=company_id,
        tipo=tipo,
        estado="abierto",
        prioridad=prioridad,
        origen=origen,
        titular_nombre=titular_nombre,
        titular_email=titular_email,
        titular_rut=titular_rut,
        descripcion=descripcion,
        fecha_recepcion=ahora,
        fecha_vencimiento=fecha_vencimiento,
        created_by=created_by,
    )
    db.add(ticket)
    db.flush()

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=None,
        estado_nuevo="abierto",
        descripcion="Ticket creado",
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
    auto_commit: bool = True,
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
    if auto_commit:
        db.commit()
    else:
        db.flush()
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