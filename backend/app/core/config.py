"""
Configuración central de la aplicación.
Carga variables de entorno y expone un objeto Settings reutilizable.
"""

from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "RAT Manager — Ley 21.719"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Sistema de gestión del Registro de Actividades de Tratamiento (RAT) "
        "conforme a la Ley 21.719 de Protección de Datos Personales de Chile."
    )

    # Base de datos (Neon PostgreSQL) - REQUIERE variable de entorno DATABASE_URL
    DATABASE_URL: str = ""

    # Seguridad JWT - REQUIERE variable de entorno SECRET_KEY
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # Ambiente: development | production
    ENVIRONMENT: str = "development"

    # Desarrollo: clave por defecto (NO usar en producción)
    _dev_secret: str = "dev-secret-never-use-in-production"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-M2.7"

    # SMTP para envío de correos
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def resolved_secret_key(self) -> str:
        if self.ENVIRONMENT in ("production", "qa", "staging"):
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY es obligatoria en producción. Genera una clave con: openssl rand -hex 64")
            return self.SECRET_KEY
        return self._dev_secret

settings = Settings()
