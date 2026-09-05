-- Migration: 2026_06_25_002_arco_gaps_21719.sql
-- Descripción: Agrega 5 campos nuevos al modelo TKT ARCO para cerrar gaps de compliance con Ley 21.719
-- Iteración: Iter 10 - Gaps RAT/ARCO/Brechas
-- Campos: metodo_verificacion_identidad, evidencia_identidad, evidencia_respuesta_hash, causal_rechazo, medio_respuesta
-- Tabla: tkt_solicitud_derecho

BEGIN;

-- Método de verificación de identidad del titular
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS metodo_verificacion_identidad VARCHAR(50);
COMMENT ON COLUMN tkt_solicitud_derecho.metodo_verificacion_identidad IS 'Método usado para verificar identidad del titular: cedula, firma_digital, video_call, otro - Ley 21.719 Art. 12';

-- Evidencia de identidad o mandato del representante
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS evidencia_identidad TEXT;
COMMENT ON COLUMN tkt_solicitud_derecho.evidencia_identidad IS 'Descripción de documentos o verificación de identidad usada - Ley 21.719 Art. 12';

-- Hash SHA-256 de la respuesta enviada (para probar que se respondió)
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS evidencia_respuesta_hash VARCHAR(64);
COMMENT ON COLUMN tkt_solicitud_derecho.evidencia_respuesta_hash IS 'SHA-256 de la respuesta enviada al titular - Prueba de respuesta en plazo - Ley 21.719 Art. 12';

-- Causal de rechazo de la solicitud
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS causal_rechazo VARCHAR(50);
COMMENT ON COLUMN tkt_solicitud_derecho.causal_rechazo IS 'Causal de rechazo: falta_identidad, solicitud_manifiestamente_infundada, excesiva, otro - Ley 21.719 Art. 12';

-- Medio elegido por el titular para recibir respuesta
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS medio_respuesta VARCHAR(50);
COMMENT ON COLUMN tkt_solicitud_derecho.medio_respuesta IS 'Medio de respuesta elegido por titular: email, domicilio, portal, telefono - Ley 21.719 Art. 12';

COMMIT;
