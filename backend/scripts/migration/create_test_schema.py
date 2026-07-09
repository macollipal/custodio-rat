"""
Crear schema en la BD de test (custodio_test).
Uso:
    python create_test_schema.py --database-url "postgresql://user:pass@host/custodio_test?sslmode=require"
    DATABASE_URL="..." python create_test_schema.py
"""
import os
import argparse

parser = argparse.ArgumentParser(description="Create test schema")
parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
args = parser.parse_args()

if not args.database_url:
    raise SystemExit(
        "ERROR: DATABASE_URL no configurada.\n"
        "Use: --database-url <URL> o variable de entorno DATABASE_URL=<URL>"
    )

os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = args.database_url

from app.database.database import Base, engine  # noqa: E402

Base.metadata.create_all(bind=engine)
print("Schema created")

import psycopg2  # noqa: E402
conn = psycopg2.connect(args.database_url)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables ({len(tables)}):")
for t in tables:
    print(f"  - {t}")
cur.close()
conn.close()
print("Ready for tests")
