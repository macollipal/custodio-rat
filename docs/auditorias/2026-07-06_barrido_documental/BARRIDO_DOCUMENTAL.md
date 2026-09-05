# Barrido documental - Custodio RAT

Fecha: 2026-07-06  
Alcance: archivos `.md`, `.doc` y `.docx` bajo el repositorio, excluyendo dependencias (`backend/venv`, `node_modules`, `.git`).  
Modo: lectura e inventario; no se eliminaron ni movieron archivos.

## Resumen ejecutivo

Custodio tiene una base documental abundante y util: manuales, auditorias, BPMN, documentos oficiales versionados, backlog, seguridad, despliegue y material de AsesorCustodio. El problema principal no es falta de documentacion, sino gobernanza documental: hay varias fuentes que dicen ser "actuales", historicos mezclados con documentos vigentes, archivos temporales de Word, rutas rotas en indices y diferencias de encoding en varios Markdown antiguos.

Estado estimado:

| Area | Estado | Comentario |
|---|---:|---|
| Cobertura funcional | Alta | RAT, ARCO, brechas, EIPD, consentimientos, transparencia, encargados y asesor estan documentados en algun nivel. |
| Trazabilidad historica | Alta | Hay documentos v1.0 a v1.9 y auditorias por fecha. |
| Claridad de fuente canonica | Media-baja | README, docs/README, CHANGELOG, SESSION_STATE y docx oficiales no estan completamente alineados. |
| Limpieza de artefactos | Media | Persisten lock files `~$*.docx` y duplicacion entre carpetas oficiales/regeneradas. |
| Riesgo de obsolescencia | Alto | `docs/README.md` referencia v1.6-BETA como actual aunque ya existe v1.9. |

## Inventario

Conteo detectado con `rg --files`:

| Tipo | Cantidad |
|---|---:|
| Markdown `.md` | 94 |
| Word `.docx` | 122 |
| Total | 216 |

Conteo extendido con lectura recursiva de `.docx` incluyendo `paso/`:

| Tipo | Cantidad |
|---|---:|
| Word `.docx` | 126 |
| Lock/temp Word `~$*.docx` | 6 |

Directorios con mayor concentracion:

| Directorio | Cantidad |
|---|---:|
| `docs/documentacion_oficial` | 97 |
| `docs/documentacion_oficial_asesorgpt/_regen` | 14 |
| `docs/auditorias/2026-06-08_auditoria_v1.2` | 11 |
| `docs/documentacion_oficial_asesorgpt` | 9 |
| `docs` | 8 |
| `docs/casos_de_uso` | 7 |
| `docs/casos_de_uso/asesor` | 7 |

## Hallazgos

### H1 - Indice documental desactualizado

`docs/README.md` todavia presenta la documentacion oficial como v1.6-BETA actual, pero existen documentos v1.9 fechados el 2026-07-05 en `docs/documentacion_oficial/` y auditoria v1.9 en `docs/auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md`.

Impacto: un usuario nuevo o auditor puede tomar como vigente una version vieja.

Recomendacion:

- Actualizar `docs/README.md` para declarar v1.9 como version vigente.
- Agregar tabla "vigente vs historico".
- Corregir enlaces a `documentacion_oficial`: el README usa `../documentacion_oficial/`, pero desde `docs/README.md` la ruta correcta es `documentacion_oficial/`.

### H2 - Documentacion oficial versionada sin politica de archivo

`docs/documentacion_oficial/` contiene 97 `.docx`, con familias desde v1.0 hasta v1.9. Esto es valioso como historico, pero actualmente el directorio no distingue claramente:

- ultima version vigente;
- historico;
- versiones intermedias reemplazadas;
- documentos antiguos que no tienen equivalente v1.9.

Ejemplos:

