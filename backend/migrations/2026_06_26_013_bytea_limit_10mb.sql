-- Migración: BYTEA 10MB limit + causal_rechazo enum
-- Aplicar a: Neon QA (ep-fragrant-wildflower-apeqosx9-pooler)

-- 1. CHECK constraint: archivo_base_legal_datos max 10MB
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT 1 FROM pg_constraint WHERE conname = 'chk_rats_archivo_base_legal_datos_size'
   ) THEN
      ALTER TABLE rats ADD CONSTRAINT chk_rats_archivo_base_legal_datos_size
         CHECK (octet_length(archivo_base_legal_datos) <= 10_000_000);
   END IF;
END $$;

-- 2. CHECK constraint: tkt_adjunto.data max 10MB
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT 1 FROM pg_constraint WHERE conname = 'chk_tkt_adjuntos_data_size'
   ) THEN
      ALTER TABLE tkt_adjuntos ADD CONSTRAINT chk_tkt_adjuntos_data_size
         CHECK (octet_length(data) <= 10_000_000);
   END IF;
END $$;

-- 3. Add comment
COMMENT ON CONSTRAINT chk_rats_archivo_base_legal_datos_size ON rats IS 'Iter 12: BYTEA max 10MB (10_000_000 bytes) - DoS protection';
COMMENT ON CONSTRAINT chk_tkt_adjuntos_data_size ON tkt_adjuntos IS 'Iter 12: BYTEA max 10MB (10_000_000 bytes) - DoS protection';
