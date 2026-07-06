# STATUS — Custodio RAT Manager

> **Fuente canonica de estado actual del proyecto.**
> Actualizar tras cada auditoria (`docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/`).

## Estado Actual

| Campo | Valor |
|---|---|
| **Version** | v1.9 |
| **Fecha** | 2026-07-05 |
| **Score Arquitectonico** | **6.7/10** |
| **Delta vs v1.8** | +0.4 |
| **RAT** | 6.5/10 |
| **ARCO** | 6.8/10 |
| **Brechas** | 5.9/10 |
| **Madurez** | Produccion Inicial |
| **Branch** | `qa` |
| **Ultima auditoria** | [2026-07-05_auditoria_v1.9](../auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md) |

## Documentacion Vigente

Ver: [documentacion_oficial/README.md](documentacion_oficial/README.md)

9 documentos v1.9 (02, 03, 04, 06, 08, 09, 10, 12, MTX).

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
| QW-ITER14-01 | Paginacion en listados >100 registros (RAT/ARCO/Brechas) | P2 |
| QW-ITER14-02 | Retry logic en OCI uploads (resilience) | P3 |
| QW-ITER14-03 | Logs de auditoria en tabla `audit_log` (Art. 28 Ley 21.719) | P2 |
| QW-ITER14-04 | ALTER TABLE `categoria_titulares` SET NOT NULL (breaking change) | P3 — **ya completado Z-04** ✅ |

### Compliance (de barrido documental 2026-07-06)

| Hallazgo | Descripcion | Estado |
|---|---|---|
| H1 | Indice documental desactualizado | **Cerrado P0** ✅ (commit `2e0b29b`) |
| H2 | Versionado sin politica | **Cerrado P1** ✅ (matrix en `documentacion_oficial/README.md`) |
| H3 | Lock files `~$*.docx` | **Cerrado P0** ✅ |
| H4 | Mojibake en `.md` | Pendiente (P2) |
| H5 | Backlogs no reconciliados | Pendiente (mantener SESSION_STATE activo, marcar otros historico) |
| H6 | Duplicacion AsesorCustodio vs `_regen` | Pendiente |
| H7 | Docs en `paso/` | NO APLICA (carpeta personal del usuario) |
| H8 | Pendientes Z- en auditorias | **Cerrado P1** ✅ (esta tabla) |

## Mejoras Recientes Cerradas (v1.9)

| Iter | RF/HU | Descripcion |
|---|---|---|
| 13 | RF-163 (CRITICO) | IDOR multi-tenant en 6 endpoints RAT |
| 13 | RF-164 | `base_legal_valida` strict contra enum taxativo |
| 13 | RF-165 | ConsentimientoAlert en RatEditForm.handleSave() |
| 13 | RF-166 | Homologacion orden campos RAT (wizard/drawer/PDF) |
| 13 | RF-167 | PDF con titulos de seccion (PASO 1, PASO 2, ...) |
| 13 | RF-168 | Encoding UTF-8 corregido en backend |
| 13 | RF-169 | Codigo muerto eliminado |

Ver detalle en [AUDITORIA_V1.9.md](../auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md).

## Proximos Pasos Sugeridos

### Corto Plazo (Sprint actual)

1. Cerrar **Z-01** y **Z-02** (security headers + CORS).
2. Cerrar **Z-03** (file upload MIME validation).
3. Cerrar **Z-06** (audit_log table).

### Mediano Plazo

1. Paginacion en listados (QW-ITER14-01).
2. Retry logic OCI (QW-ITER14-02).
3. Encoding UTF-8 normalizacion automatica (P2 del barrido).

### Largo Plazo

1. Madurez a "Produccion Empresarial" (score > 8.5/10).
2. Certificacion APDC completa.
3. Multi-empresa en arquitectura multi-tenant avanzada.

---

## Metricas Rapidas

| Metrica | Valor |
|---|---|
| Documentos v1.9 generados | 9/9 ✅ |
| Tests pasando (test_security.py) | 32/32 ✅ |
| RFs documentados | 169 (RF-001 a RF-169) |
| HUs documentados | 103 (HU-001 a HU-103) |
| Commits ultima semana | ~15 |

---

*Ultima actualizacion: 2026-07-05 (auditoria v1.9 + barrido documental P0/P1)*
*Mantenido por skill `doc-governance` (bajo demanda).*