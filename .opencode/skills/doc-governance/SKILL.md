---
name: doc-governance
description: Mantiene la gobernanza documental de Custodio RAT (docs/README.md, docs/STATUS.md, docs/documentacion_oficial/README.md, backlog canonico). Bajo demanda. Se activa cuando el usuario dice "ordena la documentacion", "limpia el README", "audita governance", "actualiza status", o despues de una auditoria nueva para sincronizar el estado vigente.
---

# Skill: doc-governance

# Custodio RAT — Gobernanza Documental

Eres el especialista en gobernanza documental del proyecto Custodio RAT. Mantienes la fuente canonica de version vigente, backlog activo y limpieza de artefactos.

---

## Cuando Usar Esta Skill

Activar cuando el usuario dice:

- "ordena la documentacion"
- "limpia el README"
- "actualiza el status"
- "audita governance"
- "que version esta vigente"
- "donde esta el backlog activo"

Tambien se activa al cierre de cada auditoria (`custodio-auditoria`) para sincronizar el estado vigente.

---

## Contexto del Proyecto

| Campo | Valor |
|---|---|
| **Nombre** | Custodio RAT Manager |
| **Version actual** | v1.9 (2026-07-05) |
| **Tecnologia** | FastAPI + Next.js + PostgreSQL/Neon |
| **Documentacion oficial** | `docs/documentacion_oficial/` (versionada v1.0 a v1.9) |
| **Estado actual** | Produccion Inicial — Score 6.7/10 |
| **Carpeta personal** | `paso/` — NO TOCAR (es del usuario) |
| **Barrido documental** | `docs/auditorias/2026-07-06_barrido_documental/BARRIDO_DOCUMENTAL.md` |

---

## Archivos que Esta Skill Mantiene

| Archivo | Proposito |
|---|---|
| `docs/README.md` | Indice vigente — apunta a v1.9 + rutas a documentacion oficial |
| `docs/STATUS.md` | Version, score, Z-pendientes activos, metricas |
| `docs/documentacion_oficial/README.md` | Matriz de vigencia: doc / version vigente / historico |
| `docs/SESSION_STATE.md` | **NO TOCAR** — backlog activo, mantenido por el usuario |

---

## Archivos que NO Se Tocan

| Archivo | Razon |
|---|---|
| `paso/**` | Carpeta personal del usuario (notas/borradores) |
| `docs/backlog_seguimiento.md` | Historico — declarado asi tras barrido 2026-07-06 |
| `docs/SESSION_STATE.md` | Mantenido por el usuario, no por esta skill |
| `docs/auditorias/2026-06-XX_*/` | Historico inmutable |

---

## Convenciones de Documentacion

### Naming

| Convencion | Ejemplo |
|---|---|
| Versionado oficial | `02_Requisitos_Custodio_RAT_Manager_v1.9.docx` |
| Carpeta audit | `docs/auditorias/2026-07-05_auditoria_v1.9/` |
| Backlog activo | `docs/SESSION_STATE.md` |
| Estado | `docs/STATUS.md` |

### Terminologia canonica (usar SIEMPRE)

| Correcto | NO usar | Razon |
|---|---|---|
| APDC (Agencia de Proteccion de Datos Personales de Chile) | APDP | Ley 21.719 oficial |
| Custodio RAT Manager | RAT Manager, Custodio RAT | Nombre oficial |
| AsesorCustodio | AsesorGPT, Asesor | Modulo IA |
| Ley 21.719 | Ley 21.789, ley 21719 | Numero exacto |

### Encoding

- Todo `.md` debe estar en **UTF-8 sin BOM**.
- Detectar mojibake: caracteres `Ã`, `â`, `ðŸ`, `Â` repetidos.
- Si se detecta: ejecutar script de normalizacion antes de commit.

---

## Workflow: Despues de Cada Auditoria

```
1. Recibir nueva auditoria en docs/auditorias/YYYY-MM-DD_auditoria_vX.Y/
2. Ejecutar barrido documental (ver seccion "Barrido")
3. Actualizar docs/STATUS.md con:
   - Nueva version vigente
   - Score actualizado
   - Z-pendientes movidos a cerrados o actualizados
4. Verificar que docs/README.md apunte a la nueva version
5. Verificar que docs/documentacion_oficial/README.md incluya los nuevos docs vX.Y
6. Si hay docs viejos que reemplazan: NO borrar, mover logica a "historico" en matriz
7. Commitear con formato: docs: governance sync vX.Y — <cambios>
```

---

## Workflow: Orden Bajo Demanda

Cuando el usuario dice "ordena la documentacion":

```
1. Ejecutar barrido documental (ver seccion)
2. Generar reporte con hallazgos priorizados (P0/P1/P2/P3)
3. Si hay P0 (lock files, links rotos): corregir inmediatamente
4. Si hay P1 (drift entre fuentes): consultar con usuario antes de mover
5. Si hay P2 (encoding, nombres): proponer fix sin aplicar
6. Si hay P3 (automatizacion): crear ticket/TODO en SESSION_STATE.md
```

---

## Barrido Documental

### Comando (Windows PowerShell)

```powershell
# Conteo de archivos
Get-ChildItem -Path "docs" -Recurse -Include "*.md","*.docx" | Measure-Object

# Lock files (~$*.docx)
Get-ChildItem -Path "docs" -Recurse | Where-Object { $_.Name -like "~$*" } | Select-Object FullName

# Documentos versionados
Get-ChildItem -Path "docs\documentacion_oficial" -Filter "*.docx" | Group-Object { $_.BaseName -replace '_v\d+(\.\d+)?$', '' } | Select-Object Name, Count

# Moijibake detector
Get-ChildItem -Path "docs" -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_ -Raw -Encoding UTF8
    if ($content -match '[ÃâðŸÂ]{2,}|\u00f1') {
        Write-Host "POSIBLE MOJIBAKE: $($_.FullName)"
    }
}
```

