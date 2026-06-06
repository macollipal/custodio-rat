# Custodio — Backend Agents

## Contexto del proyecto

**Custodio RAT Manager** — Gestión del Registro de Actividades de Tratamiento (RAT) conforme a la Ley 21.719 de Chile.

Stack: FastAPI + SQLAlchemy + PostgreSQL (Neon) / SQLite (local) + JWT + Bcrypt + ReportLab (PDF).

---

## Sistema de roles (3 niveles)

| Rol global | Descripción | is_admin |
|------------|-------------|----------|
| `superadmin` | Todo el sistema | `True` |
| `admin_empresa` | Su empresa + usuarios | `False` |
| `usuario` | Su empresa (solo lectura RATs) | `False` |

- `is_admin` es columna legacy en BD (NOT NULL) pero la lógica usa `rol_global` exclusivamente
- `admin_empresa` y `usuario` requieren `company_id` al crearse
- La columna `is_admin` se calcula como `is_admin = (rol_global == 'superadmin')` al crear usuario

---

## Despliegue

| Entorno | URL | Base de datos |
|---------|-----|---------------|
| **Producción** | https://custodio-rat.vercel.app | Neon PostgreSQL |
| **QA** | https://custodio-api-qa-git-qa-... | Neon QA |
| **Local** | http://localhost:8002 | SQLite (`data/database.db`) |

### Vercel (Producción)

- Entry point: `api/index.py` → importa de `backend/app/main.py`
- Runtime: Python 3.9 (`@vercel/python` builder, auto-detectado)
- Environment variables en Vercel:
  - `ENVIRONMENT=production` → activa modo producción (logs JSON, rate limiting)
  - `DATABASE_URL` → connection string de Neon
  - `SECRET_KEY` → generar con `openssl rand -hex 64` (requerida en producción)
  - `SEED_ADMIN=true` + `SEED_ADMIN_PASSWORD=<pwd>` → para crear admin inicial (no automático)
  - `ALLOWED_ORIGINS` → **único mecanismo de CORS** (OBLIGATORIO, sin fallback)
    - QA: `ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000`
    - Prod: `ALLOWED_ORIGINS=https://custodio-rat.vercel.app`
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` → para envío de emails reales

### Vercel (QA)

- `ALLOWED_ORIGINS` es la única variable que controla CORS — sin heurísticas, sin VERCEL_URL, sin ENVIRONMENT
- Si no está seteada, la app no levanta (fail loud)
- Recomendado: `ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000`

### Migración SQLite → Neon

```bash
# 1. Exportar datos de SQLite
python migrate_to_neon.py export    # → backend/backup_data.json

# 2. Crear schema en Neon
python migrate_to_neon.py init       # crea tablas + reinicia sequences

# 3. Importar datos a Neon
python migrate_to_neon.py import      # desde backup_data.json
```

### Desarrollo local

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
# API docs: http://localhost:8002/docs
```

---

## Middleware

### RequestIdMiddleware (`app/middleware/request_id.py`)
Genera o propaga `X-Request-ID` en cada request:
- Si el cliente envía `X-Request-ID`, se respeta
- Si no, se genera un UUID v4
- Se inyecta en `contextvars` para que el logging lo lea
- Se devuelve en la respuesta como header `X-Request-ID`

### Logging estructurado (`app/core/logging_config.py`)
- `setup_logging()` configura logger raíz con `JSONFormatter` en producción
- `RequestIdFilter` inyecta `request_id` en cada `LogRecord`
- El `request_id` se lee de `contextvars` en cada log

---

## Servicios

### Email (`app/services/email_service.py`)
Envío de emails transaccionales via SMTP:
- `notificar_nueva_brecha()` → al DPO cuando se crea una brecha
- `notificar_vencimiento_rat()` → al DPO cuando un RAT requiere revisión
- `notificar_respuesta_arco()` → al titular cuando se responde su solicitud ARCO

**Modo DRY_RUN:** si `SMTP_HOST` no está configurado, loguea la intención (no falla). En producción, las excepciones se propagan.

### Scheduler (`app/services/scheduler.py`)
Tareas periódicas en thread daemon:
- Revisión de RATs vencidos: cada 24h (umbral: DIAS_REVISION = 180 días)
- Se activa en `lifespan` de FastAPI y se detiene al shutdown

---

## Modelos

### User
```
users:
  id, username, full_name, email, hashed_password
  rol_global: SUPERADMIN | ADMIN_EMPRESA | USUARIO
  is_admin: bool (calculado de rol_global)
  created_at, updated_at
```

### Company
```
companies:
  id, nombre, rut, rubro, direccion
  contacto_dpo, email_dpo
  descripcion, canal_ejercicio_derechos
  created_at, updated_at
```

### user_companies
```
user_companies:
  id, user_id (FK), company_id (FK)
  rol: ADMIN | EDITOR | VIEWER (RolEmpresa)
  created_at
```

