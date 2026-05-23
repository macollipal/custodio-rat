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

    # Base de datos
    # Para SQLite local: sqlite:///database.db
    # Para Neon: postgresql://user:password@ep-xxx-xxx-123456.neon.tech/custodio?sslmode=require
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/database.db"

    # Seguridad JWT
    SECRET_KEY: str = ""  # Requerida en producción
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

    # CORS - en producción usar ALLOWED_ORIGINS desde .env
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8002",
        "http://127.0.0.1:8002",
    ]
    ALLOWED_ORIGINS_PROD: list[str] = []  # Configurar con el dominio de producción
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
        if self.ENVIRONMENT == "production":
            if not self.ALLOWED_ORIGINS_PROD:
                return [f"https://{self.VERCEL_URL}"] if self.VERCEL_URL else []
            return self.ALLOWED_ORIGINS_PROD
        return self.ALLOWED_ORIGINS

    @property
    def resolved_database_url(self) -> str:
        """Construye la URL de conexión a la base de datos."""
        return self.DATABASE_URL

    @property
    def is_postgres(self) -> bool:
        """True si la base de datos es PostgreSQL (Neon)."""
        return self.DATABASE_URL.startswith("postgresql")


settings = Settings()
