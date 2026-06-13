# Plan de Paso a Producción Seguro - Custodio RAT Manager

> **Versión**: 1.0
> **Fecha**: 2026-06-11
> **Origen**: Promoción QA → Producción Custodio RAT v1.3

---

## Resumen Ejecutivo

Este documento describe el **proceso canónico** para promover cambios validados en QA al ambiente de producción de Custodio RAT Manager, minimizando riesgo operacional y de pérdida de datos.

---

## Arquitectura de Ambientes

| Ambiente | Frontend | Backend | Base de Datos |
|----------|----------|---------|---------------|
| **Local** | http://localhost:3000 | http://localhost:8002 | SQLite (`backend/data/database.db`) |
| **QA** | https://custodio-qa.vercel.app | https://custodio-api-qa.vercel.app | Neon PostgreSQL QA |
| **Producción** | https://custodio-prod.vercel.app | https://custodio-api-prod.vercel.app | Neon PostgreSQL PROD (`Custodio_prod`) |

---

## Pre-Requisitos

Antes de iniciar el proceso:

- [ ] QA validados y **smoke tests pasando** en ambiente QA
- [ ] Cambios commiteados y mergeados a `qa`
- [ ] Equipo notificado (no ejecutar en horariospeak)
- [ ] Snapshot/backup de BD PROD disponible
- [ ] Credenciales de Vercel PROD accesibles
- [ ] Acceso a Neon dashboard PROD

---

## Proceso Paso a Paso

### FASE 1: Análisis Pre-Deploy (15 min)

#### 1.1 Comparar esquemas
```bash
# Conectar a ambas DBs
python -c "
import psycopg2

def get_tables(url):
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'\")
    return sorted([r[0] for r in cur.fetchall()])

qa = get_tables('QA_URL_HERE')
prod = get_tables('PROD_URL_HERE')

print('Solo en QA (faltan en PROD):', set(qa) - set(prod))
print('Solo en PROD:', set(prod) - set(qa))
"
```

#### 1.2 Identificar cambios estructurales
- Tablas nuevas en QA
- Columnas faltantes en PROD
- Nuevos constraints / foreign keys
- Cambios en enums (task_status, estados, etc.)

#### 1.3 Generar script de migración
- Usar `backend/migrations/migrate_to_<version>.sql`
- Aplicar patrón `IF NOT EXISTS` para idempotencia
- NO usar DROP/DELETE (preservar datos)
- Commitear el script al repo

---

### FASE 2: Merge a `main` (5 min)

#### 2.0 Validar env vars (BLOQUEANTE)

> ⚠️ **CRÍTICO**: Este paso evita el incidente del 2026-06-11 donde el frontend quedó apuntando a localhost por env vars no configuradas en Vercel.

```bash
# Verificar que .env files tienen los valores correctos
python scripts/validate_env.py --env prod
```

**Output esperado**:
```
[OK] Todas las env vars requeridas estan configuradas
```

Si el script reporta warnings, **NO continuar** hasta corregirlos.

#### 2.1 Merge

```bash
# 1. Verificar cambios sin commitear
git status

# 2. Stash cambios locales (si los hay)
git stash push -m "pre-deploy-$(date +%Y%m%d)"

# 3. Checkout a main
git checkout main

# 4. Pull origin main
git pull origin main

# 5. Merge qa → main
git merge qa --no-ff -m "deploy: v1.X.Y from qa to main"

# 6. Push a origin
git push origin main
```

**Resultado**: `Vercel` detecta el push y dispara **deploy automático** de `custodio-api-prod` y `custodio-prod`.

---

### FASE 3: Ejecutar Migración de BD (5 min)

> ⚠️ **Solo después de que Vercel haya desplegado el código nuevo**. Si se ejecuta antes, la app fallará al intentar leer tablas/columnas inexistentes.

```bash
# Script: migrate_prod.py
import psycopg2

PROD_URL = 'PROD_URL_HERE'

conn = psycopg2.connect(PROD_URL)
conn.autocommit = True  # CRÍTICO: cada statement se persiste
cur = conn.cursor()

with open('backend/migrations/migrate_to_v1_X.sql') as f:
    sql = f.read()

for stmt in sql.split(';'):
    stmt = stmt.strip()
    if stmt and not stmt.startswith('--'):
        cur.execute(stmt)

# Verificar
cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
print(f'Tablas en PROD: {cur.fetchone()[0]}')
```

**Verificación post-migración**:
```sql
-- Verificar tablas nuevas
SELECT 'encargados_contrato' as tabla, EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'encargados_contrato') as existe
UNION ALL SELECT 'feriados', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'feriados')
UNION ALL SELECT 'politicas_transparencia', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'politicas_transparencia')
UNION ALL SELECT 'task_queue', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'task_queue');
```

---

### FASE 4: Configurar Variables de Entorno en Vercel PROD

Ir al dashboard de Vercel → Proyecto `custodio-api-prod` → Settings → Environment Variables.

#### Variables Requeridas para Producción

| Variable | Valor | Notas |
|----------|-------|-------|
| `DATABASE_URL` | `postgresql://neondb_owner:.../Custodio_prod?sslmode=require` | Neon PROD |
| `SECRET_KEY` | (openssl rand -hex 64) | Distinto de QA |
| `ALLOWED_ORIGINS` | `https://custodio-prod.vercel.app` | **CRÍTICO** |
| `ENVIRONMENT` | `production` | Activa rate limiting, JSON logs |
| `SMTP_*` | (si aplica) | Para emails reales |

