# Custodio — Backend Agents

## Contexto del proyecto

**Custodio RAT Manager** — Gestión del Registro de Actividades de Tratamiento (RAT) conforme a la Ley 21.719 de Chile.

Stack: FastAPI + SQLAlchemy + PostgreSQL (Neon) + JWT + Bcrypt + ReportLab (PDF).

---

## LEY DIVINA DE SEGURIDAD ⚠️

**📖 Fuente canónica:** `.opencode/skills/security-secret-scan/SKILL.md`

Reglas absolutas (resumen; ver skill para detalles):

```
1. NUNCA hardcodear credenciales en código fuente
2. Todas las passwords/tokens/keys van en variables de entorno (.env)
3. NO hacer fallback con valores por defecto que expongan secretos
4. Los archivos .env están en .gitignore y NUNCA se commitear
5. Si una credencial se expone, ROTARLA inmediatamente
6. Usar Secrets Manager en producción (Vercel Env Variables)
7. Pre-commit hook con gitleaks es OBLIGATORIO (ver .git/hooks/pre-commit)
```

**Si el agente detecta un secret hardcodeado DEBE negarse a proceder y reportar al usuario antes de continuar.**
8. Si una credencial se expone en git: git filter-repo para limpiar historial + force-push
```

**Si detectas una credencial expuesta:**
1. Informar inmediatamente
2. La credencial debe ser rotada (Neon Console → Reset password)
3. Remover del historial de git con `git filter-repo --replace-text`
4. Force-push coordinated con todos los contribuidores

---

## Skills disponibles para backend

Las siguientes skills (en `.opencode/skills/`) son relevantes para este proyecto:

- **security-secret-scan**: para detectar/prevenir exposición de credenciales (OBLIGATORIA antes de commit)
- **commit-helper**: para mensajes de commit con conventional commits
- **tester-rat**: para diseñar planes de prueba (pytest + Playwright) y validar compliance Ley 21.719
- **custodio-auditoria**: para regenerar documentación oficial v1.x y validar compliance
- **qa-senior**: para revisión de calidad de código, seguridad y compliance RAT
- **architect-senior**: para auditorías arquitectónicas (score de madurez del producto)
- **deploy-cors-multienv**: para configurar CORS multi-ambiente (Dev/QA/Prod)
- **debug-login**: para diagnosticar problemas de login (401, credenciales, BD)
- **rat-compliance**: para validar compliance de un RAT (Art. 16, campos obligatorios 7+3, EIPD)
- **breach-management**: para gestionar brechas de seguridad (72h APDP, notificación titulares)
- **arco-rights**: para validar workflow ARCO (10 días hábiles, verificación identidad, causal rechazo)
- **multi-tenant-security**: para auditar aislamiento multi-tenant (IDOR, RBAC, acceso cruzado)
- **api-review**: para revisar nuevos endpoints antes de deploy (seguridad, compliance, REST)
- **eipd-management**: para validar workflow EIPD (Art. 15 bis, metodologia, plazos, resultado)
- **consentimiento-management**: para validar ciclo de vida del consentimiento (Art. 12, revocacion, evidencia)
- **politica-transparencia**: para validar politica de transparencia (Art. 14 ter, endpoint publico)
- **encargado-tratamiento**: para validar contratos de encargado (Art. 14 quater, vigencias, PDF)

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
| **Producción** | https://custodio-api-prod.vercel.app | Neon PostgreSQL |
| **QA** | https://custodio-qa.vercel.app | Neon QA |
| **Local** | http://localhost:8002 | Neon PostgreSQL (desarrollo) |

### Vercel (Producción)

- Entry point: `api/index.py` → importa de `backend/app/main.py`
- Runtime: Python 3.9 (`@vercel/python` builder, auto-detectado)
- Environment variables en Vercel:
  - `ENVIRONMENT=production` → activa modo producción (logs JSON, rate limiting)
  - `DATABASE_URL` → connection string de Neon
  - `SECRET_KEY` → generar con `openssl rand -hex 64` (requerida en producción)
  - `SEED_ADMIN=true` + `SEED_ADMIN_PASSWORD=<pwd>` → para crear admin inicial (no automático)
  - `ALLOWED_ORIGINS` → **único mecanismo de CORS** (OBLIGATORIO en todos los ambientes)
    - Prod: `ALLOWED_ORIGINS=https://custodio-rat.vercel.app`
  - `SMTP_URL` → SMTP en formato DSN (ej. `smtplib://apikey:SG.xxx@smtp.sendgrid.net:587/?use_tls=true&from_email=admin@yopmail.com&from_name=Custodio%20RAT`). Compatibilidad legacy con SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_FROM_NAME si SMTP_URL no está seteada.

