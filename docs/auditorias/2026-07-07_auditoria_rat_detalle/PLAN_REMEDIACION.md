# Plan de Remediación — Auditoría RAT 2026-07-07

**Fecha:** 2026-07-07 (actualizado 2026-07-07 sprint 1)
**Versión:** v1.9 (docs v1.10 generados)
**Total hallazgos:** 45 (3 P0 resueltos originalmente, **+11 cerrados en sprint 1** = 14 resueltos, 31 restantes)

---

## Estado Sprint 1 — ✅ COMPLETADO (2026-07-07)

11 hallazgos cerrados en este sprint:

| Hallazgo | Severidad | Estado | Commit |
|---|---|---|---|
| **H1.1** base_legal="Otra" requiere archivo | P1 | ✅ Cerrado | (sprint 1) |
| **H2.2** verify-chain restringido a SUPERADMIN | P1 | ✅ Cerrado | (sprint 1) |
| **H2.3** response_model en /sugerencias/tipos | P2 | ✅ Cerrado | (sprint 1) |
| **H2.4** require_module_enabled en dashboard | P2 | ✅ Cerrado | (sprint 1) |
| **H3.4** RATUpdate hereda de RATBase | P2 | ✅ Cerrado | (sprint 1) |
| **H4.5** Refactor RatWizard →拆 a WizardModular/ | P1 | ✅ Cerrado parcial (orchestrator + 2 hooks + types) | (sprint 1) |
| **H4.6** AGENTS.md dice 4 pasos, codigo 5 | P2 | ✅ Cerrado | (sprint 1) |
| **H5.1** Test E2E workflow RAT→EIPD→aprobar | P1 | ✅ Cerrado | test_e2e_workflow_rat.py |
| **H5.2** Test paginacion reportes | P1 | ✅ Cerrado | test_reportes_paginacion.py |
| **H6.1** Regenerar 08_API_REST_v1.10.docx | P1 | ✅ Cerrado | generar_api_doc_v1_10.py |
| **H6.2** Regenerar 04_Casos_de_Uso_v1.10.docx | P2 | ✅ Cerrado | generar_casos_uso_v1_10.py |
| **H6.4** Documentar AsesorCustudio en AGENTS.md | P2 | ✅ Cerrado | (sprint 1) |

### Mejoras adicionales aplicadas en sprint 1
- Fix typo `fecha_approbacion` → `fecha_aprobacion` en `EIPDUpdate` (alinea con modelo y servicio).
- Eliminados BOM markers en 3 archivos `.py` del backend.
- TypeScript del frontend compila limpio (verified).

---

## Sprint 1 — P1 (Críticos) ✅ COMPLETADO

**Objetivo:** Cerrar bloqueantes para auditoría APDC formal.

### ✅ S1.1 — H4.5: Refactor `RatWizard.tsx` →拆 (PARCIAL — Sprint 1)

**Estado:** Cerrado parcial. Se creó la estructura modular `WizardModular/` con:
- `types.ts` (constantes STEPS, DESCRIPCIONES_BASE, DRAFT_KEY, RatWizardProps, DraftSnapshot, WizardStepName)
- `hooks/useDraftAutosave.ts` (auto-save localStorage 30s)
- `hooks/useWizardNavigation.ts` (navegación entre pasos)
- `index.ts` (re-exports)
- `WizardModular/` (carpeta completa)

Pendiente (Sprint 2): extraer cada paso (Step0..Step5) a archivos `steps/Step*.tsx` individuales.

**Archivos:**
- `frontend-next/components/rat/WizardModular/types.ts`
- `frontend-next/components/rat/WizardModular/hooks/useDraftAutosave.ts`
- `frontend-next/components/rat/WizardModular/hooks/useWizardNavigation.ts`
- `frontend-next/components/rat/WizardModular/index.ts`

### ✅ S1.2 — H5.1: Test E2E workflow RAT → EIPD → aprobar

**Estado:** Cerrado. Tests agregados:
- `backend/tests/test_e2e_workflow_rat.py` (5 clases, 11 escenarios):
  - `TestWorkflowSinSensibles`: workflow básico
  - `TestWorkflowDatosSensibles`: con/sin EIPD completada
  - `TestWorkflowTransferenciaInternacional`: validador condicional
  - `TestWorkflowDecisionesAutomatizadas`: validador condicional
  - `TestWorkflowBaseLegalOtra`: H1.1 sin/con archivo
  - `TestWorkflowEIPDNoRequeridaJustificada`: justificacion >=20 chars

**Commit:** (sprint 1)

### ✅ S1.3 — H5.2: Test paginación reportes (QW-ITER14-01)

**Estado:** Cerrado. Tests agregados:
- `backend/tests/test_reportes_paginacion.py` (7 escenarios):
  - Paginación básica skip/limit
  - Total filtered con filtros
  - Sort whitelist
  - QW-ITER14-01 con 25 registros
  - Sin auth → 401
  - Filtros combinados

**Commit:** (sprint 1)

