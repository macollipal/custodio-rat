"""
Script de migración para agregar columnas de hash chain a audit_logs.
Ejecutar una sola vez en producción.

SQL directo (para Neon PostgreSQL):
"""

MIGRATION_SQL = """
-- Agregar columnas de hash chain a audit_logs
-- Esta migración es para implementar C6 (audit trail inmutable)

ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS prev_hash VARCHAR(64) NOT NULL DEFAULT '0000000000000000000000000000000000000000000000000000000000000000';

ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS hash VARCHAR(64) NOT NULL DEFAULT '0000000000000000000000000000000000000000000000000000000000000000';

-- Agregar índice para buscar por hash
CREATE INDEX IF NOT EXISTS ix_audit_logs_hash ON audit_logs(hash);

-- Agregar índice para timestamp (para queries ordenadas)
CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs(timestamp);

-- Migrar los hashes de los registros existentes
-- Para cada registro, calcular hash basado en los campos existentes
-- Esto solo funciona si hay pocos registros; para grandes volúmenes,
-- usar un script Python que procese en batches.

DO $$
DECLARE
    rec RECORD;
    prev_hash_val VARCHAR(64) := '0000000000000000000000000000000000000000000000000000000000000000';
BEGIN
    FOR rec IN
        SELECT id, entidad, entidad_id, accion, usuario, detalle, ip_origen, timestamp
        FROM audit_logs
        ORDER BY id ASC
    LOOP
        -- Calcular hash del registro actual usando los campos existentes
        -- Nota: esto recalcula el hash basándose en los datos actuales del registro
        UPDATE audit_logs
        SET prev_hash = prev_hash_val,
            hash = encode(
                sha256(
                    (prev_hash_val ||
                     COALESCE(to_char(rec.timestamp, 'YYYY-MM-DD"T"HH24:MI:SS.US'), '') ||
                     COALESCE(rec.accion, '') ||
                     COALESCE(rec.entidad, '') ||
                     COALESCE(rec.entidad_id::text, '') ||
                     COALESCE(rec.usuario, '') ||
                     COALESCE(rec.detalle, '')
                    )::bytea
                ),
                'hex'
            )::varchar(64)
        WHERE id = rec.id;

        -- El hash actual se convierte en el prev_hash del siguiente
        SELECT hash INTO prev_hash_val FROM audit_logs WHERE id = rec.id;
    END LOOP;
END $$;

-- Verificar que la cadena está intacta
-- (esto debería retornar valid=true si todo está bien)
-- SELECT verify_audit_chain() FROM audit_logs LIMIT 1;
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  C6 — Audit Hash Chain Migration                                            ║
║                                                                              ║
║  Para ejecutar en Neon PostgreSQL:                                          ║
║                                                                              ║
║  1. Conectar a Neon con psql:                                               ║
║     psql "postgresql://USER:PASSWORD@HOST/dbname?sslmode=require"          ║
║                                                                              ║
║  2. Ejecutar el SQL:                                                         ║
║     \\i migration_audit_hash_chain.sql                                     ║
║                                                                              ║
║  3. Verificar la cadena:                                                     ║
║     SELECT id, prev_hash, hash FROM audit_logs ORDER BY id DESC LIMIT 10;   ║
║                                                                              ║
║  Para automatizar con Alembic (futuro):                                       ║
║  1. pip install alembic                                                     ║
║  2. cd backend && alembic init migrations                                    ║
║  3. alembic revision --autogenerate -m "add audit hash chain"                ║
║  4. alembic upgrade head                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")