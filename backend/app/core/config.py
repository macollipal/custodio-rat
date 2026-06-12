"""
Configuraci├│n central de la aplicaci├│n.
Carga variables de entorno y expone un objeto Settings reutilizable.
"""

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "RAT Manager ÔÇö Ley 21.719"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Sistema de gesti├│n del Registro de Actividades de Tratamiento (RAT) "
        "conforme a la Ley 21.719 de Protecci├│n de Datos Personales de Chile."
    )

    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"
    _dev_secret: str = "dev-secret-never-use-in-production"
    ALLOWED_ORIGINS: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-M2.7"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    STORAGE_BACKEND: str = "local"
    OCI_CONFIG: str = ""
    OCI_KEY_CONTENT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def resolved_secret_key(self) -> str:
        if self.ENVIRONMENT in ("production", "qa", "staging"):
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY es obligatoria en producci├│n. Genera una clave con: openssl rand -hex 64")
            return self.SECRET_KEY
        return self._dev_secret

    @property
    def oci(self) -> dict:
        """Parsea OCI_CONFIG como dict. Vac├¡o si no est├í configurado."""
        if not self.OCI_CONFIG:
            return {}
        import json
        return json.loads(self.OCI_CONFIG)

settings = Settings()
