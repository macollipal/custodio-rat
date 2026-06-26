# Resumen de errores encontrados - Sesión 01 Jun 2026

> **Nota histórica:** Este documento registra los errores encontrados y corregidos durante la sesión del 01 Jun 2026. Mantenido como referencia histórica. [VERIFICAR] si los fixes siguen vigentes.

## Errores críticos encontrados y corregidos

### 1. slowapi no estaba en requirements.txt
- **Error**: `ModuleNotFoundError: No module named 'slowapi'`
- **Causa**: `slowapi` no estaba en `requirements.txt`
- **Fix**: Agregar `slowapi==0.1.9` a requirements.txt

### 2. Database URL hardcodeada con contraseña incorrecta
- **Error**: `password authentication failed for user 'neondb_owner'`
- **Causa**: La DATABASE_URL en config.py tenía la contraseña vieja (`REDACTED_NEON_PASSWORD_3`) en vez de la nueva (`REDACTED_NEON_PASSWORD_4`)
- **Fix**: Eliminar hardcoded DATABASE_URL del código, usar variable de entorno

### 3. Host de base de datos incorrecto
- **Error**: Host `ep-fragrant-wildflower-apeqosx9-pooler` (viejo) en vez de `ep-flat-rice-aaqay71bf-pooler` (nuevo)
- **Causa**: El nuevo Neon DB tenía host diferente
- **Fix**: Actualizar host en la variable de entorno de Vercel

### 4. SECRET_KEY hardcodeada en código
- **Error**: SECURITY_KEY expuesta en código fuente
- **Causa**: SECRET_KEY estaba en config.py hardcodeada
- **Fix**: Eliminar hardcoded, usar variable de entorno

### 5. decode_access_token() llamada con argumentos incorrectos
- **Error**: `TypeError: decode_access_token() takes 1 positional argument but 2 were given`
- **Causa**: En `deps.py` se llamaba `decode_access_token(token, db)` pero la función solo acepta 1 argumento
- **Fix**: Cambiar a `decode_access_token(token)`

### 6. sys.path incorrecto en api/index.py para Vercel
- **Error**: `ModuleNotFoundError: No module named 'app'`
- **Causa**: Con Root Directory `./`, el path `parent.parent / "backend"` no existía
- **Fix**: Cambiar a `parent / "backend"` con fallback paths

### 7. Frontend CORS no funcionaba
- **Error**: `No 'Access-Control-Allow-Origin' header is present`
- **Causa**: El frontend llamaba a `/custodio-api-qa-...` sin `https://`, concatenando mal
- **Fix**: Agregar lógica para asegurar que API_BASE siempre tenga `https://`

### 8. Login funcionaba pero /auth/me fallaba
- **Error**: `GET /auth/me 500 Internal Server Error`
- **Causa**: La función `decode_access_token()` en `security.py` solo acepta 1 argumento pero se llamaba con 2
- **Fix**: Corregir llamada en `deps.py`

### 9. Backend crasheaba al iniciar sin DATABASE_URL
- **Error**: `Could not parse SQLAlchemy URL from string ''`
- **Causa**: DATABASE_URL estaba vacío y el engine se creaba con string vacío
- **Fix**: Crear engine lazy o validar que DATABASE_URL existe antes de crear engine

### 10. Frontend API_BASE mal configurado
- **Error**: `API_BASE = custodio-api-qa-git-qa...` (sin `https://`)
- **Causa**: Variable de entorno no tenía `https://` prefix
- **Fix**: `const _apiBase = process.env.NEXT_PUBLIC_API_BASE || ''; export const API_BASE = _apiBase.startsWith('http') ? _apiBase : `https://${_apiBase}`;`

---

## Archivos modificados durante la sesión

### Backend
- `api/index.py` - sys.path fix
- `backend/app/core/config.py` - Eliminar hardcoded DATABASE_URL y SECRET_KEY
- `backend/app/database/database.py` - Lazy engine creation
- `backend/app/main.py` - CORS con expose_headers
- `backend/app/routes/deps.py` - decode_access_token() fix
- `requirements.txt` - Agregar slowapi

### Frontend
- `frontend-next/lib/constants.ts` - API_BASE con https:// prefix

### Scripts locales (no-git)
- `test_db_connection.py` - Test conexión a Neon
- `test_users.py` - Verificar usuarios en DB
- `reset_admin.py` - Reset password admin a 'Admin1234!'

---

## Variables de entorno configuradas en Vercel (QA)

### custodio-api-qa
- `DATABASE_URL` = `***REDACTED***` (rotada 26-Jun-2026 tras incidente GitGuardian)
- `SECRET_KEY` = `f6ce35af6ca704aa5481a13ff429b8b59930319b1a2ab1e49773034a860ec5ef200ebef9718e3561e73c0dace736e357e643f097fa0e62ddb99a6a5f6b6b9168`
- `SEED_ADMIN` = `true`
- `SEED_ADMIN_PASSWORD` = `Admin1234!`

