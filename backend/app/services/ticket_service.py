"""
Servicio de negocio para módulos TKT (ticketing).
Maneja lógica de SLA, estados, y estadísticas.
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.services.audit_service import log_audit


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
    rat_id: Optional[int] = None,
    company_nombre: str = "la empresa",
    representante_nombre: Optional[str] = None,
    representante_rut: Optional[str] = None,
) -> "TktSolicitudDerecho":  # noqa: F821
    """Crea un ticket TKT desde el formulario público de solicitudes y envía acuse al titular."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ahora = datetime.now(timezone.utc)
    fecha_vencimiento = calcular_dias_habiles(ahora, 10)
    tracking_token = str(uuid.uuid4())

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
        rat_id=rat_id,
        tracking_token=tracking_token,
        acuse_enviado_at=ahora,
        representante_nombre=representante_nombre,
        representante_rut=representante_rut,
    )
    db.add(ticket)
    db.flush()

    from app.services.asignacion_service import evaluar_reglas_asignacion
    responsable_id = evaluar_reglas_asignacion(db, company_id, tipo, "normal")
    if responsable_id:
        ticket.responsable_id = responsable_id

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=None,
        estado_nuevo="abierto",
        descripcion="Ticket creado desde formulario público",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="crear",
        usuario=titular_email,
        detalle={
            "tipo": tipo,
            "estado": "abierto",
            "titular_nombre": titular_nombre,
            "titular_email": titular_email,
            "origen": origen,
            "representante_nombre": representante_nombre,
            "representante_rut": representante_rut,
            "tracking_token": tracking_token,
        },
    )

    db.commit()
    db.refresh(ticket)

    try:
        from app.services.email_service import notificar_acuse_solicitud
        notificar_acuse_solicitud(
            email_titular=titular_email,
            nombre_titular=titular_nombre,
            tipo_derecho=tipo,
            empresa_nombre=company_nombre,
            ticket_id=ticket.id,
            tracking_token=tracking_token,
        )
    except Exception:
        pass

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
    rat_id: Optional[int] = None,
    representante_nombre: Optional[str] = None,
    representante_rut: Optional[str] = None,
    telefono: Optional[str] = None,
    fecha_nacimiento: Optional[str] = None,
    pais: Optional[str] = None,
    # Campos nuevos gaps Ley 21.719 (Iter 10)
    metodo_verificacion_identidad: Optional[str] = None,
    evidencia_identidad: Optional[str] = None,
    evidencia_respuesta_hash: Optional[str] = None,
    causal_rechazo: Optional[str] = None,
    medio_respuesta: Optional[str] = None,
) -> "TktSolicitudDerecho":  # noqa: F821
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
        rat_id=rat_id,
        representante_nombre=representante_nombre,
        representante_rut=representante_rut,
        telefono=telefono,
        pais=pais,
        # Campos nuevos gaps Ley 21.719 (Iter 10)
        metodo_verificacion_identidad=metodo_verificacion_identidad,
        evidencia_identidad=evidencia_identidad,
        evidencia_respuesta_hash=evidencia_respuesta_hash,
        causal_rechazo=causal_rechazo,
        medio_respuesta=medio_respuesta,
    )
    if fecha_nacimiento:
        from datetime import date
        try:
            ticket.fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            pass
    db.add(ticket)
    db.flush()

    from app.services.asignacion_service import evaluar_reglas_asignacion
    responsable_id = evaluar_reglas_asignacion(db, company_id, tipo, prioridad)
    if responsable_id:
        ticket.responsable_id = responsable_id

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=None,
        estado_nuevo="abierto",
        descripcion="Ticket creado",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="crear",
        usuario=created_by or "system",
        detalle={
            "tipo": tipo,
            "estado": "abierto",
            "prioridad": prioridad,
            "titular_nombre": titular_nombre,
            "titular_email": titular_email,
            "origen": origen,
        },
    )

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

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="cambiar_estado",
        usuario=str(user_id) if user_id else "system",
        detalle={
            "estado_anterior": estado_anterior,
            "estado_nuevo": nuevo_estado,
            "descripcion": descripcion,
        },
    )

    if auto_commit:
        db.commit()
    else:
        db.flush()
    db.refresh(ticket)
    return ticket, None