### Vercel (QA)

- `ALLOWED_ORIGINS` es la única variable que controla CORS — sin heurísticas, sin VERCEL_URL, sin ENVIRONMENT
- Si no está seteada, la app no levanta (fail loud)
- Requerido: `ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000`

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

**Modo DRY_RUN:** si `SMTP_URL` (o `SMTP_HOST` en legacy) no está configurado, loguea la intención (no falla). En producción, las excepciones se propagan.

### Scheduler (`app/services/scheduler.py`)
Tareas periódicas en thread daemon. **Modo enqueue** (compatible con Vercel serverless):
- Encola `revisar_rats_vencidos` cada 24h
- Encola `cleanup_tokens` cada 6h
- Las tareas se procesan desde el endpoint `/admin/tasks/run` (llamado por cron externo)

### Task Service (`app/services/task_service.py`)
Cola de tareas asincronas persistida en BD:
- `enqueue_task(db, task_type, payload)` → encola tarea
- `process_pending_tasks(db, max_tasks)` → ejecuta las pendientes
- `run_task(db, task)` → ejecuta una tarea individual
- Tipos: `revisar_rats_vencidos`, `notificar_brecha_dpo`, `notificar_respuesta_arco`, `cleanup_tokens`
- Reintentos automáticos con backoff (max 3 intentos)

### Audit Service (`app/services/audit_service.py`)
Registro transversal de operaciones:
- `log_audit(db, entidad, entidad_id, accion, usuario, detalle, ip_origen)`
- Se invoca desde: RAT (CRUD), Brechas (CUD), TKT (CUD), Consentimientos (CUD), EIPD (CUD), SolicitudesDerecho (responder)

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
  metodologia, objetivos, necesidad_proporcionalidad
  riesgos_identificados, medidas_propuestas
  parecer_dpo, parecer_dpo_autor, parecer_dpo_fecha
  justificacion_no_aplica
  fecha_elaboracion, fecha_aprobacion
  resultado: completada | no_requerida | no_requerida_justificada | en_proceso
  created_by, created_at, updated_at
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
# 7 obligatorios Art. 16
campos_obligatorios = [nombre_proceso, categoria_datos, categoria_titulares,
                        finalidad, base_legal, fuente_datos, plazo_retencion]
# 3 recomendados Art. 16
campos_recomendados = [medidas_seguridad, destinatarios, transferencia_datos]
# 5 Tier 1 — compliance APDP crítico
campos_tier1 = [nivel_confidencialidad, estructura_dato, datos_nna,
                datos_anonimizados, datos_seudonimizados]
# 10 Tier 2 — operativos
campos_tier2 = [sistema_almacenamiento, volumen_titulares_estimado,
                responsable_tratamiento_email, ciclo_procesamiento,
                automatizacion, frecuencia, transferencia_nacional,
                doc_clausulas, medidas_organizativas, mecanismos_eliminacion]
total = 25  # 7 + 3 + 5 + 10
# Penalización -1 si base_legal != 'Otra' y no hay documento adjunto
completitud = round((completados / total) * 100)
```

---

## Endpoints principales

### Auth
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Login JWT (access 8h + refresh 30d) |
| POST | `/auth/refresh` | Renovar access token (rotación) |
| POST | `/auth/logout` | Revocar access + refresh tokens |
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
| POST | `/ai/ask` | Chat IA genérico (requiere GROQ_API_KEY) |

### Consentimientos (Art. 12)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/consentimientos/` | Lista consentimientos (filtros: company_id, rat_id, solo_activos) |
| POST | `/consentimientos/` | Crea consentimiento vinculado a RAT |
| GET | `/consentimientos/{id}` | Detalle de consentimiento |
| POST | `/consentimientos/{id}/revocar` | Revoca consentimiento (Art. 12) |

