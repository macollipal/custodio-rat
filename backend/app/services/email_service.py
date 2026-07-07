"""
Servicio de email para notificaciones transaccionales.

Configuración vía SMTP_URL (formato DSN):
  smtplib://apikey:SG.xxx@smtp.sendgrid.net:587/?use_tls=true&from_email=admin@yopmail.com&from_name=Custodio%20RAT%20Manager

Compatibilidad hacia atrás: si SMTP_URL no está configurada, busca
SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL,
SMTP_FROM_NAME, SMTP_USE_TLS sueltas (legacy).

Si SMTP_HOST/SMTP_URL no está configurado, el servicio opera en modo DRY_RUN:
- loguea la intención de envío (incluyendo cuerpo) a nivel INFO
- NO llama a smtplib
- retorna True para no bloquear al caller

En modo real, si smtplib lanza excepción, se propaga EmailError para
que el caller decida cómo manejar (sin silenciar).
"""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.smtp_config import get_smtp_config

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Excepción para errores de envío de email."""
    pass


def _send_raw(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Envía el email. Retorna True si se envió OK o está en dry-run.
    Levanta EmailError si SMTP falla.
    """
    cfg = get_smtp_config()
    if not cfg:
        logger.info(
            f"[DRY_RUN email] to={to_email} subject={subject!r} "
            f"text_len={len(text_body)} html_len={len(html_body)}"
        )
        return True

    host = cfg.host
    port = cfg.port
    username = cfg.username
    password = cfg.password
    from_email = cfg.from_email
    from_name = cfg.from_name
    use_tls = cfg.use_tls

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


def notificar_vencimiento_encargado(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    nombre_encargado: str,
    finalidad: str,
    dias_restantes: int,
) -> None:
    """
    Notifica al DPO que un contrato de encargado del tratamiento está por vencer.
    """
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    estado = "por vencer" if dias_restantes > 0 else "ya venció"
    plazo = f"en {dias_restantes} día(s)" if dias_restantes > 0 else "(ya está vencido)"
    cuerpo = (
        f"<p>El contrato de encargado del tratamiento con <strong>{nombre_encargado}</strong> "
        f"de la empresa <strong>{nombre_empresa}</strong> está {estado} {plazo}.</p>"
        f"<ul>"
        f"<li><strong>Encargado:</strong> {nombre_encargado}</li>"
        f"<li><strong>Fines del tratamiento:</strong> {finalidad}</li>"
        f"</ul>"
        f"<p>Recuerde que, según el Art. 14 quater de la Ley 21.719, todo contrato de "
        f"encargado del tratamiento debe mantenerse vigente mientras dure el tratamiento.</p>"
        f"<p>Renueve o celebre un nuevo contrato antes de la fecha de vencimiento.</p>"
    )
    text, html = _render_template(
        f"Contrato de encargado por vencer: {nombre_encargado}", saludo, cuerpo
    )
    _send_raw(email_dpo, f"[Custodio] Contrato de encargado {estado} - {nombre_encargado}", html, text)


def notificar_sla_alert_t2(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    tickets: list[dict],
) -> None:
    """
    Notifica al DPO tickets ARCO próximos a vencer en T-2 días hábiles.
    Agrupados por responsable para facilitar la gestión.
    """
    if not tickets:
        return
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    total = len(tickets)
    vencido_txt = "ya están vencidos" if any(t["dias_restantes"] < 0 for t in tickets) else f"vence(n) en los próximos {total} día(s)"
    cuerpo = [
        f"<p>Se gefunden <strong>{total}</strong> solicitud(es) ARCO que {vencido_txt}:</p>",
        '<table style="width:100%;border-collapse:collapse;font-size:13px;">',
        "<tr style='background:#2563EB;color:white;'>",
        "<th style='padding:8px;text-align:left;'>ID</th>",
        "<th style='padding:8px;text-align:left;'>Tipo</th>",
        "<th style='padding:8px;text-align:left;'>Titular</th>",
        "<th style='padding:8px;text-align:left;'>Responsable</th>",
        "<th style='padding:8px;text-align:center;'>Días</th>",
        "<th style='padding:8px;text-align:left;'>Prioridad</th>",
        "</tr>",
    ]
    for t in tickets:
        dias = t["dias_restantes"]
        color_fila = "#FEE2E2" if dias <= 0 else ("#FEF9C8" if dias <= 2 else "#DCFCE7")
        badge = "🔴 VENCIDO" if dias < 0 else (f"🟡 T-{dias}d" if dias <= 2 else f"🟢 {dias}d")
        cuerpo.append(f"<tr style='background:{color_fila};'>")
        cuerpo.append(f"<td style='padding:6px;'>#{t['id']}</td>")
        cuerpo.append(f"<td style='padding:6px;'>{t['tipo']}</td>")
        cuerpo.append(f"<td style='padding:6px;'>{t['titular_nombre']}</td>")
        cuerpo.append(f"<td style='padding:6px;'>{t.get('responsable_nombre') or 'Sin asignar'}</td>")
        cuerpo.append(f"<td style='padding:6px;text-align:center;'>{badge}</td>")
        cuerpo.append(f"<td style='padding:6px;'>{t['prioridad']}</td>")
        cuerpo.append("</tr>")
    cuerpo.append("</table>")
    cuerpo.append("<p style='margin-top:16px;'>Recuerde que según el Art. 14 Ley 21.719, el plazo máximo de respuesta es de <strong>10 días hábiles</strong> desde la recepción.</p>")
    footer = f"{total} solicitud(es) con deadline próximo · Custodio RAT Manager · Ley 21.719"
    text, html = _render_template("Alerta SLA: solicitudes ARCO próximas a vencer", saludo, "".join(cuerpo), footer)
    _send_raw(email_dpo, f"[Custodio] Alerta SLA: {total} solicitudes ARCO próximas a vencer", html, text)


