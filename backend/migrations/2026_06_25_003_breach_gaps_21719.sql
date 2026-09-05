-- Migration: 2026_06_25_003_breach_gaps_21719.sql
-- Descripción: Agrega 6 campos nuevos al modelo SecurityBreach para cerrar gaps de compliance con Ley 21.719
-- Iteración: Iter 10 - Gaps RAT/ARCO/Brechas
-- Campos: fecha_ocurrencia_estimada, efectos_probables, causa_raiz, evidencia_notificacion_apdc_folio, estado_cierre, fecha_cierre

BEGIN;

-- Fecha estimada de ocurrencia del incidente, no solo detección
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS fecha_ocurrencia_estimada TIMESTAMP WITH TIME ZONE;
COMMENT ON COLUMN security_breaches.fecha_ocurrencia_estimada IS 'Fecha estimada de ocurrencia del incidente - Ley 21.719 Art. 14 bis';

-- Efectos o consecuencias probables para los titulares
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS efectos_probables TEXT;
COMMENT ON COLUMN security_breaches.efectos_probables IS 'Consecuencias probables para los titulares: robo identidad, fraude, daño reputacional - Ley 21.719 Art. 14 bis';

-- Causa raíz del incidente
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS causa_raiz VARCHAR(50);
COMMENT ON COLUMN security_breaches.causa_raiz IS 'Causa raíz: error_humano, malware, acceso_no_autorizado, proveedor, perdida_equipo, otro - Ley 21.719 Art. 14 bis';

-- Folio/ID de la notificación a la APDC
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS evidencia_notificacion_apdc_folio VARCHAR(100);
COMMENT ON COLUMN security_breaches.evidencia_notificacion_apdc_folio IS 'Folio o ID de la notificación a la APDC - Prueba de notificación - Ley 21.719 Art. 14 bis';

-- Estado de cierre de la brecha
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS estado_cierre VARCHAR(20);
COMMENT ON COLUMN security_breaches.estado_cierre IS 'Estado de cierre: abierta, investigando, contenida, notificada, cerrada - Ley 21.719 Art. 14 bis';

-- Fecha de cierre formal de la brecha
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS fecha_cierre TIMESTAMP WITH TIME ZONE;
COMMENT ON COLUMN security_breaches.fecha_cierre IS 'Fecha de cierre formal de la brecha con evidencia - Ley 21.719 Art. 14 bis';

COMMIT;
