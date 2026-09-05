# STATUS — Custodio RAT Manager

> **Fuente canonica de estado actual del proyecto.**
> Actualizar tras cada auditoria (`docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/`).

## Estado Actual

| Campo | Valor |
|---|---|
| **Version** | v1.9 (docs) / v1.10 (docs API + CU) |
| **Fecha** | 2026-08-24 |
| **Score Arquitectonico** | **7.8/10** (RAT: 9.0/10) |
| **Delta vs v1.8** | +1.0 (gracias a auditoria RAT 2026-07-07) |
| **RAT** | **9.0/10** ✅ (auditoria detallada 2026-07-07) |
| **ARCO** | 8.0/10 (QW6/7/8 + formulario público completo + acuse recibo) |
| **Brechas** | 7.5/10 (auto-cálculo nivel_riesgo, recalculo en update) |
| **Compliance** | **Art. 11, 12, 13, 14 bis, 14 ter, 14 quater, 15 bis, 16, 19, 28** cubiertos |
| **Madurez** | Produccion Inicial → candidato a **Produccion Empresarial** |
| **Branch** | `qa` |
| **Ultima auditoria formal** | [2026-08-22_auditoria_qa_tests](auditorias/2026-08-22_auditoria_qa_tests/AUDITORIA_QA_TESTS.md) |
| **Ultimo trabajo** | 2026-08-24 — QW5 formulario público (titular repetido), docs sync |
| **Ultima sesion** | 2026-08-24 — QW5 titular repetido; CI fixes (APDP, vitest E2E, WCAG, ruff, pip-audit); ARCO-QW6/7/8; Empresas-QW6 |
| **Administrador IA** | Claude Code (claude-sonnet-4-6) desde 2026-08-07 |

## Documentacion Vigente

Ver: [documentacion_oficial/README.md](documentacion_oficial/README.md)

- 7 documentos v1.9 (02, 03, 06, 09, 10, 12, MTX).
- **2 documentos v1.10** regenerados tras auditoria RAT detallada:
  - `04_Casos_de_Uso_v1.10.docx` (25 CUs, antes 14 en v1.9)
  - `08_API_REST_v1.10.docx` (20 endpoints, antes 6 en v1.9)

**Pendiente**: regenerar los 7 docs v1.9 a v1.10 (con código actualizado al 2026-07-18).
Ver [`auditorias/2026-07-18_auditoria_doc_drift.md`](auditorias/2026-07-18_auditoria_doc_drift.md).

### Documentacion adicional reciente (2026-07-13 → 2026-07-18)

- **`manual/README.md`** (raíz): manual para clientes no-técnicos, lenguaje claro, ejemplos reales.
- **`manual/como_se_conectan_los_modulos.md`**: diagrama + 4 flujos típicos.
- **`LEVANTAMIENTO_2026-07-18.md`** (raíz): informe detallado con 4 auditorías especializadas.
- **`docs/despliegue/RUNBOOKS/DR_TEST_RUNBOOK.md`**: runbook DR con RTO<4h, RPO<1h.
- **`SESSION_HANDOFF.md`**: handoff de sesión (formato estandarizado).

## Pendientes Tecnicos Z-

| ID | Descripcion | Prioridad | Estado | Notas |
|---|---|---|---|---|
| **Z-01** | Security headers (CSP, X-Frame-Options) | Media | **Cerrado** ✅ | `backend/app/main.py:145-167` — CSP, X-Frame-Options, HSTS, etc. Tests 6/6 |
| **Z-02** | CORS restrictivo por ruta | Baja | **Cerrado** ✅ | `CORSByPathMiddleware` — rutas `/publico/*` aceptan `*`, privadas solo `ALLOWED_ORIGINS`. 16 tests. Commit 2026-08-23 |
| **Z-03** | File upload validation tipo MIME | Media | **Cerrado** ✅ | Magic bytes en `rat_file._validate_magic_bytes()`. Commit `fe127b5` |
| **Z-04** | `categoria_titulares NOT NULL` | Alta | **Cerrado v1.9** ✅ | Commit `b776cb9` + migration `2026_07_05_001` |
| **Z-06** | Logs estructurados JSON / audit_log table | Media | **Cerrado** ✅ | `JSONFormatter` activo en ENVIRONMENT=production/qa/staging. `audit_logs` en BD con hash chain. Commit previo. |

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

### Sprint 2026-07-08 a 2026-07-13 (Sesión homologación UX + QW4)

| Hallazgo | Tipo | Descripcion |
|---|---|---|
| H3.5 | Backend Code | BASES_LEGALES deduplicado — 1 endpoint + 5 componentes frontend migrados |
| H3.12 | Backend Code | 4 endpoints de export refactorizados con helper DRY |
| Z-03 | Security | Magic bytes validation PDF/JPEG/PNG/GIF en file uploads |
| Z-01 | Security | Security headers (verificado — ya estaba implementado) |
| Homologación UX | Frontend UX | 7 componentes átomo creados + 25+ archivos migrados a `<Button>` |
| QW4 ARCO | Feature | Dashboard "Derechos más ejercidos" (por_tipo) — backend + frontend + tests |
| a11y axe-core | Quality | Login page sin violaciones críticas/serias; nuevo `e2e/19-axe-a11y.spec.ts` |
| WCAG Touch targets | A11y | Botones con `min-h-[44px]` (default en componente Button) |
| WCAG Hover handlers | A11y | Eliminados `onMouseEnter/onMouseLeave` (mobile funcional) |

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

1. ✅ Crear carpeta `manual/` para clientes no-técnicos
2. ✅ Implementar QWs del backlog (Empresas-QW6, ARCO-QW6/7/8, Público-QW1/3/4/5/9) — 9/13 pendientes cerrados
3. ✅ Cerrar **Z-02** (CORS restrictivo) — `CORSByPathMiddleware` activo
4. Actualizar documentos oficiales (.docx) a v1.10 — ver `docs/documentacion_oficial/README.md`
5. Continuar remediacion RAT — ver [PLAN_REMEDIACION.md](auditorias/2026-07-07_auditoria_rat_detalle/PLAN_REMEDIACION.md)

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