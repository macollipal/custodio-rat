"""
Configuracion para el test de flujo completo.
Soporta entornos QA y PROD.
Uso: TEST_ENV=prod python test_flujo_completo.py
"""

import os
from datetime import datetime

ENVIRONMENTS = {
    "qa": {
        "BASE_URL": "https://custodio-api-qa-git-qa-marcelos-projects-3cc299e0.vercel.app",
        "FRONTEND_URL": "https://custodio-qa.vercel.app",
        "ENV_NAME": "QA",
        "RATE_LIMIT_INTERVAL": 1.1,
 },
    "prod": {
        "BASE_URL": "https://custodio-api-prod.vercel.app",
        "FRONTEND_URL": "https://custodio-prod.vercel.app",
        "ENV_NAME": "PRODUCCION",
        "RATE_LIMIT_INTERVAL": 1.5,
    }
}

ENV = os.getenv("TEST_ENV", "qa")
ACTIVE_CONFIG = ENVIRONMENTS.get(ENV, ENVIRONMENTS["qa"])

BASE_URL = ACTIVE_CONFIG["BASE_URL"]
FRONTEND_URL = ACTIVE_CONFIG["FRONTEND_URL"]
ENV_NAME = ACTIVE_CONFIG["ENV_NAME"]
RATE_LIMIT_INTERVAL = ACTIVE_CONFIG["RATE_LIMIT_INTERVAL"]

ADMIN_USER = "admin"
ADMIN_PASS = "Admin1234!"
PREFIX_BASE = "TEST_FLUIDO_DEMO"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PREFIX = f"{PREFIX_BASE}_{TIMESTAMP}"

def generate_rut():
    """Genera un RUT chileno valido de8 digitos con digito verificador."""
    base = int(datetime.now().strftime("%H%M%S%f")[:8])
    dv = base % 10
    return f"{base}-{dv}"

RUT_TEST = generate_rut()
EMAIL_TEST_DOMAIN = "test.cl"

RAT_TEMPLATE = {
    "categoria_datos": "Datos identificativos del trabajador",
    "categoria_titulares": "Trabajadores",
    "finalidad": "Gestion de personal y nominas",
    "base_legal": "Obligacion legal",
    "fuente_datos": "Sistema interno RRHH",
    "plazo_retencion": "5 anios",
    "medidas_seguridad": "Contrasenas hasheadas, acceso por rol",
    "destinatarios": "Servicio de Impuestos Internos",
    "transferencia_datos": "No aplica",
    "transferencia_internacional": False,
    "datos_sensibles": False,
    "evaluacion_impacto": False,
    "decisiones_automatizadas": False,
    "nombre_encargado": None,
    "tiene_contrato_encargado": False,
    "test_interes_legitimo": None,
}

BRECHA_TEMPLATE = {
    "fecha_deteccion": "2026-06-01T00:00:00Z",
    "rats_afectados": "N/A",
    "datos_comprometidos": "Ninguno confirmado",
    "medidas_adoptadas": "Pendiente",
    "notificado_apdc": False,
    "notificado_titulares": False,
    "creado_por": "admin",
}

ARCO_TYPES = ["acceso", "rectificacion", "cancelacion"]

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, f"test_{PREFIX}.log")
