"""
Configuración de logging estructurado para la aplicación.
Usa formato JSON en producción para integración con observabilidad.

Incluye propagación de request_id vía contextvars para correlación
de extremo a extremo entre logs y respuestas HTTP.
"""

import contextvars
import json
import logging
import sys
import os
import uuid
from datetime import datetime, timezone

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)


def set_request_id(rid=None) -> str:
    rid = rid or str(uuid.uuid4())
    request_id_var.set(rid)
    return rid


def get_request_id() -> str:
    return request_id_var.get()


class RequestIdFilter(logging.Filter):
    """Inyecta request_id en cada LogRecord para que el formatter lo lea."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "user"):
            log_data["user"] = record.user
        if hasattr(record, "company_id"):
            log_data["company_id"] = record.company_id
        if hasattr(record, "ip"):
            log_data["ip"] = record.ip
        return json.dumps(log_data, default=str)


def setup_logging() -> logging.Logger:
    is_production = os.getenv("ENVIRONMENT") == "production"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if is_production else logging.DEBUG)

    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    if is_production:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | rid=%(request_id)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
    root_logger.addHandler(handler)

    for noisy in ("uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(
            logging.WARNING if noisy == "uvicorn.access" else logging.INFO
        )

    return root_logger