### EIPD (Art. 15 bis)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/eipd/` | Lista EIPDs (filtros: company_id, estado) |
| GET | `/eipd/rat/{rat_id}` | EIPD de un RAT específico |
| GET | `/eipd/{id}` | Obtener EIPD por ID |
| POST | `/eipd/` | Crea EIPD (1:1 con RAT) |
| PUT | `/eipd/{id}` | Actualiza EIPD (workflow) |

### ARCO — Solicitudes de Derecho (Art. 12, 12.5, 14)

Único modelo canónico: ``TktSolicitudDerecho``. La tabla y endpoints legacy ``SolicitudDerecho``
fueron eliminados completamente (jul-2026). No existe formulario público en frontend: las solicitudes
ARCO se gestionan internamente como tickets.

#### Public tracking (titular, sin auth)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/seguimiento/{tracking_token}` | Consulta pública del estado (sin auth) |

#### Workflow staff (autenticado, RBAC estricto)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/tkt-solicitud-derecho/` | Lista TKTs con filtros |
| POST | `/tkt-solicitud-derecho/` | Crear TKT interno |
| GET | `/tkt-solicitud-derecho/{id}` | Detalle TKT |
| PATCH | `/tkt-solicitud-derecho/{id}` | Actualizar (requiere `metodo_verificacion_identidad` si pasa a `resuelto`) |
| POST | `/tkt-solicitud-derecho/{id}/bloquear` | Bloquear RAT (Art. 8 ter) |
| POST | `/tkt-solicitud-derecho/{id}/desbloquear` | Desbloquear antes de vencer |
| POST | `/tkt-solicitud-derecho/{id}/rechazar` | Rechazo fundado con `causal_rechazo` enum (Art. 12.5) |
| POST | `/tkt-solicitud-derecho/{id}/subsanar` | Pedir subsanación al titular |
| POST | `/tkt-solicitud-derecho/{id}/completar-subsanacion` | Cerrar subsanación |
| POST | `/tkt-solicitud-derecho/{id}/prorrogar` | Extender plazo +10 días hábiles (Art. 12 bis) |
| POST | `/tkt-solicitud-derecho/{id}/portabilidad/guardar` | Guardar datos portabilidad |
| GET | `/tkt-solicitud-derecho/{id}/portabilidad/export` | Exportar JSON portabilidad (Art. 9) |

#### Reglas de compliance automatizadas

| Regla | Detalle |
|-------|---------|
| **Verificación de identidad** | Backend rechaza PATCH→`resuelto` si `metodo_verificacion_identidad` no existe (Art. 12) |
| **Hash de integridad** | Al resolver se computa `evidencia_respuesta_hash = SHA256(respuesta + username + timestamp)` |
| **Causal de rechazo** | `causal_rechazo` debe estar en `CausalRechazo` enum; valores: `falta_identidad`, `solicitud_manifiestamente_infundada`, `solicitud_excesiva`, `falta_poder_notorial`, `plazo_vencido`, `identidad_no_verificada`, `otro` |
| **Plazo legal** | 10 días hábiles, calculado con feriados Chile hardcoded hasta 2040 + Semana Santa (Art. 14) |
| **SLA** | Estados válido intermedio: `abierto` → `en_proceso`/`pendiente` → `resuelto`/`rechazado`. Prórroga 1 vez por ticket (Art. 12 bis). |
| **Magic bytes** | Upload de archivos valida magic bytes PDF/JPEG/PNG/GIF (S3.1) — rechaza ``.exe`` renombrado |
| **Rate-limit** | Form público: 10/h por IP (lee X-Forwarded-For). Token: 5/min. CSRF: 30/min |

#### Estructura de tablas

