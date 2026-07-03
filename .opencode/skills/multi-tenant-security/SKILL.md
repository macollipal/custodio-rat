---
name: multi-tenant-security
description: Valida seguridad multi-tenant en Custodio RAT. Detecta IDOR, problemas RBAC, acceso cruzado entre empresas, y vulnerabilidades de aislamiento.
---

# Multi-Tenant Security Validator

Especialista en seguridad de arquitectura multi-tenant. Detecta accesos cruzados no autorizados (IDOR), flaws en RBAC, y problemas de aislamiento entre empresas.

## Modelo de Amenaza

En Custodio RAT:
- Cada empresa (company) tiene sus propios datos: RATs, brechas, solicitudes ARCO, consentimientos
- Usuarios pueden pertenecer a una o más empresas (user_companies)
- Un usuario NUNCA debe poder ver/modificar datos de una empresa a la que no pertenece

## Vulnerabilidades a Detectar

### 1. IDOR (Insecure Direct Object Reference)

**Qué es:** Un usuario accede a recursos de otra empresa modificando el ID en la URL o request.

**Ejemplo:**
```
GET /rats/123  # 123 pertenece a empresa A
GET /rats/124  # 124 pertenece a empresa B (debería ser 403)
```

**Validación:**
- [ ] Endpoint filtra por company_id del usuario autenticado
- [ ] No se confía en company_id del request body
- [ ] company_id se extrae de la sesión/token, no del input

### 2. RBAC (Role-Based Access Control)

**Roles en Custodio RAT:**
| Rol | Alcance |
|-----|---------|
| SUPERADMIN | Todas las empresas, todo el sistema |
| ADMIN_EMPRESA | Su empresa + usuarios de su empresa |
| USUARIO | Su empresa, solo lectura de RATs |

**Validación por endpoint:**
| Endpoint | SUPERADMIN | ADMIN_EMPRESA | USUARIO |
|----------|------------|---------------|---------|
| GET /rats | Todas | Solo su company | Solo su company |
| POST /rats | Todas | Su company | NO (403) |
| PUT /rats/{id} | Todas | Solo su company | NO (403) |
| DELETE /rats/{id} | Todas | NO (403) | NO (403) |
| GET /brechas | Todas | Solo su company | Solo su company |
| POST /brechas | Todas | Su company | NO (403) |
| GET /companies | Todas | Solo su company | Solo su company |
| POST /companies | Todas | NO (403) | NO (403) |

### 3. Problemas de Aislamiento

- [ ] company_id en request body es ignorado si el usuario no es SUPERADMIN
- [ ] Queries de lista SIEMPRE filtran por company_id del usuario
- [ ] Relaciones entre entidades validan que pertenezcan a la misma empresa
- [ ] No hay endpoint público que exponga datos de empresas

### 4. Campos Sensibles a Filtrar

En respuestas de API, ciertos campos NO deben exponerse a usuarios no-admin:
- created_by de otros usuarios (no revelar estructura interna)
- hashed_password (nunca)
- company.internal_notes (si existe)
- Archivos binarios de otras empresas

## Checklist de Auditoría

### Endpoints CRUD por Entidad

#### RATs
```
GET /rats          → Filtrar por company_ids del usuario
POST /rats         → company_id debe ser una de las empresas del usuario
GET /rats/{id}     → Validar que rat.company_id ∈ empresas del usuario
PUT /rats/{id}    → Validar empresa del RAT
DELETE /rats/{id} → SUPERADMIN o ADMIN_EMPRESA de esa empresa
```

#### Brechas
```
Mismo patrón que RATs
```

#### Solicitudes ARCO
```
Mismo patrón — verificar company_id del usuario
```

#### Companies
```
GET /companies/{id} → Solo si el usuario pertenece a esa empresa
PUT /companies/{id} → ADMIN_EMPRESA de esa empresa o SUPERADMIN
```

### Casos de Prueba de IDOR

Probar acceder a estos recursos con usuario de empresa A:
```
GET /rats/{id_de_empresa_B}          → Esperado: 403
GET /brechas/{id_de_empresa_B}       → Esperado: 403
GET /solicitudes/{id_de_empresa_B}   → Esperado: 403
PUT /rats/{id_de_empresa_B}          → Esperado: 403
DELETE /rats/{id_de_empresa_B}       → Esperado: 403
```

## Reporte de Seguridad

```
## Multi-Tenant Security Audit

**Endpoint:** {ruta}
**Método:** {metodo}
**Entidad:** {entidad}

### Vulnerabilidades Encontradas

#### IDOR
:green_circle: NO / :red_circle: SÍ
Detalles: ...

#### RBAC
:green_circle: CUMPLE / :red_circle: FALLA
| Rol | Acceso esperado | Acceso real |
|-----|----------------|-------------|
| SUPERADMIN | Todas | ... |
| ADMIN_EMPRESA | Su empresa | ... |
| USUARIO | Solo lectura | ... |

#### Aislamiento
:green_circle: CUMPLE / :red_circle: FALLA

### Acciones Requeridas
1. [ ] Agregar filtro company_id en GET /rats
2. [ ] Validar company_id del request body contra sesión
```

## Reglas de Código

1. **NUNCA** confiar en `company_id` del request body para operaciones de lectura
2. **SIEMPRE** extraer `company_id` de `get_current_user()` o `get_empresas_usuario()`
3. **SIEMPRE** filtrar queries de lista por `company_id` del usuario
4. **SIEMPRE** validar que el recurso pertenezca a la empresa del usuario antes de retornar
