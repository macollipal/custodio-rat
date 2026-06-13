# Convenciones del módulo Custodio Asesor

## Prefijos de identificadores

| Tipo | Prefijo | Numeración | Ejemplo |
|------|---------|-----------|---------|
| Requisito funcional | `RF-ASES-` | correlativa desde 01 | `RF-ASES-01` |
| Requisito no funcional | `RNF-ASES-` | correlativa desde 01 | `RNF-ASES-01` |
| Historia de usuario | `US-ASES-` | correlativa desde 01 | `US-ASES-01` |
| Caso de uso | `CU-ASES-` | correlativa desde 01 | `CU-ASES-01` |
| Caso de prueba | `TC-ASES-` | correlativa desde 01 | `TC-ASES-01` |
| Item de backlog | `DT-ASES-` | correlativa desde 01 | `DT-ASES-01` |
| Decisión arquitectónica | `AD-ASES-` | correlativa desde 12 (post-AD Custodio) | `AD-ASES-12` |
| Riesgo | `R-NN` | correlativa global (no específico) | `R-01` |
| Endpoint | `EP-ASES-` | opcional, no obligatorio | `EP-ASES-01` |

> **Regla:** Los IDs son **inmutables**: una vez asignado, no se reutiliza ni se renumera.

---

## Prefijos de documentos

| Doc | Código |
|-----|--------|
| Visión y Alcance | `ASES-DOC-01` |
| Requisitos e Historias de Usuario | `ASES-DOC-02` |
| Casos de Uso y Diseño Funcional | `ASES-DOC-03` |
| Arquitectura y Modelo de Datos | `ASES-DOC-04` |
| API y Backlog | `ASES-DOC-05` |
| Plan de QA | `ASES-DOC-06` |
| Despliegue y Manual Técnico | `ASES-DOC-07` |
| Módulo Asesor (spec) | `ASES-DOC-08` |
| Matriz de Trazabilidad | `ASES-MTX` |

---

## Naming de archivos

### Scripts de build (`.py`)

```
build_NN_nombre_asesorgpt_vX_Y.py
```

Ejemplos:
- `build_01_vision_alcance_asesorgpt_v1_0.py`
- `build_08_modulo_asesor_asesorgpt_v1_0.py`
- `build_matriz_asesorgpt_v1_0.py`

### Documentos generados (`.docx`)

```
NN_NombreDoc_AsesorCustodio_vX.Y.docx
```

Ejemplos:
- `01_Vision_Alcance_AsesorCustodio_v1.0.docx`
- `08_Modulo_Asesor_AsesorCustodio_v1.0.docx`
- `Matriz_Trazabilidad_AsesorCustodio_v1.0.docx`

---

## Anchos de tabla (fijos)

| Tabla | Columnas | Anchos (cm) |
|-------|----------|-------------|
| Control de versiones | Versión · Fecha · Autor · Cambios | 1.5 · 2.5 · 3.0 · 10.59 |
| Estado del documento | Campo · Valor | 4.0 · 13.59 |
| Riesgos (Apéndice B) | ID · Descripción · Severidad | 2.0 · 13.0 · 2.5 |
| Glosario (Apéndice C) | ID · Nombre · Descripción | 2.5 · 5.0 · 10.0 |

---

## Regla de subrayados (cambios incrementales)

A partir de **v1.1** (v1.0 no aplica porque todo es nuevo), envolver con `_guiones bajos_` el texto que representa cambio:

```python
# v1.1 — nuevo RF detectado en código
rf_rows.append([
    "RF-ASES-13",
    "Alta",
    "Pendiente",
    "_El sistema debe permitir streaming de respuestas vía SSE._"
])
```

```python
# Llamada a add_styled_table con underline_new=True
add_styled_table(doc, headers, rows, col_widths_cm=[...], underline_new=True)
```

El theme `_theme_asesorgpt.py` (heredado de `_theme_custodio.py`) detecta texto que empieza y termina con `_` y aplica `r.underline = True`.

---

## Metadatos de portada (siempre presente)

| Campo | Valor |
|-------|-------|
| Versión | `DOC_VERSION` (override por script) |
| Fecha de emisión | `DOC_DATE` |
| Autor | `DOC_AUTHOR` |
| Empresa responsable | `Custodio SpA` |
| Clasificación | `Interno — Confidencial` |
| Producto | `Custodio Asesor (RAG)` |
| Producto padre | `Custodio RAT Manager` |
| Marco regulatorio | `Ley N.° 21.719 — Chile` |

---

## Apéndices obligatorios (siempre al final)

- **Apéndice A** — Vacíos de información (`add_open_questions`)
- **Apéndice B** — Riesgos identificados (`add_risks_appendix`)
- **Apéndice C** — Glosario de identificadores (`add_id_glossary`)
- Pie de cierre: `—  Fin del documento  —` (`add_final_note`)

---

## Auditoría: cuándo generar nueva versión

Ver SKILL.md → Paso 3 (Regla de decisión).
