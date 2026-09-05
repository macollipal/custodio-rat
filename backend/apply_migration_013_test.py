"""
Apply migration 013 a la BD de test (custodio_test).
Uso:
    python apply_migration_013_test.py --database-url "postgresql://user:pass@host/custodio_test?sslmode=require"
    DATABASE_URL="..." python apply_migration_013_test.py
"""
import psycopg2
import os
import argparse

parser = argparse.ArgumentParser(description="Apply migration 013 to test DB")
parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
args = parser.parse_args()

if not args.database_url:
    raise SystemExit(
        "ERROR: DATABASE_URL no configurada.\n"
        "Use: --database-url <URL> o variable de entorno DATABASE_URL=<URL>"
    )

conn = psycopg2.connect(args.database_url)
conn.autocommit = True
cur = conn.cursor()

sql = open('migrations/2026_06_26_013_bytea_limit_10mb.sql').read()
cur.execute(sql)
print('Migration applied to custodio_test')

cur.close()
conn.close()
print('Done')
