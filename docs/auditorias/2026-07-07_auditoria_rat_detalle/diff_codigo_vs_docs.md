# diff_codigo_vs_docs.md — Auditoría RAT 2026-07-07

**Comparativa entre código actual y documentación oficial v1.9**

---

## 1. Endpoints RAT

### Código (20 endpoints)

```
GET    /rats/reportes
GET    /rats/
GET    /rats/dashboard/{company_id}
GET    /rats/sugerencias/tipos
POST   /rats/sugerencias
GET    /rats/{rat_id}
POST   /rats/
POST   /rats/{rat_id}/consentimientos
PUT    /rats/{rat_id}
DELETE /rats/{rat_id}
POST   /rats/{rat_id}/revision
POST   /rats/{rat_id}/aprobar
GET    /rats/{rat_id}/archivo
GET    /rats/{rat_id}/auditoria
GET    /rats/auditoria/{company_id}
GET    /rats/auditoria/verify-chain
GET    /rats/export/csv
GET    /rats/export/pdf
GET    /rats/{rat_id}/export/pdf
GET    /rats/export/cni
```

### Doc oficial v1.9 (`08_API_REST_Custodio_RAT_Manager_v1.9.docx`)

```
GET    /rats/                                    ✅
GET    /rats/{rat_id}                            ✅
POST   /rats/                                    ✅
PUT    /rats/{rat_id}                            ✅
DELETE /rats/{rat_id}                            ✅
GET    /rats/{rat_id}/auditoria                  ✅
POST   /rats/{rat_id}/revision                   ✅ (parcial)
POST   /rats/{rat_id}/aprobar                    ✅ (parcial)
```

### Endpoints NO documentados (14)

1. `GET /rats/reportes` — reportes filtrados
2. `GET /rats/dashboard/{company_id}` — estadísticas
3. `GET /rats/sugerencias/tipos` — listar tipos
4. `POST /rats/sugerencias` — sugerencias automáticas
5. `POST /rats/{rat_id}/consentimientos` — registrar consentimiento
6. `GET /rats/{rat_id}/archivo` — descargar archivo base legal
7. `GET /rats/auditoria/{company_id}` — auditoría global
8. `GET /rats/auditoria/verify-chain` — verificar integridad
9. `GET /rats/export/csv` — exportar CSV
10. `GET /rats/export/pdf` — exportar PDF
11. `GET /rats/{rat_id}/export/pdf` — exportar RAT individual
12. `GET /rats/export/cni` — exportar formato CNI (APDC)
13. (campo) `nivel_confidencialidad` (Tier 1)
14. (campo) `estructura_dato` (Tier 1)

---

## 2. Campos del Modelo RAT

### Código (40 columnas)

```
Obligatorios Art. 16 (7):
  nombre_proceso, categoria_datos, categoria_titulares, finalidad,
  base_legal, fuente_datos, plazo_retencion

Recomendados Art. 16 (3):
  medidas_seguridad, destinatarios, transferencia_datos

Flags de riesgo (5):
  datos_sensibles, evaluacion_impacto, estado_eipd, fecha_eipd,
  decisiones_automatizadas

Transferencia internacional (4):
  transferencia_internacional, pais_destino, garantias_transferencia_int,
  transferencia_datos (compartido)

Encargado (2):
  nombre_encargado, tiene_contrato_encargado

Iter 10 — Gaps Ley 21.719 (5):
  sistema_almacenamiento, volumen_titulares_estimado,
  operaciones_tratamiento, logica_automatizada,
  responsable_tratamiento_email

Tier 1 — Críticos (5):
  datos_nna, nivel_confidencialidad, estructura_dato,
  datos_anonimizados, datos_seudonimizados

Tier 2 — Operativos (10):
  ciclo_procesamiento, automatizacion, frecuencia,
  transferencia_nacional, doc_clausulas, medidas_organizativas,
  mecanismos_eliminacion, tecnica_anonimizacion,
  origen_dato_portabilidad, fecha_levantamiento

Archivo base legal (5):
  archivo_base_legal_nombre, archivo_base_legal_tipo,
  archivo_base_legal_datos, archivo_base_legal_hash,
  archivo_base_legal_storage_url

Audit/metadata (8):
  estado, observaciones_auditoria, aprobado_por,
  fecha_aprobacion, created_by, updated_by,
  created_at, updated_at, bloqueado, test_interes_legitimo
```

### Doc oficial v1.9

⚠️ **No encontrado** campo `categoria_titulares` (obligatorio Art. 16) en docs.

✅ Documenta: nombre_proceso, categoria_datos, finalidad, base_legal, fuente_datos, plazo_retencion, medidas_seguridad, destinatarios.

❌ NO documenta:
- 5 campos Tier 1 (datos_nna, nivel_confidencialidad, estructura_dato, datos_anonimizados, datos_seudonimizados)
- 10 campos Tier 2
- 5 campos Iter 10 (gaps Ley 21.719)

---

## 3. Estados del RAT

### Código (modelo enum)

```
EstadoRAT:
  BORRADOR     = "borrador"
  COMPLETO     = "completo"
  EN_REVISION  = "en_revision"
  APROBADO     = "aprobado"
```

### Doc oficial

✅ Documenta los 4 estados.

---

## 4. Estados EIPD

### Código

```
EstadoEIPD:
  NO_REQUERIDA             = "no_requerida"
  PENDIENTE                = "pendiente"
  EN_PROCESO               = "en_proceso"
  COMPLETADA               = "completada"
```

Adicional en validaciones (no en enum pero usado):
- `no_requerida_justificada` (con justificación ≥20 chars)

### Doc oficial

⚠️ Documenta 4 estados pero NO menciona `no_requerida_justificada`.

