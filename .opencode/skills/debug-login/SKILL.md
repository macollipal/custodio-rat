---
name: debug-login
description: Diagnostica problemas de login en Custodio RAT. Detecta credenciales incorrectas, problemas de BD, usuarios faltantes y da mensajes accionables.
---
# Debug Login — Custodio RAT

Skill para diagnosticar login fallido en Custodio RAT. Úsalo cuando el usuario no pueda entrar o reporte errores de autenticación.

## Cuándo invocar

```
"No puedo entrar a Custodio"
"El login no funciona"
"Error de autenticación"
"401 unauthorized"
"No me deja loguear"
"Olvidé la contraseña admin"
"Login broke after..."
```

## Diagnóstico rápido (orden obligatorio)

### Paso 1 — Verificar API responde

```bash
curl -s -X POST "https://custodio-api-qa.vercel.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin1234"}'
```

**Si responde 200:** El API funciona. El problema es frontend, token expired, o credenciales del navegador.

**Si responde 401:** Credenciales incorrectas → ir a Paso 2.

**Si no responde o timeout:** El API está caído → verificar Vercel dashboard.

---

### Paso 2 — Verificar password actual del admin en BD

```bash
cd backend
$env:DATABASE_URL = "postgresql://neondb_owner:@ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
# ^ completar con password desde .env

python -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT id, username, email FROM users WHERE username=%s', ('admin',))
user = cur.fetchone()
if user:
    print(f'Usuario existe: ID={user[0]}, username={user[1]}, email={user[2]}')
else:
    print('USUARIO NO EXISTE — ejecutar seed')
conn.close()
"
```

**Si usuario no existe:** Ejecutar seed para crear admin:
```bash
cd backend
python -c "from app.core.security import get_password_hash; print(get_password_hash('admin1234'))"
# Luego actualizar BD con el hash
```

---

### Paso 3 — Verificar password conocida vs hash en BD

Passwords conocidas en el sistema (usar la que aplique):

| Entorno | Password actual |
|---------|---------------|
| QA / Local | `admin1234` |
| Prod (antes de rotación) | `Admin1234!` |
| Test (pytest) | `admin1234` |

Para verificar el hash en BD:
```bash
python -c "
import psycopg2, os, bcrypt
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT hashed_password FROM users WHERE username=%s', ('admin',))
row = cur.fetchone()
if row:
    hashed = row[0].encode() if isinstance(row[0], str) else row[0]
    for pwd in ['admin1234', 'Admin1234!']:
        if bcrypt.checkpw(pwd.encode(), hashed):
            print(f'MATCH: \"{pwd}\"')
            break
    else:
        print('Password no coincide con hashes conocidos')
conn.close()
"
```

---

### Paso 4 — Checklist de causas comunes

| Causa | Síntoma | Solución |
|-------|---------|----------|
| Password rotada en Neon | Login 401 siempre | Resetear password en Neon Console, actualizar `.env` |
| Browser con token viejo | Login redirige a home pero no funciona | Limpiar cookies, modo incógnito |
| `.env` desactualizado | Backend usa password vieja | Copiar password actual a `backend/.env` |
| Seed nunca ejecutado | Usuario admin no existe | Ejecutar `python scripts/maintenance/seed_claudio_corp.py` |
| Rate limiting | Login funciona 1 vez, luego 401 | Esperar 5 min, verificar `ENVIRONMENT=production` |
| CORS bloqueando | Opciones preflight fallan | Verificar `ALLOWED_ORIGINS` incluye la URL del frontend |

---

### Paso 5 — Reset password admin (último recurso)

Si todo falla, resetear la password via script (requiere acceso a BD):

```bash
cd backend
$env:DATABASE_URL = "postgresql://neondb_owner:@ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"

python -c "
import psycopg2, os, bcrypt
from app.core.security import get_password_hash

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
new_hash = get_password_hash('admin1234')
cur.execute('UPDATE users SET hashed_password = %s WHERE username = %s', (new_hash, 'admin'))
conn.commit()
print(f'Password reseteada a admin1234 para admin (filas afectadas: {cur.rowcount})')
cur.close()
conn.close()
"
```

---

## Mensajes de error comunes y sus causas

| Error en navegador | Causa probable |
|-------------------|----------------|
| "Invalid credentials" | Username o password incorrectos |
| "User not found" | Usuario admin no existe en BD (seed no ejecutado) |
| "Account is inactive" | `is_active=False` en BD |
| "Too many requests" | Rate limiting activo |
| "Network error" | CORS bloqueando o API caída |
| Blank screen post-login | Token en cookie corrupto / cuenta sin empresa asignada |

---

## Regla divina

Si el usuario reporta "no puedo entrar", **siempre verificar primero**:
1. API responde (curl login)
2. Password es `admin1234` (QA/local) o `Admin1234!` (prod antigua)
3. Browser en modo incógnito funciona

**No asumir** que el problema es código. El 90% de las veces es:
- Password cambiada y no文档ada
- Token viejo en browser
- `.env` desactualizado post-rotación
