"""
Apply migration: añade columnas Tier 1+Tier 2 a la tabla rats.
Uso:
    python apply_migration.py --database-url "postgresql://user:pass@host/db?sslmode=require"
    DATABASE_URL="postgresql://..." python apply_migration.py
"""
import psycopg2
import os
import argparse

parser = argparse.ArgumentParser(description="Apply migration Tier 1+Tier 2")
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

sql = """
BEGIN;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_nna VARCHAR(50);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS nivel_confidencialidad VARCHAR(20);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS estructura_dato VARCHAR(50);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_anonimizados BOOLEAN DEFAULT FALSE;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_seudonimizados BOOLEAN DEFAULT FALSE;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS ciclo_procesamiento VARCHAR(100);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS automatizacion VARCHAR(100);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS frecuencia VARCHAR(100);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS transferencia_nacional BOOLEAN DEFAULT FALSE;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS doc_clausulas TEXT;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS medidas_organizativas TEXT;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS mecanismos_eliminacion TEXT;
ALTER TABLE rats ADD COLUMN IF NOT EXISTS tecnica_anonimizacion VARCHAR(100);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS origen_dato_portabilidad VARCHAR(200);
ALTER TABLE rats ADD COLUMN IF NOT EXISTS fecha_levantamiento DATE;
COMMIT;
"""

cur.execute(sql)
print('Migration applied successfully')

cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name = 'rats'
    ORDER BY ordinal_position
""")
cols = [r[0] for r in cur.fetchall()]
new_cols = [c for c in cols if c in [
    'datos_nna', 'nivel_confidencialidad', 'estructura_dato',
    'datos_anonimizados', 'datos_seudonimizados',
    'ciclo_procesamiento', 'automatizacion', 'frecuencia',
    'transferencia_nacional', 'doc_clausulas', 'medidas_organizativas',
    'mecanismos_eliminacion', 'tecnica_anonimizacion',
    'origen_dato_portabilidad', 'fecha_levantamiento'
]]
print('New columns found:', new_cols)

cur.close()
conn.close()
print('Done!')
