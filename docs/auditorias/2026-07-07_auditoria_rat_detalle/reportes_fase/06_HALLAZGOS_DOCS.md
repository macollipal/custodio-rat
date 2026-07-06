# HALLAZGOS DOCUMENTACIÓN vs CÓDIGO — Módulo RAT

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Skills aplicadas:** `doc-governance`, `custodio-auditoria`
**Score documentación:** **6.5/10**

---

## Resumen Ejecutivo

La documentación oficial del módulo RAT está **significativamente desactualizada** respecto al código actual:

- ⚠️ **Drift de endpoints:** Código tiene **20 endpoints RAT**, doc oficial v1.9 documenta solo **~6**
- ⚠️ **AGENTS.md dice "4 pasos"** en wizard, código tiene **5 pasos**
- ⚠️ Docs oficiales no mencionan Tier 1, Tier 2 ni campos Iter 10
- ✅ Campo de compliance Ley 21.719 bien documentado en BD

---

## Análisis por Documento

### 1. `08_API_REST_Custodio_RAT_Manager_v1.9.docx`

**Score:** 5/10

**Cobertura de endpoints RAT:**

| Endpoint | En código | En doc | Notas |
|---|---|---|---|
| `GET /rats/reportes` | ✅ | ❌ | Faltante |
| `GET /rats/` | ✅ | ✅ | |
| `GET /rats/dashboard/{company_id}` | ✅ | ❌ | Faltante |
| `GET /rats/sugerencias/tipos` | ✅ | ❌ | Faltante |
| `POST /rats/sugerencias` | ✅ | ❌ | Faltante |
| `GET /rats/{rat_id}` | ✅ | ✅ | |
| `POST /rats/` | ✅ | ✅ | |
| `POST /rats/{rat_id}/consentimientos` | ✅ | ❌ | Faltante |
| `PUT /rats/{rat_id}` | ✅ | ✅ | |
| `DELETE /rats/{rat_id}` | ✅ | ✅ | |
| `POST /rats/{rat_id}/revision` | ✅ | ✅ (parcial) | |
| `POST /rats/{rat_id}/aprobar` | ✅ | ✅ (parcial) | |
| `GET /rats/{rat_id}/archivo` | ✅ | ❌ | Faltante |
| `GET /rats/{rat_id}/auditoria` | ✅ | ✅ | |
| `GET /rats/auditoria/{company_id}` | ✅ | ❌ | Faltante |
| `GET /rats/auditoria/verify-chain` | ✅ | ❌ | Faltante |
| `GET /rats/export/csv` | ✅ | ❌ | Faltante |
| `GET /rats/export/pdf` | ✅ | ❌ | Faltante |
| `GET /rats/{rat_id}/export/pdf` | ✅ | ❌ | Faltante |
| `GET /rats/export/cni` | ✅ | ❌ | Faltante |

**Cobertura:** 6/20 endpoints (30%)

#### Hallazgo H6.1: 14 endpoints RAT no documentados
- **Severidad:** **Alta**
- **Detalle:** Los 14 endpoints más nuevos (después de v1.6) no aparecen en la doc oficial.
- **Endpoints faltantes:**
  - `GET /rats/reportes` (con 12 filtros)
  - `GET /rats/dashboard/{company_id}`
  - `GET /rats/sugerencias/tipos`
  - `POST /rats/sugerencias`
  - `POST /rats/{rat_id}/consentimientos`
  - `GET /rats/{rat_id}/archivo`
  - `GET /rats/auditoria/{company_id}`
  - `GET /rats/auditoria/verify-chain`
  - `GET /rats/export/csv`
  - `GET /rats/export/pdf`
  - `GET /rats/{rat_id}/export/pdf`
  - `GET /rats/export/cni`
- **Recomendación:** Regenerar `08_API_REST_v1.10.docx` o append seccion "Endpoints nuevos v1.9".
- **Prioridad:** **P1** (compliance + onboarding devs)

---

### 2. `04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx`

**Score:** 6/10

**Casos de uso documentados:** ~10
**Casos de uso reales:** ~25+ (CRUD + filtros + exports + consentimientos + EIPD + revisión + aprobación + duplicación)

