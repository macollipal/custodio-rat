# `_build/asesor/` — Línea base de versionamiento documental

**Producto:** Custodio Asesor (módulo RAG de Custodio RAT Manager)
**Versión actual:** v1.0
**Mantenedor:** Equipo de Desarrollo — Custodio
**Skill relacionada:** `.opencode/skills/asesorgpt-docs/SKILL.md`

---

## Propósito

Esta carpeta contiene los **scripts de build** que regeneran los 8 documentos `.docx`
+ 1 matriz de trazabilidad de la carpeta `docs/documentacion_oficial_asesorgpt/`.

Es la **línea base (source of truth)** del versionamiento documental. Los `.docx`
son artefactos compilados; estos scripts son la fuente.

---

## Estructura

```
_build/asesor/
├── _theme_asesorgpt.py                  ← Tema visual (paleta verde-dorado)
├── requirements.txt                     ← Dependencias Python
├── README.md                            ← Este archivo
├── build_01_vision_alcance_asesorgpt_v1_0.py
├── build_02_requisitos_hu_asesorgpt_v1_0.py
├── build_03_cu_diseno_asesorgpt_v1_0.py
├── build_04_arquitectura_datos_asesorgpt_v1_0.py
├── build_05_api_backlog_asesorgpt_v1_0.py
├── build_06_qa_asesorgpt_v1_0.py
├── build_07_despliegue_tecnico_asesorgpt_v1_0.py
├── build_08_modulo_asesor_asesorgpt_v1_0.py
└── build_matriz_asesorgpt_v1_0.py
```

---

## Cómo regenerar un documento

```powershell
# Activar venv del backend (que tiene python-docx instalado)
& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" `
    "paso\desarrollo_de_software_estandar\_build\asesor\build_01_vision_alcance_asesorgpt_v1_0.py"
```

El script genera el archivo directamente en `docs/documentacion_oficial_asesorgpt/`
sobrescribiendo el `.docx` existente.

## Cómo regenerar todos los documentos en batch

```powershell
cd "C:\Users\chelo\Desktop\RAT_opencode\paso\desarrollo_de_software_estandar\_build\asesor"
Get-ChildItem build_*.py | ForEach-Object {
    & "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" $_.FullName
}
```

## Cómo generar una nueva versión (v1.1, v1.2, ...)

1. Copiar el script `build_NN_..._v1_0.py` → `build_NN_..._v1_1.py`
2. En el nuevo script, agregar (después del import):
   ```python
   import _theme_asesorgpt
   _theme_asesorgpt.DOC_VERSION = "v1.1"
   ```
3. Actualizar la lista `changes` en `add_version_control(...)` con la nueva fila
4. Envolver con `_guiones bajos_` el texto nuevo en las tablas (convención de subrayados)
5. Pasar `underline_new=True` a `add_styled_table(...)` para que se renderice
6. Cambiar `OUT_FILE = ...v1.0.docx` → `...v1.1.docx`
7. Correr el script y validar abriendo el `.docx` en Word

---

## Convenciones del módulo Asesor

| Aspecto | Convención |
|---------|-----------|
| Prefijo de documentos | `ASES-DOC-NN` |
| Prefijo de identificadores | `RF-ASES-NN`, `RNF-ASES-NN`, `US-ASES-NN`, `CU-ASES-NN`, `TC-ASES-NN`, `DT-ASES-NN`, `AD-ASES-NN` |
| Carpeta de salida | `docs/documentacion_oficial_asesorgpt/` |
| Theme | `_theme_asesorgpt.py` (paleta verde-dorado) |
| Naming archivos .docx | `NN_NombreDoc_AsesorCustodio_vX.Y.docx` |
| Naming archivos .py | `build_NN_nombre_asesorgpt_vX_Y.py` |
| Anchos de tabla control versiones | 1.5 / 2.5 / 3.0 / 10.59 cm |
| Subrayado de cambios | `_texto nuevo_` → se renderiza con underline |
| Producto en metadatos | "Custodio Asesor (módulo RAG de Custodio RAT Manager)" |

---

## Dependencias

- **python-docx** ≥ 1.0 — manipulación de `.docx`
- **Pillow** ≥ 10.0 — escalado de imágenes Mermaid
- **npx / @mermaid-js/mermaid-cli** ≥ 10.9 — renderizado de diagramas (opcional;
  si no está disponible, los `add_figure()` insertan un placeholder PNG de 1x1)

Si las dependencias no están en el venv del backend, instalarlas con:
```powershell
& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\pip.exe" install -r requirements.txt
```

---

## Validación de los `.docx` regenerados

Después de regenerar, comparar contra los originales en `docs/documentacion_oficial_asesorgpt/`:

```powershell
& "C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe" -c "
from docx import Document
d1 = Document(r'docs\documentacion_oficial_asesorgpt\01_Vision_Alcance_AsesorCustodio_v1.0.docx')
d2 = Document(r'docs\documentacion_oficial_asesorgpt\_regen\01_Vision_Alcance_AsesorCustodio_v1.0.docx')
print('Párrafos: orig=%d regen=%d' % (len(d1.paragraphs), len(d2.paragraphs)))
print('Tablas: orig=%d regen=%d' % (len(d1.tables), len(d2.tables)))
"
```

Una diferencia menor en número de párrafos/tablas es esperable por rsids de
python-docx. Lo importante es que el contenido textual y la estructura coincidan.

---

*Mantenedor: equipo Custodio · Última actualización: Junio 2026*
