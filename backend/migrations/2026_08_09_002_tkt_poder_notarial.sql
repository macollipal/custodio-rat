-- M-06: Campo poder notarial representante ARCO (Art. 14 quater)
-- Aplica en: Neon QA + Prod
-- Fecha: 2026-08-09

ALTER TABLE tkt_solicitud_derecho DROP COLUMN IF EXISTS representante_poder_notarial_notas;
ALTER TABLE tkt_solicitud_derecho ADD COLUMN representante_poder_notarial_notas TEXT DEFAULT NULL;

COMMENT ON COLUMN tkt_solicitud_derecho.representante_poder_notarial_notas
  IS 'Descripcion o referencia del poder notarial que acredita la representacion (Art. 14 quater Ley 21.719)';
