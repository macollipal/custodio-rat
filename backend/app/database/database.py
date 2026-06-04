"""
Configuración de SQLAlchemy: engine, sesión y función de inicialización de tablas.
PostgreSQL/Neon en producción.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


DATABASE_URL = os.getenv("DATABASE_URL") or settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in Vercel project settings."
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
)


@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, connection_record):
    """Saneamiento de conexión nueva en Neon (evita mensajes 'channel binding required')."""
    try:
        dbapi_conn.autocommit = True
        cursor = dbapi_conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        dbapi_conn.autocommit = False
    except Exception:
        pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI: entrega una sesión de BD con retry en conexiones caídas."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Crea todas las tablas si no existen. Llamar al arrancar la app."""
    from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido, solicitud_derecho, token_blacklist, solicitud_token  # noqa: F401
    Base.metadata.create_all(bind=engine)
