# Incidente: Frontend Prod apunta a localhost (2026-06-11)

## Resumen

Durante el deploy de v1.3 a producción, el frontend en `https://custodio-prod.vercel.app` quedó apuntando a `http://localhost:8002` en lugar de `https://custodio-api-prod.vercel.app`. Esto causó que **todas las requests del navegador fallaran con `ERR_CONNECTION_REFUSED`**.

## Impacto

- Frontend inaccesible funcionalmente (página carga pero no se puede usar)
- Backend funcionando correctamente (verificado con `/health` y `/health/db`)
- Login via API funcionaba (probado con `claudio_admin` / `Claudio2026!`)
- CORS configurado correctamente

## Causa Raíz

El proyecto `custodio-prod` (frontend) en Vercel **no tenía configuradas las variables de entorno** `NEXT_PUBLIC_API_BASE` y `NEXT_PUBLIC_DEPLOY_ENV` para el ambiente **Production**.

El código en `frontend-next/lib/constants.ts` tiene un fallback a localhost:

```ts
const _apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8002';
```

Sin la env var configurada, Vercel usó este fallback durante el build.

## Por qué no se detectó antes

El smoke test post-deploy solo validaba:
- Health check del backend
- Conectividad de BD
- Accesibilidad del frontend (página HTML carga)

**NO validaba** que el bundle JS del frontend apuntara a la URL correcta del backend.

## Solución Inmediata

Agregar las variables de entorno en Vercel Dashboard:
- `NEXT_PUBLIC_API_BASE` = `https://custodio-api-prod.vercel.app`
- `NEXT_PUBLIC_DEPLOY_ENV` = `production`

Y forzar redeploy del proyecto `custodio-prod`.

## Solución de Largo Plazo

Implementadas 4 capas de defensa para prevenir reincidencia:

### 1. Smoke Test Post-Deploy (`scripts/smoke_test_prod.py`)

Detecta automáticamente el problema. Valida que el bundle JS del frontend:
- NO contenga `localhost:8002`
- SÍ contenga la URL del backend correcta

**Uso**:
```bash
python scripts/smoke_test_prod.py --env prod
```

**Output del incidente detectado**:
```
[3] VERIFICACION DE ENV VARS EN BUNDLE (CRITICO)
  [FAIL] Bundle NO contiene localhost:8002: 1/5 bundles con localhost
  [WARN] Bundle contiene URL del backend (https://custodio-api-prod.vercel.app): 0/5 bundles
```

### 2. Validacion Pre-Build (`scripts/validate_env.py`)

Falla loud si las env vars requeridas no estan configuradas.

**Uso**:
```bash
python scripts/validate_env.py --env prod
```

**Output del problema actual**:
```
[FRONTEND]
  [WARN] NEXT_PUBLIC_API_BASE = http://localhost:8002 (esperado: https://custodio-api-prod.vercel.app)
  [WARN] NEXT_PUBLIC_DEPLOY_ENV = local (esperado: production)
```

### 3. Documentacion en Plan de Deploy

`docs/PLAN_DEPLOY_PRODUCCION_SEGURO.md` ahora incluye:
- Checklist explicito de env vars por ambiente
- Smoke test post-deploy como paso obligatorio
- Comandos exactos para validar antes y despues

### 4. Pipeline Recomendado (futuro)

Para CI/CD futuro, el orden deberia ser:

```
1. validate_env.py --env prod   (bloquea si faltan vars)
2. git merge qa → main
3. git push origin main
4. Vercel auto-deploy
5. smoke_test_prod.py --env prod  (falla si frontend apunta a localhost)
```

## Lecciones Aprendidas

1. **Los fallbacks en codigo son un anti-patron en configs criticas**. Deberian ser fail-loud.
2. **El smoke test debe validar el bundle compilado**, no solo endpoints accesibles.
3. **Las env vars son el eslabon debil** en deploys a Vercel - se olvidan facilmente.
4. **QA y Prod deben tener el mismo codigo** - el problema NO es el codigo, es la config de Vercel.

## Accion Requerida (todavia pendiente)

- [ ] Configurar `NEXT_PUBLIC_API_BASE` en Vercel PROD
- [ ] Configurar `NEXT_PUBLIC_DEPLOY_ENV` en Vercel PROD
- [ ] Redeploy `custodio-prod`
- [ ] Ejecutar `smoke_test_prod.py --env prod` para confirmar fix
