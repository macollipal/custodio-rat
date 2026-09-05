-- Migración: Correcciones de cumplimiento Ley 21.719 (Auditoría Sep 2026)
-- Aplicar en: Neon QA (custodio_test) y Neon Producción
-- Autor: Auditoría automatizada Custodio RAT Manager

BEGIN;

-- ============================================================
-- CRÍTICO 1: fecha_conocimiento en security_breaches
-- Art. 14 bis: las 72h corren desde el conocimiento, no desde la detección
-- ============================================================
ALTER TABLE security_breaches
    ADD COLUMN IF NOT EXISTS fecha_conocimiento TIMESTAMPTZ NULL;

-- ============================================================
-- CRÍTICO 2: Renombrar notificado_apdc → notificado_apdp
-- La Agencia se llama APDP, no APDC
-- ============================================================
ALTER TABLE security_breaches
    RENAME COLUMN notificado_apdc TO notificado_apdp;

ALTER TABLE security_breaches
    RENAME COLUMN fecha_notificacion_apdc TO fecha_notificacion_apdp;

ALTER TABLE security_breaches
    RENAME COLUMN reportable_apdc_calculado TO reportable_apdp_calculado;

ALTER TABLE security_breaches
    RENAME COLUMN evidencia_notificacion_apdc_folio TO evidencia_notificacion_apdp_folio;

-- ============================================================
-- MEDIO 1: version_politica en consentimientos (Art. 12)
-- Permite probar qué versión del aviso de privacidad aceptó el titular
-- ============================================================
ALTER TABLE consentimientos
    ADD COLUMN IF NOT EXISTS version_politica VARCHAR(100) NULL;

-- ============================================================
-- MEDIO 2: origen_datos en rats (Art. 14 ter lit. e)
-- Enum: titular / tercero / fuente_publica / mixto
-- Cuando no proviene del titular hay obligación de informar al titular el origen
-- ============================================================
ALTER TABLE rats
    ADD COLUMN IF NOT EXISTS origen_datos VARCHAR(50) NULL;

COMMIT;

-- Verificación post-migración
SELECT
    column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'security_breaches'
  AND column_name IN ('fecha_conocimiento', 'notificado_apdp', 'fecha_notificacion_apdp',
                      'reportable_apdp_calculado', 'evidencia_notificacion_apdp_folio')
ORDER BY column_name;

SELECT column_name FROM information_schema.columns
WHERE table_name = 'consentimientos' AND column_name = 'version_politica';

SELECT column_name FROM information_schema.columns
WHERE table_name = 'rats' AND column_name = 'origen_datos';
