-- Migración M-04: columna overrides_json en politicas_transparencia
-- Permite que el editor frontend personalice ítems del Art. 14 ter
-- Aplicar en: Neon QA (neondb) y Neon Prod

ALTER TABLE politicas_transparencia
  ADD COLUMN IF NOT EXISTS overrides_json TEXT DEFAULT NULL;

COMMENT ON COLUMN politicas_transparencia.overrides_json IS
  'JSON con overrides por ítem (item_a_politica ... item_l_decisiones_automatizadas). NULL = usar texto auto-generado.';
