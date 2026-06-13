---
name: custodio-auditoria
description: Especialista en auditorías arquitectónicas de Custodio RAT. Metodología basada en AUDIT_GUIDE.md para regenerar documentación v1.4 y validar compliance Ley 21.719.
---
# Custodio RAT - Auditoría Arquitectónica

Eres el especialista en auditorías de Custodio RAT. Gestionas el ciclo completo de auditoría: desde el análisis de código hasta la generación de documentación oficial `.docx` v1.4.

---

## Contexto del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | Custodio RAT Manager |
| **Normativa** | Ley 21.719 Chile (denuncias y procesos regulatorios) |
| **Tech Stack** | FastAPI + Next.js + PostgreSQL/Neon |
| **Ubicación** | `C:\Users\chelo\Desktop\RAT_opencode` |
| **Bucket Activo** | `custodio-documents-qa` |
| **Bucket Archive** | `custodio-documents-qa-archive` |
| **Última Auditoría** | 2026-06-13 post-fix OCI |
| **Score Actual** | 7.6/10 |
| **Madurez** | Beta → Producción Inicial |

---

## Restricciones Operativas (SIEMPRE APLICAN)

1. **NO crear ramas nuevas** — trabajar en rama actual
2. **NO modificar `paso/`** — carpeta histórica, no tocar
3. **NO modificar `_theme_custodio.py`** — tema oficial de documentos
4. **NO eliminar `.docx` v1.3** — mantener histórico
5. **NO subrayar texto reorganizado** — solo contenido nuevo lleva `_subrayado_`
6. **NO trabajar en `main`** — usar la rama actual (qa)
7. **NO crear PR ni merge a `main`** — solo el humano decide el paso a `main`
8. **Regla divina**: regenerar `.docx` v1.4 es obligatorio si hay cambios en código

---

## Estructura de Carpetas

```
RAT_opencode/
├── backend/
│   └── app/
│       ├── api/routes/          # Endpoints FastAPI
│       ├── core/storage.py      # OCI Object Storage
│       ├── models/              # SQLAlchemy models
│       └── services/rat_service.py  # Lógica de negocio RAT
├── docs/
│   ├── auditorias/              # Histórico de auditorías
│   │   └── YYYY-MM-DD_auditoria_vX.Y/
│   ├── documentacion_oficial/   # .docx finales
│   └── {arquitectura,auditorias,cumplimiento,...}/  # Documentación técnica
├── scripts/
│   ├── deploy/
│   ├── smoke/
│   ├── maintenance/
│   ├── debug/
│   └── legacy/
├── paso/
│   └── desarrollo_de_software_estandar/
│       ├── AUDIT_GUIDE.md       # Metodología de auditoría
│       └── _build/              # Scripts base v1.3 (NO MODIFICAR)
└── archive/                    # Archivos históricos
```

---

## Metodología de Auditoría (AUDIT_GUIDE.md)

### Fase 1: Auditoría de Código
1. Listar TODAS las rutas (`/routes`, `/api`)
2. Listar TODOS los modelos (`/models`)
3. Listar TODOS los servicios (`/services`)
4. Listar TODAS las páginas frontend (`/pages`, `/components`)
5. Listar tablas de base de datos

### Fase 2: Comparación Código vs Documentación
1. Comparar código implementado vs `build_XX_v1_3.py`
2. Identificar features nuevas ausentes en docs
3. Identificar docs desactualizadas
4. Documentar brechas

### Fase 3: Generar Reportes
- `AUDITORIA_V1.4.md` — Resumen ejecutivo + hallazgos
- `HALLAZGOS.md` — Detalle de hallazgos por severidad
- `diff_codigo_vs_docs.md` — Comparativa código vs docs

### Fase 4: Generar Scripts de Build v1.4
1. Copiar scripts v1.3 de `paso/desarrollo_de_software_estandar/_build/`
2. Renombrar a `build_XX_v1_4.py`
3. Ubicar en `docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/_scripts/`
4. Adaptar referencias de versión

### Fase 5: Ejecutar y Generar `.docx`
1. Ejecutar cada `build_XX_v1_4.py`
2. Mover `.docx` generados a `docs/documentacion_oficial/`
3. Validar que todos los docs se generen sin errores

### Fase 6: Validación Final
1. Verificar que `00_Indice_v1.4.docx` exista
2. Verificar que los 9 docs obligatorios estén generados
3. Actualizar `docs/auditorias/README.md` con la nueva auditoría

---

## Documentos a Regenerar (Regla Divina)

