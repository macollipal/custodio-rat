"""Sanitizacion de PII en textos embebidos (Art. 5 Ley 21.719 — principio de minimizacion).

Aplica a exports CSV/PDF y a cualquier serializacion de texto que pueda incluir
RUTs, RUNs, emails o IPs embebidos dentro de campos libres (finalidad,
observaciones_auditoria, etc.).
"""

import re


_RUT_PATTERN = re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}-[\dkK]\b")
_RUN_PATTERN = re.compile(r"\b\d{7,8}-[\dkK]\b")
_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def _mask_email(match: re.Match) -> str:
    text = match.group(0)
    if "@" not in text:
        return text
    user, domain = text.rsplit("@", 1)
    if len(user) <= 1:
        return f"*@{domain}"
    return f"{user[0]}***@{domain}"


def _mask_ipv4(match: re.Match) -> str:
    parts = match.group(0).split(".")
    if len(parts) != 4:
        return match.group(0)
    return f"***.***.***.{parts[3]}"


def sanitize_pii(text) -> str:
    """Reemplaza RUTs, RUNs, emails e IPs embebidos en un texto por versiones enmascaradas.

    Si el valor no es string se retorna sin cambios (se formatea aparte). Si es None
    o vacio se retorna tal cual.
    """
    if not text or not isinstance(text, str):
        return text or ""
    result = _RUT_PATTERN.sub(lambda m: m.group(0)[:-2] + "-*", text)
    result = _RUN_PATTERN.sub(lambda m: m.group(0)[:-2] + "-*", result)
    result = _EMAIL_PATTERN.sub(_mask_email, result)
    result = _IPV4_PATTERN.sub(_mask_ipv4, result)
    return result