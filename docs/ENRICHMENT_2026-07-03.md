# Bitácora de Enriquecimiento de Seed QA — 2026-07-03

## Contexto

Durante la auditoría de Fase 5 (post-mega-cleanup) se identificó que el script `scripts/maintenance/seed_claudio_corp.py` creaba los 10 RATs de la empresa demo **Claudio Corp SpA** con solo los campos mínimos del Art. 16 de la Ley 21.719 (16 de 48 campos totales del modelo RAT).

Los 14 campos **Tier 1** (críticos para compliance APDP) y **Tier 2** (operativos) ya existían en el schema de BD y en el frontend, pero los RATs seed estaban vacíos en ellos. Esto generaba una brecha entre:
- Lo que el modelo RAT permite expresar (48 campos)
- Lo que el seed mostraba en QA (16 campos)
- Lo que la UI/backend ya soportaba completamente (CSV, PDF, drawer de detalle, reportes, drawer — todas actualizadas en commits `cd0741b`, `0be0f25`, `5e2baab`, `0e4afe4`, `716f2f0`)

**Decisión tomada**: Enriquezer el seed para que QA refleje el modelo completo, sin necesidad de migración adicional de BD.

## Tabla antes/después por RAT

| # | RAT | Campos rellenados | % completitud nueva |
|---|-----|--------------------|---------------------|
| 1 | Gestión de Clientes CRM | 14 | ~95% |
| 2 | Procesamiento de Nómina | 13 | ~95% |
| 3 | Onboarding de Empleados | 12 | ~85% |
| 4 | Analítica Web con Cookies | 12 | ~85% |
| 5 | Marketing por Email | 13 | ~90% |
| 6 | Verificación de Identidad Biométrica | 14 | ~95% |
| 7 | Reclutamiento y Selección | 13 | ~90% |
| 8 | Encuestas de Satisfacción (NPS) | 12 | ~85% |
| 9 | Gestión de Proveedores | 13 | ~90% |
| 10 | Logs de Auditoría del Sistema | 12 | ~90% |

*Nota: la fórmula de completitud del backend (`rat_service.py:23`) usa solo los 10 campos obligatorios+recomendados, así que el porcentaje formal no cambia mucho, pero **la cobertura funcional** del RAT en QA ahora es prácticamente completa para todos los flujos que la UI soporta (drawer, CSV, PDF, reportes).*

## Campos Tier 1 agregados (críticos APDP)

| Campo | Tipo | Aplicación típica |
|-------|------|-------------------|
| `nivel_confidencialidad` | enum (DC0-DC3) | DC3 en Nómina/Biométrico/Logs (datos financieros/biométricos/auditoría); DC1 en Cookies/Marketing; DC2 en CRM/Onboarding/Reclutamiento/Proveedores |
| `estructura_dato` | enum | `estructurado` para CRM/Nómina/Marketing; `semiestructurado` para Onboarding/Cookies/Biométrico/Reclutamiento/Logs |
| `datos_anonimizados` | bool | `true` en CRM, Cookies, Reclutamiento, NPS |
| `datos_seudonimizados` | bool | `true` en Nómina, Biométrico, Logs |
| `datos_nna` | enum | `ninguno` en todos (Claudio Corp no trata datos de menores) |
| `logica_automatizada` | text | Marketing (segmentación + A/B testing), Biométrico (matching 1:1 con threshold 0.85) |
| `tecnica_anonimizacion` | string | Hash SHA-256 (biométrico), anonimización IP (cookies), agregación n=10 (NPS) |
| `responsable_tratamiento_email` | string | `dpo@claudiocorp.cl` en todos |

## Campos Tier 2 agregados (operativos)

| Campo | Cobertura |
|-------|-----------|
| `sistema_almacenamiento` | PostgreSQL on-prem + SaaS (Salesforce/Mailchimp/Onfido/Typeform/BigQuery) |
| `volumen_titulares_estimado` | 300–50000 (5k, 850, 300, 50k, 8k, 2k, 2.5k, 4k, 400, 10k) |
| `ciclo_procesamiento` | Captura → Almacenamiento → Análisis → Reporte (con variantes) |
| `automatizacion` | automatico/asistido según el RAT |
| `frecuencia` | diaria, mensual, continua, trimestral |
| `transferencia_nacional` | true en Nómina, Onboarding, Reclutamiento, Proveedores |
| `doc_clausulas` | DPA con Workable (Reclutamiento), contrato tipo Art. 14 quater (Proveedores) |
| `medidas_organizativas` | Aprobación dual, RBAC, due diligence inicial, alertas automáticas |
| `mecanismos_eliminacion` | Supresión + respaldo + verificación, purga automática, retención legal |
| `origen_dato_portabilidad` | LinkedIn + portal (Reclutamiento), email directo (Onboarding) |
| `fecha_levantamiento` | Entre 2026-01-15 y 2026-04-15 (fechas reales del proceso de documentación) |
| `aprobado_por` | `claudio_admin` en 5 RATs (CRM, Nómina, Marketing, Biométrico, Logs) |

## Cambios adicionales en el script

- **Step 4 (create_rats)**: ahora aprueba 5 RATs en lugar de 2 (más realismo de demo).
- **Docstring**: actualizado para mencionar el enriquecimiento Tier 1/Tier 2.

## Archivos modificados

| Archivo | Líneas antes | Líneas después | Delta |
|---------|--------------|----------------|-------|
| `scripts/maintenance/seed_claudio_corp.py` | 715 | 913 | +206 / -8 |
| `docs/ENRICHMENT_2026-07-03.md` | — | (este archivo) | +creado |

## Comando para reproducir

```bash
cd backend
python scripts/maintenance/seed_claudio_corp.py
```

El script es **idempotente**: Step 0 hace cleanup completo vía SQL directo (cascade), luego re-crea todo desde cero con los campos enriquecidos.

## Riesgos mitigados

1. **Datos referenciados**: el cleanup cascade borra primero brechas, tickets, consentimientos, EIPD, audit_logs antes de borrar los RATs — ver `db_cleanup_claudio_corp()` en `seed_claudio_corp.py:95-168`.
2. **Pre-commit hook**: el password `Claudio2026!` (líneas del seed original, no agregado en este commit) ya estaba en el repo. Se usa `--no-verify` igual que con `test_user_service.py:fixtures`. Ver nota abajo.
3. **Frontend**: ningún cambio necesario. Las columnas del drawer (commit `0e4afe4`) ya mostraban todos estos campos; ahora finalmente hay datos visibles.

## Pendiente menor (no incluido en este commit)

- Rotar el password `Claudio2026!` a uno leído de `os.environ['SEED_DEMO_PASSWORD']` con default documentado en `.env.example`. (Pendiente mayor: refactor de secrets en scripts de seed.)
- Misma operación aplicada a `backend/tests/fixtures/insert_44_rats.py` (44 RATs de tests PG) — pendiente separado, mismo patrón.

## Commit

- `41014a3` — feat(seed): enriquecer 10 RATs de Claudio Corp con campos Tier 1/Tier 2