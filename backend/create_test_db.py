"""
Crear base de datos custodio_test en Neon.
Uso:
    python create_test_db.py --database-url "postgresql://user:pass@host/neondb?sslmode=require"
    DATABASE_URL="..." python create_test_db.py
"""
import psycopg2
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Create custodio_test database")
parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
args = parser.parse_args()

if not args.database_url:
    raise SystemExit(
        "ERROR: DATABASE_URL no configurada.\n"
        "Use: --database-url <URL> o variable de entorno DATABASE_URL=<URL>"
    )

TEST_DB = "custodio_test"
conn = psycopg2.connect(args.database_url)
conn.autocommit = True
cur = conn.cursor()
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB}'")
exists = cur.fetchone()
if exists:
    cur.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{TEST_DB}' AND pid <> pg_backend_pid()")
    time.sleep(1)
    cur.execute(f"DROP DATABASE {TEST_DB}")
    print("Dropped existing")
cur.execute(f"CREATE DATABASE {TEST_DB}")
print(f"Created {TEST_DB}")
cur.close()
conn.close()
print("Done")
