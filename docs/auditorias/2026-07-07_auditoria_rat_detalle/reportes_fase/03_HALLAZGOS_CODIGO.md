# HALLAZGOS CALIDAD DE CÓDIGO — Backend RAT

**Fecha:** 2026-07-07
**Versión auditada:** v1.9
**Skill aplicada:** `qa-senior`
**Score global calidad:** **7.8/10**

---

## Resumen Ejecutivo

El código del backend RAT es **funcionalmente sólido** pero presenta oportunidades de mejora en:
- ⚠️ **Complejidad ciclomática alta** en `rat_service.py` (640 líneas, una sola clase de funciones)
- ⚠️ **Magic strings/numbers** en validators (ej: `>=20 chars`, `>=50 chars`)
- ⚠️ **Schema duplicado** entre `RATBase` (40 campos) y `RATUpdate` (40 campos)
- ✅ Buena separación de responsabilidades (model / schema / service / route)
- ✅ Audit log + hash chain bien implementados
- ✅ Multi-tenant via `get_rat_for_user` consistente

---

## Análisis por Archivo

### 1. `backend/app/models/rat.py` (209 líneas)

**Score:** 9/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Tamaño | ✅ | 209 líneas — razonable para 40 columnas |
| Separación | ✅ | Mixin-like pattern OK |
| Naming | ✅ | `snake_case`, claro |
| Type hints | ✅ | `Mapped[T]` consistente |
| Indexes | ✅ | `ix_rats_company_estado` |
| **Hallazgo** | ⚠️ | `calcular_completitud()` (línea 133) está en modelo, no en servicio |

#### Hallazgo H3.1: Lógica de negocio en modelo
- **Severidad:** Baja
- **Detalle:** Los métodos `calcular_completitud()` y `calcular_nivel_riesgo()` son lógica de negocio, no representación de datos.
- **Recomendación:** Mover a `rat_service.py` como funciones puras o a un `RATCalculator` separado.
- **Prioridad:** P3 (refactor)

#### ✅ H3.2: Fórmula de completitud comprehensiva
25 campos: 7 obligatorios + 3 recomendados + 5 Tier 1 + 10 Tier 2. Penalización correcta por falta de documento base legal.

#### ⚠️ H3.3: Magic number `>=7`, `>=5`, `>=3` en `calcular_nivel_riesgo`
- **Severidad:** Baja
- **Líneas:** 203-208
- **Recomendación:** Definir constantes `UMBRAL_RIESGO_CRITICO = 7`, etc.

---

### 2. `backend/app/schemas/rat.py` (252 líneas)

**Score:** 6.5/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Validadores | ✅ | `field_validator`, `model_validator` |
| **Hallazgo** | ⚠️ | **Schema duplicado RATBase vs RATUpdate** |
| Base options | ✅ | Lista de 7 opciones hardcoded |

#### Hallazgo H3.4: Duplicación masiva entre `RATBase` y `RATUpdate`
- **Severidad:** **Media**
- **Detalle:** `RATUpdate` repite los 40 campos de `RATBase` con `Optional`. Si se agrega un campo al modelo, hay que actualizar 3 lugares (model, RATBase, RATUpdate). Riesgo de drift.
- **Recomendación:** Refactorizar a:
```python
class RATUpdate(RATBase):
    pass
# pydantic permite Optional via Config o __get_validators__
```
O usar `RATBase.model_fields` + `Optional` en tiempo de ejecución.
- **Prioridad:** P2

#### ⚠️ H3.5: Constantes `BASES_LEGALES` duplicadas backend/frontend
- **Severidad:** Baja
- **Detalle:** `schemas/rat.py:97-105` (7 opciones) vs `frontend-next/lib/constants.ts:36` (7 opciones).
- **Recomendación:** Documentar que ambos deben estar sincronizados, o generar el frontend desde el backend (OpenAPI generator).
- **Prioridad:** P3

#### ⚠️ H3.6: Magic numbers en validators
- **Severidad:** Baja
- **Detalle:** `min_length=3` (categoría_titulares), `min_length=50` (test_interes_legitimo), `>=20 chars` en `_validar_eipd_obligatoria`.
- **Recomendación:** Constantes nombradas.
- **Prioridad:** P3

#### ✅ H3.7: Email validator correcto
Regex `^[\w.\-]+@[\w.\-]+\.\w{2,}$` cumple RFC 5322 básico.

---

### 3. `backend/app/services/rat_service.py` (640 líneas)

**Score:** 7.5/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Funciones | 17 públicas + 6 internas | Muchas funciones pero relacionadas |
| **Hallazgo** | ⚠️ | **Archivo grande** — 640 líneas |
| Audit log | ✅ | Consistente en todas las operaciones |
| Validators | ✅ | `_validar_*` funciones bien aisladas |

#### Hallazgo H3.8: `rat_service.py` excede 600 líneas
- **Severidad:** Media
- **Detalle:** El archivo tiene 17 funciones públicas + 6 internas = 23 funciones en un solo archivo. Single Responsibility violado.
- **Recomendación:** Dividir en:
  - `rat_crud.py` (create, update, delete, get_*)
  - `rat_validators.py` (_validar_*)
  - `rat_alerts.py` (ALERTAS_AUDITORIA, _generar_alertas)
  - `rat_file.py` (_procesar_archivo, download_rat_file)
  - `rat_service.py` (orquestador)
- **Prioridad:** P2

#### ✅ H3.9: ALERTAS_AUDITORIA bien estructurado
Diccionario inmutable de 11 alertas con descripciones claras.

#### ⚠️ H3.10: Regex de plazo_retencion hardcoded
- **Severidad:** Baja
- **Línea:** 478
- **Detalle:** `re.search(r"(\d+)\s*(?:año|años)", plazo, re.IGNORECASE)` solo detecta años, no meses/días.
- **Recomendación:** Usar `dateutil.relativedelta` para parsing más robusto.
- **Prioridad:** P3

