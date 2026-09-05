-- Migration: QW3 - Workflow Subsanación
-- Version: 1.8.0
-- Date: 2026-06-18
-- Description:
--   Agrega columnas para tracking de subsanación en tkt_solicitud_derecho
--   - subsanacion_detalle: texto con la información faltante solicitada
--   - subsanacion_fecha_pedido: timestamp cuando se solicitó la subsanación
--
-- Para ejecutar en Neon PostgreSQL:
--   psql "postgresql://USER:PASSWORD@HOST/dbname?sslmode=require"
--   \i backend/migrations/migration_subsanacion.sql
--

BEGIN;

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS subsanacion_detalle VARCHAR(1000);

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS subsanacion_fecha_pedido TIMESTAMPTZ;

COMMIT;
