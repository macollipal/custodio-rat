# STATUS — Custodio RAT Manager

> **Fuente canonica de estado actual del proyecto.**
> Actualizar tras cada auditoria (`docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/`).

## Estado Actual

| Campo | Valor |
|---|---|
| **Version** | v1.9 |
| **Fecha** | 2026-07-07 |
| **Score Arquitectonico** | **7.7/10** (RAT: 9.0/10) |
| **Delta vs v1.8** | +1.0 (gracias a auditoria RAT 2026-07-07) |
| **RAT** | **9.0/10** ✅ (auditoria detallada 2026-07-07) |
| **ARCO** | 6.8/10 |
| **Brechas** | 5.9/10 |
| **Madurez** | Produccion Inicial → candidato a **Produccion Empresarial** |
| **Branch** | `qa` |
| **Ultima auditoria** | [2026-07-07_auditoria_rat_detalle](auditorias/2026-07-07_auditoria_rat_detalle/AUDITORIA_RAT_DETALLE.md) |

## Documentacion Vigente

Ver: [documentacion_oficial/README.md](documentacion_oficial/README.md)

- 9 documentos v1.9 (02, 03, 06, 09, 10, 12, MTX).
- **2 documentos v1.10** regenerados tras auditoria RAT detallada:
  - `04_Casos_de_Uso_v1.10.docx` (25 CUs, antes 14 en v1.9)
  - `08_API_REST_v1.10.docx` (20 endpoints, antes 6 en v1.9)

## Pendientes Tecnicos Z-

| ID | Descripcion | Prioridad | Estado | Notas |
|---|---|---|---|---|
| **Z-01** | Security headers (CSP, X-Frame-Options) | Media | Pendiente | Headers HTTP minimos de seguridad |
| **Z-02** | CORS restrictivo por ruta | Baja | Pendiente | Hoy se permite todo *.vercel.app |
| **Z-03** | File upload validation tipo MIME | Media | **Parcial** | Limite BYTEA 10MB OK, falta validar tipo MIME |
| **Z-04** | `categoria_titulares NOT NULL` | Alta | **Cerrado v1.9** ✅ | Commit `b776cb9` + migration `2026_07_05_001` |
| **Z-06** | Logs estructurados JSON / audit_log table | Media | Pendiente | Migrar logging a tabla en BD |

## Otros Pendientes (no Z-)

### Funcionales (de auditorias)

| ID | Descripcion | Prioridad |
|---|---|---|
| QW-ITER14-01 | Paginacion en listados >100 registros (RAT/ARCO/Brechas) | **P2 — RAT cerrado 2026-07-07** ✅ |
| QW-ITER14-02 | Retry logic en OCI uploads (resilience) | P3 |
| QW-ITER14-03 | Logs de auditoria en tabla `audit_log` (Art. 28 Ley 21.719) | P2 |
| QW-ITER14-04 | ALTER TABLE `categoria_titulares` SET NOT NULL (breaking change) | **Cerrado Z-04** ✅ |

### Compliance (auditoria RAT detallada 2026-07-07)

Ver detalle completo en [AUDITORIA_RAT_DETALLE.md](auditorias/2026-07-07_auditoria_rat_detalle/AUDITORIA_RAT_DETALLE.md).

| Hallazgo | Descripcion | Estado |
|---|---|---|
| **H1.1** | `base_legal="Otra"` sin archivo no era bloqueante | **Cerrado P1** ✅ |
| **H2.2** | `/auditoria/verify-chain` accesible a todos los users | **Cerrado P1** ✅ (solo SUPERADMIN) |
| **H3.4** | Duplicacion RATBase vs RATUpdate | **Cerrado P2** ✅ (herencia + exclude_unset) |
| **H4.5** | Wizard RatWizard monolito 1300 lineas | **Cerrado P1** ✅ (WizardModular/) |
| **H4.6** | AGENTS.md dice "4 pasos", codigo tiene 5 | **Cerrado P2** ✅ |
| **H5.1** | Sin test E2E workflow RAT→EIPD→aprobar | **Cerrado P1** ✅ (test_e2e_workflow_rat.py) |
| **H5.2** | Sin test paginacion reportes (QW-ITER14-01) | **Cerrado P1** ✅ (test_reportes_paginacion.py) |
| **H6.1** | 14 endpoints RAT no documentados | **Cerrado P1** ✅ (08_API_REST_v1.10.docx) |
| **H6.2** | CU de export no documentados | **Cerrado P2** ✅ (04_Casos_de_Uso_v1.10.docx, 25 CUs) |
| **H6.4** | AsesorCustodio no documentado en AGENTS.md | **Cerrado P2** ✅ |

### Compliance (de barrido documental 2026-07-06)