#### ⚠️ H3.11: Sin test del flujo completo crear RAT → EIPD → aprobar
- **Severidad:** Media
- **Detalle:** Existen tests unitarios pero no integración end-to-end del workflow completo.
- **Recomendación:** Test en `test_e2e.py` con flujo:
  1. Crear RAT con `datos_sensibles=True`
  2. Crear EIPD vinculada
  3. Completar EIPD
  4. Aprobar RAT
  5. Verificar estado APROBADO + audit log completo
- **Prioridad:** P2

---

### 4. `backend/app/routes/rats.py` (568 líneas)

**Score:** 8/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Endpoints | 20 | Bien organizados |
| REST naming | ✅ | Kebab-case plural |
| Status codes | ✅ | 201, 401, 403, 404, 422 |
| **Hallazgo** | ⚠️ | **DRY: copy-paste en endpoints de export** |

#### Hallazgo H3.12: DRY violado en exports
- **Severidad:** Media
- **Líneas:** 471-561 (CSV, PDF, CNI, individual PDF)
- **Detalle:** 4 endpoints con código idéntico:
```python
if not current_user.rol_global == "superadmin":
    ids = get_empresas_usuario(db, current_user.id)
    if company_id not in ids:
        raise HTTPException(status_code=403, detail="...")
```
- **Recomendación:** Extraer a helper `validar_acceso_empresa(db, current_user, company_id)`.
- **Prioridad:** P2

#### ✅ H3.13: _safe_filename robusto
Normalización NFD + ASCII filter + spaces to underscores.

#### ⚠️ H3.14: `from app.services.rat_service import download_rat_file, get_rat` inline
- **Severidad:** Baja
- **Línea:** 369
- **Detalle:** Import inline dentro de función. Anti-pattern.
- **Recomendación:** Mover al top del archivo.
- **Prioridad:** P3

#### ⚠️ H3.15: Manejo de errores inconsistente entre endpoints
- **Severidad:** Baja
- **Detalle:** Algunos usan `from fastapi import HTTPException` inline, otros no.
- **Recomendación:** Centralizar imports.
- **Prioridad:** P3

---

### 5. `backend/app/services/export_service.py` (439 líneas)

**Score:** 8.5/10

| Aspecto | Estado | Detalle |
|---|---|---|
| Sanitización CSV | ✅ | `_DANGEROUS_CSV_PREFIXES` con prefijos peligrosos |
| UTF-8 BOM | ✅ | Para Excel compatibility |
| PDF generación | ✅ | ReportLab con estilos |
| **Hallazgo** | ⚠️ | 439 líneas mezcla CSV + PDF |

#### Hallazgo H3.16: `export_service.py` mezcla CSV + PDF
- **Severidad:** Baja
- **Recomendación:** Dividir en `csv_export.py` y `pdf_export.py`.
- **Prioridad:** P3

#### ✅ H3.17: CSV injection prevention correcto
`sanitize_csv_value()` con prefijos `=`, `+`, `-`, `\t`, `\r` es el patrón estándar OWASP.

---

## Análisis SOLID

| Principio | Cumplimiento | Detalle |
|---|---|---|
| **S** Single Responsibility | ⚠️ 7/10 | `rat_service.py` muy grande, `export_service.py` mezcla CSV/PDF |
| **O** Open/Closed | ✅ 9/10 | Validadores extensibles, alertas configurables |
| **L** Liskov Substitution | ✅ 10/10 | Modelos bien definidos |
| **I** Interface Segregation | ✅ 9/10 | Schemas granulares (Create/Update/Out separados) |
| **D** Dependency Inversion | ✅ 8/10 | Services inyectados, pero algunas dependencias inline |

---

## Métricas de Código

| Archivo | Líneas | Funciones | Complejidad promedio |
|---|---|---|---|
| `models/rat.py` | 209 | 4 (incluyendo 2 métodos) | Baja |
| `schemas/rat.py` | 7 clases + 5 funciones | Media |
| `services/rat_service.py` | 640 | 17 + 6 | **Alta** en `_generar_alertas_auditoria` (cadena de if) |
| `routes/rats.py` | 568 | 20 endpoints | Baja por endpoint |
| `services/export_service.py` | 439 | 3 funciones | Media |

---

## Hallazgos Consolidados por Prioridad

### P1 (Crítico)
- Ninguno.

### P2 (Importante)
| Código | Hallazgo |
|---|---|
| H3.4 | Schema duplicado RATBase vs RATUpdate |
| H3.8 | rat_service.py excede 600 líneas |
| H3.11 | Sin test E2E del workflow RAT→EIPD→aprobar |
| H3.12 | DRY violado en 4 endpoints de export |

### P3 (Mejoras)
| Código | Hallazgo |
|---|---|
| H3.1 | Lógica de negocio en modelo |
| H3.3 | Magic numbers en calcular_nivel_riesgo |
| H3.5 | BASES_LEGALES duplicado backend/frontend |
| H3.6 | Magic numbers en validators |
| H3.10 | Regex plazo_retencion solo detecta años |
| H3.14 | Import inline en route handler |
| H3.15 | Manejo de errores inconsistente |
| H3.16 | export_service.py mezcla CSV/PDF |

---

## Score Final

| Categoría | Score |
|---|---|
| Seguridad | 9.5/10 |
| Mantenibilidad | 7.5/10 |
| Rendimiento | 8/10 |
| Testing | 7/10 |
| Calidad General | 7.8/10 |
| **TOTAL** | **7.8/10** |

---

**Próxima fase:** Auditoría Frontend (Fase 4)