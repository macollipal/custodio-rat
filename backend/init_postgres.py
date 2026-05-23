"""
Crea el schema completo en PostgreSQL/Neon.
Usa Base.metadata para crear todas las tablas.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.database import Base


def get_neon_engine():
    """Crea engine para PostgreSQL/Neon sin el connect_args de SQLite."""
    url = settings.resolved_database_url
    return create_engine(url, echo=False, pool_pre_ping=True)


def init_schema():
    """Crea todas las tablas en PostgreSQL."""
    engine = get_neon_engine()

    # Importar todos los models para que Base.metadata los registre
    from app.models import (  # noqa: F401
        company, rat, user, audit_log, user_company,
        breach, eipd, consentimiento, rubro, rats_sugerido
    )

    print("Creando tablas en PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    # Reiniciar sequences al valor máximo existente
    with engine.connect() as conn:
        tables_with_serial = [
            ("users", "id"),
            ("rubros", "id"),
            ("companies", "id"),
            ("rats_sugeridos", "id"),
            ("user_companies", "id"),
            ("rats", "id"),
            ("audit_logs", "id"),
            ("eipds", "id"),
            ("security_breaches", "id"),
            ("consentimientos", "id"),
        ]
        for table, col in tables_with_serial:
            result = conn.execute(
                __import__("sqlalchemy").text(f"SELECT MAX({col}) FROM {table}")
            )
            max_val = result.scalar() or 0
            conn.execute(
                __import__("sqlalchemy").text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), {max_val}, true)"
                )
            )
        print("Sequences reiniciadas.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Solo verificar conexión
        try:
            engine = get_neon_engine()
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            print("Conexión a PostgreSQL/Neon: OK")
            sys.exit(0)
        except Exception as e:
            print(f"Conexión fallida: {e}")
            sys.exit(1)
    else:
        init_schema()