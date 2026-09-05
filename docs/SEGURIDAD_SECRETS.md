# Seguridad y Secrets · Custodio RAT Manager

**📖 Fuente canónica:** `.opencode/skills/security-secret-scan/SKILL.md`

Este documento complementa la skill con detalles específicos del proyecto Custodio RAT.

---

## ⚠️ Ley Divina — Resumen ejecutivo

> **Si tenés que escribir una credencial en código, estás haciéndolo mal.**

Cualquier credencial en código fuente o historial de git es una **violación crítica**.

---

## Tipos de secretos que protegemos

| Tipo | Ejemplo | Dónde va |
|------|---------|----------|
| **Database URL** | `postgresql://user:npg_xxx@host/db` | `DATABASE_URL` en `.env` |
| **Test DB URL** | `postgresql://user:npg_xxx@host/custodio_test` | `TEST_DATABASE_URL` en `.env` |
| **JWT Secret** | hex 64 chars | `SECRET_KEY` en `.env` |
| **OpenAI API key** | `sk-abc123...` | `OPENAI_API_KEY` en `.env` |
| **SMTP credentials** | `smtps://user:pass@smtp.host` | `SMTP_URL` en `.env` |
| **OCI credentials** | tenancy OCID + key content | Vercel Env Vars |

---

## Configuración correcta por ambiente

### Local (developer)

```bash
# 1. Copiar .env.example a .env
cp backend/.env.example backend/.env

# 2. Editar .env con valores REALES (no commitear)
DATABASE_URL=postgresql://user:REAL_PASSWORD@host/db?sslmode=require
SECRET_KEY=tu_secret_real_generado_con_openssl_rand_hex_64

# 3. Verificar que .env está gitignored
git check-ignore backend/.env  # debe devolver "backend/.env"
```

### QA (Vercel)

1. Vercel Dashboard → `custodio-qa` → Settings → Environment Variables
2. Configurar todas las variables (sin valores reales en commits)
3. Redeploy automático

### Producción (Vercel)

1. Vercel Dashboard → `custodio-rat` → Settings → Environment Variables
2. Configurar variables DIFERENTES a QA
3. Secrets Manager (recomendado para producción)

---

## Cómo generar secrets seguros

```bash
# JWT secret (64 chars hex)
openssl rand -hex 64

# Database password (32 chars alfanuméricos)
openssl rand -base64 32 | tr -d '+/=' | head -c 32

# API key random (si necesitás generar uno nuevo)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Procedimiento de emergencia ante leak

### Si commiteaste un secret accidentalmente:

```bash
# 1. ROTAR la credencial comprometida INMEDIATAMENTE
#    - Neon Console > Settings > Reset Password
#    - Vercel Dashboard > Environment Variables > Update
#    - OpenAI / otros servicios: revoke + regenerate

# 2. Limpiar historial de git
pip install git-filter-repo
echo "PASSWORD_ANTIGUO==>REDACTED" > replacements.txt
python -m git_filter_repo --replace-text replacements.txt --force

# 3. Force-push
git push --force origin qa

# 4. Notificar al equipo
#    Slack/Discord/email con:
#    - Qué credencial se expuso
#    - Dónde (archivo, commit, línea)
#    - Acciones tomadas

# 5. Actualizar CHANGELOG.md
## [DATE] - Security incident
- **CRITICAL**: Credencial [tipo] expuesta en [commit]
- **Acción**: rotación + filter-repo + force-push
- **Impacto**: [evaluar alcance]
```

---

## Verificación periódica

### Antes de cada commit

```bash
# Buscar patrones comunes en archivos staged
git diff --cached | grep -E "npg_|sk-[A-Za-z0-9]{20,}|password.*="

# Verificar que .env no se commitea
git status | grep "\.env$"  # no debe aparecer
```

### Antes de cada deploy

```bash
# Buscar secrets en historial completo
git log --all -p | grep -E "npg_[A-Za-z0-9]{10,}|sk-[A-Za-z0-9]{20,}" | head -20

# Escanear repo con gitleaks (si está instalado)
gitleaks detect --no-banner --source .

# Verificar archivos .env tracked
git ls-files | grep -E "\.env$|\.env\.local$|\.env\.prod$"
# Output esperado: (vacío)
```

### Auditoría mensual

```bash
# 1. Listar todos los archivos con secrets potenciales
grep -rn "npg_\|sk-\|AKIA\|SECRET_KEY" backend/ frontend-next/ \
  --include="*.py" --include="*.ts" --include="*.tsx" \
  --include="*.js" --include="*.json" --include="*.yaml" \
  | grep -v ".env.example" | grep -v "REDACTED" | grep -v "test_"

# 2. Revisar manualmente cada match
# 3. Reportar en CHANGELOG si hay hallazgos
```

---

## Herramientas de soporte

| Herramienta | Propósito | Estado |
|-------------|-----------|--------|
| `.git/hooks/pre-commit` | Bloquea secrets antes de commit | ✅ Activo |
| `.gitleaks.toml` | Reglas de detección | ✅ Configurado |
| `security-secret-scan` skill | Guía al agente | ✅ Activa |
| gitleaks CLI | Escaneo completo | ⚠️ Opcional (instalar local) |
| GitHub Secret Scanning | Detección automática GitHub | ⚠️ Configurar en repo |

---

## Checklist de onboarding para nuevos developers

Cuando alguien nuevo se une al proyecto:

- [ ] Leer `.opencode/skills/security-secret-scan/SKILL.md`
- [ ] Leer este documento (`docs/SEGURIDAD_SECRETS.md`)
- [ ] Copiar `.env.example` a `.env` localmente
- [ ] Generar sus propios secrets con `openssl rand`
- [ ] Verificar que `git status` no muestra `.env`
- [ ] Hacer un commit de prueba con un secret falso para verificar que el pre-commit hook lo bloquea
- [ ] Configurar Vercel Env Vars si tiene acceso

---

## Contacto ante incidente

Si descubrís un leak o tenés dudas sobre seguridad:

1. **NO** commitees nada más
2. Reportá inmediatamente al equipo
3. Seguí el "Procedimiento de emergencia ante leak" de este documento

---

**Última actualización:** 2026-07-03
**Mantenido por:** Equipo Custodio RAT