- `02_Requisitos_*` existe en v1.0, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6, v1.6.5, v1.7, v1.9.
- `06_Arquitectura_*` existe en varias versiones, pero v1.6.5 y v1.9 son mucho mas livianos que v1.7, lo que sugiere cambio de generacion o posible perdida de contenido/imagenes.
- `05_Diseno_Funcional_*`, `07_Modelo_Datos_*` y `11_Manual_Despliegue_*` no tienen version v1.9.

Recomendacion:

- Crear `docs/documentacion_oficial/README.md` con matriz de vigencia.
- Mantener solo links canonicos a v1.9 para documentos activos.
- Mover versiones antiguas a `docs/documentacion_oficial/historico/` o dejarlas con un README que explique que son historicas.

### H3 - Archivos temporales de Word versionados o presentes en el workspace

Se detectaron lock files:

- `docs/~$nual_Usuario_Custodio.docx`
- `docs/documentacion_oficial_asesorgpt/_regen/~$_QA_AsesorCustodio_v1.0.docx`
- `docs/documentacion_oficial_asesorgpt/_regen/~$_Modulo_AsesorCustodio_v1.0.docx`
- `docs/documentacion_oficial_asesorgpt/_regen/~$_CU_Diseno_AsesorCustodio_v1.0.docx`
- `docs/documentacion_oficial_asesorgpt/_regen/~$_Arquitectura_Datos_AsesorCustodio_v1.0.docx`
- `docs/documentacion_oficial_asesorgpt/_regen/~$_API_Backlog_AsesorCustodio_v1.0.docx`

Impacto: ruido, riesgo de conflicto, falsos positivos en inventario y mala senal para entrega a terceros.

Recomendacion:

- Eliminar esos archivos del workspace si no estan abiertos por Word.
- Verificar que `.gitignore` cubra `~$*.docx` y `~$*`.

### H4 - Encoding inconsistente en varios Markdown

Varios archivos Markdown muestran mojibake (`Ã`, `â`, `ðŸ`, etc.). Ejemplos visibles:

- `README.md`
- `docs/README.md`
- `docs/backlog_seguimiento.md`
- `docs/CLEANUP_2026-07-03.md`

Impacto: deteriora lectura, busqueda, presentacion y exportacion a documentos oficiales.

Recomendacion:

- Normalizar todos los `.md` a UTF-8.
- Ejecutar una pasada de deteccion de mojibake.
- Priorizar README raiz, `docs/README.md`, backlog y docs de entrega.

### H5 - Backlogs y estados no reconciliados

Hay al menos tres fuentes de estado:

- `docs/backlog_seguimiento.md`
- `docs/SESSION_STATE.md`
- `docs/auditorias/2026-07-05_auditoria_v1.9/AUDITORIA_V1.9.md`

No estan completamente alineadas. Por ejemplo, `docs/backlog_seguimiento.md` mantiene muchas mejoras como pendientes en una consultoria 2026-06-23, mientras auditorias posteriores declaran algunos avances y nuevos pendientes tecnicos.

Impacto: dificulta decidir que construir primero y que ya esta cerrado.

Recomendacion:

- Crear un backlog canonico unico: `docs/backlog.md` o issue tracker.
- Marcar `docs/backlog_seguimiento.md` como historico si no se va a mantener.
- En cada auditoria, agregar seccion "actualiza backlog canonico: si/no".

### H6 - Duplicacion entre AsesorCustodio y `_regen`

Existen dos arboles:

- `docs/documentacion_oficial_asesorgpt/`
- `docs/documentacion_oficial_asesorgpt/_regen/`

Ambos contienen documentos con nombres equivalentes. `_regen` parece mas nuevo (2026-06-15) pero no hay README que explique si reemplaza al directorio base o si es salida temporal.

Impacto: ambiguedad sobre que documento debe compartirse o auditarse.

Recomendacion:

- Definir fuente canonica: base o `_regen`.
- Si `_regen` es temporal, moverlo a `archive/` o excluirlo de entrega.
- Si `_regen` es vigente, promoverlo y eliminar/marcar obsoletos los equivalentes.