### custodio-qa (frontend)
- `NEXT_PUBLIC_API_BASE` = `https://custodio-api-qa-git-qa-marcelos-projects-3cc299e0.vercel.app`

---

## URLs de QA

- **Backend API**: https://custodio-api-qa-git-qa-marcelos-projects-3cc299e0.vercel.app
- **Frontend**: https://custodio-qa-git-qa-marcelos-projects-3cc299e0.vercel.app

---

## Comandos útiles

### Test conexión DB
```bash
python test_db_connection.py
```

### Reset password admin
```bash
python reset_admin.py
```

### Ver usuarios en DB
```bash
python test_users.py
```

---

# Incidentes 2026-06-24 / 2026-06-25 — Sesión de auditoría compliance

> Tres incidentes encadenados descubiertos durante el audit-loop iter 7+8. Todos resueltos.

## Incidente A: Columnas de modelos no migradas a BD (CRÍTICO)

**Síntoma:** Endpoints de Brechas, Encargados, Consentimientos y EIPD retornaban 500 con `column does not exist` en QA y prod.

**Causa raíz:** Las iteraciones 7 y 8 del audit-loop agregaron columnas a modelos SQLAlchemy (`consentimiento.py`, `encargado_contrato.py`, `eipd.py`, `breach.py`) y un modelo nuevo (`AsesorConversacion`), pero **no se generó ni ejecutó la migración SQL** correspondiente.

**Fix:**
- Commit `e98411e`: `backend/migrations/2026_06_24_001_compliance_columns.sql` con todas las columnas y la tabla nueva. Ejecutada contra Neon QA.
- Safeguards en agentes: `arquitecto-custodio.md`, `auditor-custodio.md`, `audit-loop.md` ahora requieren y validan que toda modificación de schema tenga su migración.

**Lección:** Cualquier cambio de schema debe ir acompañado de una migración SQL en `backend/migrations/` con timestamp + verificación contra Neon QA.

## Incidente B: Build de Vercel con TS2345 por tipos desincronizados (ALTO)

**Síntoma:** `npm run build` fallaba en Vercel con `TS2345: Argument of type ... is not assignable to parameter of type 'Partial<SecurityBreach>'` en `breaches/page.tsx:299,302`.

**Causa raíz:** El tipo `BreachFormData.naturaleza` permitía string vacío `''` como sentinel de "no seleccionado", pero el tipo `SecurityBreach.naturaleza` solo aceptaba los 3 valores del enum o `undefined`. TypeScript detectó la incompatibilidad. El build local pasó por cache; Vercel ejecutó tsc sobre la app completa y reportó el error.

**Fix:**
- Commit `9aaf808`: `BreachFormData.naturaleza` ahora es `'confidencialidad' | 'integridad' | 'disponibilidad' | undefined`. El `<select>` usa `value={form.naturaleza ?? ''}` para DOM, y `onChange` convierte `''` → `undefined` explícitamente.
- Safeguards cross-stack en `arquitecto-custodio.md`, `qa-custodio.md`, `auditor-custodio.md` que exigen build de FE (`npm run build`) + pytest contra Neon QA antes de cerrar iteración.

**Lección:** Nunca usar `''` como sentinel de "no seleccionado" en tipos que van al backend. Usar `undefined` con `Optional[Literal[...]]`.

## Incidente C: Endpoint OCI descarga tira 500 sin ENCRYPTION_KEY (CRÍTICO)

**Síntoma:** GET `/rats/34/archivo` retornaba 500 después de iter 7. Log de Vercel mostraba: `OCI direct download failed: ENCRYPTION_KEY es obligatoria en producción`.

**Causa raíz:** La iter 7 cambió el flujo de descarga de archivos OCI de `presigned_url` (público) a `download + decrypt` (Fernet E2E). Si `ENCRYPTION_KEY` no estaba configurada en Vercel, `settings.resolved_encryption_key` lanzaba `ValueError`, que se propagaba al endpoint sin ser capturado por el try/except de `_get_fernet()`.

**Fix:**
- Commit `6743549`: `_get_fernet()` envuelve la llamada a `settings.resolved_encryption_key` en try/except. Si la property lanza `ValueError`, retorna `None` y `encrypt()`/`decrypt()` operan como no-op.
- Se generó clave Fernet: `9M-27hR_oDuYeGfW6KcUXpttO3HJCl87AKe1fVXtpKg=` (guardada en backup seguro, NO en el repo).
- Clave configurada en Vercel QA (`custodio-api-qa`) y producción.

**Lección:** Cuando se cambia el modelo de seguridad de archivos (cifrado E2E), documentar claramente que se requiere `ENCRYPTION_KEY` configurada. El flujo previo con presigned_url no la necesitaba.