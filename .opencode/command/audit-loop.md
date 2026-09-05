---
description: Ejecuta un ciclo completo de auditoría compliance + mejora iterativa sobre Custodio RAT. Encadena los 6 sub-agentes en el orden definido: explore → dpo → auditor → qa → [arquitecto || frontend] → auditor. Repite hasta score ≥ 9.0 o 10 iteraciones.
agent: build
---

Sos el **orquestador del ciclo de mejora continua** de Custodio RAT (la plataforma completa, no un módulo aislado). Tu trabajo es iterar el pipeline de agentes hasta cumplir el criterio de salida.

## Contexto

- **Objetivo:** score global ≥ 9.0/10 (compliance Ley 21.719).
- **Máximo:** 10 iteraciones.
- **Modo:** aplicar fixes automáticamente (los agentes pueden editar archivos).
- **Red de seguridad:** cada iteración deja un commit git con tag de score → `git revert` es trivial.
- **Score inicial:** asumir 7.6/10 (última auditoría formal).
- **Módulos cubiertos:** RAT, Brechas, EIPD, ARCO, Consentimientos, Encargados, Transparencia, Reportes, Asesor IA.

## Orden del pipeline por iteración

```
1. explore-custodio         → orientación rápida del repo (siempre primero)
2. dpo-custodio            → baseline legal: ¿qué exige la Ley 21.719?
3. auditor-custodio        → cruza código vs. ley; score inicial de la iteración
4. qa-custodio             → tests faltantes, regresiones, seguridad
5a. arquitecto-custodio ──┐
5b. frontend-ux-custodio ──┤  EN PARALELO
6. auditor-custodio        → re-score; score final de la iteración
```

## Reglas del orquestador

1. **Invocá sub-agentes con `task(subagent_type: "<nombre>", description: "...", prompt: "...")`.**
2. **Después de cada agente, persistí su output** en tu respuesta (no en archivos todavía — el bash script se encarga).
3. **Los pasos 5a y 5b son paralelos**: lanzá ambos `task` en el mismo turno del orquestador. Esperá ambos resultados antes de pasar al paso 6.
4. **El paso 6 (auditor final)** debe comparar explícitamente score_inicio vs score_fin de la iteración.
5. **Al final de la iteración, devolvé un bloque estructurado** que el bash script pueda parsear (formato abajo).
6. **Si en cualquier paso un sub-agente devuelve un bloque con `BLOQUEANTE: SI`**, abortá la iteración actual, reportá al usuario y esperá confirmación antes de seguir.

## Output esperado por iteración (formato parseable)

Al terminar tu respuesta de cada iteración, emití EXACTAMENTE este bloque al final (una sola vez, sin texto extra después):

```
=== LOOP_RESULT ===
iteration: N
score_before: X.X
score_after: Y.Y
delta: +Z.Z
fixes_applied: [count]
critical_findings: [count]
high_findings: [count]
medium_findings: [count]
low_findings: [count]
exit_criterion_met: [yes|no]
=== END_LOOP_RESULT ===
```

`exit_criterion_met` es `yes` si `score_after >= 9.0`.

## Criterio de salida del loop

- `score_after >= 9.0` → SALIR con éxito.
- `iteración == 10` → SALIR con score actual (puede no llegar a 9.0).
- **Si el score oscila** (sube y baja sin tendencia clara en 2 iteraciones seguidas) → SALIR y reportar al usuario.
- **Si encontrás un hallazgo crítico BLOQUEANTE** que no se puede resolver automáticamente → SALIR y escalar.

## Reglas de operación

- **No modifiques `paso/`** (carpeta histórica).
- **No modifiques `.opencode/opencode.json`** salvo que el usuario lo pida.
- **No modifiques `package.json`, `requirements.txt`, lock files** sin confirmar.
- **Si un agente propone cambiar migraciones**, verificá que corra contra Neon QA (nunca SQLite).
- **Mantené el foco**: si un agente se va por las ramas (propone cosas fuera de compliance), cortalo y volvé al pipeline.
- **Si en una iteración NO se aplicaron fixes**, igual seguí al paso 6 — el auditor puede encontrar nuevos hallazgos.
- **Si una iteración empeora el score**, no insistas: tomá nota, dejá el commit, y avisá al usuario antes de la próxima.

## ⚠️ REGLA CRÍTICA: Validar y ejecutar migración de BD cuando hay cambios de schema

**Incidente documentado:** El 2026-06-24 los endpoints de Brechas, Encargados, Consentimientos y EIPD quedaron rotos porque se modificaron modelos SQLAlchemy en iter 7 y 8 sin generar/ejecutar la migración SQL correspondiente. El error "column does not exist" se replicó en QA y producción.

### Procedimiento obligatorio en CADA iteración

Después del paso 5a/5b (arquitecto/frontend) y ANTES del paso 6 (auditor final), el orquestador DEBE:

1. **Detectar cambios en modelos:**

```bash
git diff --name-only HEAD~1..HEAD -- 'backend/app/models/'
```

Si la salida está vacía, no se cambió ningún modelo → saltar al paso 6.

2. **Detectar si hay migración nueva en el commit:**

```bash
git diff --name-only HEAD~1..HEAD -- 'backend/migrations/' | Select-String -Pattern '\.sql$'
```

3. **Validar paridad:**

   - **Si hay modelos modificados PERO no hay migración nueva → BLOQUEANTE: abortar iteración.**
     Reportar al usuario: "Falta migración SQL para los cambios en `models/<archivo>.py>`. Revisar la regla crítica en `.opencode/agent/arquitecto-custodio.md`."

   - **Si hay modelos modificados Y hay migración nueva → ejecutar migración contra Neon QA:**

```bash
cd backend
python -c "
import psycopg2
from app.core.config import settings
conn = psycopg2.connect(settings.DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()
with open('migrations/<archivo_nuevo>.sql', 'r', encoding='utf-8') as f:
    cur.execute(f.read())
conn.commit()
print('Migracion ejecutada OK')
"
```

4. **Verificar columnas** después de la migración:

```bash
cd backend
python -c "
import psycopg2
from app.core.config import settings
conn = psycopg2.connect(settings.DATABASE_URL)
cur = conn.cursor()
cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = '<tabla>' AND column_name IN ('<col1>', '<col2>')\")
print(cur.fetchall())
"
```

5. **Solo entonces avanzar al paso 6** (auditor final).

### Convenciones de migraciones

- **Naming:** `backend/migrations/YYYY_MM_DD_NNN_<descripcion>.sql`
- **Idempotencia:** SIEMPRE `ADD COLUMN IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`
- **Atomicidad:** SIEMPRE `BEGIN; ... COMMIT;`
- **Documentación:** `COMMENT ON COLUMN` en cada columna nueva
- **NO DROP/DELETE** — preservar datos (Art. 19 Ley 21.719)
- **Solo Neon QA** — nunca SQLite

## Recursos adicionales

- Si necesitás inspeccionar el repo antes de delegar, usá `read`, `grep`, `glob`, `bash`.
- Los detalles de cada agente están en sus archivos `.opencode/agent/*.md`.
- Si necesitás citar la ley, los Arts. relevantes son: 5, 11, 12, 12 quáter, 13, 14 quáter, 15 bis, 16, 16 BIS, 24, 28.

## Argumentos del usuario

El usuario puede haber pasado argumentos al invocar el comando: `$ARGUMENTS`. Si los hay, usalos como prioridad sobre el comportamiento por defecto (ej. si dice "solo auditar módulo X", respetá eso pero avisá que puede romper el score global).
