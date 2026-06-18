-- Migration: Add soft-delete columns to companies table
-- Version: 1.6.1
-- Date: 2026-06-17
-- Description: Adds activa, desactivada_at, desactivada_por columns for soft-delete support

BEGIN;

ALTER TABLE companies
ADD COLUMN IF NOT EXISTS activa BOOLEAN NOT NULL DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS desactivada_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS desactivada_por VARCHAR(100);

COMMENT ON COLUMN companies.activa IS 'False = empresa desactivada (soft-delete), no aparece en listados';
COMMENT ON COLUMN companies.desactivada_at IS 'Timestamp de desactivación';
COMMENT ON COLUMN companies.desactivada_por IS 'Username del usuario que desactivó';

-- Ensure existing companies are active
UPDATE companies SET activa = TRUE WHERE activa IS NULL;

COMMIT;
