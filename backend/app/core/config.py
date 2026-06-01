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

    # Base de datos (Neon PostgreSQL)
    DATABASE_URL: str = "postgresql://neondb_owner:npg_Rem3X0tGwUxv@ep-flat-rice-aaqay71bf-pooler.c-8.us-east-1.aws.neon.tech/Custodio_dev?sslmode=require&channel_binding=require"

    # Seguridad JWT
    SECRET_KEY: str = "cambia-esta-clave-en-produccion-por-una-de-256-bits"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas

    # Ambiente: development | production
    ENVIRONMENT: str = "development"

    # Desarrollo: clave por defecto (NO usar en producción)
    _dev_secret: str = "cambia-esta-clave-en-produccion-por-una-de-256-bits"

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

    # CORS - en producción usar ALLOWED_ORIGINS desde .env
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8002",
        "http://127.0.0.1:8002",
    ]
    ALLOWED_ORIGINS_PROD: list[str] = [
        "https://custodio-rat-iy24-iyhtfb8jm-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-rat-iy24-2grukh4cj-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-rat-iy24-nnmjz7ri6-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-rat-iy24-pjyrvtf4d-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-rat-iy24.vercel.app",
        "https://custodio-indol.vercel.app",
        "https://custodio-b5o2s7ily-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-2a6ifunvu-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-f0p0m9vfs-marcelos-projects-3cc299e0.vercel.app",
        "https://custodio-api-git-qa-marcelos-projects-3cc299e0.vercel.app",
    ]
    VERCEL_URL: str = ""  # URL del frontend en Vercel (ej: custodiokey.vercel.app)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def resolved_secret_key(self) -> str:
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY es obligatoria en producción. Genera una clave con: openssl rand -hex 64")
            return self.SECRET_KEY
        return self._dev_secret

    @property
    def resolved_allowed_origins(self) -> list[str]:
        if self.ENVIRONMENT in ("production", "qa", "staging"):
            if self.VERCEL_URL and not self.ALLOWED_ORIGINS_PROD:
                return [f"https://{self.VERCEL_URL}"]
            return self.ALLOWED_ORIGINS_PROD
        return self.ALLOWED_ORIGINS

settings = Settings()
