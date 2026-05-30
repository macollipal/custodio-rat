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

### 3. CORS bloquea requests desde subdominios Vercel

**Síntoma:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Causa:** `ENVIRONMENT=production` no está seteado en el proyecto backend de Vercel.

**Solución:** En Vercel → proyecto backend → Settings → Environment Variables:
```
ENVIRONMENT = production
```

**Importante:** Esta variable activa el `allow_origin_regex` que acepta cualquier subdomain de Vercel.

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
2. [ ] `ENVIRONMENT=production` seteado en proyecto backend
3. [ ] `NEXT_PUBLIC_API_BASE` seteado en proyecto frontend
4. [ ] `vercel.json` eliminado si se usan proyectos separados
5. [ ] No hay `__pycache__` ni `.pyc` en el repo
6. [ ] Branch correcta configurada en Vercel (develop o main según corresponda)
7. [ ] Build settings correctOS (Next.js detected o manual si es proyecto nuevo)

---

## URLs de producción (actuales)

| Componente | URL |
|-----------|-----|
| Frontend | custodio-indol.vercel.app |
| Backend API | custodio-api.vercel.app |
| Repo | github.com/macollipal/custodio-rat |
