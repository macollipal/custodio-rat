# Documentacion Oficial — Custodio RAT Manager

> **Version vigente:** v1.11 (2026-08-22) — regenerada por auditoria QA total (78 fallos → 0)
> **Politica:** los docs vigentes se versionan en git. Las versiones anteriores quedan como historico y NO se usan como fuente operativa.

## Matriz de Vigencia

| Codigo | Documento | Version Vigente | Historico | Observaciones |
|---|---|---|---|---|
| **00** | Indice | _(no regenerado)_ | v1.0, v1.1 | Sin equivalente v1.9 — `docs/README.md` raiz hace esta funcion. |
| **01** | Vision de Producto | _(no regenerado)_ | v1.0 | Sin equivalente v1.9. |
| **02** | Requisitos | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18. Cubre RFs v1.9 + nuevos (RF-170 BaseLegal enum, etc.). |
| **03** | Historias de Usuario | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18. Cubre HUs v1.9 + SLA T-2, soft delete, etc. |
| **04** | Casos de Uso | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18 (sobrescribe v1.10 de auditoría RAT). Cubre 25+ CUs con QW5 SLA T-2. |
| **05** | Diseno Funcional | _(no regenerado)_ | v1.0, v1.1, v1.2, v1.3 | Sin equivalente v1.9 — evaluar si necesario. |
| **06** | Arquitectura Software | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18. Incluye versionamiento /api/v1/, soft delete, cifrado Fernet fail-loudly, DR plan. |
| **07** | Modelo de Datos Detallado | _(no regenerado)_ | v1.0, v1.1 | Sin equivalente v1.9 — evaluar si necesario. |
| **08** | API REST | **v1.11** ✅ | v1.0–v1.10 (v1.5, v1.6 faltan) | **Regenerado en auditoria 2026-08-22.** POST /auth/users → 201, GET /publico/csrf-token, PUT /transparencia/{id}. |
| **09** | Backlog de Producto | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18. Incluye QW5 (SLA T-2 RATs) y QW4 cerrado. |
| **10** | Plan de QA | **v1.11** ✅ | v1.0–v1.10 (v1.5 falta) | Regenerado 2026-08-22. TC-047 a TC-055 (QA total 78→0 fallos). 732 tests passing. |
| **11** | Manual de Despliegue | _(no regenerado)_ | v1.0, v1.1 | Sin equivalente v1.9 — `docs/despliegue/` cumple esta funcion. |
| **12** | Manual Tecnico | **v1.11** ✅ | v1.0–v1.10 | Regenerado 2026-08-22. Sprint A+B+UX + fixes QA (auth 201, prorroga, encrypt_migration). |
| **MTX** | Matriz de Trazabilidad | **v1.10** ✅ | v1.0–v1.9 | Regenerado 2026-07-18. Incluye RF-170 (BaseLegal), RF-171 (Soft delete), RF-172 (Versionamiento API), RF-173 (SLA T-2). |

## Documentos SIN Version v1.9 (vigente es historica)

Estos docs NO fueron regenerados en la auditoria v1.9. La fuente de verdad para cada area es:

| Codigo | Vigente desde v1.x | Fuente actual alternativa |
|---|---|---|
| 00 Indice | v1.1 | `docs/README.md` (raiz) |
| 01 Vision | v1.0 | `docs/backlog_seguimiento.md` + `docs/SESSION_STATE.md` (historicos) |
| 05 Diseno Funcional | v1.3 | `frontend-next/components/`, `docs/arquitectura/` |
| 07 Modelo Datos Detallado | v1.1 | Modelos en `backend/app/models/` |
| 11 Manual Despliegue | v1.1 | `docs/despliegue/PLAN_DEPLOY.md`, `docs/despliegue/RUNBOOKS/` |

## Como Leer Esta Matriz

- **Version Vigente** ✅: archivo canonico, usalo como fuente operativa.
- **Historico**: cada version anterior es evidencia historica, NO operativa.
- **Sin equivalente v1.9**: no fue regenerado; consulta la fuente alternativa listada.

## Como Anadir una Nueva Version (al cerrar auditoria nueva)

1. Generar los nuevos `.docx` con los scripts de build en `docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/_scripts/`.
2. Ejecutarlos y guardar en `docs/documentacion_oficial/` con sufijo `_vX.Y.docx`.
3. Actualizar esta matriz:
   - Marcar nueva fila como vigente ✅.
   - Mover la fila anterior a "Historico".
4. Actualizar `docs/README.md` para reflejar nueva version.
5. Actualizar `docs/STATUS.md` con nuevo score y pendientes.
6. Commit con formato: `docs: governance sync vX.Y — <cambios>`.

## Archivos Historicos Sin Reemplazo

Los siguientes documentos historicos NO tienen equivalente v1.9. Mantenerlos por trazabilidad, pero no usarlos como referencia operativa.

- `00_Indice_..._v1.0.docx`, `00_Indice_..._v1.1.docx`
- `01_Vision_Producto_..._v1.0.docx`
- `05_Diseno_Funcional_..._v1.0/1/2/3.docx`
- `07_Modelo_Datos_..._v1.0/1.docx`
- `11_Manual_Despliegue_..._v1.0/1.docx`

## Scripts de Regeneracion

| Version | Carpeta build |
|---|---|
| v1.10 (vigente — RAT API) | `scripts/maintenance/generar_api_doc_v1_10.py` |
| v1.10 (vigente — CU RAT) | `scripts/maintenance/generar_casos_uso_v1_10.py` |
| v1.9 (vigente) | `docs/auditorias/2026-07-05_auditoria_v1.9/_scripts/build_*.py` |
| v1.8 | `docs/auditorias/2026-06-26_auditoria_v1.8/_scripts/build_*.py` |
| v1.7 | `docs/auditorias/2026-06-24_auditoria_v1.7/_scripts/build_*.py` |

> Los scripts en `paso/desarrollo_de_software_estandar/_build/` son base historica — **NO TOCAR**.

---

*Ultima actualizacion: 2026-07-18 (regeneracion v1.10 por auditoria de drift documental)*