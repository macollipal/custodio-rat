"""
Servicio de email para notificaciones transaccionales.

Configuración vía env vars:
  SMTP_HOST         (ej. smtp.sendgrid.net)
  SMTP_PORT         (ej. 587)
  SMTP_USERNAME     (ej. apikey)
  SMTP_PASSWORD     (password o API key)
  SMTP_FROM_EMAIL   (ej. noreply@custodio-rat.cl)
  SMTP_FROM_NAME    (ej. Custodio RAT Manager)
  SMTP_USE_TLS      ("true" por defecto)

Si SMTP_HOST no está configurado, el servicio opera en modo DRY_RUN:
- loguea la intención de envío (incluyendo cuerpo) a nivel INFO
- NO llama a smtplib
- retorna True para no bloquear al caller

En modo real (SMTP_HOST configurado), si smtplib lanza excepción, se
propaga EmailError para que el caller decida cómo manejar (sin
silenciar).
"""

import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Excepción para errores de envío de email."""
    pass


def _is_configured() -> bool:
    return bool(os.getenv("SMTP_HOST"))


def _send_raw(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Envía el email. Retorna True si se envió OK o está en dry-run.
    Levanta EmailError si SMTP falla.
    """
    if not _is_configured():
        logger.info(
            f"[DRY_RUN email] to={to_email} subject={subject!r} "
            f"text_len={len(text_body)} html_len={len(html_body)}"
        )
        return True

    host = os.environ["SMTP_HOST"]
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@localhost")
    from_name = os.getenv("SMTP_FROM_NAME", "Custodio RAT")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
                if username:
                    server.login(username, password)
                server.sendmail(from_email, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                if use_tls:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                if username:
                    server.login(username, password)
                server.sendmail(from_email, [to_email], msg.as_string())
    except smtplib.SMTPException as e:
        raise EmailError(f"SMTP error enviando a {to_email}: {e}") from e
    except (OSError, ssl.SSLError) as e:
        raise EmailError(f"Error de red/SSL enviando a {to_email}: {e}") from e

    logger.info(f"Email enviado OK a {to_email} subject={subject!r}")
    return True


def _render_template(
    titulo: str, saludo: str, cuerpo_html: str, footer: str = ""
) -> tuple[str, str]:
    text = f"{titulo}\n\n{saludo}\n\n{cuerpo_html}\n\n{footer}\n— Custodio RAT Manager"
    html = f"""
    <html><body style="font-family: -apple-system, system-ui, sans-serif; color:#111827; line-height:1.5;">
      <div style="max-width:560px; margin:0 auto; padding:24px;">
        <h2 style="color:#1E40AF; margin:0 0 16px;">{titulo}</h2>
        <p>{saludo}</p>
        <div>{cuerpo_html}</div>
        {f'<p style="margin-top:24px; color:#6B7280; font-size:12px;">{footer}</p>' if footer else ""}
        <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0;" />
        <p style="color:#9CA3AF; font-size:11px;">Custodio RAT Manager · Ley 21.719</p>
      </div>
    </body></html>
    """
    return text, html


def notificar_nueva_brecha(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    descripcion: str,
    fecha_deteccion: str,
) -> None:
    """
    Notifica al DPO que se reportó una nueva brecha de seguridad.
    """
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    cuerpo = (
        f"<p>Se ha reportado una nueva brecha de seguridad en la empresa "
        f"<strong>{nombre_empresa}</strong>:</p>"
        f"<ul>"
        f"<li><strong>Fecha de detección:</strong> {fecha_deteccion}</li>"
        f"<li><strong>Descripción:</strong> {descripcion}</li>"
        f"</ul>"
        f"<p>Recuerde que la Ley 21.719 exige notificar a la APDP en un plazo "
        f"máximo de 72 horas desde la detección.</p>"
    )
    footer = "Plazo APDC: 72 horas desde la detección."
    text, html = _render_template(
        "Nueva brecha de seguridad detectada", saludo, cuerpo, footer
    )
    _send_raw(email_dpo, f"[Custodio] Nueva brecha - {nombre_empresa}", html, text)


def notificar_vencimiento_rat(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    nombre_proceso: str,
    rat_id: int,
    dias_remanente: int,
) -> None:
    """
    Notifica al DPO que un RAT está próximo a vencer o ya venció.
    """
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    estado = "ya venció" if dias_remanente <= 0 else f"vence en {dias_remanente} día(s)"
    cuerpo = (
        f"<p>El proceso <strong>{nombre_proceso}</strong> (ID #{rat_id}) de la empresa "
        f"<strong>{nombre_empresa}</strong> requiere revisión periódica ({estado}).</p>"
        f"<p>La Ley 21.719 exige mantener el RAT actualizado. Por favor, revise los "
        f"datos del proceso en el sistema.</p>"
    )
    text, html = _render_template(
        f"RAT requiere revisión: {nombre_proceso}", saludo, cuerpo
    )
    _send_raw(email_dpo, f"[Custodio] RAT {estado}: {nombre_proceso}", html, text)


def notificar_respuesta_arco(
    email_titular: str,
    nombre_titular: Optional[str],
    tipo_derecho: str,
    respuesta: str,
    empresa_nombre: str,
) -> None:
    """
    Notifica al titular que su solicitud ARCO fue respondida.
    (Usado por V1-07.)
    """
    saludo = f"Estimado/a {nombre_titular or 'titular'}:"
    cuerpo = (
        f"<p>Su solicitud de derecho <strong>{tipo_derecho}</strong> presentada ante "
        f"<strong>{empresa_nombre}</strong> ha sido respondida:</p>"
        f"<blockquote style=\"border-left:3px solid #2563EB; padding:8px 12px; "
        f"margin:12px 0; color:#374151; background:#F9FAFB;\">{respuesta}</blockquote>"
        f"<p>Si requiere aclaraciones adicionales, responda a este correo.</p>"
    )
    text, html = _render_template(
        f"Respuesta a su solicitud {tipo_derecho}", saludo, cuerpo
    )
    _send_raw(email_titular, f"[Custodio] Respuesta a su solicitud {tipo_derecho}", html, text)
