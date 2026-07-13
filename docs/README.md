# Índice de Documentación — Custodio RAT

> **Versión vigente:** v1.9 (2026-07-05)
> **Estado actual:** Producción Inicial — Score 6.7/10
> **Última actualización:** 2026-07-05

## Handoff y estado de sesiones

- 📅 [`SESSION_HANDOFF.md`](SESSION_HANDOFF.md) — **ÚLTIMO HANDOFF: 2026-07-13** — Punto de entrada para retomar sesiones (resumen trabajo + pendientes)
- [`STATUS.md`](STATUS.md) — Estado actual, score, pendientes activos
- [`SESSION_STATE.md`](SESSION_STATE.md) — Handoff sesión 2026-07-03 (histórico)

---

## Documentación oficial vigente

La documentación oficial vigente (v1.9) está en [`documentacion_oficial/`](documentacion_oficial/). Ver la matriz de vigencia en [`documentacion_oficial/README.md`](documentacion_oficial/README.md) para identificar qué versión aplica a cada documento y qué versiones quedan como histórico.

| Doc | Versión vigente | Carpeta |
|---|---|---|
| 02 — Requisitos | v1.9 | `documentacion_oficial/02_Requisitos_..._v1.9.docx` |
| 03 — Historias de Usuario | v1.9 | `documentacion_oficial/03_Historias_Usuario_..._v1.9.docx` |
| 04 — Casos de Uso | v1.9 | `documentacion_oficial/04_Casos_de_Uso_..._v1.9.docx` |
| 06 — Arquitectura | v1.9 | `documentacion_oficial/06_Arquitectura_..._v1.9.docx` |
| 08 — API REST | v1.9 | `documentacion_oficial/08_API_REST_..._v1.9.docx` |
| 09 — Backlog | v1.9 | `documentacion_oficial/09_Backlog_Producto_..._v1.9.docx` |
| 10 — Plan QA | v1.9 | `documentacion_oficial/10_Plan_QA_..._v1.9.docx` |
| 12 — Manual Técnico | v1.9 | `documentacion_oficial/12_Manual_Tecnico_..._v1.9.docx` |
| MTX — Matriz Trazabilidad | v1.9 | `documentacion_oficial/Matriz_Trazabilidad_..._v1.9.docx` |

> **Auditoría vigente:** [`auditorias/2026-07-05_auditoria_v1.9/`](auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md)

## Estructura de Carpetas

```
docs/
├── README.md                       # Este archivo
├── STATUS.md                       # Estado actual, score, pendientes activos
├── documentacion_oficial/          # Docs .docx versionados (v1.0 a v1.9)
│   └── README.md                   # Matriz de vigencia
├── auditorias/                     # Auditorías históricas (jun–jul 2026)
│   └── README.md
├── arquitectura/                   # Diseño técnico, ADRs, diagramas
├── cumplimiento/                   # Ley 21.719, matrices
├── despliegue/                     # Deploy, runbooks, incidentes
├── desarrollo/                     # Guías para devs
├── exposiciones/                   # Material académico/presentaciones
├── infraestructura/                # OCI, setup ambientes
├── manuales/                       # Manuales de usuario
└── barrido_documental/             # Informes de gobernanza documental
```

## Auditorías Disponibles

| Fecha | Versión | Score |
|---|---|---|
| 2026-07-05 | v1.9 (Iter 13) | **6.7/10** ⬅ vigente |
| 2026-06-26 | v1.8 (Iter 11+12) | 6.3/10 |
| 2026-06-24 | v1.7 | 9.0/10 |
| 2026-06-15 | v1.6-BETA | 8.7/10 |
| 2026-06-14 | v1.5 | 8.3/10 |
| 2026-06-13 | Post-fix OCI | 7.6/10 |
| 2026-06-12 | v1.4 | 7.6/10 |
| 2026-06-08 | v1.2 | 4.83 → 7.5/10 |
| 2026-05-31 | Opinión arquitectónica | 6.3/10 |

Ver: [auditorias/README.md](auditorias/README.md)

## Documentación por Área

### Arquitectura
- [Arquitectura General](arquitectura/ARQUITECTURA.md) *(por crear)*
- [Flujo de Datos](arquitectura/FLUJO_DATOS.md)
- Diagramas: [arquitectura/diagramas/](arquitectura/diagramas/)

### Cumplimiento Legal (Ley 21.719 Chile)
- [Ley 21.719](cumplimiento/ley_21719.txt)
- Matriz vigente: `documentacion_oficial/Matriz_Trazabilidad_..._v1.9.docx`
- [Checklist Compliance](cumplimiento/CHECKLIST_LEY_21719.md) *(por crear)*

### Despliegue
- [Plan de Deploy Producción](despliegue/PLAN_DEPLOY.md)
- [Troubleshooting Vercel](despliegue/TROUBLESHOOTING.md)
- [Incidentes](despliegue/INCIDENTES.md)
- Runbooks: [despliegue/RUNBOOKS/](despliegue/RUNBOOKS/) *(por crear)*

### Desarrollo
- [Estado TKT](desarrollo/ESTADO_TKT.md)
- [Plan Skills](desarrollo/PLAN_SKILLS.md)
- [Guía de Desarrollo](desarrollo/GUIA_DESARROLLO.md) *(por crear)*

### Infraestructura
- [Manual OCI Configuration](infraestructura/MANUAL_OCI.md)
- [Setup Ambientes](infraestructura/SETUP_AMBIENTES.md) *(por crear)*

### Manuales
- [Manual Usuario Funcional](manuales/MANUAL_USUARIO.md)
- [Manual de Pruebas](manuales/MANUAL_PRUEBAS.md)
- [Qué es un RAT](manuales/que_es_rat.md)

## Scripts Disponibles

Ver: [scripts/README.md](../scripts/README.md)

## Changelog

Ver: [CHANGELOG.md](../CHANGELOG.md)

---

## Estados Históricos (Solo Referencia)

> Las versiones v1.0 a v1.8 permanecen en `documentacion_oficial/` como histórico.
> NO se usan como fuente operativa. La fuente operativa es v1.9.

> La carpeta `paso/` es personal del desarrollador (notas/borradores). NO está enlazada como documentación oficial.

> `docs/backlog_seguimiento.md` quedó como histórico tras el barrido documental del 2026-07-06. La fuente activa del backlog es `docs/SESSION_STATE.md`.