def get_dashboard_stats(db: Session, company_id: Optional[int] = None) -> dict:
    """Calcula estadísticas de tickets para dashboard.

    Optimizado: 1 GROUP BY + 1 vencidos + 1 avg en vez de 9 COUNT queries.
    """
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from sqlalchemy import func

    base_filter = []
    if company_id:
        base_filter.append(TktSolicitudDerecho.company_id == company_id)

    # 1 COUNT total
    total = db.query(func.count(TktSolicitudDerecho.id)).filter(*base_filter).scalar() or 0

    # 1 GROUP BY para todos los estados
    estado_counts = (
        db.query(
            TktSolicitudDerecho.estado,
            func.count(TktSolicitudDerecho.id).label("count"),
        )
        .filter(*base_filter)
        .group_by(TktSolicitudDerecho.estado)
        .all()
    )
    counts = {row.estado: row.count for row in estado_counts}
    abiertos = counts.get("abierto", 0)
    en_proceso = counts.get("en_proceso", 0)
    pendientes = counts.get("pendiente", 0)
    resueltos = counts.get("resuelto", 0)
    bloqueados = counts.get("bloqueado", 0)
    rechazados = counts.get("rechazado", 0)
    subsanacion = counts.get("subsanacion", 0)
    prorrogas = counts.get("prorroga", 0)

    # 1 COUNT vencidos
    ahora = datetime.now(timezone.utc)
    vencidos_filter = base_filter + [
        TktSolicitudDerecho.estado.in_(["abierto", "en_proceso", "pendiente", "bloqueado", "subsanacion", "prorroga"]),
        TktSolicitudDerecho.fecha_vencimiento < ahora,
    ]
    vencidos = db.query(func.count(TktSolicitudDerecho.id)).filter(*vencidos_filter).scalar() or 0

    # Cumplimiento SLA
    resueltos_en_tiempo = (
        db.query(func.count(TktSolicitudDerecho.id))
        .filter(
            *base_filter,
            TktSolicitudDerecho.estado == "resuelto",
            TktSolicitudDerecho.respuesta_fecha <= TktSolicitudDerecho.fecha_vencimiento,
        )
        .scalar()
    ) or 0
    cumplimiento = round((resueltos_en_tiempo / resueltos) * 100, 1) if resueltos > 0 else 100.0

    # 1 AVG query para tiempo promedio
    avg_seconds = (
        db.query(
            func.avg(
                func.extract("epoch", TktSolicitudDerecho.respuesta_fecha) -
                func.extract("epoch", TktSolicitudDerecho.fecha_recepcion)
            )
        )
        .filter(
            *base_filter,
            TktSolicitudDerecho.estado == "resuelto",
            TktSolicitudDerecho.respuesta_fecha.isnot(None),
        )
        .scalar()
    )
    tiempo_promedio = round(avg_seconds / 3600, 1) if avg_seconds else 0

    # QW4 ARCO: derechos más ejercidos (1 GROUP BY extra por tipo)
    tipo_counts = (
        db.query(
            TktSolicitudDerecho.tipo,
            func.count(TktSolicitudDerecho.id).label("count"),
        )
        .filter(*base_filter)
        .group_by(TktSolicitudDerecho.tipo)
        .all()
    )
    por_tipo = {row.tipo: row.count for row in tipo_counts}

    return {
        "total": total,
        "abiertos": abiertos,
        "en_proceso": en_proceso,
        "pendientes": pendientes,
        "resueltos": resueltos,
        "bloqueados": bloqueados,
        "rechazados": rechazados,
        "subsanacion": subsanacion,
        "prorrogas": prorrogas,
        "vencidos": vencidos,
        "cumplimiento_sla": cumplimiento,
        "tiempo_promedio_horas": tiempo_promedio,
        "por_tipo": por_tipo,
    }


