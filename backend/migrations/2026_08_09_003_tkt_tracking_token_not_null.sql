-- Backfill tracking_token NULL → UUID aleatorio, luego hacer columna NOT NULL
-- Ejecutar en Neon QA y Prod ANTES de deploying el modelo actualizado.

UPDATE tkt_solicitud_derecho
SET tracking_token = gen_random_uuid()::TEXT
WHERE tracking_token IS NULL;

ALTER TABLE tkt_solicitud_derecho
  ALTER COLUMN tracking_token SET NOT NULL;
