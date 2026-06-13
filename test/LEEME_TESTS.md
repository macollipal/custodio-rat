# Tests — Custodio RAT Manager

## Ejecutar todos los tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

## Ejecutar solo tests P0 (nuevos)

```bash
cd backend
python -m pytest tests/test_hash_chain.py tests/test_arco_tickets.py tests/test_rbac_deep.py -v
```

## Ejecutar con coverage

```bash
cd backend
python -m pytest tests/ --cov=app --cov-report=html
```

Abrir: `backend/htmlcov/index.html`

## Tests existentes (baseline)

- `test_auth.py` — Login, logout, JWT
- `test_rats.py` — CRUD RAT
- `test_companies.py` — CRUD Empresas
- `test_dashboard.py` — Dashboard y auditoría
- `test_security.py` — RBAC, IDOR, token blacklist
- `test_exports.py` — CSV y PDF
- `test_riesgo_razonable.py` — Brechas y reportabilidad
- `test_bloqueo_temporal.py` — Bloqueo y portabilidad
- `test_arco_tickets.py` — Tickets ARCO (nuevo)
- `test_hash_chain.py` — Hash chain auditoría (nuevo)
- `test_rbac_deep.py` — RBAC profundo (nuevo)

## Fallos conocidos (no resolver en esta sesión)

1. `/health` endpoint no existe → 2 tests fallan
2. Import `engine_test` en `test_csv_export_sanitizes_all_cells` → 1 test falla

## Gaps de seguridad documentados (skipped)

- `test_admin_empresa_no_puede_crear_rat_en_empresa_ajena` → `/rats` no verifica rol global
- `test_usuario_no_puede_crear_brecha` → `/brechas` no verifica rol global

##Último resultado

```
Total: 216 tests
Passed: 211 (97.7%)
Failed: 3 (pre-existentes)
Skipped: 2 (security gaps documentados)
```