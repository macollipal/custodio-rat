"""
Configuración de SQLAlchemy: engine, sesión y función de inicialización de tablas.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Solo SQLite
    echo=False,
)

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
    from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate_rats_table()
    _migrate_companies_table()


def _migrate_rats_table():
    """Agrega columnas nuevas a la tabla rats si no existen (migraciones incrementales)."""
    nuevas_columnas = [
        ("categoria_titulares", "VARCHAR(500)"),
        ("garantias_transferencia_int", "VARCHAR(500)"),
        ("tipo_dato_sensible", "VARCHAR(500)"),
        ("decisiones_automatizadas", "BOOLEAN DEFAULT 0"),
        ("estado_eipd", "VARCHAR(50) DEFAULT 'no_requerida'"),
        ("fecha_eipd", "DATE"),
        ("nombre_encargado", "VARCHAR(500)"),
        ("tiene_contrato_encargado", "BOOLEAN DEFAULT 0"),
        ("test_interes_legitimo", "TEXT"),
    ]
    with engine.connect() as conn:
        resultado = conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(rats)")
        )
        columnas_existentes = {row[1] for row in resultado}
        for nombre_col, tipo_col in nuevas_columnas:
            if nombre_col not in columnas_existentes:
                conn.execute(
                    __import__("sqlalchemy").text(
                        f"ALTER TABLE rats ADD COLUMN {nombre_col} {tipo_col}"
                    )
                )
        conn.commit()


def _migrate_companies_table():
    """Agrega columnas nuevas a la tabla companies si no existen."""
    nuevas_columnas = [
        ("canal_ejercicio_derechos", "TEXT"),
    ]
    with engine.connect() as conn:
        resultado = conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(companies)")
        )
        columnas_existentes = {row[1] for row in resultado}
        for nombre_col, tipo_col in nuevas_columnas:
            if nombre_col not in columnas_existentes:
                conn.execute(
                    __import__("sqlalchemy").text(
                        f"ALTER TABLE companies ADD COLUMN {nombre_col} {tipo_col}"
                    )
                )
        conn.commit()