```sql
-- Tabla canónica (moderna)
tkt_solicitud_derecho(
  id, company_id, tipo, estado, prioridad, origen,
  titular_nombre, titular_email, titular_rut,
  descripcion, fecha_recepcion, fecha_vencimiento,
  responsable_id, respuesta_texto, respuesta_fecha,
  rat_id, plazo_bloqueo_vencimiento, portability_data,
  tracking_token, acuse_enviado_at,
  -- Compliance Ley 21.719 (Iter 10)
  metodo_verificacion_identidad, evidencia_identidad,
  evidencia_respuesta_hash, causal_rechazo, medio_respuesta,
  -- Workflow extension
  subsanacion_detalle, subsanacion_fecha_pedido,
  prorroga_fecha, prorroga_dias,
  -- Multi-representante
  representante_nombre, representante_rut,
  telefono, fecha_nacimiento, pais,
  created_by, created_at, updated_at
)
```

> **Nota:** La tabla legacy `solicitudes_derecho` y el modelo `SolicitudDerecho` fueron eliminados en julio 2026.
> `TktSolicitudDerecho` es la única entidad ARCO canónica. La sincronización legacy ya no existe.

### Admin - Cola de Tareas
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/tasks/` | Lista tareas de la cola |
| GET | `/admin/tasks/stats` | Estadísticas (pending/running/done/failed) |
| POST | `/admin/tasks/run` | Procesa tareas pendientes (llamado por cron) |
| POST | `/admin/tasks/enqueue` | Encola tarea manualmente |

### Discovery & Mapping
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/discovery/sources` | Lista fuentes de datos de la empresa |
| POST | `/discovery/sources` | Crear fuente de datos |
| PATCH | `/discovery/sources/{id}` | Actualizar fuente de datos |
| DELETE | `/discovery/sources/{id}` | Desactivar fuente (soft delete) |
| POST | `/discovery/sources/{id}/scan` | Ejecutar escaneo automático |
| POST | `/discovery/sources/{id}/scan/manual` | Escaneo manual (el usuario provee columnas) |
| GET | `/discovery/sources/{id}/runs` | Listar escaneos de una fuente |
| GET | `/discovery/runs/{id}` | Detalle de un escaneo (findings + sugerencias) |
| GET | `/discovery/runs/{id}/gaps/export` | Exportar gaps sin RAT a CSV |
| PATCH | `/discovery/findings/{id}/vincular-rat` | Vincular hallazgo a RAT o marcar descartado |

---

## RBAC por módulo — reglas críticas

Estas reglas fueron auditadas y corregidas. **No modificar sin revisar el código correspondiente.**

