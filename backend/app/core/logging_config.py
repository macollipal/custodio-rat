"""
Configuración de logging estructurado para la aplicación.
Usa formato JSON en producción para integración con observabilidad.
"""

import json
import logging
import sys
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
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


def setup_logging():
    is_production = os.getenv("ENVIRONMENT") == "production"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if is_production else logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    if is_production:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    return root_logger
