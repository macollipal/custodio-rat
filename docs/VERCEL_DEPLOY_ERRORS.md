# Errores de Deploy Vercel — LecAprendidos

## Problemas frecuentes y soluciones

### 1. Archivos faltantes en `main` vs `develop`

**Síntoma:** `ModuleNotFoundError: No module named 'app.models.solicitud_derecho'`

**Causa:** Merge PR #6 a `main` no incluía todos los archivos de `develop`. Archivos ARCO quedaban huérfanos.

**Prevención:** Antes de deployar, verificar que `main` tenga todos los archivos comparando con `develop`:
```bash
git diff --stat origin/develop origin/main -- backend/ frontend-next/
```

**Solución:** Copiar archivos de `origin/develop` a `main`:
```bash
git checkout origin/develop -- ruta/al/archivo
git push
```

---

### 2. Archivos corruptos con bytes nulos

**Síntoma:** `SyntaxError: source code string cannot contain null bytes`

**Causa:** Al copiar archivos entre ramas con `git show` o cherry-pick mal手段, se introducen bytes nulos que Python no puede parsing.

**Solución:** Reescribir el archivo a mano — no usar `git show | file.py` para transferir contenido entre ramas.

---

### 3. CORS bloquea requests

**Síntoma:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Causa:** `ALLOWED_ORIGINS` no está configurada correctamente en el proyecto backend de Vercel.

**Solución:** En Vercel → proyecto backend → Settings → Environment Variables:
```
ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000  (QA)
ALLOWED_ORIGINS=https://custodio-rat.vercel.app  (Producción)
```

**Importante:** `ALLOWED_ORIGINS` es la **única** variable que controla CORS. Sin ella, la app no levanta (fail loud). No usar `ENVIRONMENT` ni `VERCEL_URL` para CORS.

---

### 4. Frontend llama a `/api` relativo (404)

**Síntoma:** Login hace requests a `https://xxx.vercel.app/api/auth/login` en vez del backend real.

**Causa:** `API_BASE` en `constants.ts` usa `/api` como fallback (monorepo) cuando `NEXT_PUBLIC_API_BASE` no está disponible.

**Solución correcta:**
```typescript
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || (
  process.env.NODE_ENV === 'development' ? 'http://localhost:8002' : ''
);
```

El fallback en producción debe ser `''` (vacío) para forzar el uso de `NEXT_PUBLIC_API_BASE`.

---

### 5. Proyecto nuevo no detecta Next.js

**Síntoma:** Deploy da 404, no hay logs de build.

**Solución:** Al crear proyecto nuevo, seleccionar "Next.js" como framework manualmente en Configure Project. Si no aparece, borrar y recrear.

---

### 6. `vercel.json` en monorepo interfere con proyectos separados

**Síntoma:** Routing incorrecto cuando se tienen proyectos backend/frontend separados.

**Solución:** Si usás proyectos separados en Vercel, NO tener `vercel.json` en la raíz del repo. Borrarlo:
```bash
git rm vercel.json
git push
```

---

### 7. Rama `develop` vs `main`

**Situación:**
- `develop` = rama de desarrollo (todo el código nuevo)
- `main` = rama de producción (lo que se deploya)

**Problema:** Cuando se usa `main` para deployar, archivos nuevos en `develop` no están disponibles.

**Regla:** Mantener `main` actualizado con `develop` antes de cualquier deploy significativo:
```bash
git checkout main
git pull origin main
git merge develop
git push
```

---

### 8. Archivos residuales de Vercel en el repo

**Síntoma:** `vercel.svg` aparece en cambios pendientes.

**Solución:** Eliminarlos y no commitearlos:
```bash
git rm backend/frontend-next/public/vercel.svg
git commit -m "chore: remove vercel.svg artifact"
git push
```

---

## Checklist antes de deployar a Vercel

1. [ ] `main` está actualizado con `develop`
2. [ ] `ALLOWED_ORIGINS` configurada correctamente en proyecto backend
3. [ ] `NEXT_PUBLIC_API_BASE` seteado en proyecto frontend apuntando al backend correcto
4. [ ] `SECRET_KEY` de producción configurada en Vercel (no en filesystem)
5. [ ] `vercel.json` eliminado si se usan proyectos separados
6. [ ] No hay `__pycache__` ni `.pyc` en el repo
7. [ ] Branch correcta configurada en Vercel (qa para preview, main para producción)
8. [ ] Build settings correctos (Next.js detected o manual si es proyecto nuevo)

---

---

