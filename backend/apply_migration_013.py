"""
Apply migration 013: CHECK constraint BYTEA 10MB.
Uso:
    python apply_migration_013.py --database-url "postgresql://user:pass@host/db?sslmode=require"
    DATABASE_URL="..." python apply_migration_013.py
"""
import psycopg2
import os
import argparse

parser = argparse.ArgumentParser(description="Apply migration 013 BYTEA limit")
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
print('Migration applied')

cur.execute("SELECT conname FROM pg_constraint WHERE conname LIKE '%bytea%' OR conname LIKE '%chk_%'")
constraints = cur.fetchall()
print('Constraints:', constraints)

cur.close()
conn.close()
print('Done')
