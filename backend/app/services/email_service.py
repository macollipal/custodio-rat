"""
Servicio de envío de correos electrónicos via SMTP.
Usa smtplib estándar de Python (sin dependencias extra).
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Raised when email sending fails despite SMTP being configured."""
    pass


def send_email(to: str, subject: str, html_body: str, text_body: str = "", *, raise_on_failure: bool = False) -> bool:
    """
    Envía un correo electrónico.
    Retorna True si fue exitoso, False si falló (no lanza excepciones).
    Si raise_on_failure=True, lanza EmailError en vez de retornar False.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP no configurado. Correo no enviado.")
        if raise_on_failure:
            raise EmailError("SMTP no configurado")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
        msg["To"] = to

        msg.attach(MIMEText(text_body or html_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM or settings.SMTP_USER, [to], msg.as_string())

        logger.info(f"Correo enviado a {to}: {subject}")
        return True
    except EmailError:
        raise
    except Exception as e:
        logger.error(f"Error al enviar correo a {to}: {e}")
        if raise_on_failure:
            raise EmailError(f"Error al enviar correo a {to}: {e}")
        return False


def _estado_label(estado: str) -> str:
    labels = {
        "pendiente": "Pendiente",
        "en_proceso": "En proceso",
        "resuelta": "Resuelta",
        "rechazada": "Rechazada",
    }
    return labels.get(estado, estado)


def notificar_cambio_estado_solicitud(
    email_titular: str,
    nombre_titular: str,
    tipo_derecho: str,
    estado: str,
    respuesta: str,
    empresa_nombre: str,
) -> bool:
    """
    Envía notificación al titular cuando cambia el estado de su solicitud ARCO.
    """
    tipo_labels = {
        "acceso": "Acceso",
        "rectificacion": "Rectificación",
        "cancelacion": "Cancelación",
        "oposicion": "Oposición",
    }
    tipo = tipo_labels.get(tipo_derecho, tipo_derecho)
    estado_label = _estado_label(estado)

    subject = f"Respuesta a tu solicitud de {tipo} — {empresa_nombre}"

    text = f"""
Estimado/a {nombre_titular},

Tu solicitud de {tipo} ha sido actualizada.

Empresa: {empresa_nombre}
Estado: {estado_label}

{respuesta if respuesta else "(Sin mensaje adicional)"}

Si tienes consultas, contacta directamente a la empresa.

Saludos,
Sistema Custodio — Gestión RAT
    """.strip()

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #374151;">
  <div style="background: linear-gradient(135deg, #1E3A5F, #2563EB); padding: 20px; border-radius: 8px 8px 0 0;">
    <h1 style="color: white; margin: 0; font-size: 18px;">Custodio — Gestión RAT</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 13px;">{empresa_nombre}</p>
  </div>
  <div style="background: #fff; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
    <p style="margin: 0 0 16px;">Estimado/a <strong>{nombre_titular}</strong>,</p>
    <p style="margin: 0 0 16px;">Tu solicitud de <strong>{tipo}</strong> ha sido actualizada.</p>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px; width: 120px;">Empresa</td>
        <td style="padding: 6px 0; font-size: 14px;"><strong>{empresa_nombre}</strong></td>
      </tr>
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px;">Estado</td>
        <td style="padding: 6px 0; font-size: 14px;">
          <span style="display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
            {("background: #FEF3C7; color: #92400E;" if estado == "pendiente" else
              "background: #DBEAFE; color: #1E40AF;" if estado == "en_proceso" else
              "background: #DCFCE7; color: #166534;" if estado == "resuelta" else
              "background: #FEE2E2; color: #991B1B;")}">{estado_label}</span>
        </td>
      </tr>
    </table>
    {f'<div style="background: #f3f4f6; padding: 12px; border-radius: 6px; font-size: 14px; margin-bottom: 16px;"><strong>Respuesta:</strong><br>{respuesta}</div>' if respuesta else ''}
    <p style="font-size: 13px; color: #9ca3af; margin-top: 24px;">
      Si tienes consultas, contacta directamente a la empresa.
    </p>
  </div>
</body>
</html>
"""

    return send_email(email_titular, subject, html, text)


