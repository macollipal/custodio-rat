-- Migration: Agregar columnas compliance Ley 21.719 faltantes (iter 7+8)
-- Version: 1.6.2
-- Date: 2026-06-24
-- Description: Resuelve el error "column does not exist" al cargar Brechas,
--              Encargados, Consentimientos y EIPD. Columnas agregadas:
--              - consentimientos: nombre_titular_cipher, email_titular_cipher,
--                texto_consentimiento_hash, ip_origen_masked (Art. 11, 19)
--              - encargados_contrato: pais, direccion (Art. 14 quater)
--              - eipds: parecer_dpo_autor, parecer_dpo_fecha, justificacion_no_aplica (Art. 15 bis)
--              - security_breaches: naturaleza (Art. 14 bis)
--              - asesor_conversaciones: tabla nueva (Arts. 19, 20)

BEGIN;

-- 1. Consentimientos: columnas de cifrado y hash para PII
ALTER TABLE consentimientos
ADD COLUMN IF NOT EXISTS nombre_titular_cipher BYTEA NULL,
ADD COLUMN IF NOT EXISTS email_titular_cipher BYTEA NULL,
ADD COLUMN IF NOT EXISTS texto_consentimiento_hash VARCHAR(64) NULL,
ADD COLUMN IF NOT EXISTS ip_origen_masked VARCHAR(18) NULL;

COMMENT ON COLUMN consentimientos.nombre_titular_cipher IS 'Nombre del titular cifrado con Fernet (Art. 11)';
COMMENT ON COLUMN consentimientos.email_titular_cipher IS 'Email del titular cifrado con Fernet (Art. 11)';
COMMENT ON COLUMN consentimientos.texto_consentimiento_hash IS 'SHA-256 de texto_consentimiento para integridad (Art. 12)';
COMMENT ON COLUMN consentimientos.ip_origen_masked IS 'IP del titular anonimizada /16 (Art. 19)';

-- 2. Encargados: país y dirección del encargado
ALTER TABLE encargados_contrato
ADD COLUMN IF NOT EXISTS pais VARCHAR(100) NULL,
ADD COLUMN IF NOT EXISTS direccion TEXT NULL;

COMMENT ON COLUMN encargados_contrato.pais IS 'País del encargado del tratamiento (Art. 14 quater)';
COMMENT ON COLUMN encargados_contrato.direccion IS 'Dirección del encargado del tratamiento (Art. 14 quater)';

-- 3. EIPD: campos del parecer DPO y justificación de no aplica
ALTER TABLE eipds
ADD COLUMN IF NOT EXISTS parecer_dpo_autor VARCHAR(200) NULL,
ADD COLUMN IF NOT EXISTS parecer_dpo_fecha TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS justificacion_no_aplica TEXT NULL;

COMMENT ON COLUMN eipds.parecer_dpo_autor IS 'Autor del parecer del DPO (Art. 15 bis)';
COMMENT ON COLUMN eipds.parecer_dpo_fecha IS 'Fecha del parecer del DPO';
COMMENT ON COLUMN eipds.justificacion_no_aplica IS 'Justificación cuando EIPD es no requerida justificada';

-- 4. Brechas: naturaleza de la brecha
ALTER TABLE security_breaches
ADD COLUMN IF NOT EXISTS naturaleza VARCHAR(20) NULL;

COMMENT ON COLUMN security_breaches.naturaleza IS 'Naturaleza: confidencialidad, integridad o disponibilidad (Art. 14 bis)';

-- 5. Asesor IA: tabla de conversaciones para trazabilidad
CREATE TABLE IF NOT EXISTS asesor_conversaciones (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources_json TEXT,
    latency_ms INTEGER DEFAULT 0,
    provider VARCHAR(50),
    embedding_provider VARCHAR(50),
    ip_origen VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_asesor_conversaciones_user ON asesor_conversaciones(user_id);
CREATE INDEX IF NOT EXISTS ix_asesor_conversaciones_company ON asesor_conversaciones(company_id);
CREATE INDEX IF NOT EXISTS ix_asesor_conversaciones_created ON asesor_conversaciones(created_at);

COMMENT ON TABLE asesor_conversaciones IS 'Trazabilidad de conversaciones con el Asesor IA (Arts. 19, 20)';

COMMIT;