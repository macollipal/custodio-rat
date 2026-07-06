# HALLAZGOS FRONTEND — Módulo RAT

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Skills aplicadas:** `frontend-guardian`, `qa-senior`
**Stack:** Next.js 16 + React 19 + TypeScript + Tailwind v4
**Score global frontend:** **7.5/10**

---

## Resumen Ejecutivo

El frontend del módulo RAT es **funcionalmente completo** pero tiene oportunidades de mejora en:
- ⚠️ **Wizard de 1300 líneas** — necesita拆分
- ⚠️ **Documentación desactualizada** — `frontend-next/AGENTS.md` dice "4 pasos" pero el código tiene 5
- ⚠️ **Inline styles** generalizados (no usa solo Tailwind)
- ✅ Buena accesibilidad (aria-labels, semantic HTML)
- ✅ Responsive dual: desktop grid + mobile card view
- ✅ Estados de loading/error bien manejados

---

## Análisis por Componente

### 1. `RatTable.tsx` (302 líneas) — Score 8.5/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Responsive | ✅ Excelente | Desktop grid (`sm:grid`) + mobile card (`sm:hidden`) |
| Accesibilidad | ✅ | `aria-label` en filtros, semantic buttons |
| Estados | ✅ | Loading (`exporting`, `duplicating`), error (toast) |
| Filtros | ✅ | 4 filtros + búsqueda + limpiar |
| **Hallazgo** | ⚠️ | Estilos inline repetidos |

#### Hallazgo H4.1: Estilos inline duplicados en todas las columnas
- **Severidad:** Baja
- **Detalle:** `selectCls`, `selectStyle`, `style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}` se repiten.
- **Recomendación:** Extraer a constantes o componente `<FilterBar>`.
- **Prioridad:** P3

#### ✅ H4.2: Vista mobile dedicada
Línea 244-286: vista card separada para mobile con flex-wrap de badges. Patrón correcto.

#### ✅ H4.3: Empty state con CTA
Línea 170-193: Cuando no hay RATs, muestra empty state con botón "Crear mi primer proceso". Solo visible si `puedeEditar`.

#### ⚠️ H4.4: Sin virtualización para tablas grandes
- **Severidad:** Media
- **Detalle:** Para 100+ RATs el render se vuelve lento.
- **Recomendación:** `react-window` o `react-virtual`.
- **Prioridad:** P3 (no bloqueante para v1.9 con 44 RATs seed)

---

### 2. `RatWizard.tsx` (~1300 líneas) — Score 6/10

| Aspecto | Estado | Detalle |
|---|---|---|
| **Tamaño** | ⚠️ **CRÍTICO** | 1300 líneas — excede recomendaciones |
| Auto-save | ✅ | localStorage cada 30s (líneas 90-103) |
| Onboarding tour | ✅ | Primera vez (líneas 106-111) |
| Sugerencias | ✅ | Por rubro en Paso 0 |
| Validación | ✅ | Por paso en `ratWizardValidation.ts` |
| **Hallazgo** | ⚠️ | **5 pasos reales vs docs dice 4** |

#### Hallazgo H4.5: Wizard excede 1300 líneas
- **Severidad:** **Alta**
- **Detalle:** Single file con Paso 0 + Paso 1 + Paso 2 + Paso 3 + Paso 4 + handlers + state + UI. Imposible de mantener.
- **Recomendación:** Refactor a:
  - `RatWizard/index.tsx` (orquestador)
  - `RatWizard/steps/Step0Sugerencias.tsx`
  - `RatWizard/steps/Step1Identificacion.tsx`
  - `RatWizard/steps/Step2Datos.tsx`
  - `RatWizard/steps/Step3Finalidad.tsx`
  - `RatWizard/steps/Step4Almacenamiento.tsx`
  - `RatWizard/steps/Step5Compliance.tsx`
  - `RatWizard/hooks/useDraftAutosave.ts`
- **Prioridad:** P1

#### ⚠️ H4.6: Docs dicen "4 pasos" pero código tiene 5
- **Severidad:** Media
- **Detalle:** `frontend-next/AGENTS.md` línea 105-110 dice wizard de 4 pasos. Código real tiene:
  - Paso 0: Sugerencias por rubro
  - Paso 1: Identificación
  - Paso 2: Datos tratados
  - Paso 3: Finalidad y ley
  - Paso 4: Almacenamiento y transferencias
  - Paso 5: Compliance operativo (Tier 2)
- **Recomendación:** Actualizar AGENTS.md a 5 pasos (o 4 + sugerencias previas).
- **Prioridad:** P2

#### ✅ H4.7: Auto-save robusto
localStorage cada 30 segundos, previene pérdida de datos.

#### ⚠️ H4.8: Validación duplicada cliente vs servidor
- **Severidad:** Baja
- **Detalle:** `ratWizardValidation.ts` (86 líneas) duplica parcialmente la lógica de `RATCreate.validar_campos_condicionales`.
- **Recomendación:** Idealmente generada desde Pydantic schema, pero aceptable duplicación cliente-servidor para UX inmediata.
- **Prioridad:** P3

---

### 3. `RatEditForm.tsx` (805 líneas) — Score 6.5/10

Similar problema que `RatWizard.tsx`:
- ⚠️ 805 líneas
- ⚠️ Mismos 5 pasos duplicados
- ⚠️ Parsing de `test_interes_legitimo` (líneas 32-42) es frágil

#### Hallazgo H4.9: Parsing de `test_interes_legitimo` con delimitador `\n`
- **Severidad:** Media
- **Líneas:** 32-42
- **Detalle:** Split por `\nPaso 2:` y `\nPaso 3:`. Frágil si el usuario incluye la frase "Paso 2" en su texto.
- **Recomendación:** Guardar como JSON estructurado en BD o usar campos separados en el schema.
- **Prioridad:** P2

