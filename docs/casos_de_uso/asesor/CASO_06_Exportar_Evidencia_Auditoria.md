# Caso de Uso 6: Exportar Evidencia para Auditoría

## Objetivo
Generar evidencia formal del RAT para demostrar cumplimiento ante una fiscalización o auditoría.

## Contexto

La Ley 21.719 establece que el RAT es el documento que la Agencia de Protección de Datos Personales (APDC) solicitará primero en caso de fiscalización. No basta tener los datos — hay que demostrar orden, trazabilidad y cumplimiento.

**Tu sistema NO vende: formularios.**
**Tu sistema vende: orden, trazabilidad, cumplimiento, evidencia, reducción de riesgo legal.**

## Paso a paso

### Paso 1 — Ir a Reportes
- El usuario va al menú lateral: **"Reportes"**
- Ve un dashboard con KPIs, mini gráficos y tabla de RATs

### Paso 2 — Aplicar filtros
- Filtra por estado, base legal, datos sensibles, EIPD, transferencia internacional
- Agrupa por: estado / base legal / nivel de riesgo
- Guarda filtros con nombre para reuse
- Resultado: vista filtrada específica para la auditoría

### Paso 3 — Exportar evidencia

**Opción A — Exportar CSV**
- Click en botón **"📥 CSV"**
- Descarga archivo con todas las columnas configuradas
-可用于导入 a Excel, Google Sheets, sistemas de gestión documental

**Opción B — Exportar PDF**
- Click en botón **"📥 PDF"**
- Genera documento formal con:
  - Título del reporte
  - Nombre de la empresa responsable
  - Fecha de generación
  - Tabla con columnas configuradas
  - Encabezado azul corporativo

### Paso 4 — Revisar detalle de cada RAT
- Click en cualquier RAT de la tabla → se abre Drawer lateral
- Muestra historial completo de auditoría (creado, editado, revisado)
- Test de interés legítimo documentado
- Flags activos (sensible, EIPD, transferencia, decisiones automatizadas)

## Qué exporta el PDF

| Campo | Descripción |
|-------|-------------|
| ID | Identificador único del RAT |
| Proceso | Nombre del tratamiento |
| Base Legal | Fundamento jurídico (Art. 13) |
| Estado | Borrador / Completo / En revisión / Aprobado |
| Compl. | Porcentaje de completitud |
| Riesgo | Bajo / Medio / Alto / Crítico |
| Sens. | Si trata datos sensibles |
| EIPD | Si requiere evaluación de impacto |
| Transf. Int. | Si tiene transferencia internacional |

## Qué exporta el CSV

Incluye todas las columnas configurables (14 opciones):

```
Proceso, Base legal, Estado, Creado por, Completitud, Flags,
Categoría titulares, Fuente de datos, Finalidad, Plazo retención,
Medidas seguridad, Destinatarios, País destino, Nivel riesgo
```

## Filtros disponibles para auditoría

| Filtro | Uso en auditoría |
|--------|-----------------|
| Estado | RATs completos = cumplimiento mínimo |
| Datos sensibles | Mostrar qué trata categorías especiales |
| EIPD requerida | RATs con obligación de evaluación |
| Transferencia internacional | Datos fuera de Chile = garantías |
| Base legal | Distribución de fundamentos jurídicos |
| Agrupar por estado/riesgo/base legal | Vista ejecutiva para el DPO |

## Qué está vendiendo realmente el sistema

### Antes de Custodio
- La empresa no sabe qué datos tiene
- No puede demostrar cuándo se creó cada RAT
- No hay evidencia de quién hizo cambios
- Las bases legales son genéricas o incorrectas
- Si viene una fiscalización → chaos

### Después de Custodio
- El DPO tiene vista clara de todos los tratamientos
- Cada RAT tiene trazabilidad completa (creado por, fecha, cambios)
- Las alertas automáticas indican qué está incompleto
- La evidencia está lista para exportar en minutos
- En caso de fiscalización → orden, calma, evidencia

## Evidencia de cumplimiento que genera

| Tipo de evidencia | Qué demuestra |
|-------------------|---------------|
| PDF formal | Existenssssscia formal del RAT para la APDC |
| CSV con metadata | Detalle técnico de cada campo |
| Historial de auditoría | Quién, cuándo, qué cambió |
| KPIs de completitud | Madurez del programa de cumplimiento |
| Alertas activas | Qué falta por corregir |

## Diagrama de flujo de exportación

```
┌──────────────────────────────┐
│  Módulo Reportes             │
│  /reportes                   │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Filtros aplicados:          │
│  - Estado                    │
│  - Base legal                │
│  - Datos sensibles           │
│  - EIPD                      │
│  - Transf. internacional      │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Vista previa:               │
│  - KPI cards                 │
│  - Mini gráficos             │
│  - Tabla filtrada            │
└──────────┬───────────────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
┌──────────┐ ┌──────────┐
│  📥 CSV  │ │  📥 PDF  │
│          │ │          │
│ jsPDF +  │ │ Export   │
│ autotable│ │ formal   │
└──────────┘ └──────────┘
```

## Archivos técnicos involucrados

| Archivo | Función |
|---------|---------|
| `app/(app)/reportes/page.tsx` | UI de reportes con filtros y exportación |
| `lib/api.ts` | Endpoints de exportación (`exportarCsv`, `exportarPdf`) |
| `services/export_service.py` | Lógica de generación CSV/PDF desde el backend |
| `services/export_cni_service.py` | Formato CNI para la APDC |

## Para la APDC — Formato CNI

El sistema también puede exportar en formato **CNI** (Comunicación de No Inclusión), utilizado para presentar el RAT ante la Agencia de Protección de Datos Personales de Chile.

```
GET /rats/export/cni?company_id=X
```

Genera archivo de texto formateado específicamente para cumplimiento regulatorio chileno.