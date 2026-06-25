-- Migration: 2026_06_25_001_rat_gaps_21719.sql
-- Descripción: Agrega 5 campos nuevos al modelo RAT para cerrar gaps de compliance con Ley 21.719
-- Iteración: Iter 10 - Gaps RAT/ARCO/Brechas
-- Campos: sistema_almacenamiento, volumen_titulares_estimado, operaciones_tratamiento, logica_automatizada, responsable_tratamiento_email

BEGIN;

-- Sistema o lugar donde viven los datos (Excel, CRM, correo, Google Drive, sistema clínico, etc.)
ALTER TABLE rats ADD COLUMN IF NOT EXISTS sistema_almacenamiento VARCHAR(500);
COMMENT ON COLUMN rats.sistema_almacenamiento IS 'Sistema o lugar donde viven los datos del tratamiento (Excel, CRM, correo, Google Drive, sistema clínico, etc.) - Ley 21.719 Art. 16';

-- Volumen aproximado de titulares
ALTER TABLE rats ADD COLUMN IF NOT EXISTS volumen_titulares_estimado INTEGER;
COMMENT ON COLUMN rats.volumen_titulares_estimado IS 'Volumen aproximado de titulares afectados por este tratamiento - Criterio para EIPD obligatoria';

-- Operaciones de tratamiento (JSONB: recolección, almacenamiento, consulta, uso, comunicación, cesión, eliminación)
ALTER TABLE rats ADD COLUMN IF NOT EXISTS operaciones_tratamiento JSONB;
COMMENT ON COLUMN rats.operaciones_tratamiento IS 'Lista de operaciones de tratamiento: recolección, almacenamiento, consulta, uso, comunicación, cesión, eliminación - Ley 21.719 Art. 16';

-- Lógica de decisiones automatizadas
ALTER TABLE rats ADD COLUMN IF NOT EXISTS logica_automatizada TEXT;
COMMENT ON COLUMN rats.logica_automatizada IS 'Lógica aplicada en decisiones automatizadas, consecuencias para el titular, intervención humana disponible - Ley 21.719 Art. 16';

-- Email del responsable legal del tratamiento
ALTER TABLE rats ADD COLUMN IF NOT EXISTS responsable_tratamiento_email VARCHAR(200);
COMMENT ON COLUMN rats.responsable_tratamiento_email IS 'Email del responsable legal del tratamiento (no DPO) - Clarifica responsabilidad según Ley 21.719';

COMMIT;