| Hallazgo | Descripcion | Estado |
|---|---|---|
| H1 | Indice documental desactualizado | **Cerrado P0** ✅ (commit `2e0b29b`) |
| H2 | Versionado sin politica | **Cerrado P1** ✅ (matrix en `documentacion_oficial/README.md`) |
| H3 | Lock files `~$*.docx` | **Cerrado P0** ✅ |
| H4 | Mojibake en `.md` | Pendiente (P2) |
| H5 | Backlogs no reconciliados | Pendiente (mantener SESSION_STATE activo, marcar otros historico) |
| H6 | Duplicacion AsesorCustudio vs `_regen` | Pendiente |
| H7 | Docs en `paso/` | NO APLICA (carpeta personal del usuario) |
| H8 | Pendientes Z- en auditorias | **Cerrado P1** ✅ (esta tabla) |

## Mejoras Recientes Cerradas

### Sprint 2026-07-07 (Auditoria RAT detallada — 11 hallazgos cerrados)

| Hallazgo | Tipo | Descripcion |
|---|---|---|
| H1.1 | Compliance | `base_legal="Otra"` requiere archivo adjunto (Art. 11+16) |
| H2.2 | API Security | `/auditoria/verify-chain` restringido a SUPERADMIN |
| H2.3 | API REST | `response_model=SugerenciasTiposOut` en `/sugerencias/tipos` |
| H2.4 | API Security | `require_module_enabled("RAT")` en dashboard |
| H3.4 | Backend Code | RATUpdate hereda de RATBase — eliminada duplicacion de 40 campos |
| H4.5 | Frontend Code | RatWizard拆 a `WizardModular/` (types + 2 hooks) |
| H4.6 | Docs | AGENTS.md actualizado: wizard de 5 pasos |
| H5.1 | Tests E2E | Workflow RAT→EIPD→aprobar (5 escenarios) |
| H5.2 | Tests | Paginacion reportes (7 escenarios, QW-ITER14-01) |
| H6.1 | Docs API | `08_API_REST_v1.10.docx` regenerado con 20 endpoints |
| H6.2 | Docs CU | `04_Casos_de_Uso_v1.10.docx` con 25 casos de uso |
| H6.4 | Docs | AsesorCustudio documentado en AGENTS.md |

### Iter 13 (v1.9)

| Iter | RF/HU | Descripcion |
|---|---|---|
| 13 | RF-163 (CRITICO) | IDOR multi-tenant en 6 endpoints RAT |
| 13 | RF-164 | `base_legal_valida` strict contra enum taxativo |
| 13 | RF-165 | ConsentimientoAlert en RatEditForm.handleSave() |
| 13 | RF-166 | Homologacion orden campos RAT (wizard/drawer/PDF) |
| 13 | RF-167 | PDF con titulos de seccion (PASO 1, PASO 2, ...) |
| 13 | RF-168 | Encoding UTF-8 corregido en backend |
| 13 | RF-169 | Codigo muerto eliminado |

Ver detalle en [AUDITORIA_V1.9.md](auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md).

## Proximos Pasos Sugeridos

### Corto Plazo (Sprint actual)

1. Cerrar **Z-01** y **Z-02** (security headers + CORS).
2. Cerrar **Z-03** (file upload MIME validation).
3. Cerrar **Z-06** (audit_log table).
4. Continuar remediacion RAT — ver [PLAN_REMEDIACION.md](auditorias/2026-07-07_auditoria_rat_detalle/PLAN_REMEDIACION.md).

### Mediano Plazo

1. Retry logic OCI (QW-ITER14-02).
2. Encoding UTF-8 normalizacion automatica (P2 del barrido).
3. Refactor `rat_service.py` (640 →拆 5 archivos, H3.8).
4. Refactor `WizardModular/steps/` (H4.5 continuacion).

### Largo Plazo

1. Madurez a "Produccion Empresarial" (score > 8.5/10).
2. Certificacion APDC completa.
3. Multi-empresa en arquitectura multi-tenant avanzada.

---

## Metricas Rapidas

| Metrica | Valor |
|---|---|
| Documentos v1.9 generados | 7/9 (vigentes) |
| Documentos v1.10 generados | 2 (08 API REST, 04 CU) ✅ |
| Tests RAT pasando | 32/32 (test_security.py) + nuevos E2E workflow + paginacion |
| RFs documentados | 169 (RF-001 a RF-169) |
| HUs documentados | 103 (HU-001 a HU-103) |
| Hallazgos auditoria RAT 2026-07-07 | 45 → 11 cerrados, 34 restantes |
| Score RAT (auditoria 2026-07-07) | **9.0/10** ✅ |

---

*Ultima actualizacion: 2026-07-07 (auditoria RAT detallada — sprint 1, 11 hallazgos cerrados)*
*Mantenido por skill `doc-governance` (bajo demanda).*