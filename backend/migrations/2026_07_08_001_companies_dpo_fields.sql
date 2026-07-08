-- Migration: Add telefono_dpo + representante_legal to companies table
-- Version: 1.6.x
-- Date: 2026-07-08
-- Description: QWs Companies backend — campos faltantes DPO + representante legal
--              para cumplir con Art. 5 Ley 21.719 (identificación responsable)

BEGIN;

ALTER TABLE companies
ADD COLUMN IF NOT EXISTS telefono_dpo VARCHAR(50),
ADD COLUMN IF NOT EXISTS representante_legal VARCHAR(300);

COMMENT ON COLUMN companies.telefono_dpo IS 'Teléfono del Delegado de Protección de Datos (Art. 21 Ley 21.719)';
COMMENT ON COLUMN companies.representante_legal IS 'Nombre del representante legal de la empresa responsable';

COMMIT;