### H7 - Documentos generados fuera de `docs/` sin clasificacion

Se detectaron documentos en `paso/`, por ejemplo:

- `paso/docs/Documentacion_Custodio_RAT_Manager.docx`
- `paso/ley_21719/Auditoria_Cumplimiento_Custodio_Ley21719_v1.0.docx`
- `paso/ley_21719/Auditoria_Cumplimiento_Custodio_Ley21719_v1.1.docx`

Impacto: material importante puede quedar fuera de indices y entregables.

Recomendacion:

- Decidir si `paso/` es staging, archivo historico o fuente activa.
- Si contiene entregables reales, enlazarlo desde `docs/README.md` o migrarlo a `docs/`.

### H8 - Pendientes tecnicos de auditoria v1.9 deben subir al roadmap

La auditoria v1.9 deja pendientes criticos/no abordados:

- Z-01: Security headers (CSP, X-Frame-Options).
- Z-02: CORS restrictivo por ruta.
- Z-03: File upload validation tipo MIME (parcialmente resuelto por limite BYTEA 10MB).
- Z-04: `categoria_titulares nullable=False` con migracion breaking.
- Z-06: logs estructurados JSON / audit log table.

Impacto: son mejoras transversales de seguridad, cumplimiento y operacion; no deberian quedar solo en una auditoria historica.

Recomendacion:

- Copiarlas al backlog canonico con prioridad y responsable.
- Mantener la auditoria como evidencia, no como tablero operativo.

## Recomendaciones priorizadas

### P0 - Limpieza segura inmediata

1. Borrar lock files `~$*.docx` si Word no los esta usando.
2. Actualizar `docs/README.md` para v1.9.
3. Corregir rutas rotas o relativas incorrectas del indice documental.
4. Marcar `docs/backlog_seguimiento.md` como historico o reconciliarlo.

### P1 - Gobernanza documental

1. Crear `docs/documentacion_oficial/README.md` con:
   - documento;
   - version vigente;
   - fecha;
   - versiones historicas;
   - observacion.
2. Crear `docs/STATUS.md` como fuente canonica de estado actual.
3. Definir regla: auditorias historicas no son backlog activo.
4. Definir regla para `_regen`: temporal, historico o canonico.

### P2 - Calidad editorial

1. Normalizar encoding UTF-8 en Markdown.
2. Homologar nombres: `APDP` vs `APDC`, "Custodio RAT" vs "RAT Manager", "AsesorGPT" vs "AsesorCustodio".
3. Separar documentos tecnicos, legales y comerciales.
4. Agregar fecha de vigencia y estado a cada README importante.

### P3 - Automatizacion

1. Agregar script `scripts/maintenance/docs_inventory.py` o equivalente PowerShell.
2. Validar links Markdown en CI.
3. Detectar lock files `~$*` en pre-commit.
4. Detectar mojibake y documentos sin indice.

## Propuesta de estructura objetivo

```text
docs/
  README.md                         # indice vigente, apunta a estado actual
  STATUS.md                         # version actual, score, pendientes activos
  backlog.md                        # backlog canonico
  documentacion_oficial/
    README.md                       # matriz de vigencia
    vigente/
    historico/
  auditorias/
    README.md                       # indice historico por fecha/version
  manuales/
  cumplimiento/
  arquitectura/
  despliegue/
  desarrollo/
```

## Conclusion

La documentacion de Custodio es amplia y con buen nivel de trazabilidad, pero necesita una capa de gobierno: una fuente canonica de version vigente, separacion entre activo e historico, limpieza de temporales y normalizacion de encoding. La mejora con mayor retorno es ordenar `docs/README.md`, `documentacion_oficial` y el backlog; eso reduce confusion de inmediato y deja las auditorias como evidencia, no como sistema de gestion.
