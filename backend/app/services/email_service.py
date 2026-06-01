"""
Servicio de email para notificaciones.
Actualmente stub: las funciones existen pero el envío está deshabilitado.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Excepción para errores de envío de email."""
    pass


def notificar_nueva_brecha(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    descripcion: str,
    fecha_deteccion: str,
) -> None:
    """
    Envía notificación al DPO cuando se crea una nueva brecha de seguridad.
    Por ahora es un stub que solo loguea; implementar con SendGrid/AWS SES/etc.
    """
    logger.info(
        f"[STUB] Notificación brecha -> DPO: {nombre_dpo} <{email_dpo}> "
        f"Empresa: {nombre_empresa} | Fecha: {fecha_deteccion} | "
        f"Descripción: {descripcion[:100]}"
    )
    raise EmailError("Email service not configured")