-- Migration F3.2: Soft delete en users y security_breaches.
-- Compliance Art. 19 Ley 21.719: retencion de registros sin hard delete.
--
-- Antes: usuarios y breaches se "eliminaban" fisicamente. Perdiendo trazabilidad.
-- Despues: deleted_at + deleted_by_id permiten recuperacion + auditoria.

BEGIN;

-- 1. Users: agregar deleted_at y deleted_by_id
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS deleted_by_id INTEGER REFERENCES users(id);

CREATE INDEX IF NOT EXISTS ix_users_deleted_at ON users (deleted_at);

COMMENT ON COLUMN users.deleted_at IS 'F3.2: soft delete timestamp. NULL = activo. Compliance Art. 19 Ley 21.719.';
COMMENT ON COLUMN users.deleted_by_id IS 'F3.2: usuario que realizo el soft delete (audit trail).';

-- 2. Security breaches: agregar deleted_at
ALTER TABLE security_breaches
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS deleted_by_id INTEGER REFERENCES users(id);

CREATE INDEX IF NOT EXISTS ix_security_breaches_deleted_at ON security_breaches (deleted_at);

COMMENT ON COLUMN security_breaches.deleted_at IS 'F3.2: soft delete timestamp. NULL = activo. Compliance Art. 19.';
COMMENT ON COLUMN security_breaches.deleted_by_id IS 'F3.2: usuario que realizo el soft delete (audit trail).';

-- 2b. Rats: agregar deleted_at (QW5 SLA T-2 excluye rats soft-deleted)
ALTER TABLE rats
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS deleted_by_id INTEGER REFERENCES users(id);

CREATE INDEX IF NOT EXISTS ix_rats_deleted_at ON rats (deleted_at);

COMMENT ON COLUMN rats.deleted_at IS 'F3.2: soft delete timestamp. NULL = activo. Compliance Art. 19.';
COMMENT ON COLUMN rats.deleted_by_id IS 'F3.2: usuario que realizo el soft delete (audit trail).';

-- 3. NOTA: no eliminamos registros existentes (preservar data historica).
-- Si hay registros viejos que ya no existen, el campo deleted_at quedara NULL
-- y apareceran como activos en queries normales. Para casos de "ya eliminados",
-- se puede ejecutar UPDATE separado.

COMMIT;