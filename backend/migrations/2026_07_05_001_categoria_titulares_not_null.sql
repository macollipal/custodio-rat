-- Migration: categoria_titulares NOT NULL (Art. 16 Ley 21.719 — campo mínimo obligatorio)
-- Date: 2026-07-05
-- Issue: Gap #1 — categoria_titulares es nullable pero el Art. 16 lo considera obligatorio mínimo

BEGIN;

-- Paso 1: Actualizar valores NULL existentes a 'No especificado' (valor seguro temporal)
UPDATE rats
SET categoria_titulares = 'No especificado'
WHERE categoria_titulares IS NULL;

-- Paso 2: Agregar constraint NOT NULL
ALTER TABLE rats
ALTER COLUMN categoria_titulares SET NOT NULL;

-- Paso 3: Agregar constraint CHECK para que no sea vacío (por lo menos 3 caracteres)
ALTER TABLE rats
ADD CONSTRAINT chk_rats_categoria_titulares_min_length
CHECK (char_length(categoria_titulares) >= 3);

COMMIT;