---

### 4. `RatDetailView.tsx` (677 líneas) — Score 7.5/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Audit log timeline | ✅ | Render de historial |
| Badges | ✅ | Estado, completitud, riesgo |
| **Hallazgo** | ⚠️ | Drawer responsive |

#### ✅ H4.10: Drawer responsive
`Drawer` componente (`95vw` mobile, `60vw` desktop, max-width 640px). Sigue convención del proyecto.

#### ⚠️ H4.11: `criticalIfEmpty` para campos pendientes en rojo
- **Severidad:** Baja (funcional, no es bug)
- **Detalle:** Buena UX para mostrar campos obligatorios faltantes.

#### ⚠️ H4.12: 677 líneas con markup extenso
- **Severidad:** Media
- **Recomendación:** Extraer secciones a sub-componentes (`<DetailSection>`, `<DetailRow>`).
- **Prioridad:** P3

---

### 5. `RatDetailModal.tsx` (191 líneas) — Score 8/10

| Aspecto | Estado |
|---|---|
| Mode toggle (view/edit) | ✅ |
| Audit logs fetch | ✅ |
| Responsive | ✅ |

✅ Buen componente.

---

### 6. `PdfPreview.tsx` (99 líneas) — Score 8/10

| Aspecto | Estado |
|---|---|
| Blob URL cleanup | ✅ |
| Download fallback | ✅ |
| Mobile-friendly | ✅ |

✅ Buen componente.

---

### 7. `ratWizardValidation.ts` (86 líneas) — Score 8/10

| Aspecto | Estado |
|---|---|
| Validadores por paso | ✅ |
| Paridad con backend | ✅ Mayormente |

#### ⚠️ H4.13: Paridad cliente/servidor — sin checks de `archivo_base_legal`
- **Severidad:** Baja
- **Detalle:** Backend valida `archivo_base_legal_datos` para `base_legal="Otra"` (en completitud), pero cliente no valida.
- **Recomendación:** Agregar validación en wizard para que el usuario suba archivo antes de submit.
- **Prioridad:** P3

---

## Accesibilidad (a11y)

| Criterio | Estado | Detalle |
|---|---|---|
| ARIA labels | ✅ | Filtros y botones tienen `aria-label` |
| Semantic HTML | ✅ | `<button>`, `<details>`, `<select>` |
| Focus management | ⚠️ | No verificado en modales/wizard |
| Screen reader | ⚠️ | Sin testing explícito |
| Color contrast | ✅ | Texto en `#111827` sobre fondos claros |

#### Hallazgo H4.14: Sin testing de a11y con axe-core
- **Severidad:** Media
- **Detalle:** No hay tests automatizados de accesibilidad.
- **Recomendación:** Agregar `axe-core` o `@axe-core/react` en tests E2E.
- **Prioridad:** P2

---

## Responsive Design

| Breakpoint | Soporte | Detalle |
|---|---|---|
| Mobile (<640px) | ✅ | Cards dedicados, filtros wrap |
| Tablet (640-1024px) | ✅ | Grid adapta |
| Desktop (>1024px) | ✅ | Full grid |

✅ Buena estrategia responsive.

---

## Performance

| Aspecto | Score | Detalle |
|---|---|---|
| Code splitting | ⚠️ | Wizard completo en bundle |
| Lazy loading | ⚠️ | Sin lazy load de pasos |
| Memoization | ⚠️ | Sin `useMemo` en filtros |
| Image optimization | ✅ | No hay imágenes pesadas |

#### Hallazgo H4.15: Wizard no usa lazy loading
- **Severidad:** Baja
- **Recomendación:** `React.lazy()` para cada paso del wizard.
- **Prioridad:** P3

---

## Hallazgos Consolidados

### P1 (Crítico)
| Código | Hallazgo |
|---|---|
| **H4.5** | Wizard de 1300 líneas — refactor a sub-componentes |

### P2 (Importante)
| Código | Hallazgo |
|---|---|
| H4.6 | Docs dicen 4 pasos, código tiene 5 |
| H4.9 | Parsing frágil de `test_interes_legitimo` |
| H4.14 | Sin tests automatizados de a11y |

### P3 (Mejoras)
| Código | Hallazgo |
|---|---|
| H4.1 | Estilos inline duplicados |
| H4.4 | Sin virtualización para tablas grandes |
| H4.8 | Validación duplicada cliente/servidor |
| H4.11 | Drawer sin foco automático |
| H4.12 | RatDetailView 677 líneas — extraer secciones |
| H4.13 | Sin validación cliente de `archivo_base_legal` |
| H4.15 | Wizard sin lazy loading |

---

## Score Final Frontend

| Categoría | Score |
|---|---|
| Responsive Design | 9/10 |
| Accesibilidad | 7/10 |
| Visual Hierarchy | 8.5/10 |
| Performance | 7/10 |
| Mantenibilidad | 5.5/10 (por tamaño de archivos) |
| Calidad General | 7.5/10 |
| **TOTAL** | **7.5/10** |

---

## Recomendaciones Priorizadas

### Sprint 1 (P1)
1. **H4.5:** Refactor `RatWizard.tsx` →拆 a 7 archivos.

### Sprint 2 (P2)
2. **H4.6:** Actualizar AGENTS.md con wizard de 5 pasos.
3. **H4.9:** Cambiar `test_interes_legitimo` a JSON estructurado.
4. **H4.14:** Integrar axe-core en tests E2E.

### Backlog (P3)
- Mejorar memoización, lazy loading, virtualización.

---

**Próxima fase:** Cobertura de tests (Fase 5)