### RAT
```
rats:
  # Obligatorios (7): nombre_proceso, categoria_datos, categoria_titulares,
  #                   finalidad, base_legal, fuente_datos, plazo_retencion
  # Recomendados (3): medidas_seguridad, destinatarios, transferencia_datos
  # Flags: datos_sensibles, evaluacion_impacto, decisiones_automatizadas,
  #        transferencia_internacional, tiene_contrato_encargado
  # EIPD: evaluacion_impacto, estado_eipd, fecha_eipd
  # Encargado: nombre_encargado, tiene_contrato_encargado
  # Test IL: test_interes_legitimo
  # Metadatos: estado, observaciones_auditoria, created_by, updated_by
  company_id (FK)
```

### SecurityBreach
```
security_breaches:
  id, company_id (FK)
  descripcion, fecha_deteccion
  rats_afectados, datos_comprometidos
  medidas_adoptadas
  notificado_apdc, fecha_notificacion_apdc
  notificado_titulares, fecha_notificacion_titulares
  creado_por, created_at, updated_at
```

### EIPD (1:1 con RAT)
```
eipds:
  id, rat_id (FK, unique)
  estado, fecha_inicio, fecha_completacion
  responsables, recursos_necesarios
  hallazgos, medidas_propuestas
```

### Consentimiento (1:N con RAT)
```
consentimientos:
  id, rat_id (FK)
  canal, texto_original, fecha_obtencion
  fecha_revocado, observaciones
```

---

## Fórmula de completitud

```python
campos_obligatorios = [nombre_proceso, categoria_datos, categoria_titulares,
                        finalidad, base_legal, fuente_datos, plazo_retencion]
campos_recomendados = [medidas_seguridad, destinatarios, transferencia_datos]
total = 10  # 7 + 3
completitud = round((completados / total) * 100)
```

---

## Endpoints principales

### Auth
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login JWT |
| GET | `/auth/me` | Usuario actual |

### Companies
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/companies` | Lista empresas |
| POST | `/companies` | Crear empresa |
| GET | `/companies/{id}` | Detalle empresa |
| PUT | `/companies/{id}` | Editar empresa |
| DELETE | `/companies/{id}` | Eliminar empresa |

### Rats
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/rats` | Lista RATs |
| POST | `/rats` | Crear RAT |
| GET | `/rats/{id}` | Detalle RAT |
| PUT | `/rats/{id}` | Editar RAT |
| DELETE | `/rats/{id}` | Eliminar RAT |
| GET | `/rats/{id}/audit` | Auditoría del RAT |
| GET | `/rats/{id}/export/pdf` | Exportar RAT individual a PDF |
| GET | `/rats/export/pdf` | Exportar todos los RATs de empresa a PDF |
| GET | `/rats/export/csv` | Exportar a CSV |
| GET | `/rats/export/cni` | Formato APDC (Ley 21.719) |
| GET | `/rats/reportes` | Reportes filtrados con paginación |

### Brechas
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/brechas` | Lista brechas |
| POST | `/brechas` | Crear brecha (dispara email al DPO si está configurado) |
| PUT | `/brechas/{id}` | Editar brecha |
| DELETE | `/brechas/{id}` | Eliminar brecha |

### Encargados contrato
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/encargados-contrato/` | Lista contratos de encargado |
| POST | `/encargados-contrato/` | Crear contrato |
| PUT | `/encargados-contrato/{id}` | Editar contrato |
| DELETE | `/encargados-contrato/{id}` | Eliminar contrato |

### Transparencia
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/publico/transparencia/{company_id}` | Política de transparencia (Art. 14 ter) |

### AI
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/ai/ask` | Chat IA (requiere MINIMAX_API_KEY u OPENAI_API_KEY) |

---

## Notas importantes

- Puerto: `8002`, URL base: `http://localhost:8002`
- Reiniciar backend: `run_server.bat` (cmd.exe, porque `&` no funciona en PowerShell)
- Base de datos: `backend/database.db` (SQLite)
- El usuario `admin` existente fue renombrado a `superadmin` y `jpe` a `admin_empresa`
- Para queries que filtran por empresa sin ser superadmin: usar `get_empresas_usuario(db, user_id)` que retorna lista de `company_ids`
- `get_current_user` en `routes/deps.py` extrae el usuario del token JWT
- **CORS:** se usa `ALLOWED_ORIGINS` (env var, lista blanca). Si no está definida, la app no levanta (fail loud)
- **Email:** si `SMTP_HOST` no está configurado, opera en modo DRY_RUN (loguea sin enviar)
- **Logs:** en producción los logs son JSON con `request_id` para correlación de extremo a extremo

---

## Dependencias clave

- `fastapi`, `uvicorn` — servidor
- `sqlalchemy` — ORM
- `pydantic` — validación
- `python-jose` — JWT
- `passlib` + `bcrypt` — contraseñas
- `reportlab` — generación PDF
- `pytest` + `httpx` — tests

---

## Tests

```bash
cd backend
pytest tests/ -v
```

Los tests couvren: CRUD RAT, completitud, dashboard stats, auth, brechas, auditoría, exportación.
