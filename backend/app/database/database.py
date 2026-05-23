"""
Configuración de SQLAlchemy: engine, sesión y función de inicialización de tablas.
Soporta SQLite (desarrollo) y PostgreSQL/Neon (producción).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

_is_postgres = settings.DATABASE_URL.startswith("postgresql")


def _engine_kwargs():
    if _is_postgres:
        return {"pool_pre_ping": True}
    return {"connect_args": {"check_same_thread": False}}


engine = create_engine(settings.DATABASE_URL, echo=False, **_engine_kwargs())

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
    from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if not _is_postgres:
        _migrate_rats_table()
        _migrate_companies_table()
        _migrate_rubros_table()
        _migrate_rats_sugeridos_table()


def _migrate_rats_table():
    """Agrega columnas nuevas a la tabla rats si no existen (migraciones incrementales SQLite)."""
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
    """Agrega columnas nuevas a la tabla companies si no existen (SQLite)."""
    nuevas_columnas = [
        ("canal_ejercicio_derechos", "TEXT"),
        ("rubro_id", "INTEGER REFERENCES rubros(id)"),
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


def _migrate_rubros_table():
    """Agrega columna rubro_id a companies si no existe (SQLite)."""
    with engine.connect() as conn:
        resultado = conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(companies)")
        )
        columnas_existentes = {row[1] for row in resultado}
        if "rubro_id" not in columnas_existentes:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE companies ADD COLUMN rubro_id INTEGER REFERENCES rubros(id)"
                )
            )
            conn.commit()


def _migrate_rats_sugeridos_table():
    """Crea tabla rats_sugeridos si no existe (SQLite)."""
    with engine.connect() as conn:
        resultado = conn.execute(
            __import__("sqlalchemy").text("SELECT name FROM sqlite_master WHERE type='table' AND name='rats_sugeridos'")
        )
        if not resultado.fetchone():
            conn.execute(
                __import__("sqlalchemy").text("""
                    CREATE TABLE rats_sugeridos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rubro_id INTEGER NOT NULL REFERENCES rubros(id),
                        nombre_proceso VARCHAR(300) NOT NULL,
                        categoria_datos VARCHAR(500) NOT NULL,
                        categoria_titulares VARCHAR(500),
                        finalidad TEXT,
                        base_legal VARCHAR(300),
                        plazo_retencion VARCHAR(200),
                        datos_sensibles BOOLEAN DEFAULT 0,
                        evaluacion_impacto BOOLEAN DEFAULT 0,
                        decisiones_automatizadas BOOLEAN DEFAULT 0
                    )
                """)
            )
            conn.commit()