def notificar_eipd_vencida(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    rat_nombre: str,
    rat_id: int,
    dias_abierta: int,
) -> None:
    """
    Notifica al DPO que una EIPD vinculada a un RAT está abierta desde hace más de 90 días.
    Conforme al Art. 15 bis Ley 21.719.
    """
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    cuerpo = (
        f"<p>La Evaluación de Impacto en Protección de Datos (EIPD) asociada al proceso "
        f"<strong>{rat_nombre}</strong> (ID #{rat_id}) de la empresa "
        f"<strong>{nombre_empresa}</strong> lleva <strong>{dias_abierta} días</strong> abierta sin completarse.</p>"
        f"<p>Según el Art. 15 bis de la Ley 21.719, la EIPD debe completarse <strong>antes de iniciar</strong> "
        f"el tratamiento de datos sensibles o transferencias internacionales. Un RAT con EIPD pendiente "
        f"no puede ser aprobado hasta que la evaluación esté completada.</p>"
        f"<p>Acceda al sistema para completar la EIPD o documentar la justificación de por qué no es requerida.</p>"
    )
    footer = "Custodio RAT Manager · Ley 21.719 · Art. 15 bis — EIPD obligatoria"
    text, html = _render_template(
        f"EIPD pendiente: {rat_nombre}", saludo, cuerpo, footer
    )
    _send_raw(email_dpo, f"[Custodio] EIPD pendiente hace {dias_abierta} días: {rat_nombre}", html, text)


def notificar_consentimiento_por_vencer(
    email_dpo: str,
    nombre_dpo: str,
    nombre_empresa: str,
    rat_nombre: str,
    rat_id: int,
    dias_activo: int,
) -> None:
    """
    Notifica al DPO que un consentimiento lleva más de 2 años activo y debe renovarse.
    Conforme al Art. 12 Ley 21.719 (consentimiento válido mientras sea necesario).
    """
    saludo = f"Estimado/a {nombre_dpo or 'DPO'}:"
    cuerpo = (
        f"<p>El consentimiento registrado para el proceso "
        f"<strong>{rat_nombre}</strong> (ID #{rat_id}) de la empresa "
        f"<strong>{nombre_empresa}</strong> lleva <strong>{dias_activo} días</strong> activo.</p>"
        f"<p>Se recomienda evaluar si el consentimiento sigue siendo válido y está actualizado. "
        f"Según el Art. 12 de la Ley 21.719, el consentimiento debe ser的自由撤回ible en cualquier momento. "
        f"Considere renovar el consentimiento si las circunstancias del tratamiento han cambiado "
        f"o si el período de retención lo requiere.</p>"
    )
    footer = "Custodio RAT Manager · Ley 21.719 · Art. 12 — Consentimiento"
    text, html = _render_template(
        f"Consentimiento activo hace {dias_activo} días: {rat_nombre}", saludo, cuerpo, footer
    )
    _send_raw(email_dpo, f"[Custodio] Consentimiento activo hace {dias_activo} días: {rat_nombre}", html, text)


def notificar_acuse_solicitud(
    email_titular: str,
    nombre_titular: Optional[str],
    tipo_derecho: str,
    empresa_nombre: str,
    ticket_id: int,
    tracking_token: str,
    portal_url: str = "https://app.custodio.cl/seguimiento",
) -> None:
    """
    Envía acuse de recibo al titular confirmando que su solicitud ARCO fue recibida.
    Incluye link de seguimiento al portal del titular.
    """
    saludo = f"Estimado/a {nombre_titular or 'titular'}:"
    link_seguimiento = f"{portal_url}/{tracking_token}"
    cuerpo = (
        f"<p>Hemos recibido correctamente su solicitud de derecho "
        f"<strong>{tipo_derecho}</strong> presentada ante "
        f"<strong>{empresa_nombre}</strong>.</p>"
        f"<p><strong>Su número de seguimiento:</strong></p>"
        f'<p style="word-break:break-all;font-family:monospace;font-size:14px;color:#111827;">'
        f"{tracking_token}</p>"
        f"<p>Puede hacer seguimiento de su solicitud en nuestro portal:</p>"
        f'<p><a href="{link_seguimiento}" style="background:#2563EB;color:#fff;padding:10px 20px;'
        f'text-decoration:none;border-radius:6px;display:inline-block;">'
        f"Ver estado de mi solicitud</a></p>"
        f"<p>O copie este enlace en su navegador:</p>"
        f'<p style="word-break:break-all;color:#6B7280;font-size:12px;">{link_seguimiento}</p>'
        f"<p>El plazo máximo para responder su solicitud es de <strong>10 días hábiles</strong> "
        f"contados desde la recepción de este acuse (Art. 14 Ley 21.719).</p>"
        f"<p>Si no realizó esta solicitud, por favor ignore este correo.</p>"
    )
    footer = f"Correo enviado por Custodio RAT Manager · Ley 21.719 · Solicitud #{ticket_id}"
    text, html = _render_template(
        f"Acuse de recibo: Solicitud {tipo_derecho} recibida", saludo, cuerpo, footer
    )
    _send_raw(
        email_titular,
        f"[Custodio] Acuse: Solicitud {tipo_derecho} recibida - #{ticket_id}",
        html,
        text,
    )
