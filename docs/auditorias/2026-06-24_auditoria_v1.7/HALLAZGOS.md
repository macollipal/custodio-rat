# Hallazgos v1.7 — 2026-06-24

## Resumen de Hallazgos

| Severidad | Cantidad | Estado |
|-----------|----------|--------|
| Críticos | 0 | — |
| Altos | 0 | — |
| Medios | 0 | — |
| Bajos | 1 | ✅ Cerrado |

## Detalle de Hallazgos

### 🔴 G1 — Gap documental Doc 08 (API) desactualizado (BAJO)

**Descripción:** El documento 08 (API REST) estaba en v1.4 desde Jun-12. Nunca fue regenerado para v1.5 ni v1.6, generando un drift de 2 versiones en los endpoints documentados.

**Impacto:** Documentación desalineada con el código. Endpoints nuevos no documentados.

**Acción tomada:**
- Creado `build_08_api_v1_7.py` desde cero
- Documentados 60+ endpoints con método, path, auth, RBAC, params, response, tags
- Endpoints Sprint 2: `/export/tkt/{csv,excel,pdf}`, `/admin/tasks/enqueue-sla-alerts`
- Ejecutado: `08_API_REST_Custodio_RAT_Manager_v1.7.docx` ✅

**Estado:** ✅ Cerrado en v1.7

---

## Hallazgos Pre-Existentes (No Abordados en v1.7)

| ID | Descripción | Severidad | Razón de Postergación |
|----|-------------|------------|----------------------|
| G2 | Doc 05 (Modelo de Datos) en v1.3 | Medio | No en scope v1.7 |
| G3 | Doc 07 (Modelo Datos Detallado) en v1.1 | Medio | No en scope v1.7 |
| G4 | Doc 11 (Despliegue) en v1.1 | Medio | No en scope v1.7 |
| Z-01 | Security headers (HSTS, CSP, etc.) | Alto | Pendiente |
| Z-02 | CORS restrictivo por ruta | Alto | Pendiente |
| Z-03 | File upload validation (tipo MIME, tamaño) | Alto | Pendiente |
| Z-06 | Logs estructurados (JSON) | Medio | Pendiente |