| Módulo | Endpoint | Rol mínimo requerido |
|--------|----------|---------------------|
| RATs | GET (listar/detalle) | cualquier rol autenticado con acceso a empresa |
| RATs | POST / PUT / DELETE / archivar / clonar / aprobar | `editor` o `admin` per-empresa (bloquea `viewer`) |
| Brechas | GET (listar) | cualquier rol |
| Brechas | POST / PUT / DELETE / evaluar-riesgo | `admin_empresa` o `superadmin` (bloquea `usuario` global) |
| Consentimientos | GET | cualquier rol |
| Consentimientos | POST (crear) / POST (revocar) | bloquea `usuario` global |
| EIPD | GET (listar / detalle) | cualquier rol con acceso a empresa |
| EIPD | POST (crear) / PUT (actualizar) | `editor` o `admin` per-empresa (bloquea `viewer`) |
| Contratos encargado | GET | cualquier rol con acceso a empresa |
| Contratos encargado | POST / PUT / DELETE | `editor` o `admin` per-empresa (bloquea `viewer`) |
| TKT tickets | GET (listar/detalle) | cualquier rol con acceso a empresa |
| TKT tickets | POST notas | bloquea `usuario` global |
| TKT reglas asignación | GET | `admin_empresa` o `superadmin` (bloquea `usuario`) |
| TKT reglas asignación | POST / PUT / DELETE | misma restricción + valida `company_id` destino (anti-IDOR) |
| Discovery | GET (sources/runs/findings) | cualquier rol con acceso a empresa |
| Discovery | POST / PATCH / DELETE (sources, scan, vincular) | `editor` o `admin` per-empresa (bloquea `viewer`) |
| Empresas | GET | cualquier rol con acceso |
| Empresas | POST | `superadmin` |
| Empresas | PUT / PATCH desactivar | `editor` o `admin` per-empresa |
| Empresas | DELETE | `superadmin` |
| Rubros | GET | cualquier rol autenticado |
| Rubros | POST / PUT / DELETE | `superadmin` |
| Accesos empresa | todos | `admin` per-empresa o `superadmin` |
| Política transparencia | GET público | sin autenticación (rate-limited) |
| Política transparencia | PUT | `admin_empresa` o `superadmin` |
| ARCO público | GET /publico/* | sin autenticación (rate-limited, CSRF en POST) |
| Admin tareas | todos | `superadmin` |

### Función RBAC canónica por tipo de check

```python
# Verifica solo acceso a empresa (lectura)
check_company_access(current_user, company_id, db)

# Verifica que no sea VIEWER per-empresa (escritura en módulos de datos)
require_editor_or_admin_empresa(company_id, db, current_user)

# Verifica rol ADMIN per-empresa (gestión de usuarios)
_require_company_admin(db, current_user, company_id)

# Verifica superadmin global
require_admin(current_user)  # como Depends()
```

---

## Fixes de integridad / completitud (2026-09)

- **`_truthy(False)` bug** (`rat_calculations.py`): `isinstance(value, bool): return value` — booleanos `False` eran contados como "completados".
- **`evidencia_respuesta_hash`** (`tkt_solicitud_derecho.py`): se usa `data.respuesta_texto or ticket.respuesta_texto` para hashear, evitando hash vacío cuando ambos campos llegan en el mismo PATCH.
- **CSRF frontend** (`api.ts`): `getCsrfToken()` lee `data.token` (no `data.csrf_token`) del endpoint `GET /publico/csrf-token`.
- **Limits de queries**: `get_audit_logs` → `.limit(500)`, notas/historial TKT → `.limit(200/.limit(500)`, Discovery findings → `.limit(5000)`.

---

## Notas importantes

- Puerto: `8002`, URL base: `http://localhost:8002`
- Reiniciar backend: `run_server.bat` (cmd.exe, porque `&` no funciona en PowerShell)
- Base de datos: Neon PostgreSQL (todas las bases de datos son Neon)
- El usuario `admin` existente fue renombrado a `superadmin` y `jpe` a `admin_empresa`
- Para queries que filtran por empresa sin ser superadmin: usar `get_empresas_usuario(db, user_id)` que retorna lista de `company_ids`
- `get_current_user` en `routes/deps.py` extrae el usuario del token JWT
- **CORS:** se usa `ALLOWED_ORIGINS` (env var, lista blanca). Si `ENVIRONMENT=production` y no está definida, la app levanta con `RuntimeError`
- **Email:** si `SMTP_URL` (o `SMTP_HOST` legacy) no está configurado, opera en modo DRY_RUN (loguea sin enviar)
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

### REGLA INVIOLABLE: Tests contra PostgreSQL (Neon QA)

**Los tests DEBEN ejecutarse contra PostgreSQL (Neon QA)** antes de cualquier deploy.

### Setup

```bash
cd backend

# 1. Crear/resetear BD de test en Neon QA
python reset_test_db.py

# 2. Ejecutar TODOS los tests contra PostgreSQL
python -m pytest tests/ -v

# 3. Ejecutar solo tests ARCO (más rápido para desarrollo iterativo)
python -m pytest tests/test_arco_tickets.py \
  tests/test_subsanacion.py tests/test_prorroga.py \
  tests/test_qw8_seguimiento.py tests/test_qw10_formulario.py \
  tests/test_plantillas.py tests/test_reglas_asignacion.py \
  tests/test_hash_chain.py -v
```

### BD de test

- **Host:** Neon QA (`ep-fragrant-wildflower-apeqosx9-pooler.c-7.us-east-1.aws.neon.tech`)
- **Database:** `custodio_test` (aislada, no afecta prod ni QA)
- **Connection:** configurable via `TEST_DATABASE_URL` env var
- **Schema:** creado desde modelos Python (equivalente a ejecutar todas las migraciones)

### Pre-deploy checklist

1. `python reset_test_db.py`
2. `python -m pytest tests/ -v`
3. Si hay cambios de schema: ejecutar migraciones en Neon QA manualmente
4. Commit + push
5. Verificar deploy en Vercel

Los tests couvren: CRUD RAT, completitud, dashboard stats, auth, brechas, auditoría, exportación, ARCO completo.