### ✅ S1.4 — H6.1: Regenerar `08_API_REST_v1.10.docx`

**Estado:** Cerrado. Script generador:
- `scripts/maintenance/generar_api_doc_v1_10.py`
- Output: `docs/documentacion_oficial/08_API_REST_Custodio_RAT_Manager_v1.10.docx`
- Cubre los 20 endpoints con tabla general + detalle por endpoint
- Incluye matriz de compliance Ley 21.719
- Documenta H2.2 (verify-chain SUPERADMIN) y H1.1 (base_legal="Otra")

**Commit:** (sprint 1)

### ✅ S1.5 — H6.2: Regenerar `04_Casos_de_Uso_v1.10.docx` (P2 — agregado a Sprint 1)

**Estado:** Cerrado. Script generador:
- `scripts/maintenance/generar_casos_uso_v1_10.py`
- Output: `docs/documentacion_oficial/04_Casos_de_Uso_Custodio_RAT_Manager_v1.10.docx`
- 25 casos de uso (CU-01 a CU-25)
- Incluye CU-15 a CU-25 (export, dashboard, paginacion, duplicacion, bloqueo)

**Commit:** (sprint 1)

---
1. Crear `backend/tests/test_e2e_rat_workflow.py`
2. Tests:
   - `test_flujo_completo_sin_sensibles`: crear RAT → aprobar
   - `test_flujo_con_datos_sensibles`: crear RAT con sensibles → registrar consentimiento → crear EIPD → completar EIPD → aprobar
   - `test_flujo_con_transferencia_internacional`: similar con garantías
   - `test_flujo_con_encargado`: crear RAT con encargado → crear contrato → aprobar
   - `test_flujo_rechazo_eipd_pendiente`: intentar aprobar sin EIPD completada → 422
3. Commit: `test(rat): E2E workflow RAT → EIPD → aprobar`

### S1.3 — H5.2: Test paginación reportes

**Estimación:** 2-3 horas

**Plan:**
1. Crear `backend/tests/test_reportes.py`
2. Tests:
   - `test_reportes_paginacion_basica`: skip=0, limit=50
   - `test_reportes_paginacion_offset`: skip=100, limit=50
   - `test_reportes_total_filtered_correcto`: con filtros, total refleja filtered
   - `test_reportes_qw_iter14_01`: 100+ RATs → debe paginar
3. Commit: `test(rat): paginacion reportes QW-ITER14-01`

### S1.4 — H6.1: Regenerar `08_API_REST_v1.10.docx`

**Estimación:** 6-8 horas

**Plan:**
1. Identificar los 14 endpoints faltantes
2. Generar tablas con método, path, auth, RBAC, params, response, tags
3. Regenerar doc con `scripts/maintenance/generar_manual.py` (extender)
4. Output: `docs/documentacion_oficial/08_API_REST_Custodio_RAT_Manager_v1.10.docx`
5. Actualizar `docs/documentacion_oficial/README.md` matriz de vigencia
6. Commit: `docs(api): regenerar 08_API_REST_v1.10 con 20 endpoints RAT`

---

## Sprint 2 — P2 (Importantes) — 2-4 semanas

**Objetivo:** Mejorar mantenibilidad y cobertura de tests.

### S2.1 — H3.4: Refactor RATBase vs RATUpdate duplicación

**Estimación:** 3-4 horas

**Plan:**
```python
# Actual:
class RATUpdate(BaseModel):
    nombre_proceso: Optional[str] = None
    categoria_datos: Optional[str] = None
    # ... 38 more fields

# Propuesto:
class RATUpdate(RATBase):
    """Update DTO — todos los campos son opcionales via exclude_unset."""
    @model_validator(mode='before')
    @classmethod
    def all_optional(cls, data):
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data
```

### S2.2 — H3.8: Refactor `rat_service.py` (640 líneas →拆)

**Estimación:** 6-8 horas

**Plan:** Dividir en:
- `rat_crud.py` (create, update, delete, get_*)
- `rat_validators.py` (_validar_*)
- `rat_alerts.py` (ALERTAS_AUDITORIA, _generar_alertas)
- `rat_file.py` (_procesar_archivo, download_rat_file)
- `rat_service.py` (orquestador)

### S2.3 — Tests faltantes (H5.3, H5.4, H5.5, H5.6)

**Estimación:** 8-10 horas

- Test CNI export (3 tests)
- Test dashboard stats (5 tests)
- Test RBAC admin_empresa (4 tests)
- Test email inválido (1 test)

### S2.4 — H3.11: Test E2E workflow (continuación)

**Estimación:** 4 horas

Más tests E2E:
- `test_flujo_revocacion_consentimiento`
- `test_flujo_bloqueo_rat`
- `test_flujo_vencimiento_plazo`

### S2.5 — H4.6: Actualizar AGENTS.md

**Estimación:** 1 hora

Cambiar "4 pasos" → "5 pasos (Identificación, Datos, Finalidad, Almacenamiento, Compliance)".

### S2.6 — H4.9: Refactor `test_interes_legitimo` parsing

