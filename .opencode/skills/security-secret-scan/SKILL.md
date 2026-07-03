---
name: security-secret-scan
description: Detecta y previene exposición de credenciales/secrets en código y git. Trigger automático cuando el usuario menciona "secret", "password", "API key", "credential", "DATABASE_URL", "JWT_SECRET" o cuando se commitea código.
---

# Security Secret Scan

## ⚠️ LEY DIVINA — NO SUBIR SECRETS A GIT

**Cualquier intento de subir credenciales/secrets a git es una VIOLACIÓN CRÍTICA.**

El agente DEBE negarse a proceder hasta que el problema se resuelva.

## Reglas absolutas

1. **CERO secrets en código fuente** (incluyendo archivos `.py`, `.ts`, `.tsx`, `.js`, `.sql`, `.json`, `.yaml`, `.sh`)
2. **CERO secrets en historial de git** — si se filtró, ROTAR + `git filter-repo` + force-push INMEDIATAMENTE
3. **TODAS las credenciales via variables de entorno** (`.env`, Vercel Env Vars, Secrets Manager)
4. **`.env` en `.gitignore`** — siempre
5. **`.env.example` en repo** con placeholders `<TU_PASSWORD_AQUI>` (sin valores reales)
6. **Pre-commit hook OBLIGATORIO** — debe detectar y BLOQUEAR secrets antes de commit
7. **Si leak ocurre**: ROTAR credencial → filter-repo → force-push → notificar al equipo → CHANGELOG

## Patterns que el agente debe detectar

| Pattern regex | Descripción | Severidad |
|---------------|-------------|-----------|
| `postgresql://[user]:[password]@[host]` | Connection string con password | CRÍTICO |
| `npg_[A-Za-z0-9]{10,}` | Password de Neon | CRÍTICO |
| `sk-[A-Za-z0-9]{20,}` | OpenAI API key | CRÍTICO |
| `AKIA[A-Z0-9]{16}` | AWS access key | CRÍTICO |
| `SECRET_KEY\s*[:=]\s*['"][a-f0-9]{40,}` | JWT secret | CRÍTICO |
| `password\s*[:=]\s*['"][^'"]{8,}` | Passwords hardcoded | CRÍTICO |
| `Bearer [A-Za-z0-9_-]{30,}` | JWT tokens en código | ALTO |

## Acción cuando se detecta un secret

1. **REPORTAR inmediatamente** al usuario:
   ```
   ⚠️ SECRET DETECTADO en [archivo:línea]
   Pattern: [tipo de secret]
   Recomendación: usar os.environ['NOMBRE_VAR'] en lugar de hardcodear
   ```
2. **NO continuar** con la tarea hasta que se resuelva
3. **Sugerir el fix** apropiado (Python, TypeScript, etc.)
4. **Verificar** que `.env.example` tiene el placeholder (no valor real)
5. **Recordar**: si ya está en git, hay que ROTAR y limpiar historial

## Workflow correcto para nuevas credenciales

```python
# 1. Variable de entorno en código
import os
db_url = os.environ["DATABASE_URL"]
secret_key = os.environ["JWT_SECRET_KEY"]

# 2. .env.example en repo (solo placeholders)
DATABASE_URL=postgresql://user:<TU_PASSWORD>@host/db?sslmode=require
JWT_SECRET_KEY=<GENERA_CON_openssl_rand_hex_64>

# 3. .env local (gitignored)
DATABASE_URL=postgresql://user:password_real@host/db?sslmode=require
JWT_SECRET_KEY=tu_secret_real_aqui

# 4. Vercel Dashboard > Settings > Environment Variables
#    Configurar para cada ambiente (qa, production)
```

## Workflow correcto para TypeScript/JavaScript

```typescript
// ✅ CORRECTO - variable pública (NEXT_PUBLIC_*)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// ✅ CORRECTO - variable privada (server-side)
const secret = process.env.JWT_SECRET;

// ❌ INCORRECTO - hardcoded
const apiUrl = "https://api.example.com";
const secret = "sk-abc123def456";
```

## Lo que NO hacer (ejemplos)

```python
# ❌ NUNCA
password = "MyP@ssw0rd123"
DB_URL = "postgresql://user:npg_xxx@host/db"
API_KEY = "sk-abc123def456"
SECRET_KEY = "a" * 64  # hardcoded
```

```typescript
// ❌ NUNCA
const apiKey = "sk-abc123def456";
const dbUrl = "postgresql://user:pass@host/db";
```

```bash
# ❌ NUNCA hacer commit de:
echo "DATABASE_URL=postgresql://user:realpass@host/db" >> .env
git add .env  # NO! .env debe estar en .gitignore
git commit -m "Add config" .env
```

```markdown
# ❌ NUNCA en commit messages, PR descriptions, issues:
"Here's my API key: sk-abc123def456"
"The DATABASE_URL is postgresql://user:npg_xxx@host/db"
```

## Auditoría periódica

Antes de cada deploy/audit, ejecutar:

```bash
# Buscar secrets en historial completo de git
git log -p --all | grep -E "npg_|sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}" | head -20

# Escanear repo actual con gitleaks
gitleaks detect --no-banner --source .

# Verificar archivos .env tracked
git ls-files | grep -E "\.env$|\.env\.local$|\.env\.prod$"

# Verificar .gitignore cubre .env
cat .gitignore | grep -E "^\.env"
```

## Procedimiento de emergencia si hay leak

```bash
# 1. ROTAR credencial INMEDIATAMENTE
#    - Neon Console > Settings > Reset Password
#    - Vercel > Settings > Environment Variables > Update
#    - Otros servicios: rotar API keys/tokens

# 2. Limpiar historial de git
pip install git-filter-repo
python -m git_filter_repo --replace-text replacements.txt --force

# 3. Force-push (los clones existentes quedan con el historial viejo)
git push --force origin qa

# 4. Notificar al equipo
#    - Slack/Discord/email
#    - Lista de credenciales comprometidas
#    - Acciones tomadas

# 5. Actualizar CHANGELOG.md
#    ## [DATE] - Security incident
#    - Credenciales comprometidas: [lista]
#    - Acciones: rotación, filter-repo, force-push
```

## Integración con el resto del proyecto

| Componente | Cómo usa la skill |
|------------|-------------------|
| `backend/CLAUDE.md` | Referencia a esta skill |
| `frontend-next/AGENTS.md` | Referencia a esta skill |
| `README.md` | Sección visible de seguridad |
| `.git/hooks/pre-commit` | Enforcement automático |
| `.gitleaks.toml` | Reglas técnicas |
| `docs/SEGURIDAD_SECRETS.md` | Documentación detallada |
| `CHANGELOG.md` | Historial de incidentes |

## Recordatorio final

> **"Si tienes que escribir una credencial en código, estás haciéndolo mal."**
>
> Usa variables de entorno. Si no sabes cómo, pregunta antes de commitear.
> Es mejor pedir ayuda que exponer un secret en un repo público.