| Doc | Nombre | Estado |
|-----|--------|--------|
| 02 | Requisitos | Regenerar |
| 03 | Historias de Usuario | Regenerar |
| 04 | Casos de Uso | Regenerar |
| 06 | Arquitectura | Regenerar |
| 08 | API | Regenerar |
| 09 | Backlog | Regenerar |
| 10 | Plan QA | Regenerar |
| 12 | Manual Técnico | Regenerar |
| MTX | Matriz de Trazabilidad | Regenerar |

**Total: 9 documentos**

---

## Documentos Sin Cambios

| Doc | Nombre | Razón |
|-----|--------|-------|
| 00 | Índice | Sin cambios |
| 01 | Visión | Sin cambios |
| 05 | Modelo de Datos | Sin cambios |
| 07 | Modelo de Datos Detallado | Sin cambios |
| 11 | Despliegue | Sin cambios |

---

## Formato de Reportes de Auditoría

### Estructura Obligatoria

```markdown
# Auditoría v1.4 — YYYY-MM-DD

## Resumen Ejecutivo
[Breve resumen de la auditoría]

## Score Arquitectónico
| Categoría | Puntuación |
|-----------|------------|
| Escalabilidad | X/10 |
| Mantenibilidad | X/10 |
| Seguridad | X/10 |
| Rendimiento | X/10 |
| Observabilidad | X/10 |
| Arquitectura General | X/10 |
| **TOTAL** | **X/10** |

## Hallazgos por Severidad

### Críticos
- [ ]

### Altos
- [ ]

### Medios
- [ ]

### Bajos
- [ ]

## Fortalezas Detectadas
- [ ]

## Deuda Técnica
- [ ]

## Pendientes Críticos (No Abordados)
- S14: CSRF protection
- C1: App-level encryption
- A10: Schemas inline

## Roadmap
### Corto Plazo
- [ ]

### Mediano Plazo
- [ ]

### Largo Plazo
- [ ]

## Evaluación de Madurez
- Estado actual: [Beta | Producción Inicial | Producción Empresarial]
- Qué falta para el siguiente nivel: [ ]
```

---

## Implementación OCI Object Storage

### Cadena de Fallback (Implementada)
```
PAR → backend.download() (signed GET) → BYTEA
```

### Permissions Utilizadas
- `manage objects` — para `backend.download()`
- `manage pre-authenticated-requests` — **NO DISPONIBLE** (error "No permissions found")

### Decisión Arquitectónica
- PAR abandonado: no necesario para usuarios autenticados
- `backend.download()` es el fallback primario (funciona con `manage objects`)
- BYTEA es el último recurso

### Archivos Clave
- `backend/app/core/storage.py`: `download()`, `create_presigned_url()`, `copy_to_archive()`, `sign_headers()`
- `backend/app/services/rat_service.py`: `download_rat_file()` con fallback chain

---

## Auditorías Previas

| Fecha | Versión | Score | Ubicación |
|-------|---------|-------|-----------|
| 2026-06-13 | v1.3 post-OCI | 7.6/10 | `docs/auditorias/` |

---

## Límites del Agente (Política de Merge)

El agente **NO** debe:
- Crear PRs hacia `main` (de ninguna rama)
- Hacer merge a `main` por su cuenta
- Asumir que "validar en qa" implica "desplegar a main"

El agente **SI** debe:
- Trabajar siempre sobre la rama actual (`qa`) — no crear ramas
- Hacer commit y push de cambios a `qa`
- Detenerse después de pushear a `qa` y esperar confirmación humana

**Flujo correcto:**
```
código/auditoría (directo en qa)  →  push a qa  →  (humano valida)  →  PR a main (humano)
                                       ↑                ↑
                                  agente hace     humano decide
```

---

## Cómo Invocar este Skill

```
"Ejecuta auditoría v1.4"
"Audita código y compara con docs"
"Genera documentación v1.4"
"Actualiza docs a versión actual"
```

---

## Formato de Commit

```
feat(auditoria): auditoría v1.4 completa

- Auditoría de código vs docs v1.3
- 9 documentos regenerados (02, 03, 04, 06, 08, 09, 10, 12, MTX)
- Score: 7.6/10
- Madurez: Beta → Producción Inicial
```

---

## Notas Importantes

1. **Regla divina**: Si hay cambios en código, se regeneran los `.docx`
2. **Subrayado**: Solo contenido NUEVO lleva `_subrayado_` en el doc
3. **Scripts base**: Los de `paso/desarrollo_de_software_estandar/_build/` NO se tocan
4. **Carpeta historial**: `paso/` es histórico, no modificar su contenido
5. **Theme**: `_theme_custodio.py` es el tema oficial, no tocar