---

## 5. Categorías de Titulares

### Código (`categoria_titulares`)

Tipo libre (String 500). Valores comunes:
- Clientes, Empleados, Proveedores, Pacientes, Postulantes, Estudiantes,
  Usuarios web, Menores de edad, Acreedores

### Doc oficial

⚠️ Lista valores ejemplo pero no establece lista cerrada.

---

## 6. Tipos de Dato Sensible (Art. 2 g + Art. 16 BIS)

### Código (frontend + backend)

7 categorías (validadas en schema):
1. Origen racial o étnico
2. Situación socioeconómica
3. Salud (física o mental)
4. Vida sexual, orientación sexual e identidad de género
5. Opiniones políticas, creencias religiosas o filosóficas
6. Afiliación sindical
7. Datos biométricos de identificación (Art. 16 BIS)

### Doc oficial

✅ Documenta las 7 categorías correctamente.

---

## 7. Bases Legales

### Código (validación estricta)

7 opciones (enum cerrado):
1. Consentimiento del titular
2. Ejecución de contrato
3. Obligación legal
4. Interés legítimo
5. Interés vital del titular
6. Misión de interés público
7. Otra

### Doc oficial

✅ Documenta las 7 opciones.

---

## 8. Wizard RAT (Frontend)

### Código (`RatWizard.tsx`)

5 pasos reales:
- Paso 0: Sugerencias por rubro
- Paso 1: Identificación del proceso
- Paso 2: Datos personales tratados
- Paso 3: Finalidad y base legal
- Paso 4: Almacenamiento y transferencias
- Paso 5: Compliance operativo (Tier 2)

### Doc (`frontend-next/AGENTS.md`)

❌ Dice "4 pasos":
1. Identificación
2. Datos tratados
3. Finalidad y ley
4. Almacenamiento y transferencias

**Drift:** +1 paso no documentado (Compliance operativo).

---

## 9. Componentes Frontend

### Código (7 componentes en `components/rat/`)

```
RatTable.tsx (302 líneas)
RatWizard.tsx (~1300 líneas)
RatEditForm.tsx (805 líneas)
RatDetailView.tsx (677 líneas)
RatDetailModal.tsx (191 líneas)
PdfPreview.tsx (99 líneas)
ratWizardValidation.ts (86 líneas)
```

### Doc (`frontend-next/AGENTS.md`)

✅ Documenta:
- RatTable (CRUD + sort + export)
- RatWizard (4 pasos — desactualizado)
- RatEditForm (4 pasos — desactualizado)

❌ NO documenta:
- RatDetailView
- RatDetailModal
- PdfPreview
- ratWizardValidation

⚠️ Menciona OnboardingChecklist pero no en `components/rat/`.

---

## 10. Constantes Compartidas

### Código (`frontend-next/lib/constants.ts`)

11 catálogos:
- BASES_LEGALES (7)
- TIPOS_DATO_SENSIBLE (7)
- DATOS_NNA_OPCIONES (4)
- NIVEL_CONFIDENCIALIDAD_OPCIONES (4)
- ESTRUCTURA_DATO_OPCIONES
- OPERACIONES_TRATAMIENTO_OPCIONES (7)
- AUTOMATIZACION_OPCIONES (4)
- FRECUENCIA_OPCIONES (6)
- ESTADO_MAP/OPTIONS
- RIESGO_OPTIONS
- DIAS_REVISION

### Doc (`frontend-next/AGENTS.md`)

❌ No documenta estas constantes explícitamente.

---

## 11. Tests

### Código (6 archivos pytest + 2 Playwright)

```
backend/tests/test_rats.py (288 líneas, ~25 tests)
backend/tests/test_rat_gaps_21719.py (178 líneas, ~12 tests)
backend/tests/test_rat_tier1_tier2.py (325 líneas, ~20 tests)
backend/tests/rat_archivo_test.py (150 líneas, 5 tests)
backend/tests/rat_auditoria_test.py (84 líneas, 4 tests)
backend/tests/test_security.py::TestRATValidators (~178 líneas, 8 tests)
frontend-next/e2e/05-rat.spec.ts (70 líneas, ~4 tests)
frontend-next/e2e/15-rat-modal.spec.ts (~3 tests)
```

### Doc oficial

❌ NO menciona tests en absoluto.

---

## 12. Resumen de Drift

| Aspecto | Código | Doc | Drift |
|---|---|---|---|
| Endpoints | 20 | 6 | 14 faltantes |
| Campos modelo | 40 | ~15 | 25 faltantes |
| Estados EIPD | 4+1 | 4 | 1 no documentado |
| Wizard pasos | 5 | 4 | 1 no documentado |
| Componentes frontend | 7 | 3 | 4 no documentados |
| Constantes frontend | 11 | 0 | 11 no documentadas |
| Tests | 8 archivos | 0 | 0 mencionado |
| **TOTAL** | | | **56 elementos no documentados** |

---

## 13. Recomendaciones de Sincronización

### Prioridad Alta (P1)
1. Regenerar `08_API_REST_v1.10.docx` con los 14 endpoints faltantes.
2. Agregar al doc el campo `categoria_titulares` (obligatorio Art. 16).
3. Documentar los 15 campos Tier 1 + Tier 2.

### Prioridad Media (P2)
4. Actualizar AGENTS.md con wizard de 5 pasos.
5. Documentar `no_requerida_justificada` como estado EIPD válido.
6. Documentar los 4 componentes frontend faltantes.

### Prioridad Baja (P3)
7. Documentar las 11 constantes frontend.
8. Mencionar tests en docs oficiales (apéndice).

---

**Fecha:** 2026-07-07
**Versión código:** v1.9
**Versión docs:** v1.9