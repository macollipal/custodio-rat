"""
Script para resetear la base de datos de test en Neon QA.
Uso:
    python reset_test_db.py --database-url "postgresql://user:pass@host/neondb?sslmode=require"
    DATABASE_URL="..." python reset_test_db.py
"""
import psycopg2
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Reset custodio_test database")
parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
args = parser.parse_args()

if not args.database_url:
    raise SystemExit(
        "ERROR: DATABASE_URL no configurada.\n"
        "Use: --database-url <URL> o variable de entorno DATABASE_URL=<URL>"
    )

TEST_DB = "custodio_test"

def reset_test_db():
    print("Conectando a Neon QA...")
    conn = psycopg2.connect(args.database_url)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB}'")
    if cur.fetchone():
        print(f"Dropping existing {TEST_DB} database...")
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB}'
              AND pid <> pg_backend_pid()
        """)
        time.sleep(1)
        cur.execute(f"DROP DATABASE {TEST_DB}")

    cur.execute(f"CREATE DATABASE {TEST_DB}")
    print(f"Created fresh {TEST_DB} database")

    cur.close()
    conn.close()

    print("Creando schema desde modelos...")
    os.environ['ENV'] = 'test'
    os.environ['DATABASE_URL'] = f"{args.database_url.split('/neondb')[0]}/{TEST_DB}?sslmode=require"

    from app.database.database import Base, engine
    from app.models import (
        company, rat, user, audit_log, user_company, breach, eipd,
        consentimiento, rubro, rats_sugerido,
        token_blacklist, solicitud_token,
        tkt_solicitud_derecho, tkt_nota, tkt_adjunto, tkt_historial,
        tkt_plantilla, tkt_regla_asignacion,
        asesor,
    )

    Base.metadata.create_all(bind=engine)
    print("Schema creado exitosamente")

    db_url = f"{args.database_url.split('/neondb')[0]}/{TEST_DB}?sslmode=require"
    conn2 = psycopg2.connect(db_url)
    cur2 = conn2.cursor()
    cur2.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [r[0] for r in cur2.fetchall()]
    print(f"\nTablas creadas ({len(tables)}):")
    for t in tables:
        print(f"  - {t}")
    cur2.close()
    conn2.close()
    print("\nListo para tests!")

if __name__ == "__main__":
    reset_test_db()
