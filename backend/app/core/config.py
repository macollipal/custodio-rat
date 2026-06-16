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

    MINIMAX_API_KEY: str = ""
    MINIMAX_MODEL: str = "MiniMax-M2.7"

    GROQ_API_KEY: str = ""
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    ASESOR_CONFIG: str = ""
    ASESOR_CHUNK_SIZE: int = 800
    ASESOR_CHUNK_OVERLAP: int = 100
    ASESOR_TOP_K: int = 5
    ASESOR_MIN_SIMILARITY: float = 0.7
    ASESOR_LLM_MAX_TOKENS: int = 1000
    ASESOR_LLM_TEMPERATURE: float = 0.3
    ASESOR_CORPUS_PATH: str = "data/asesor_corpus"
    ASESOR_EMBEDDING_MODEL: str = "MiniMax-M2.7"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    STORAGE_BACKEND: str = "local"
    OCI_CONFIG: str = ""
    OCI_KEY_CONTENT: str = ""

    ENCRYPTION_KEY: str = ""
    _dev_encryption_key: str = "dev-key-do-not-use-in-production-use-openssl-rand-hex-32"

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

    @property
    def resolved_encryption_key(self) -> str:
        if self.ENCRYPTION_KEY:
            return self.ENCRYPTION_KEY
        if self.ENVIRONMENT in ("production", "qa", "staging"):
            raise ValueError("ENCRYPTION_KEY es obligatoria en producci├│n. Genera una clave con: python -c \"from app.core.crypto import generate_key; print(generate_key())\"")
        return self._dev_encryption_key

    def asesor_config(self) -> dict:
        """Retorna config del Asesor. Si ASESOR_CONFIG esta vacio, usa los defaults.
        Si tiene JSON, esos valores toman prioridad sobre los defaults.
        Unica credencial: MINIMAX_API_KEY.
        """
        defaults = {
            "chunk_size": self.ASESOR_CHUNK_SIZE,
            "chunk_overlap": self.ASESOR_CHUNK_OVERLAP,
            "top_k": self.ASESOR_TOP_K,
            "min_similarity": self.ASESOR_MIN_SIMILARITY,
            "llm_max_tokens": self.ASESOR_LLM_MAX_TOKENS,
            "llm_temperature": self.ASESOR_LLM_TEMPERATURE,
            "corpus_path": self.ASESOR_CORPUS_PATH,
            "embedding_model": self.ASESOR_EMBEDDING_MODEL,
        }
        if not self.ASESOR_CONFIG:
            return defaults
        import json
        try:
            parsed = json.loads(self.ASESOR_CONFIG)
            return {**defaults, **parsed}
        except (json.JSONDecodeError, TypeError, ValueError):
            import logging
            logging.getLogger(__name__).warning(
                f"ASESOR_CONFIG JSON malformado, usando defaults: {self.ASESOR_CONFIG[:100]}"
            )
            return defaults

settings = Settings()
