# Skill: asesorgpt-docs

**Propósito:** Mantener la consistencia del estándar documental del módulo **Custodio Asesor (RAG)** en todas sus iteraciones futuras.

**Producto:** Custodio Asesor (RAG)
**Versión actual:** v1.0
**Mantenedor:** Equipo de Desarrollo — Custodio

---

## Cuándo usar esta skill

Activa esta skill cuando:

- El usuario pida **generar**, **actualizar** o **auditar** la documentación del Asesor.
- Se agreguen nuevos RF-ASES, HU-ASES, CU-ASES, TC-ASES, endpoints o items de backlog.
- Se modifique el código backend/frontend del Asesor y haya que reflejarlo en los .docx.
- Se ejecute una **auditoría** (comparación código vs docs).
- Se cambie la versión (v1.0 → v1.1, etc.).

---

## Workflow de mantenimiento documental

### Paso 1 — Auditar el código del Asesor

Ejecutar en paralelo (vía agente `explore` o `general`):

1. Backend: listar `backend/app/services/asesor_*.py`, `backend/app/routes/asesor.py`, `backend/app/routes/admin_asesor.py`, `backend/app/models/asesor.py`, `backend/app/schemas/asesor.py`.
2. Frontend: listar `frontend-next/app/(app)/asesor/`, `frontend-next/components/asesor/`, `frontend-next/lib/asesor-api.ts`.
3. Configuración: settings `ASESOR_*` en `backend/app/core/config.py`.

Generar tabla de hallazgos en `auditorias/[FECHA]_asesorgpt_vX.Y/AUDITORIA_ASES_VX.Y.md`.

### Paso 2 — Comparar código vs documentación

Para cada uno de los 8 documentos:

| Doc | Qué auditar |
|-----|-------------|
| ASES-DOC-01 | RF, RNF, US de alto nivel, riesgos del producto |
| ASES-DOC-02 | Cada RF-ASES coincide con su US-ASES; criterios de aceptación actualizados |
| ASES-DOC-03 | CU-ASES reflejan los flujos reales; mapa de pantallas incluye `/asesor` |
| ASES-DOC-04 | Diagrama C4 refleja nuevos componentes; ER `asesor_chunks` actualizado |
| ASES-DOC-05 | Cada endpoint tiene su request/response/error; backlog sincronizado |
| ASES-DOC-06 | TC-ASES nuevos cubiertos; criterios de salida cumplidos |
| ASES-DOC-07 | Variables `ASESOR_*` documentadas; troubleshooting actualizado |
| ASES-DOC-08 | Spec del RAG actualizado si cambia arquitectura o tuning |
| ASES-MTX | Cada fila tiene: RF → HU → CU → TC → endpoint → script |

### Paso 3 — Regla de decisión

| Pregunta | Respuesta | Acción |
|----------|-----------|--------|
| ¿Hay cambios en el código NO reflejados en docs? | Sí | GENERAR vX.Y+1 con subrayados |
| ¿El contenido del doc ya refleja el código actual? | Sí | NO generar nueva versión |
| ¿Solo cambió formato (versión en portada)? | Sí | Solo si el jefe lo requiere |
| ¿Hay nuevos endpoints/RF/HU/CU/TC detectados? | Sí | GENERAR con contenido subrayado |

### Paso 4 — Generar nueva versión

1. Copiar script existente: `build_NN_*_vX_Y.py` → `build_NN_*_vX_Y+1.py`.
2. Modificar el nuevo script:
   ```python
   import _theme_asesorgpt
   _theme_asesorgpt.DOC_VERSION = "vX.Y+1"
   ```
3. Actualizar tabla de control de versiones:
   ```python
   add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
       ("1.0", "Junio 2026", "Creación inicial del documento."),
       ("1.1", "Junio 2026", "_Auditoría: se agregan RF-ASES-13 y US-ASES-07 detectados en el código._"),
   ])
   ```
4. Contenido nuevo en tablas: envolver con `_guiones bajos_` para subrayado automático.
5. Ejecutar script con venv: `& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" ruta\script_vX_Y.py`
6. Validar `.docx` abriéndolo en Word.
7. Copiar a `docs/documentacion_oficial_asesorgpt/`.

### Paso 5 — Verificación de cierre

- [ ] Los 8 docx + matriz existen y abren en Word.
- [ ] Control de versiones presente.
- [ ] TOC insertado.
- [ ] Apéndices A/B/C en cada documento.
- [ ] Matriz de trazabilidad completa: `len(rf_ids) == len(hu_ids) == len(cu_ids) == len(tc_ids)`.
- [ ] AUDITORIA_ASES_VX.Y.md generada.
- [ ] Commit con mensaje `docs(asesorgpt): vX.Y+1` siguiendo convención.

---

## Convenciones del módulo Asesor

Ver `references/conventions.md` para detalle completo.

| Aspecto | Convención |
|---------|-----------|
| Prefijo de documentos | `ASES-DOC-NN` |
| Prefijo de identificadores | `RF-ASES-NN`, `RNF-ASES-NN`, `US-ASES-NN`, `CU-ASES-NN`, `TC-ASES-NN`, `DT-ASES-NN`, `AD-ASES-NN` |
| Carpeta de salida | `docs/documentacion_oficial_asesorgpt/` |
| Carpeta de scripts | `paso/desarrollo_de_software_estandar/_build/asesor/` |
| Theme | `_theme_asesorgpt.py` (paleta verde-dorado) |
| Naming archivos .docx | `NN_NombreDoc_AsesorCustodio_vX.Y.docx` |
| Naming archivos .py | `build_NN_nombre_asesorgpt_vX_Y.py` |
| Anchos de tabla control versiones | 1.5/2.5/3.0/10.59 cm |
| Subrayado de cambios | `_texto nuevo_` → se renderiza con underline |
| Producto en metadatos | "Custodio Asesor (módulo RAG de Custodio RAT Manager)" |

---

## Comandos útiles

```powershell
# Verificar carga del theme
& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" -c "import _theme_asesorgpt as t; print(t.BRAND_FULL)"

# Generar un documento (ejemplo)
cd "C:\Users\chelo\Desktop\RAT_opencode\paso\desarrollo_de_software_estandar\_build\asesor"
& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" build_01_vision_alcance_asesorgpt_v1_0.py

# Generar todos los documentos en batch
Get-ChildItem build_*.py | ForEach-Object {
    & "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" $_.FullName
}
```

---

## Referencias

- `references/conventions.md` — Convenciones de IDs, prefijos, naming
- `references/templates.md` — Snippets reutilizables para secciones comunes
- `references/mermaid-patterns.md` — Patrones de diagramas (C4, secuencias, ER)
- `../../paso/desarrollo_de_software_estandar/AUDIT_GUIDE.md` — Guía general de auditoría (Custodio RAT Manager, base conceptual)

---

*Skill controlada — actualizar al cambiar el estándar documental.*