### 9. Secuencias de PostgreSQL desincronizadas con Neon (connection pooler)

**Síntoma:** `IntegrityError: duplicate key value violates unique constraint "audit_logs_pkey" DETAIL: Key (id)=(X) already exists.`

**Causa:** El connection pooler de Neon cachea valores de secuencia. Cuando se importa datos de SQLite a Neon, las secuencias se reinician correctamente, pero el pooler puede servir IDs antiguos a nuevas conexiones.

**Impacto:** Operaciones `INSERT` en tablas con secuencias (audit_logs, companies, rats, etc.) fallan con unique violation aunque la secuencia en PostgreSQL muestra valores altos.

**Diagnóstico:**
```python
import sqlalchemy as sa
engine = sa.create_engine('postgresql://...')
with engine.connect() as conn:
    seq_name = conn.execute(sa.text("SELECT pg_get_serial_sequence('audit_logs', 'id')")).scalar()
    seq_val = conn.execute(sa.text(f"SELECT last_value FROM {seq_name}")).scalar()
    ids = conn.execute(sa.text('SELECT id FROM audit_logs ORDER BY id')).fetchall()
    print(f'Secuencia: {seq_val}, IDs reales: {[r[0] for r in ids]}')
```

**Solución temporal — TRUNCATE:**
```sql
TRUNCATE TABLE audit_logs RESTART IDENTITY CASCADE;
```
Esto limpia la tabla y reinicia la secuencia a 1. Advertencia: perder todos los datos de auditoría.

**Solución preventiva — forzar secuencias altas:**
```python
sequences = {
    'users': 10000, 'companies': 10000, 'rats': 10000,
    'audit_logs': 100000, 'token_blacklist': 100000,
}
for table, val in sequences.items():
    seq_name = conn.execute(sa.text(f"SELECT pg_get_serial_sequence('{table}', 'id')")).scalar()
    conn.execute(sa.text(f"SELECT setval('{seq_name}', {val}, true)"))
```

**Nota:** Este es un problema conocido de Neon con connection pooler y PostgreSQL SERIAL. El cacheo de secuencias puede persistir incluso después de reiniciar el backend.

---

### 10. TokenBlacklist falla en desarrollo (tabla no existe)

**Síntoma:** `ProgrammingError: relation "token_blacklist" does not exist`

**Causa:** El modelo `TokenBlacklist` se creó después de que las tablas ya estaban creadas en Neon.

**Solución:** Recrear la tabla ejecutando `migrate_to_neon.py init` o crear la tabla manualmente:
```python
from app.database.database import Base
from app.models.token_blacklist import TokenBlacklist
Base.metadata.create_all(bind=engine)  # solo crea lo que falta
```

---

## URLs de producción (actuales)

| Componente | URL |
|-----------|-----|
| Frontend | https://custodio-rat.vercel.app |
| Backend API | https://custodio-api-prod.vercel.app |
| Repo | github.com/macollipal/custodio-rat |

---

## CORS — Solución Definitiva (Q3 2026)

**PROBLEMA:** `No 'Access-Control-Allow-Origin' header is present`

**SOLUCIÓN:** `ALLOWED_ORIGINS` es la **única** variable que controla CORS. Sin ella, la app **no levanta** (fail loud).

### Configuración en Vercel (Backend)

| Entorno | `ALLOWED_ORIGINS` |
|---------|-------------------|
| QA | `https://custodio-qa.vercel.app,http://localhost:3000` |
| Producción | `https://custodio-rat.vercel.app` |

### Reglas
- Sin `ALLOWED_ORIGINS` → la app no levanta
- Sin wildcards, sin `VERCEL_URL`, sin `ENVIRONMENT` para CORS
- Cada nuevo dominio de preview debe agregarse a `ALLOWED_ORIGINS`

---

## Entornos Vercel

| Entorno | Rama Git | Base de datos Neon | Secret Key |
|---------|---------|-------------------|------------|
| Producción | `main` | Custodio_dev (Neon) | `SECRET_KEY` en Vercel env |
| QA | `qa` | Custodio_QA (Neon) | `SECRET_KEY` en Vercel env |

⚠️ **NUNCA** poner secrets en el filesystem del repo. Usar siempre Environment Variables en Vercel.

## Desarrollo local

⚠️ El `.env` local apunta a **Neon Custodio_dev** (no SQLite). Trabajar localmente = trabajar directo en la base de desarrollo. La `DEV_SECRET_KEY` es obligatoria en desarrollo (sin fallback hardcodeado).
