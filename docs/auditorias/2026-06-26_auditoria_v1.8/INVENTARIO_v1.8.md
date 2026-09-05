# Inventario v1.8 — 2026-06-26

## Archivos Iter 11 (15 Campos Tier 1+Tier 2)

### Nuevos
| Archivo | Descripción |
|---------|-------------|
| `backend/migrations/2026_06_25_012_rat_tier1_tier2.sql` | Migración idempotente con COMMENT |
| `backend/tests/test_rat_tier1_tier2.py` | 9 tests de paridad Pydantic↔TS |

### Modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/models/rat.py` | 15 columnas nuevas + LargeBinary(10_000_000) |
| `backend/app/schemas/rat.py` | 15 campos en RATBase, RATUpdate, RATOut + Field(min_length=50) para test_IL |
| `frontend-next/types/index.ts` | 15 campos en RAT + RATWizardData |
| `frontend-next/lib/constants.ts` | 6 constantes nuevas con tooltips |
| `frontend-next/components/rat/RatWizard.tsx` | Paso 5 (Tier 1+Tier 2) + aria-required + tooltip accesible |
| `frontend-next/components/rat/RatDetailView.tsx` | Renderiza los 15 campos |
| `frontend-next/components/rat/RatEditForm.tsx` | Paso 5 completo + aria-required + AlertBanner Test IL |

## Archivos Iter 12 (9 Fixes CRÍTICOS+ALTOS)

### Modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/models/tkt_adjunto.py` | LargeBinary(10_000_000) |
| `backend/app/models/tkt_solicitud_derecho.py` | CausalRechazo enum |
| `backend/app/schemas/tkt_solicitud_derecho.py` | CausalRechazoEnum literal |
| `backend/app/routes/tkt_solicitud_derecho.py` | Hash SHA-256 auto + validación evidencia HTTP 400 |
| `backend/app/services/breach_service.py` | Notificaciones APDC + titulares automatizadas |
| `frontend-next/app/solicitud_derecho/page.tsx` | Toggle 44x44px |
| `frontend-next/components/tkt/TicketDrawer.tsx` | Dropdown causal_rechazo + toast error |

### Nuevos
| Archivo | Descripción |
|---------|-------------|
| `backend/migrations/2026_06_26_013_bytea_limit_10mb.sql` | CHECK constraints 10MB |

## Scripts de Build v1.8

| Script | Doc | Estado |
|--------|-----|--------|
| `build_02_requisitos_v1_8.py` | 02 | ✅ |
| `build_03_historias_usuario_v1_8.py` | 03 | ✅ |
| `build_04_casos_uso_v1_8.py` | 04 | ✅ |
| `build_06_arquitectura_v1_8.py` | 06 | ✅ |
| `build_08_api_v1_8.py` | 08 | ✅ |
| `build_09_backlog_v1_8.py` | 09 | ✅ |
| `build_10_plan_qa_v1_8.py` | 10 | ✅ |
| `build_12_manual_tecnico_v1_8.py` | 12 | ✅ |
| `build_MTX_matriz_v1_8.py` | MTX | ✅ |

## Dependencias

Ninguna nueva (no se agregaron paquetes).
