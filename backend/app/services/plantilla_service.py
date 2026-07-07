"""
Servicio de negocio para plantillas de respuesta ARCO.
Maneja renderizado con variables y seed de plantillas por defecto.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.tkt_plantilla import TktPlantilla


PLANTILLAS_DEFAULT = [
    {
        "tipo": "acceso",
        "nombre": "Respuesta estándar — Acceso",
        "contenido": (
            "Estimado/a {{nombre_titular}}:\n\n"
            "En respuesta a su solicitud de derecho de acceso (Art. 12.1 Ley 21.719), "
            "presentada el {{fecha}}, le informamos que {{empresa}} ha procedido a identificar "
            "y entregar la totalidad de los datos personales que mantenemos tratados sobre su persona.\n\n"
            "Los datos entregados corresponden a: categoría de datos, finalidad del tratamiento, "
            "fuentes de origen, destinatarios y plazos de retención, segúnconsta en nuestro "
            "Registro de Actividades de Tratamiento (RAT).\n\n"
            "Número de solicitud: {{numero_solicitud}}\n\n"
            "Si requiere aclaraciones adicionales, responda a este correo.\n\n"
            "Atentamente,\n{{empresa}}"
        ),
    },
    {
        "tipo": "rectificacion",
        "nombre": "Respuesta estándar — Rectificación",
        "contenido": (
            "Estimado/a {{nombre_titular}}:\n\n"
            "En respuesta a su solicitud de rectificación (Art. 12.2 Ley 21.719), "
            "presentada el {{fecha}}, le informamos que {{empresa}} ha procedido a realizar "
            "las correcciones solicitadas en sus datos personales.\n\n"
            "Los campos rectificados son: los que usted indicó en su solicitud original.\n\n"
            "Número de solicitud: {{numero_solicitud}}\n\n"
            "Si requiere aclaraciones adicionales, responda a este correo.\n\n"
            "Atentamente,\n{{empresa}}"
        ),
    },
    {
        "tipo": "cancelacion",
        "nombre": "Respuesta estándar — Cancelación",
        "contenido": (
            "Estimado/a {{nombre_titular}}:\n\n"
            "En respuesta a su solicitud de cancelación (Art. 12.3 Ley 21.719), "
            "presentada el {{fecha}}, le informamos que {{empresa}} ha procedido a "
            "cancelar el tratamiento de sus datos personales, salvo en los casos en que "
            "exista una obligación legal que requiera su conservación "
            "(Art. 13 Ley 21.719).\n\n"
            "Número de solicitud: {{numero_solicitud}}\n\n"
            "Si ejerce el derecho de bloqueo temporal previo a la cancelación, "
            "indíquenos dentro de los próximos 5 días hábiles.\n\n"
            "Atentamente,\n{{empresa}}"
        ),
    },
    {
        "tipo": "oposicion",
        "nombre": "Respuesta estándar — Oposición",
        "contenido": (
            "Estimado/a {{nombre_titular}}:\n\n"
            "En respuesta a su solicitud de oposición (Art. 12.4 Ley 21.719), "
            "presentada el {{fecha}}, le informamos que {{empresa}} ha procedido a "
            "cesar el tratamiento de sus datos personales para los fines indicados "
            "en su solicitud, en cumplimiento del artículo 12 numeral 4 de la Ley 21.719.\n\n"
            "Esta oposición applies a: los tratamientos basados en interés legítimo o "
            "misión de interés público, según consta en nuestro RAT.\n\n"
            "Número de solicitud: {{numero_solicitud}}\n\n"
            "Si requiere aclaraciones adicionales, responda a este correo.\n\n"
            "Atentamente,\n{{empresa}}"
        ),
    },
    {
        "tipo": "bloqueo",
        "nombre": "Respuesta estándar — Bloqueo temporal",
        "contenido": (
            "Estimado/a {{nombre_titular}}:\n\n"
            "En respuesta a su solicitud de bloqueo temporal (Art. 8 ter Ley 21.719), "
            "presentada el {{fecha}}, le informamos que {{empresa}} ha procedido a "
            "bloquear el tratamiento de sus datos personales por un plazo de "
            "{{dias_bloqueo}} días hábiles.\n\n"
            "Durante este período, sus datos serán tratados exclusivamente con el fin "
            "de ser transmitidos a otro responsable del tratamiento o ser eliminados, "
            "según lo solicitado por usted.\n\n"
            "Número de solicitud: {{numero_solicitud}}\n\n"
            "Vencimiento del bloqueo: {{fecha_vencimiento}}\n\n"
            "Atentamente,\n{{empresa}}"
        ),
    },
]


def render_plantilla(
    contenido: str,
    nombre_titular: str,
    empresa: str,
    fecha: Optional[str] = None,
    numero_solicitud: Optional[str] = None,
    dias_bloqueo: Optional[int] = None,
    fecha_vencimiento: Optional[str] = None,
) -> str:
    """Renderiza una plantilla reemplazando variables {{variable}}."""
    if fecha is None:
        fecha = datetime.now(timezone.utc).strftime("%d-%m-%Y")
    if numero_solicitud is None:
        numero_solicitud = "—"

    resultado = contenido
    resultado = resultado.replace("{{nombre_titular}}", nombre_titular)
    resultado = resultado.replace("{{empresa}}", empresa)
    resultado = resultado.replace("{{fecha}}", fecha)
    resultado = resultado.replace("{{numero_solicitud}}", str(numero_solicitud))
    if dias_bloqueo is not None:
        resultado = resultado.replace("{{dias_bloqueo}}", str(dias_bloqueo))
    if fecha_vencimiento is not None:
        resultado = resultado.replace("{{fecha_vencimiento}}", fecha_vencimiento)

    return resultado


def seed_plantillas_default(db: Session) -> None:
    """Inserta las plantillas por defecto si no existen."""
    for data in PLANTILLAS_DEFAULT:
        existe = db.query(TktPlantilla).filter(
            TktPlantilla.tipo == data["tipo"],
            TktPlantilla.company_id.is_(None),
            TktPlantilla.nombre == data["nombre"],
        ).first()
        if not existe:
            plantilla = TktPlantilla(
                company_id=None,
                tipo=data["tipo"],
                nombre=data["nombre"],
                contenido=data["contenido"],
                activo=True,
            )
            db.add(plantilla)
    db.commit()


def get_plantillas_por_tipo(db: Session, tipo: str, company_id: Optional[int] = None) -> list[TktPlantilla]:
    """Retorna plantillas activas para un tipo, buscando primero por empresa luego globales."""
    q = db.query(TktPlantilla).filter(
        TktPlantilla.tipo == tipo,
        TktPlantilla.activo,
    )
    if company_id is not None:
        q = q.filter(
            (TktPlantilla.company_id == company_id) | (TktPlantilla.company_id.is_(None))
        )
    else:
        q = q.filter(TktPlantilla.company_id.is_(None))
    return q.order_by(TktPlantilla.company_id.desc().nullslast(), TktPlantilla.nombre).all()
