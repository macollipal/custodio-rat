# Caso de Uso 4: Detectar Incumplimiento Automáticamente

## Objetivo
Que el sistema detecte automáticamente riesgos de incumplimiento cuando el usuario configura un proceso que trata datos biométricos.

## Caso real
Una empresa implementa un sistema de reconocimiento facial para controlar el acceso de empleados a sus instalaciones. Al crear el RAT, el sistema detecta inmediatamente que se trata de datos biométricos y genera alertas de cumplimiento.

## Paso a paso

### Paso 1 — Crear nuevo RAT biométrico
- El usuario va a **"Procesos RAT"**
- Click en **"+ Nuevo proceso"**
- Nombre del proceso: `"Control de acceso facial"`

### Paso 2 — Aplicar plantilla o marcar flags
El usuario puede:
- **Opción A**: Usar plantilla `"Control biométrico asistencia"` → campos prellenados automáticamente
- **Opción B**: Marcar manualmente los flags:
  - ✅ **"El proceso trata datos sensibles"**
  - ✅ **Tipo de dato sensible**: `"Datos biométricos de identificación (Art. 16 BIS)"`

### Paso 3 — Sistema detecta incumplimiento

El sistema analiza los campos y detecta:

1. **Datos biométricos** → activa Art. 16 BIS
2. **Base legal**: por defecto viene `"Consentimiento del titular"` → **INCUMPLIMIENTO**
3. **No tiene EIPD completada** → **ALERTA**
4. **No hay encargado con contrato** → **ALERTA**

### Paso 4 — Alertas generadas automáticamente

El sistema muestra estas alertas en la auditoría:

**⚠️ Consentimiento + datos sensibles**: El consentimiento del empleado NO es base válida para biometría en contextos laborales (relación jerárquica asimétrica).

**🔐 BIOMETRÍA**: Los datos biométricos destinados a identificar inequívocamente a una persona se rigen por el Art. 16 BIS. Requieren base legal específica y EIPD previa.

**📋 EIPD PENDIENTE**: Este proceso requiere Evaluación de Impacto en Protección de Datos y aún no está completada.

**📄 ENCARGADO SIN CONTRATO**: Se registró un encargado del tratamiento pero no se ha confirmado la existencia de un contrato de encargo.

### Paso 5 — Correcciones sugeridas

| Campo | Error detectado | Corrección sugerida |
|-------|-----------------|---------------------|
| base_legal | Consentimiento inválido para biometría laboral | Cambiar a: `"Obligación legal"` (Art. 33 Código del Trabajo) |
| evaluacion_impacto | No está marcada | Activar → EIPD obligatoria |
| tiene_contrato_encargado | No especificado | Agregar contrato con proveedor |
| test_interes_legitimo | No aplica | Eliminar (no corresponde a obligación legal) |

## Qué logró la empresa

1. **Entiende los riesgos** → sabe que su implementación actual es insuficiente
2. **Evita incumplimientos** → corrige antes de una fiscalización
3. **Documenta correctamente** → tiene evidencia de que evaluó los riesgos
4. **Reduce exposición** → el Art. 16 BIS exige EIPD previa, sin ella es infracción gravísima

## Detección de riesgos — Lógica del sistema

El nivel de riesgo se calcula automáticamente:

```python
score = 0
if datos_sensibles: score += 2
if evaluacion_impacto and estado_eipd != "completada": score += 2
if decisiones_automatizadas: score += 2
if transferencia_internacional and not garantias: score += 1
if "biométric" in tipo_dato_sensible: score += 1
if nombre_encargado and not tiene_contrato_encargado: score += 1

# score >= 7 → "critico"
# score >= 5 → "alto"
# score >= 3 → "medio"
# score < 3 → "bajo"
```

Para biométricos sin EIPD: **score = 2 (sensibles) + 2 (EIPD pendiente) + 1 (biométricos) = 5 → riesgo "alto"**

## Alertas específicas de biométricos

| Alerta | Causa | Referencia legal |
|--------|-------|------------------|
| Base legal inválida | Consentimiento para biometría laboral | Art. 16 BIS + caso Martorell (AEPD) |
| EIPD requerida | Datos biométricos identificados | Art. 15 bis Ley 21.719 |
| Contrato de encargado | Proveedor externo trata los datos | Art. 14 quáter Ley 21.719 |
| Medidas de seguridad | Datos biométricos requieren cifrado | Art. 14 Ley 21.719 |

## Campos que el sistema valida para biométricos

| Campo | Obligatorio | Valor correcto |
|-------|:-----------:|----------------|
| base_legal | ✅ | "Obligación legal" (no consentimiento) |
| datos_sensibles | ✅ | true |
| tipo_dato_sensible | ✅ | "Datos biométricos de identificación (Art. 16 BIS)" |
| evaluacion_impacto | ✅ | true |
| estado_eipd | ✅ | "completada" |
| tiene_contrato_encargado | ✅ | true |
| nombre_encargado | ✅ | Nombre del proveedor |
| medidas_seguridad | ✅ | Cifrado, acceso por roles |
| test_interes_legitimo | ❌ | No corresponde |

## Diagrama de flujo de detección

```
┌──────────────────────────────┐
│  Usuario marca:              │
│  datos_sensibles = true      │
│  tipo_dato_sensible =        │
│  "Biométricos (Art. 16 BIS)" │
└──────────────┬───────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Sistema detecta:               │
│  1. ¿base_legal = Consentimiento│
│     → ⚠️ ALERTA: inválido       │
│  2. ¿evaluacion_impacto?        │
│     → ⚠️ EIPD obligatoria       │
│  3. ¿nombre_encargado?          │
│     → ⚠️ Falta contrato         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Observaciones de auditoría     │
│  generadas automáticamente     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Nivel de riesgo = ALTO (score=5)│
│  Dashboard muestra alerta 🚨    │
└──────────────────────────────┘
```

## Multas asociadas a incumplimiento biométrico (Art. 14 bis)

| Infracción | Multa |
|------------|-------|
| Tratamiento de datos biométricos sin EIPD | Hasta 20.000 UTM (~USD 1.550.000) |
| Base legal incorrecta para sensibles | 10.000 a 20.000 UTM |
| Falta de contrato con encargado | 5.000 a 10.000 UTM |
| No notificación de brechas (si aplica) | Hasta 20.000 UTM |