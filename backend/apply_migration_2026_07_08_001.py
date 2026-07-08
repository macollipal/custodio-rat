"""
Apply migration 2026_07_08_001: Add telefono_dpo + representante_legal to companies.
Uso:
    DATABASE_URL="postgresql://..." python apply_migration_2026_07_08_001.py
"""
import psycopg2
import os
import argparse

parser = argparse.ArgumentParser(description="Apply migration 2026_07_08_001 companies DPO fields")
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

sql = open('migrations/2026_07_08_001_companies_dpo_fields.sql').read()
cur.execute(sql)
print('[OK] Migration 2026_07_08_001 applied')

cur.execute(
    """
    SELECT column_name, data_type, is_nullable, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'companies' AND column_name IN ('telefono_dpo', 'representante_legal')
    ORDER BY column_name
    """
)
for row in cur.fetchall():
    print('  ', row)

cur.close()
conn.close()
print('Done')
