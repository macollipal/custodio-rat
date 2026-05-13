@../backend/CLAUDE.md

## Reglas adicionales de Custodio Frontend

### Flujo de onboarding
- Si el usuario hace login y no hay empresas → redirige a `/onboarding`
- Si el usuario tiene sesión activa pero el backend retorna 401 → limpia localStorage y redirige a `/login`
- AppContext valida el token con `GET /auth/me` al cargar

### Ley 21.719 — Conceptos clave

**RAT (Registro de Actividades de Tratamiento)** — Art. 16
9 campos mínimos obligatorios: nombre_proceso, categoria_titulares, categoria_datos, finalidad, base_legal, fuente_datos, plazo_retencion.

**Datos sensibles** — Art. 2 letra g
7 categorías: origen racial/étnico, situación socioeconómica, salud, vida sexual, opiniones políticas, afiliación sindical, biometría.

**Art. 16 BIS** — Datos biométricos de identificación
Tratamiento específico para identificar inequívocamente. Requiere EIPD previa. En laboral, consentimiento NO es base válida.

**Base legal: Interés legítimo** — Art. 16
Requiere test de 3 pasos documentado:
1. ¿Existe interés legítimo real?
2. ¿El tratamiento es necesario para ese interés?
3. ¿Prevalece sobre los derechos del titular?

**Encargado del tratamiento** — Art. 14 quáter
Todo tercero que trata datos por cuenta del responsable debe tener contrato de encargo.

**Brechas de seguridad** — Art. 14 bis
72 horas para notificar a la APDP. Notificar a titulares sin dilación si hay datos sensibles, menores o financieros.

**EIPD** — Art. 15 bis
Evaluación de Impacto en Protección de Datos. Obligatoria cuando hay datos sensibles, perfilamiento automatizado o transferencias internacionales de alto riesgo.

### Convenciones de datos

- Estados RAT: `borrador` | `completo` | `en_revision` | `aprobado`
- Estados EIPD: `no_requerida` | `pendiente` | `en_proceso` | `completada`
- Roles empresa: `admin` | `editor` | `viewer`
- Roles globales: `superadmin` | `admin_empresa` | `usuario`

### Patrón de guardado

Para crear o actualizar entidades, el flujo es:
1. Validar campos obligatorios con `toast.error()` si faltan
2. Llamar función de `api.ts`
3. En `onDone` limpiar view y hacer `load()` o actualizar cache
4. En `catch` mostrar `toast.error(e instanceof Error ? e.message : 'Error al guardar.')`

### Mapeo de campos RAT — Backend vs Frontend

El backend calcula completitud con 10 campos (7 obligatorios + 3 recomendados).
El drawer del RAT debe mostrar TODOS los campos del modelo para que el usuario sepa qué falta.

**Campos en el modelo RAT (backend):**
```
# Identificación
nombre_proceso, categoria_titulares, fuente_datos, destinatarios, nombre_encargado
tiene_contrato_encargado

# Base legal y finalidad
base_legal, finalidad, test_interes_legitimo

# Datos tratados
categoria_datos, tipo_dato_sensible
datos_sensibles, evaluacion_impacto, estado_eipd, fecha_eipd, decisiones_automatizadas

# Almacenamiento y transferencias
plazo_retencion, medidas_seguridad
transferencia_datos, transferencia_internacional, pais_destino, garantias_transferencia_int

# Metadatos
estado, observaciones_auditoria, created_by, updated_by, created_at, updated_at
```

**Secciones del drawer:**
1. Identificación → categoria_titulares, fuente_datos, destinatarios, nombre_encargado
2. Base legal y finalidad → base_legal, finalidad, test_interes_legitimo
3. Datos tratados → categoria_datos, tipo_dato_sensible
4. Almacenamiento y transferencias → plazo_retencion, medidas_seguridad, transferencia_datos, pais_destino, garantias_transferencia_int
5. Información del registro → created_by, created_at, updated_at, observaciones_auditoria

**Badges de flags** (arriba del drawer, junto a estado):
- `datos_sensibles` → amarillo
- `evaluacion_impacto` → azul
- `transferencia_internacional` → púrpura
- `decisiones_automatizadas` → gris

**Nivel de riesgo:**
- `Crítico` → badge rojo con ⚠️
- `Alto` → badge amarillo
- `Medio` → badge azul
- `Bajo` → badge gris