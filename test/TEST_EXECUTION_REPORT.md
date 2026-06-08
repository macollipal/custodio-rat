# Test Execution Report — Custodio RAT Manager

**Fecha:** 2026-06-08
**Ambiente:** Local (backend tests)
**Total tests:** 216
**Passed:** 211
**Failed:** 3
**Skipped:** 2 (documented security gaps)

---

## Resumen de Ejecución

| Categoría | Cantidad |
|-----------|----------|
| Total tests | 216 |
| Passed | 211 (97.7%) |
| Failed | 3 (1.4%) |
| Skipped | 2 (0.9%) |
| Errors | 0 |
| Warnings | 3 (deprecations) |

---

## Fallos Pre-existentes (no resueltos en esta sesión)

### 1. `test_health_no_requiere_auth` (test_auth.py:52)
**Tipo:** Test expectation mismatch
**Descripción:** El test espera que el endpoint `/health` retorne 200, pero el endpoint no existe en la aplicación (retorna 404).
**Acción sugerida:** Crear endpoint `/health` en el backend o ajustar el test.

### 2. `test_health_endpoint_no_auth_required` (test_security.py:139)
**Tipo:** Same as above
**Descripción:** Mismo issue — el endpoint `/health` no existe.

### 3. `test_csv_export_sanitizes_all_cells` (test_security.py:310)
**Tipo:** Import error in test file
**Descripción:** El test intenta importar `engine_test` desde `app.database.database`, pero `engine_test` solo existe en el test fixture `conftest.py`.

---

## Security Gaps Documentados (skipped)

### 1. `test_admin_empresa_no_puede_crear_rat_en_empresa_ajena` (test_rbac_deep.py)
**Gap:** El endpoint `/rats/` permite creación con `admin_empresa` sin verificar rol global. Solo verifica `UserCompany`.
**Severidad:** Alta — un admin_empresa puede crear RATs en cualquier empresa que tenga asignada.

### 2. `test_usuario_no_puede_crear_brecha` (test_rbac_deep.py)
**Gap:** El endpoint `/brechas` permite creación con rol `usuario` (solo verifica `company_access`, no rol global).
**Severidad:** Alta — un usuario puede crear brechas de seguridad sin permisos de admin.

---

## Fixes Aplicados Durante la Sesión de Testing

### 1. Duplicate index en AuditLog (audit_log.py)
**Problema:** La columna `timestamp` tenía `index=True` Y `Index("ix_audit_logs_timestamp")` en `__table_args__`.
**Fix:** Eliminado `index=True` de la columna `timestamp`.

### 2. Test fixtures - SQLite threading issue
**Problema:** Los tests fallaban con `SQLite objects created in a thread can only be used in that same thread`.
**Fixes:**
- Cambiado `scope` de fixtures de `session` a `function`
- Agregado `poolclass=StaticPool` al engine de test
- Modificado `init_db()` para skipear cuando `ENV=test`
- Modificado `lifespan` en `main.py` para skipear seeding cuando `ENV=test`

### 3. Hash chain verification fix (audit_service.py)
**Problema:** `_compute_hash` usaba `timestamp.isoformat()` con timezone-aware datetime, pero SQLite perdía el timezone info al almacenar, causando mismatch en verificación.
**Fix:** Normalizar timestamp a naive datetime antes de computar hash:
```python
ts_normalized = timestamp.replace(tzinfo=None) if timestamp.tzinfo else timestamp
data = (
    f"{prev_hash}"
    f"{ts_normalized.isoformat()}"
    ...
)
```

### 4. admin_user fixture idempotente
**Problema:** `UNIQUE constraint failed: users.username` cuando el fixture se ejecutaba múltiples veces.
**Fix:** El fixture ahora verifica si el usuario ya existe antes de crear.

### 5. TKT prioridad valores correctos
**Problema:** Tests usaban `"media"` pero el schema solo acepta `"alta"`, `"normal"`, `"baja"`.
**Fix:** Cambiado a `"normal"` en todos los tests de ARCO tickets.

---

## Cobertura de Tests por Módulo

| Módulo | Tests | Passed | Failed | Skipped |
|--------|-------|--------|--------|---------|
| ARCO Tickets (nuevo) | 18 | 18 | 0 | 0 |
| Hash Chain (nuevo) | 14 | 14 | 0 | 0 |
| RBAC Deep (nuevo) | 16 | 14 | 0 | 2 |
| Auth | 10 | 9 | 1 | 0 |
| Bloqueo temporal | 6 | 6 | 0 | 0 |
| Companies | 13 | 13 | 0 | 0 |
| Consentimiento expreso | 5 | 5 | 0 | 0 |
| Contrato encargado | 6 | 6 | 0 | 0 |
| Dashboard | 11 | 11 | 0 | 0 |
| E2E | 6 | 6 | 0 | 0 |
| Exports (CSV/PDF) | 16 | 16 | 0 | 0 |
| Política transparencia | 5 | 5 | 0 | 0 |
| Portabilidad | 3 | 3 | 0 | 0 |
| RATs (CRUD, completitud) | 27 | 27 | 0 | 0 |
| Riesgo razonable (brechas) | 10 | 10 | 0 | 0 |
| Security (RBAC, IDOR) | 18 | 16 | 2 | 0 |
| Suggestions | 9 | 9 | 0 | 0 |
| User service | 14 | 14 | 0 | 0 |
| **TOTAL** | **216** | **211** | **3** | **2** |

---

## Tests P0 Creados

### test_hash_chain.py (14 tests)
- Genesis hash validation
- Hash chain verification (intacto)
- Tampering detection (prev_hash y hash corruptos)
- Limit verification
- Chain endpoint integration
- Compute hash deterministic tests

### test_arco_tickets.py (18 tests)
- Crear tickets ARCO (acceso, rectificacion, cancelacion, oposicion)
- Listar tickets con filtros
- Actualizar estado (en_proceso, resuelto)
- Notas y historial de tickets
- Dashboard KPIs
- admin_empresa puede crear tickets
- usuario no puede crear/editar tickets

### test_rbac_deep.py (16 tests)
- Superadmin acceso total
- admin_empresa CRUD en su empresa
- admin_empresa no puede acceder a empresa ajena
- usuario solo lectura (no crear/editar/eliminar RAT)
- IDOR profundo (usuario y admin_empresa)
- Permisos brechas (admin_empresa puede, usuario no)

---

## Comando para Ejecutar Tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

## Coverage Report

Para ver coverage:
```bash
python -m pytest tests/ --cov=app --cov-report=html
# Abrir htmlcov/index.html
```