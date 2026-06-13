# Índice de Documentación — Custodio RAT

## Estructura de Carpetas

```
docs/
├── arquitectura/      # Diseño técnico, ADRs, diagramas
├── auditorias/        # Auditorías históricas (junio 2026)
├── cumplimiento/      # Ley 21.719, matrices de trazabilidad
├── despliegue/        # Deploy, runbooks, incidentes
├── desarrollo/        # Guías para devs (testing, código, skills)
├── documentacion_oficial/   # Docs .docx por versión
├── exposiciones/      # Material académico/presentaciones
├── infraestructura/   # OCI, setup ambientes
├── manuales/          # Manuales de usuario
└── legacy/            # Docs históricos archivados
```

## Auditorías Disponibles

| Fecha | Auditoría | Score |
|-------|-----------|-------|
| 2026-05-31 | Opinión arquitectónica | 6.3/10 |
| 2026-06-08 | Auditoría v1.2 | 4.83/10 → 7.5/10 |
| 2026-06-09 | Beta Launch | 7.5/10 |
| 2026-06-11 | Incidente ENV_VARS | Resuelto |
| 2026-06-13 | Post-fix OCI | 7.6/10 |

Ver: [auditorias/README.md](auditorias/README.md)

## Documentación por Área

### Arquitectura
- [Arquitectura General](arquitectura/ARQUITECTURA.md) *(por crear)*
- [Flujo de Datos](arquitectura/FLUJO_DATOS.md)
- Diagramas: [arquitectura/diagramas/](arquitectura/diagramas/)

### Cumplimiento Legal (Ley 21.719 Chile)
- [Ley 21.719](cumplimiento/ley_21719.txt)
- [Matriz de Trazabilidad](../documentacion_oficial/Matriz_Trazabilidad_Custodio_RAT_Manager_v1.3.docx)
- [Checklist Compliance](cumplimiento/CHECKLIST_LEY_21719.md) *(por crear)*

### Despliegue
- [Plan de Deploy Producción](despliegue/PLAN_DEPLOY.md)
- [Troubleshooting Vercel](despliegue/TROUBLESHOOTING.md)
- [Incidentes](despliegue/INCIDENTES.md)
- Runbooks: [despliegue/RUNBOOKS/](despliegue/RUNBOOKS/)

### Desarrollo
- [Estado TKT](desarrollo/ESTADO_TKT.md)
- [Plan Skills](desarrollo/PLAN_SKILLS.md)
- [Guía de Desarrollo](desarrollo/GUIA_DESARROLLO.md) *(por crear)*
- [Convenciones de Código](desarrollo/CONVENCIONES_CODIGO.md) *(por crear)*
- [Guía de Testing](desarrollo/GUIA_TESTING.md) *(por crear)*

### Infraestructura
- [Manual OCI Configuration](infraestructura/MANUAL_OCI.md)
- [Setup Ambientes](infraestructura/SETUP_AMBIENTES.md) *(por crear)*
- [Troubleshooting](infraestructura/TROUBLESHOOTING.md) *(por crear)*

### Manuales
- [Manual Usuario Funcional](manuales/MANUAL_USUARIO.md)
- [Manual de Pruebas](manuales/MANUAL_PRUEBAS.md)
- [Qué es un RAT](manuales/que_es_rat.md)
- [Caso de Estudio](manuales/CASO_ESTUDIO.md)

### Documentación Oficial (.docx)
- [Versión v1.3](../documentacion_oficial/) (actual)
- [Versión v1.2](../documentacion_oficial/)
- [Versión v1.1](../documentacion_oficial/)
- [Versión v1.0](../documentacion_oficial/)

## Scripts Disponibles

Ver: [scripts/README.md](../scripts/README.md)

## Changelog

Ver: [CHANGELOG.md](../CHANGELOG.md)

---

*Última actualización: 2026-06-13*