def bloquear_ticket(
    db: Session,
    ticket_id: int,
    rat_id: int,
    dias_bloqueo: int,
    user_id: Optional[int] = None,
) -> tuple:
    """Bloquea un RAT y marca el ticket como bloqueado (Art. 8 ter)."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.rat import RAT as RATModel
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    rat = db.query(RATModel).filter(RATModel.id == rat_id).first()
    if not rat:
        return None, "RAT no encontrado"

    if rat.company_id != ticket.company_id:
        return None, "El RAT no pertenece a la empresa del ticket"

    estado_anterior = ticket.estado
    fecha_vencimiento = calcular_dias_habiles(datetime.now(timezone.utc), dias_bloqueo)

    ticket.estado = "bloqueado"
    ticket.rat_id = rat_id
    ticket.plazo_bloqueo_vencimiento = fecha_vencimiento

    rat.bloqueado = True

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="bloqueado",
        user_id=user_id,
        descripcion=f"RAT id={rat_id} bloqueado por {dias_bloqueo} días hábiles",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="bloquear",
        usuario=str(user_id) if user_id else "system",
        detalle={
            "rat_id": rat_id,
            "dias_bloqueo": dias_bloqueo,
            "fecha_vencimiento_bloqueo": ticket.plazo_bloqueo_vencimiento.isoformat() if ticket.plazo_bloqueo_vencimiento else None,
        },
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def desbloquear_ticket(
    db: Session,
    ticket_id: int,
    user_id: Optional[int] = None,
) -> tuple:
    """Desbloquea un RAT antes del vencimiento y marca ticket como resuelto."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.rat import RAT as RATModel
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if ticket.estado != "bloqueado":
        return None, "El ticket no está en estado bloqueado"

    estado_anterior = ticket.estado

    if ticket.rat_id:
        rat = db.query(RATModel).filter(RATModel.id == ticket.rat_id).first()
        if rat:
            rat.bloqueado = False

    ticket.estado = "resuelto"
    ticket.plazo_bloqueo_vencimiento = None
    ticket.respuesta_texto = "RAT desbloqueado antes del vencimiento"
    ticket.respuesta_fecha = datetime.now(timezone.utc)

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="resuelto",
        user_id=user_id,
        descripcion="Desbloqueo anticipado del RAT",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="desbloquear",
        usuario=str(user_id) if user_id else "system",
        detalle={"rat_id": ticket.rat_id},
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def rechazar_ticket(
    db: Session,
    ticket_id: int,
    motivo: str,
    user_id: Optional[int] = None,
    motivo_detalle: Optional[str] = None,
) -> tuple:
    """Rechaza una solicitud ARCO con motivo fundado (Art. 12.5).

    Args:
        motivo: Causal de rechazo (debe estar en ``CausalRechazo``).
        motivo_detalle: Texto libre que amplía la justificación.
    """
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho, CausalRechazo
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if motivo not in [e.value for e in CausalRechazo]:
        return None, f"causal_rechazo inválida (esperado: {[e.value for e in CausalRechazo]})"

    estado_anterior = ticket.estado

    ticket.estado = "rechazado"
    ticket.causal_rechazo = motivo
    ticket.respuesta_texto = (motivo_detalle or "").strip() or motivo
    ticket.respuesta_fecha = datetime.now(timezone.utc)

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="rechazado",
        user_id=user_id,
        descripcion=f"Rechazo fundado ({motivo})" + (f": {motivo_detalle}" if motivo_detalle else ""),
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="rechazar",
        usuario=str(user_id) if user_id else "system",
        detalle={"causal_rechazo": motivo, "motivo_detalle": motivo_detalle},
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def responder_ticket_service(
    db: Session,
    ticket_id: int,
    estado: str,
    respuesta: Optional[str],
    user_id: int,
    username: str,
    descripcion_accion: Optional[str] = None,
    medio_respuesta: Optional[str] = None,
) -> tuple:
    """Wrapper centralizado para responder/solucionar un ticket ARCO.

    Centraliza:
    - Validación de identidad si estado == 'resuelto' (Art. 12).
    - Cómputo de evidencia_respuesta_hash SHA-256 (Art. 12.5).

    Returns ``(ticket, None)`` o ``(None, error_message)``.
    """
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if estado == "resuelto" and not ticket.metodo_verificacion_identidad:
        return None, (
            "Antes de marcar como resuelta debe registrar el método de verificación de identidad "
            "(Art. 12 Ley 21.719). Editá el ticket y agregá 'metodo_verificacion_identidad'."
        )

    if estado == "resuelto" and not (respuesta and respuesta.strip()):
        return None, (
            "La respuesta_texto es obligatoria para resolver una solicitud ARCO. "
            "El responsable del tratamiento debe informar su decisión al titular (Art. 12 Ley 21.719). "
            "Incluye la decisión y los motivos en el campo 'respuesta'."
        )

    ahora = datetime.now(timezone.utc)

    ticket, err = cambiar_estado_ticket(
        db=db,
        ticket_id=ticket_id,
        nuevo_estado=estado,
        user_id=user_id,
        descripcion=descripcion_accion or f"Respuesta: {estado}",
        auto_commit=False,
    )
    if err:
        return None, err

    if respuesta is not None:
        ticket.respuesta_texto = respuesta
    ticket.respuesta_fecha = ahora
    if medio_respuesta is not None:
        ticket.medio_respuesta = medio_respuesta

    if estado == "resuelto" and not ticket.evidencia_respuesta_hash:
        import hashlib
        hash_input = f"{(ticket.respuesta_texto or '').strip()}|{username}|{ahora.isoformat()}"
        ticket.evidencia_respuesta_hash = hashlib.sha256(
            hash_input.encode("utf-8")
        ).hexdigest()

    db.commit()
    db.refresh(ticket)

    return ticket, None