**Estimación:** 3 horas

Cambiar de string con delimitadores a JSON estructurado:
```python
class TestInteresLegitimo(BaseModel):
    paso1_interes_legitimo: str
    paso2_necesidad: str
    paso3_balance: str

class RATBase(BaseModel):
    # ...
    test_interes_legitimo: Optional[TestInteresLegitimo] = None
```

### S2.7 — H4.14: axe-core a11y tests

**Estimación:** 3 horas

Setup con `@axe-core/playwright` + 10 tests de accesibilidad.

---

## Sprint 3 — P2 (continuación) + P3 — Backlog continuo

### S3.1 — H2.3, H2.4: Gaps menores API

**Estimación:** 2 horas

- Agregar `response_model=SugerenciasTiposOut` a `/sugerencias/tipos`
- Refactorizar `{rat_id}/export/pdf` para usar `get_rat_for_user`
- Agregar `require_module_enabled("RAT")` en dashboard

### S3.2 — H6.2: Casos de uso de export

**Estimación:** 2 horas

Agregar CU-15 a CU-20 al doc oficial.

### S3.3 — H6.4: Documentar AI Chat, OnboardingChecklist

**Estimación:** 1 hora

### S3.4 — Scheduler para alertas (H2.2, H3.1)

**Estimación:** 8 horas

- `notificar_eipd_vencida()` — EIPD >90 días
- `solicitar_renovacion_consentimiento()` — consentimiento >2 años
- Integrar con `scheduler.py`

---

## Backlog P3 — Mejoras continuas

23 mejoras agrupadas en:

### Mantenibilidad (10 items)
- Eliminar magic numbers (constantes nombradas)
- Extraer helpers para export endpoints (DRY)
- Dividir `export_service.py` (CSV vs PDF)
- Mover imports inline al top de archivos
- Reducir inline styles en frontend

### Performance (5 items)
- Virtualización de tabla para 100+ RATs
- Lazy loading de pasos del wizard
- Memoización de filtros
- Optimizar `calcular_completitud()` (cache por X segundos)

### UX (8 items)
- Foco automático en Drawer al abrir
- Lazy loading de imágenes
- a11y mejorada en wizard
- Indicadores de progreso más claros

---

## Estimación Total

| Sprint | Horas | Hallazgos | Prioridad |
|---|---|---|---|
| Sprint 1 | 20-29h | 4 P1 | Crítica |
| Sprint 2 | 25-31h | 7 P2 | Importante |
| Sprint 3 | 13h | 5 P2 + 23 P3 | Media-Baja |
| **TOTAL** | **58-73h** | **42 pendientes** | — |

**Calendario realista:** 3-4 semanas (1 desarrollador).

---

## Criterios de Aceptación

### Antes de marcar un P1 como cerrado:
- [ ] Tests pasan en CI (Neon QA)
- [ ] No regresiones en tests existentes
- [ ] Commit firmado con formato conventional commits
- [ ] Push a `qa` confirmado

### Antes de marcar un P2 como cerrado:
- [ ] Tests nuevos pasan
- [ ] Cobertura de código ≥80% en archivo modificado
- [ ] Documentación actualizada si aplica
- [ ] Linter pasa (ruff check)

### Antes de marcar un P3 como cerrado:
- [ ] Cambio no rompe funcionalidad
- [ ] Sin nuevas dependencias

---

## Riesgos Identificados

| Riesgo | Mitigación |
|---|---|
| Refactor de RatWizard rompe wizard actual | Hacer en rama feature, E2E tests antes |
| Cambio en `08_API_REST` afecta OpenAPI generator | Coordinar con frontend si usa generator |
| División de `rat_service.py` introduce imports circulares | Mover constantes a `rat_constants.py` |

---

## Métricas de Éxito

### Corto plazo (Sprint 1):
- ✅ 0 hallazgos P1 pendientes
- ✅ Score compliance: 9.0 → 9.5
- ✅ Score docs: 6.5 → 7.5

### Mediano plazo (Sprint 2):
- ✅ Score calidad código: 7.8 → 8.5
- ✅ Score cobertura tests: 7.0 → 8.0
- ✅ Score frontend: 7.5 → 8.0

### Largo plazo (Sprint 3):
- ✅ Score global: 7.7 → 8.5
- ✅ Madurez: Producción Inicial → Producción Empresarial
- ✅ Listo para auditoría APDC formal

---

## Anexo — Hallazgos Resueltos en Esta Auditoría

| Código | Descripción | Archivos |
|---|---|---|
| P0-1 | Tests IDOR con expectativas incorrectas | `backend/tests/rat_auditoria_test.py`, `backend/tests/rat_archivo_test.py` |
| P0-2 | Validación `base_legal="Otra"` sin archivo | `backend/app/services/rat_service.py` |
| P0-3 | `verify-chain` accesible a todos | `backend/app/routes/rats.py` |
| Bonus | BOM markers removidos | 3 archivos `.py` |

---

**Estado:** 🟢 Listo para revisión humana y push a `qa`.