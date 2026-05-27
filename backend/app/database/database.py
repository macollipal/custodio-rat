"""
Configuración de SQLAlchemy: engine, sesión y función de inicialización de tablas.
PostgreSQL/Neon en producción.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI: entrega una sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas si no existen. Llamar al arrancar la app."""
    from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido, solicitud_derecho  # noqa: F401
    Base.metadata.create_all(bind=engine)
