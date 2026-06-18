-- Migration: Consolidate ARCO - extend tkt_solicitud_derecho + backfill from solicitudes_derecho
-- Version: 1.7.0
-- Date: 2026-06-18
-- Description:
--   1. Agrega columnas rat_id, plazo_bloqueo_vencimiento, portability_data a tkt_solicitud_derecho
--   2. Agrega indices para nuevas columnas
--   3. Backfill de rat_id y plazo_bloqueo_vencimiento desde solicitudes_derecho
--   4. Backfill de portability_data para tickets de portabilidad
--   5. NOTE: La tabla solicitudes_derecho se depreca; el formulario público ahora crea SOLO TKT
--
-- IMPORTANTE: Ejecutar ANTES de hacer deploy. Hacer backup de la BD antes.
--
-- Para ejecutar en Neon PostgreSQL:
--   psql "postgresql://USER:PASSWORD@HOST/dbname?sslmode=require"
--   \i backend/migrations/migration_consolidate_arco.sql
--
-- Verificar después:
--   SELECT COUNT(*) FROM tkt_solicitud_derecho WHERE rat_id IS NOT NULL;
--   SELECT COUNT(*) FROM tkt_solicitud_derecho WHERE portability_data IS NOT NULL;

BEGIN;

-- 1. Agregar columnas a tkt_solicitud_derecho
ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS rat_id INTEGER REFERENCES rats(id);

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS plazo_bloqueo_vencimiento TIMESTAMPTZ;

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS portability_data TEXT;

-- 2. Indices para nuevas columnas
CREATE INDEX IF NOT EXISTS idx_tkt_rat_id ON tkt_solicitud_derecho(rat_id);
CREATE INDEX IF NOT EXISTS idx_tkt_plazo_bloqueo ON tkt_solicitud_derecho(plazo_bloqueo_vencimiento);

-- 3. Backfill rat_id y plazo_bloqueo_vencimiento desde solicitudes_derecho
--    Matching por: company_id + tipo + titular_email + diff de timestamp <= 60 segundos
UPDATE tkt_solicitud_derecho tkt
SET
    rat_id = sd.rat_id,
    plazo_bloqueo_vencimiento = sd.plazo_bloqueo_vencimiento
FROM solicitudes_derecho sd
WHERE
    tkt.company_id = sd.company_id
    AND tkt.tipo = sd.tipo
    AND tkt.titular_email = sd.email_titular
    AND tkt.titular_nombre = sd.nombre_titular
    AND ABS(EXTRACT(EPOCH FROM (tkt.fecha_recepcion - sd.solicitud_fecha))) <= 60;

-- 4. Backfill portability_data para tickets de portabilidad ya resueltos
--    Cuando la solicitud de portabilidad tiene respuesta, esa respuesta es el dato de portabilidad
UPDATE tkt_solicitud_derecho tkt
SET portability_data = (
    SELECT json_build_object(
        'id', sd.id,
        'company_id', sd.company_id,
        'nombre_titular', sd.nombre_titular,
        'rut_titular', sd.rut_titular,
        'email_titular', sd.email_titular,
        'respuesta', sd.respuesta,
        'respuesta_fecha', sd.respuesta_fecha,
        'rat_id', sd.rat_id,
        'exportado_en', NOW()
    )::text
    FROM solicitudes_derecho sd
    WHERE
        sd.company_id = tkt.company_id
        AND sd.tipo = 'portabilidad'
        AND sd.email_titular = tkt.titular_email
        AND sd.nombre_titular = tkt.titular_nombre
        AND ABS(EXTRACT(EPOCH FROM (tkt.fecha_recepcion - sd.solicitud_fecha))) <= 60
    LIMIT 1
)
WHERE tkt.tipo = 'portabilidad';

-- 5. Verificar counts
--    Tickets con rat_id backfilleado:
--    SELECT COUNT(*) FROM tkt_solicitud_derecho WHERE rat_id IS NOT NULL;

--    Tickets con plazo_bloqueo_vencimiento backfilleado:
--    SELECT COUNT(*) FROM tkt_solicitud_derecho WHERE plazo_bloqueo_vencimiento IS NOT NULL;

--    Tickets de portabilidad con datos:
--    SELECT COUNT(*) FROM tkt_solicitud_derecho WHERE tipo = 'portabilidad' AND portability_data IS NOT NULL;

-- 6. Agregar constraint para asegurar que rat_id solo se usa con tipo='bloqueo'
--    (opcional - descomentar si se quiere validación estricta)
-- ALTER TABLE tkt_solicitud_derecho
-- ADD CONSTRAINT chk_rat_id_solo_bloqueo
-- CHECK (rat_id IS NULL OR tipo = 'bloqueo');

COMMIT;
