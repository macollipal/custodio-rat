"""
Parser para SMTP_URL en formato DSN.

Formatos soportados:
  - Nueva forma (SMTP_URL):
      smtplib://apikey:SG.xxx@smtp.sendgrid.net:587/?use_tls=true&from_email=admin@yopmail.com&from_name=Custodio%20RAT
  - Fallback legacy (SMTP_HOST, SMTP_PORT, etc. sueltos):
      SMTP_HOST=smtp.sendgrid.net
      SMTP_PORT=587
      SMTP_USERNAME=apikey
      SMTP_PASSWORD=SG.xxx
      SMTP_FROM_EMAIL=admin@yopmail.com
      SMTP_FROM_NAME=Custodio RAT
      SMTP_USE_TLS=true

Si SMTP_URL está configurada, se usa esa y se ignoran las legacy.
Si solo están las legacy, se usan igual (compatibilidad hacia atras).
Si ninguna esta configurada, get_smtp_config() retorna None (modo dry-run).
"""

from urllib.parse import urlparse, parse_qs, unquote
import os
from typing import Optional


class SmtpConfig:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        from_email: str,
        from_name: str,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_email = from_email
        self.from_name = from_name

    def __bool__(self) -> bool:
        return bool(self.host)

    def __repr__(self) -> str:
        return (
            f"SmtpConfig(host={self.host!r}, port={self.port}, "
            f"username={self.username!r}, password=***, "
            f"use_tls={self.use_tls}, from_email={self.from_email!r}, "
            f"from_name={self.from_name!r})"
        )


def _parse_smtp_url(url: str) -> SmtpConfig:
    p = urlparse(url)
    q = parse_qs(p.query)
    return SmtpConfig(
        host=p.hostname or "",
        port=p.port or 587,
        username=unquote(p.username or ""),
        password=unquote(p.password or ""),
        use_tls=q.get("use_tls", ["true"])[0].lower() == "true",
        from_email=unquote(q.get("from_email", [""])[0]),
        from_name=unquote(q.get("from_name", ["Custodio RAT"])[0]),
    )


def _legacy_fallback() -> Optional[SmtpConfig]:
    host = os.getenv("SMTP_HOST")
    if not host:
        return None
    return SmtpConfig(
        host=host,
        port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("SMTP_USERNAME", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        from_email=os.getenv("SMTP_FROM_EMAIL", "noreply@localhost"),
        from_name=os.getenv("SMTP_FROM_NAME", "Custodio RAT"),
    )


def get_smtp_config() -> Optional[SmtpConfig]:
    url = os.getenv("SMTP_URL")
    if url:
        return _parse_smtp_url(url)
    return _legacy_fallback()