def notificar_nueva_solicitud_arco(
    email_dpo: str,
    nombre_dpo: str,
    nombre_titular: str,
    tipo_derecho: str,
    empresa_nombre: str,
) -> bool:
    """
    Envía notificación al DPO de la empresa cuando llega una nueva solicitud ARCO.
    """
    tipo_labels = {
        "acceso": "Acceso",
        "rectificacion": "Rectificación",
        "cancelacion": "Cancelación",
        "oposicion": "Oposición",
    }
    tipo = tipo_labels.get(tipo_derecho, tipo_derecho)

    subject = f"Nueva solicitud ARCO Received — {empresa_nombre}"

    text = f"""
Se ha recibido una nueva solicitud de ejercicio de derechos.

Empresa: {empresa_nombre}
Titular: {nombre_titular}
Tipo de derecho: {tipo}

Accede al sistema Custodio para procesarla dentro de los plazos legales.

Sistema Custodio — Gestión RAT
    """.strip()

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #374151;">
  <div style="background: linear-gradient(135deg, #1E3A5F, #DC2626); padding: 20px; border-radius: 8px 8px 0 0;">
    <h1 style="color: white; margin: 0; font-size: 18px;">Nueva solicitud ARCO</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 13px;">{empresa_nombre}</p>
  </div>
  <div style="background: #fff; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
    <p style="margin: 0 0 16px;">Estimado/a <strong>{nombre_dpo or 'DPO'}</strong>,</p>
    <p style="margin: 0 0 16px;">Se ha recibido una nueva solicitud de ejercicio de derechos que requiere su atención.</p>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px; width: 120px;">Titular</td>
        <td style="padding: 6px 0; font-size: 14px;"><strong>{nombre_titular}</strong></td>
      </tr>
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px;">Tipo</td>
        <td style="padding: 6px 0; font-size: 14px;"><strong>{tipo}</strong></td>
      </tr>
    </table>
    <p style="font-size: 13px; color: #9ca3af; margin-top: 24px;">
      Accede al sistema Custodio para procesarla.
    </p>
  </div>
</body>
</html>
"""

    return send_email(email_dpo, subject, html, text)


def notificar_nueva_brecha(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    descripcion: str,
    fecha_deteccion: str,
) -> bool:
    """
    Envía notificación al DPO cuando se registra una nueva brecha de seguridad.
    Advierte sobre el plazo legal de 72 horas para notificar a APDC.
    """
    subject = f"Brecha de seguridad detectada — {nombre_empresa}"

    text = f"""
SE HA REGISTRADO UNA BRECHA DE SEGURIDAD.

Empresa: {nombre_empresa}
Fecha de detección: {fecha_deteccion}
Descripción: {descripcion}

PLAZO LEGAL: Debe notificar a la APDP (Agencia de Protección de Datos Personales)
dentro de las próximas 72 horas desde la fecha de detección.

Accede al sistema Custodio para registrar la notificación y notificar a los titulares
afectados si corresponde.

Sistema Custodio — Gestión RAT
    """.strip()

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #374151;">
  <div style="background: linear-gradient(135deg, #7F1D1D, #DC2626); padding: 20px; border-radius: 8px 8px 0 0;">
    <h1 style="color: white; margin: 0; font-size: 18px;">Brecha de seguridad detectada</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 4px 0 0; font-size: 13px;">{nombre_empresa}</p>
  </div>
  <div style="background: #fff; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 8px 8px;">
    <p style="margin: 0 0 16px;">Estimado/a <strong>{nombre_dpo or 'DPO'}</strong>,</p>
    <p style="margin: 0 0 16px; color: #DC2626; font-weight: 600;">Se ha registrado una nueva brecha de seguridad en su organización.</p>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px; width: 140px;">Fecha de detección</td>
        <td style="padding: 6px 0; font-size: 14px;"><strong>{fecha_deteccion}</strong></td>
      </tr>
      <tr>
        <td style="padding: 6px 0; color: #6b7280; font-size: 14px; width: 140px;">Descripción</td>
        <td style="padding: 6px 0; font-size: 14px;">{descripcion}</td>
      </tr>
    </table>
    <div style="background: #FEE2E2; border: 1px solid #FECACA; border-radius: 6px; padding: 12px; margin-bottom: 16px;">
      <p style="margin: 0; font-size: 14px; font-weight: 600; color: #991B1B;">⚠️ Plazo legal: 72 horas para notificar a la APDP</p>
      <p style="margin: 4px 0 0; font-size: 13px; color: #B91C1C;">Notifique a la Agencia de Protección de Datos Personales dentro de este plazo.</p>
    </div>
    <p style="font-size: 13px; color: #9ca3af; margin-top: 24px;">
      Accede al sistema Custodio para gestionar la brecha.
    </p>
  </div>
</body>
</html>
"""

    return send_email(email_dpo, subject, html, text)
