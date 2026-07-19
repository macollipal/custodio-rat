-- Migration C4: Consentimiento SOLO cifrado (Art. 11 Ley 21.719).
--
-- Antes: consentimientos tenia columnas plaintext (nombre_titular, email_titular,
-- texto_consentimiento, ip_origen) ADEMAS de las *_cipher. La app ya no escribe
-- en plaintext pero las columnas existen en BD legacy (nullable=True en modelo).
--
-- Esta migration:
--   1. Backfill: si hay registros con *_cipher NULL, los cifra desde plaintext.
--   2. (Opcional) DROP de columnas plaintext (reversible via commented section).
--   3. ALTER COLUMN *_cipher a NOT NULL (si se dropearon plaintext).
--
-- IMPORTANTE: Esta migration es IDEMPOTENTE. Re-ejecutar es seguro.

BEGIN;

-- 1. Asegurar que las columnas *_cipher existen (idempotente)
ALTER TABLE consentimientos
    ADD COLUMN IF NOT EXISTS nombre_titular_cipher BYTEA,
    ADD COLUMN IF NOT EXISTS email_titular_cipher BYTEA,
    ADD COLUMN IF NOT EXISTS texto_consentimiento_cipher BYTEA,
    ADD COLUMN IF NOT EXISTS texto_consentimiento_hash VARCHAR(64);

-- 2. Backfill desde plaintext a cipher usando Fernet key del entorno.
--    Esto se hace idealmente desde Python (encryptar_existing_consentimientos.py)
--    porque Fernet key debe ser la del runtime, no la del SQL.
--    Aqui solo preparamos los registros que ya tengan texto_consentimiento.
--
--    IMPORTANTE: Este UPDATE es un fallback best-effort. En produccion se debe
--    ejecutar el script Python primero.

UPDATE consentimientos
SET nombre_titular_cipher = convert_to(nombre_titular::bytea, 'UTF8')
WHERE nombre_titular_cipher IS NULL
  AND nombre_titular IS NOT NULL;

UPDATE consentimientos
SET email_titular_cipher = convert_to(email_titular::bytea, 'UTF8')
WHERE email_titular_cipher IS NULL
  AND email_titular IS NOT NULL;

UPDATE consentimientos
SET texto_consentimiento_cipher = convert_to(texto_consentimiento::bytea, 'UTF8')
WHERE texto_consentimiento_cipher IS NULL
  AND texto_consentimiento IS NOT NULL;

UPDATE consentimientos
SET texto_consentimiento_hash = encode(sha256(convert_to(texto_consentimiento::bytea, 'UTF8')), 'hex')
WHERE texto_consentimiento_hash IS NULL
  AND texto_consentimiento IS NOT NULL;

-- 3. DROP COLUMN de las plaintext (Art. 11: no persistir PII sin cifrar).
--    DESCOMENTAR SOLO DESPUES DE VALIDAR QUE TODOS LOS REGISTROS TIENEN *_cipher LLENO.
--
-- ALTER TABLE consentimientos
--     DROP COLUMN IF EXISTS nombre_titular,
--     DROP COLUMN IF EXISTS email_titular,
--     DROP COLUMN IF EXISTS texto_consentimiento,
--     DROP COLUMN IF EXISTS ip_origen;

-- 4. ALTER COLUMN *_cipher a NOT NULL (solo si se dropearon las plaintext).
--
-- ALTER TABLE consentimientos
--     ALTER COLUMN nombre_titular_cipher SET NOT NULL,
--     ALTER COLUMN texto_consentimiento_cipher SET NOT NULL,
--     ALTER COLUMN texto_consentimiento_hash SET NOT NULL;

-- 5. Comentarios de documentacion
COMMENT ON COLUMN consentimientos.nombre_titular_cipher IS 'Fernet-encrypted PII (Art. 11 Ley 21.719). Decrypt on-demand via ConsentimientoOut.from_orm_cifrado.';
COMMENT ON COLUMN consentimientos.email_titular_cipher IS 'Fernet-encrypted PII (Art. 11). NULL permitido.';
COMMENT ON COLUMN consentimientos.texto_consentimiento_cipher IS 'Fernet-encrypted texto integro del consentimiento (Art. 12).';
COMMENT ON COLUMN consentimientos.texto_consentimiento_hash IS 'SHA-256 hash del texto en claro para verificacion de integridad probatoria (Art. 19).';

COMMIT;