### Hallazgos tipicos

| Codigo | Hallazgo | Accion |
|---|---|---|
| H1 | Indice desactualizado | Actualizar `docs/README.md` |
| H2 | Versionado sin politica | Crear `documentacion_oficial/README.md` matriz |
| H3 | Lock files `~$*.docx` | Borrar + verificar `.gitignore` |
| H4 | Mojibake en `.md` | Normalizar UTF-8 |
| H5 | Backlogs no reconciliados | Mantener SESSION_STATE activo, marcar otros historico |
| H6 | Duplicacion _regen vs base | Definir canonico, mover o archivar |
| H7 | Docs en `paso/` | Dejar (es del usuario) |
| H8 | Pendientes Z- en auditoria | Mover a STATUS.md activo |

---

## Inventario de Documentacion Vigente

### v1.9 (2026-07-05) — Vigente

| Doc | Archivo |
|---|---|
| 02 Requisitos | `02_Requisitos_Custodio_RAT_Manager_v1.9.docx` |
| 03 Historias de Usuario | `03_Historias_Usuario_Custodio_RAT_Manager_v1.9.docx` |
| 04 Casos de Uso | `04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx` |
| 06 Arquitectura | `06_Arquitectura_Software_Custodio_RAT_Manager_v1.9.docx` |
| 08 API REST | `08_API_REST_Custodio_RAT_Manager_v1.9.docx` |
| 09 Backlog | `09_Backlog_Producto_Custodio_RAT_Manager_v1.9.docx` |
| 10 Plan QA | `10_Plan_QA_Custodio_RAT_Manager_v1.9.docx` |
| 12 Manual Tecnico | `12_Manual_Tecnico_Custodio_RAT_Manager_v1.9.docx` |
| MTX Matriz Trazabilidad | `Matriz_Trazabilidad_Custodio_RAT_Manager_v1.9.docx` |

### Documentos SIN version v1.9

| Doc | Ultima version | Observacion |
|---|---|---|
| 05 Diseno Funcional | v1.0 | No regenerado en v1.9 — evaluar si necesario |
| 07 Modelo Datos Detallado | v1.0 | No regenerado en v1.9 — evaluar si necesario |
| 11 Despliegue | v1.0 | No regenerado en v1.9 — evaluar si necesario |

---

## Pre-commit Hook Sugerido

```bash
#!/bin/bash
# .git/hooks/pre-commit — bloquea lock files y mojibake

# Detectar ~$*.docx
if git diff --cached --name-only | grep -E '^\$\.?[A-Za-z].*\.docx$|~$' > /dev/null; then
  echo "ERROR: lock file detectado. Cerrar Word y volver a commitear."
  exit 1
fi

# Detectar mojibake en .md
for f in $(git diff --cached --name-only --diff-filter=AM | grep '\.md$'); do
  if grep -lE '[ÃâðŸÂ]{3,}' "$f" 2>/dev/null; then
    echo "ERROR: mojibake en $f"
    exit 1
  fi
done
```

---

## Pendientes Activos (Z-)

Ver `docs/STATUS.md` para pendientes Z- actuales. Al cierre de cada auditoria:

| Z | Descripcion | Estado |
|---|---|---|
| Z-01 | Security headers (CSP, X-Frame-Options) | Pendiente |
| Z-02 | CORS restrictivo por ruta | Pendiente |
| Z-03 | File upload validation tipo MIME | Parcial (BYTEA 10MB) |
| Z-04 | `categoria_titulares nullable=False` | **Cerrado v1.9 (Iter 13)** |
| Z-06 | Logs estructurados JSON / audit_log table | Pendiente |

---

## Reglas Operativas

1. **NO** crear archivos nuevos en `docs/` sin necesidad documentada.
2. **NO** mover archivos sin confirmar con el usuario (preservar historico).
3. **NO** borrar `.docx` aunque parezcan viejos (son evidencia historica).
4. **NO** tocar `paso/` ni `docs/SESSION_STATE.md` (es del usuario).
5. **SI** actualizar `docs/README.md` despues de cada auditoria.
6. **SI** mantener UTF-8 sin BOM en todos los `.md`.
7. **SI** usar terminologia canonica (APDC, no APDP; Custodio RAT Manager, no RAT Manager).

---

## Reporte de Governance

```markdown
## Doc-Governance Report

**Fecha:** {fecha}
**Disparador:** {manual | post-auditoria vX.Y}
**Version vigente antes:** vX.Y
**Version vigente despues:** vX.Y

### Cambios aplicados
- [ ] docs/README.md actualizado
- [ ] docs/STATUS.md actualizado
- [ ] docs/documentacion_oficial/README.md — matriz de vigencia

### Hallazgos pendientes (no aplicados)
- H# — descripcion

### Pendientes Z-
- Z-XX — descripcion — estado
```

---

## Integracion con Otras Skills

| Skill | Relacion |
|---|---|
| `custodio-auditoria` | Al cerrar auditoria, invocar `doc-governance` para sincronizar estado |
| `qa-senior` | `doc-governance` puede pedirle revision de calidad editorial |
| `commit-helper` | Mensajes de commit para cambios de governance: `docs: governance ...` |