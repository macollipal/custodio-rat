---
name: api-review
description: Revisa nuevos endpoints antes de deploy. Valida seguridad, compliance Ley 21.719, performance, dokumentacion y adherence al REST standard del proyecto.
---

# API Review Validator

Especialista en revisión de endpoints REST antes de deploy. Asegura que cada nuevo endpoint cumpla con los estándares de seguridad, compliance, y arquitectura del proyecto.

## Cuando Usar Esta Skill

- Se crea un nuevo endpoint en `backend/app/routes/`
- Se modifica un endpoint existente con cambios significativos
- Se prepara un PR con cambios de API
- Se solicita code review de un endpoint

## Checklist de Revisión

### 1. Seguridad

#### Autenticación y Autorización
- [ ] Endpoint tiene `Depends(get_current_user)` si requiere auth
- [ ] Validación de rol correcta (SUPERADMIN / ADMIN_EMPRESA / USUARIO)
- [ ] No hay bypass de autenticación (ENDPOINTS PÚBLICOS deben ser explícitos)

#### Isolation Multi-Tenant
- [ ] Queries filtran por `company_id` del usuario
- [ ] No se confía en `company_id` del request body
- [ ] Validar que el recurso pertenezca a la empresa del usuario

#### Validación de Inputs
- [ ] Schema Pydantic definido (BaseModel o similar)
- [ ] Validación de tipos en todos los campos
- [ ] Validación de longitud máxima en strings
- [ ] No se usa `exclude_none=True` en responses (oculta campos requeridos)
- [ ] SQL injection: usar SQLAlchemy ORM, nunca concatenar strings en queries

#### Datos Sensibles
- [ ] No se expone `hashed_password` en response
- [ ] No se expone información innecesaria en logs
- [ ] Secrets en headers de respuesta → ERROR CRÍTICO

### 2. Compliance Ley 21.719

#### Trazabilidad
- [ ] Operaciones sensibles invocan `log_audit()`
- [ ] Campos de auditoría (`created_by`, `updated_by`) se setean correctamente
- [ ] Timestamps con timezone (`datetime.now(timezone=True)`)

#### Consentimientos (Art. 12)
- [ ] Si el endpoint crea/modifica datos que requieren consentimiento, validar que existe consentimiento activo
- [ ] Revocar consentimiento debe reflejarse en próximos queries

#### RATs
- [ ] Si el endpoint modifica un RAT, validar completitud del registro
- [ ] Si el RAT tiene `datos_sensibles = True`, verificar EIPD

### 3. Performance

#### Consultas a BD
- [ ] No hay N+1 queries (usar `joinedload` para relaciones)
- [ ] Paginación en endpoints de lista (> 100 registros = paginar)
- [ ] Índices adecuados (`index=True` en ForeignKeys y campos filtrados)

#### Tiempo de Respuesta
- [ ] Operaciones pesadas (> 1s) deberían ser async o en background
- [ ] No hacer sync I/O en endpoint que bloquee el event loop

### 4. REST Standards

#### Naming
- [ ] Route en kebab-case plural: `/security-breaches` no `/security_breach`
- [ ] Verbos HTTP correctos:
  - GET → retrieve (no modifica estado)
  - POST → create
  - PUT → full update
  - PATCH → partial update
  - DELETE → delete
- [ ] Código de estado HTTP correcto:
  - 200 OK
  - 201 Created
  - 400 Bad Request (validación)
  - 401 Unauthorized (no auth)
  - 403 Forbidden (auth pero sin permisos)
  - 404 Not Found
  - 422 Unprocessable Entity (schema validation)

#### Response Format
```python
# Correcto: schema con response_model
@router.get("/{id}", response_model=SolicitudDerechoOut)
# Incorrecto: retornar dict sin schema
```

### 5. Documentación

#### Docstrings
- [ ] Docstring en función del endpoint describiendo propósito
- [ ] Comentario con Art. de la ley si aplica

#### OpenAPI/Swagger
- [ ] Tags definidos para agrupar endpoints
- [ ] Descripción en docstring visible en /docs

### 6. Tests

- [ ] Test de auth (sin token → 401)
- [ ] Test de autorización (usuario wrong company → 403)
- [ ] Test de validación (payload inválido → 400)
- [ ] Test de éxito (payload válido → 200/201)
- [ ] Tests contra PostgreSQL (Neon QA), no SQLite

## Reporte de API Review

```
## API Review Report

**Endpoint:** {metodo} /{ruta}
**Archivo:** backend/app/routes/{archivo}.py:{linea}

### Seguridad
| Check | Estado |
|-------|--------|
| Auth requerida | :green_circle: / :red_circle: |
| Validación company_id | :green_circle: / :red_circle: |
| Schema Pydantic | :green_circle: / :yellow_circle: |
| SQL Injection | :green_circle: / :red_circle: |
| Exposición secrets | :green_circle: / :red_circle: |

### Compliance
| Check | Estado |
|-------|--------|
| Audit log | :green_circle: / :yellow_circle: |
| Timestamps TZ | :green_circle: / :red_circle: |
| Consentimiento | :green_circle: / :yellow_circle: / N/A |

### Performance
| Check | Estado |
|-------|--------|
| No N+1 | :green_circle: / :yellow_circle: |
| Paginación | :green_circle: / :yellow_circle: / N/A |

### REST
| Check | Estado |
|-------|--------|
| Naming | :green_circle: / :red_circle: |
| HTTP status | :green_circle: / :red_circle: |
| response_model | :green_circle: / :yellow_circle: |

### Tests
| Check | Estado |
|-------|--------|
| auth test | :green_circle: / :red_circle: |
| 403 test | :green_circle: / :red_circle: |
| validation test | :green_circle: / :red_circle: |
| success test | :green_circle: / :red_circle: |

### Score
SEGURIDAD: {n}/5
COMPLIANCE: {n}/3
PERFORMANCE: {n}/2
REST: {n}/3
TESTS: {n}/4
**TOTAL: {n}/17**

### Comments
{comentarios}

### Acciones Requeridas
1. [ ] Agregar Depends(get_current_user)
2. [ ] Agregar response_model
...
```

## Reglas de Aprobación

Para que un endpoint sea aprobado:
- Seguridad: 5/5 (bloqueante)
- Compliance: 3/3 (bloqueante)
- REST: 2/3 mínimo
- Tests: 3/4 mínimo

Si hay FALLA en cualquier check de Seguridad → RECHAZO TOTAL
