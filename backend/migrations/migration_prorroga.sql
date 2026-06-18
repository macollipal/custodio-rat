-- Migration: QW4 - Workflow Prórroga
-- Version: 1.8.1
-- Date: 2026-06-18
-- Description:
--   Agrega columnas para tracking de prorroga en tkt_solicitud_derecho
--   - prorroga_fecha: timestamp cuando se granted la prorroga
--   - prorroga_dias: cantidad de días prorrogados
--
-- Para ejecutar en Neon PostgreSQL:
--   psql "postgresql://USER:PASSWORD@HOST/dbname?sslmode=require"
--   \i backend/migrations/migration_prorroga.sql
--

BEGIN;

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS prorroga_fecha TIMESTAMPTZ;

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS prorroga_dias INTEGER;

COMMIT;