def guardar_portability_data(
    db: Session,
    ticket_id: int,
    portability_data: str,
    user_id: Optional[int] = None,
) -> tuple:
    """Guarda datos de portabilidad en el ticket y lo marca como resuelto."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if ticket.tipo != "portabilidad":
        return None, "El ticket no es de portabilidad"

    estado_anterior = ticket.estado

    ticket.portability_data = portability_data
    ticket.estado = "resuelto"
    ticket.respuesta_texto = "Datos de portabilidad exportados"
    ticket.respuesta_fecha = datetime.now(timezone.utc)

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="resuelto",
        user_id=user_id,
        descripcion="Exportación de portabilidad completada",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="portabilidad",
        usuario=str(user_id) if user_id else "system",
        detalle={"portability_data_length": len(portability_data)},
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def solicitar_subsanacion(
    db: Session,
    ticket_id: int,
    detalle: str,
    user_id: Optional[int] = None,
) -> tuple:
    """Solicita subsanación al titular (Art. 12 — solicitud incompleta). Pausa y extiende el plazo."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if ticket.estado not in ("abierto", "en_proceso", "pendiente"):
        return None, f"No se puede solicitar subsanación desde estado '{ticket.estado}'"

    estado_anterior = ticket.estado
    ahora = datetime.now(timezone.utc)

    ticket.estado = "subsanacion"
    ticket.subsanacion_detalle = detalle
    ticket.subsanacion_fecha_pedido = ahora
    ticket.fecha_vencimiento = calcular_dias_habiles(ahora, 10)

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="subsanacion",
        user_id=user_id,
        descripcion=f"Subsanación solicitada: {detalle}",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="subsanacion_solicitar",
        usuario=str(user_id) if user_id else "system",
        detalle={
            "detalle": detalle,
            "nuevo_plazo": ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        },
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def completar_subsanacion(
    db: Session,
    ticket_id: int,
    user_id: Optional[int] = None,
) -> tuple:
    """Completa la subsanación y vuelve a poner el ticket en proceso (plazo resumes)."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if ticket.estado != "subsanacion":
        return None, f"El ticket no está en estado subsanacion (estado actual: '{ticket.estado}')"

    estado_anterior = ticket.estado
    ahora = datetime.now(timezone.utc)

    ticket.estado = "en_proceso"
    ticket.subsanacion_detalle = None
    ticket.subsanacion_fecha_pedido = None
    ticket.fecha_vencimiento = calcular_dias_habiles(ahora, 10)

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="en_proceso",
        user_id=user_id,
        descripcion="Subsanación completada, titular entregó información faltante",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="subsanacion_completar",
        usuario=str(user_id) if user_id else "system",
        detalle={
            "nuevo_plazo": ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        },
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None


def prorrogar_ticket(
    db: Session,
    ticket_id: int,
    dias: int = 10,
    motivo: Optional[str] = None,
    user_id: Optional[int] = None,
) -> tuple:
    """Extiende el plazo de respuesta (Art. 12 bis — máximo 10 días hábiles adicionales)."""
    from app.models.tkt_solicitud_derecho import TktSolicitudDerecho
    from app.models.tkt_historial import TktHistorial

    ticket = db.query(TktSolicitudDerecho).filter(TktSolicitudDerecho.id == ticket_id).first()
    if not ticket:
        return None, "Ticket no encontrado"

    if ticket.estado in ("resuelto", "rechazado", "bloqueado"):
        return None, f"No se puede prorrogar desde estado '{ticket.estado}'"

    if ticket.prorroga_fecha is not None:
        return None, "El ticket ya fue prorrogado anteriormente"

    estado_anterior = ticket.estado
    ahora = datetime.now(timezone.utc)

    nueva_vencimiento = calcular_dias_habiles(ahora, dias)

    ticket.estado = "prorroga"
    ticket.prorroga_fecha = ahora
    ticket.prorroga_dias = dias
    ticket.fecha_vencimiento = nueva_vencimiento

    historial = TktHistorial(
        ticket_id=ticket.id,
        estado_anterior=estado_anterior,
        estado_nuevo="prorroga",
        user_id=user_id,
        descripcion=f"Prórroga de {dias} días: {motivo or 'Sin motivo'}",
    )
    db.add(historial)

    log_audit(
        db=db,
        entidad="tkt_solicitud_derecho",
        entidad_id=ticket.id,
        accion="prorrogar",
        usuario=str(user_id) if user_id else "system",
        detalle={
            "dias": dias,
            "motivo": motivo,
            "nuevo_plazo": ticket.fecha_vencimiento.isoformat() if ticket.fecha_vencimiento else None,
        },
    )

    db.commit()
    db.refresh(ticket)
    return ticket, None