#### Frontend (`custodio-prod`)
| Variable | Valor |
|----------|-------|
| `NEXT_PUBLIC_API_BASE` | `https://custodio-api-prod.vercel.app` |
| `NEXT_PUBLIC_DEPLOY_ENV` | `production` |

> ⚠️ **Nunca commitear secrets al repo**. Usar siempre Vercel dashboard.

---

### FASE 5: Verificación Post-Deploy (10 min)

> ⚠️ **CRÍTICO**: Ejecutar el smoke test automatizado ANTES de cualquier prueba manual. Detecta el problema de "frontend apunta a localhost" en segundos.

#### 5.1 Smoke Test Automatizado (OBLIGATORIO)

```bash
# Detecta: env vars mal configuradas, CORS, health, login
python scripts/smoke_test_prod.py --env prod
```

**Output esperado**:
```
============================================================
SMOKE TEST - Ambiente: PROD
============================================================
[1] HEALTH CHECKS
  [OK] Backend /health
  [OK] Backend /health/db
[2] FRONTEND
  [OK] Frontend accesible
  [OK] JS bundles encontrados
[3] VERIFICACION DE ENV VARS EN BUNDLE (CRITICO)
  [OK] Bundle NO contiene localhost:8002
  [OK] Bundle contiene URL del backend
[4] CORS
  [OK] CORS permite https://custodio-prod.vercel.app
[5] LOGIN FUNCIONAL
  [OK] Login claudio_admin
  [OK] Token recibido
  [OK] User data recibido
  [OK] Endpoint protegido /auth/me
============================================================
[OK] Todos los smoke tests pasaron
```

**Si FALLA**: NO completar el deploy. Hacer rollback (Fase 6) y corregir.

#### 5.2 Verificacion Manual (solo si smoke test pasa)

- [ ] Login manual en navegador con `claudio_admin` / `Claudio2026!`
- [ ] Crear/editar empresa
- [ ] Crear RAT
- [ ] Verificar RAT de ejemplo persiste
- [ ] Generar PDF/CSV
- [ ] Verificar hash chain de auditoría

#### 5.3 Monitoreo Inicial (primeras 2 horas)
- [ ] Vercel Analytics: sin errores 5xx
- [ ] Neon dashboard: sin queries lentas
- [ ] Logs: sin stack traces repetidos

---

### FASE 6: Rollback Plan (si algo falla)

#### Opción A: Rollback de código (rápido)
1. Vercel Dashboard → Deployments → seleccionar deploy anterior → "Promote to Production"
2. Tiempo de recuperación: ~2 minutos

#### Opción B: Rollback de BD (lento, destructivo)
1. **Solo si la migración dañó datos**:
   - Neon Dashboard → Branch → Restore to point-in-time
2. Tiempo: 10-30 minutos (según tamaño)

#### Opción C: Rollback parcial de migración
```sql
-- Solo si la nueva tabla no se está usando
DROP TABLE IF EXISTS new_table;
ALTER TABLE old_table DROP COLUMN IF EXISTS new_column;
```

---

## Checklists de Seguridad

### Antes del Deploy
- [ ] Secretos NO están en código
- [ ] Variables de entorno PROD son diferentes a QA
- [ ] ALLOWED_ORIGINS apunta a dominio PROD
- [ ] Rate limiting activado (ENVIRONMENT=production)
- [ ] HTTPS forzado (Vercel lo hace por defecto)

### Después del Deploy
- [ ] CORS headers correctos
- [ ] Sin exposición de stack traces en respuestas
- [ ] PII masking en logs (email, RUT, IP, tokens)
- [ ] Audit log registrando acciones

---

## Convenciones

### Naming de migraciones
- `migrate_to_v1_X.sql` (siguiente versión)
- Ubicación: `backend/migrations/`
- Idempotente: usar `IF NOT EXISTS` siempre que sea posible

### Naming de commits
- `deploy: v1.X.Y from qa to main` (merge a main)
- `fix(prod): <descripción>` (hotfixes directos)

### Horario de deploys
- **Preferente**: Martes a Jueves, 10:00-16:00 (hora local)
- **Evitar**: Viernes tarde, fines de semana, feriados

---

## Responsabilidades

| Rol | Responsabilidad |
|-----|-----------------|
| **Dev** | Comparar esquemas, generar script de migración, ejecutar smoke tests |
| **Tech Lead** | Aprobar merge a main, monitorear deploy |
| **DevOps** | Configurar variables en Vercel, ejecutar rollback si es necesario |

---

## Historial de Deploys

| Versión | Fecha | Migración BD | Issues |
|---------|-------|--------------|--------|
| v1.3 | 2026-06-11 | 18→22 tablas | CORS configurado por primera vez |
| MVP | (anterior) | N/A | Sin ALLOWED_ORIGINS (necesario ahora) |

---

## Referencias

- Manual de Despliegue v1.0: `docs/documentacion_oficial/11_Manual_Despliegue_Custodio_RAT_Manager_v1.0.docx`
- Errores frecuentes: `docs/VERCEL_DEPLOY_ERRORS.md`
- Arquitectura v1.3: `docs/documentacion_oficial/06_Arquitectura_Software_Custodio_RAT_Manager_v1.3.docx`