#### Hallazgo H6.2: Casos de uso de export no documentados
- **Severidad:** Media
- **Detalle:** Los flujos de export (CSV/PDF/CNI) y dashboard no aparecen como casos de uso.
- **Recomendación:** Agregar CU-15 a CU-20.
- **Prioridad:** P2

---

### 3. `frontend-next/AGENTS.md` — Score 6/10

#### Hallazgo H6.3: Wizard dice "4 pasos" pero código tiene 5
- **Severidad:** Media
- **Línea:** 105-110
- **Detalle:** El doc dice 4 pasos (Identificación, Datos, Finalidad, Almacenamiento). El código real tiene 5 (los 4 anteriores + Compliance operativo con Tier 2).
- **Recomendación:** Actualizar a 5 pasos o 4 + Sugerencias (Paso 0).
- **Prioridad:** P2

#### ⚠️ H6.4: Otros componentes no documentados
- `OnboardingChecklist` mencionado en doc pero no en AGENTS.md
- `Drawer` componente sí documentado
- `AI Chat` en `/reportes` no mencionado

---

### 4. `docs/README.md` — Score 7/10

✅ Buena estructura general.

#### ⚠️ H6.5: Falta referencia a auditoria_rat_detalle
- **Severidad:** Baja
- **Detalle:** El nuevo directorio de auditoría detallado no está mencionado.
- **Recomendación:** Agregar al índice.

---

### 5. `docs/STATUS.md` — Score 8/10

✅ Bien mantenido, refleja Z-04 cerrado, score 6.7/10, v1.9 vigente.

---

### 6. `docs/SESSION_STATE.md` — Score N/A

Es backlog activo del usuario, no se audita.

---

### 7. `docs/bpmn/PROCESS_01_RAT/PROCESS_01_RAT.md` — Score 7.5/10

✅ Proceso BPMN RAT bien documentado. Menciona Iter 10, Tier 1, Tier 2.

---

## Matriz Docs vs Código

| Aspecto | Código | Doc oficial | Drift |
|---|---|---|---|
| Endpoints RAT | 20 | 6 | **14 faltantes** |
| Campos modelo RAT | 40 | ~15 | **25 faltantes** |
| Wizard steps | 5 | 4 | **1 faltante** |
| Tests | 6 archivos | 0 referenciados | N/A |
| Compliance Ley 21.719 | 9 artículos | 9 artículos | ✅ |

---

## Hallazgos Consolidados

### P1 (Crítico)
| Código | Hallazgo |
|---|---|
| **H6.1** | 14 endpoints RAT no documentados en `08_API_REST_v1.9.docx` |

### P2 (Importante)
| Código | Hallazgo |
|---|---|
| H6.2 | Casos de uso de export no documentados |
| H6.3 | Wizard dice 4 pasos, código tiene 5 |
| H6.4 | Otros componentes frontend no documentados |

### P3 (Mejoras)
| Código | Hallazgo |
|---|---|
| H6.5 | Falta referencia a auditoría detallada en README |

---

## Score por Documento

| Documento | Score |
|---|---|
| `08_API_REST_v1.9.docx` | 5/10 |
| `04_Casos_de_Uso_v1.9.docx` | 6/10 |
| `frontend-next/AGENTS.md` | 6/10 |
| `docs/README.md` | 7/10 |
| `docs/STATUS.md` | 8/10 |
| `docs/bpmn/PROCESS_01_RAT.md` | 7.5/10 |
| **TOTAL** | **6.5/10** |

---

## Recomendaciones

### Sprint 1 (P1)
1. **H6.1:** Regenerar `08_API_REST_v1.10.docx` con los 20 endpoints.

### Sprint 2 (P2)
2. **H6.2:** Agregar casos de uso de export/dashboard.
3. **H6.3:** Actualizar AGENTS.md con wizard de 5 pasos.

### Backlog
4. **H6.4:** Documentar AI Chat, OnboardingChecklist en AGENTS.md.
5. **H6.5:** Agregar `auditoria_rat_detalle` al README principal.

---

**Próxima fase:** Reporte ejecutivo final (Fase 7)