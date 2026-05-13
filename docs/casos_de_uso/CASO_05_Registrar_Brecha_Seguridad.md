# Caso de Uso 5: Registrar Brecha de Seguridad

## Objetivo
Registrar una brecha de seguridad para cumplir la obligación legal del Art. 14 bis y mantener trazabilidad ante la APDC.

## Caso real
Una empresa sufre un hackeo que expone datos de clientes. La ley exige notificar a la Agencia de Protección de Datos (APDC) dentro de 72 horas y a los afectados "sin dilación".

## Paso a paso

### Paso 1 — Ir a Brechas
- El usuario va al menú lateral: **"Brechas"**
- Click en el botón: **"+ Nueva brecha"**

### Paso 2 — Completar formulario
El usuario llena:

| Campo | Valor |
|-------|-------|
| Descripción | `"Ataque ransomware al servidor CRM. Extracción de base de datos de clientes con RUT, email y teléfonos."` |
| Fecha de detección | `12-05-2026 08:00` |
| RATs afectados | `"Gestión de clientes web"`, `"Marketing email"` |
| Datos comprometidos | `"Datos identificativos: nombre, RUT, email, teléfono"` |
| Medidas adoptadas | `"Servidor desconectado, cambio de credenciales, backup restaurado"` |

### Paso 3 — Sistema calcula plazos

El sistema automáticamente:

1. **Calcula horas transcurridas** → desde `fecha_deteccion` hasta ahora
2. **Muestra alerta de plazo APDC** → 72 horas para notificar
3. **Detecta urgencia** → si hay datos sensibles o menores, la notificación a titulares es inmediata
4. **Genera registro de auditoría** → cada acción queda documentada

### Paso 4 — Registrar notificaciones

El usuario marca:

| Campo | Estado |
|-------|--------|
| Notificado APDC | ☑️ (marca al notificar) |
| Fecha notificación APDC | `13-05-2026 10:30` (automático) |
| Notificado titulares | ☑️ (si corresponde) |
| Fecha notificación titulares | `13-05-2026 12:00` (automático) |

## Qué hizo el sistema internamente

1. **Registró la brecha** → tabla `security_breaches`
2. **Calculó tiempo transcurrido** → horas desde detección
3. **Mostró alertas de urgencia** → plazo APDC vs. tiempo transcurrido
4. **Validó RATs afectados** → vinculados al proceso de tratamiento
5. **Auditó cada cambio** → timestamps de notificación

## Obligaciones legales (Art. 14 bis Ley 21.719)

### Notificación a la APDC

| Plazo | Condición |
|-------|-----------|
| **72 horas** | Desde la detección de la brecha |
| Excepción | Si no hay riesgo para derechos de titulares, se puede no notificar |

### Notificación a los afectados

| Cuándo | Qué datos |
|--------|-----------|
| **Sin dilación** | Si hay datos sensibles, menores de edad, o datos financieros |

## Alertas automáticas del sistema

| Alerta | Condición |
|--------|-----------|
| 🚨 **APDC por vencer** | Quedan menos de 12 horas para notificar |
| 🚨 **APDC vencida** | Pasaron las 72 horas sin notificación |
| ⚠️ **Notificación inmediata a titulares** | Si hay datos sensibles o menores |
| 📋 **RATs afectados sin EIPD** | Refuerza la gravedad de la brecha |

## Cálculo de horas del sistema

```python
from datetime import datetime, timezone

def horas_desde_deteccion(fecha_deteccion):
    ahora = datetime.now(timezone.utc)
    return (ahora - fecha_deteccion).total_seconds() / 3600

# Ejemplo:
# Detectado: 12-05-2026 08:00
# Actual: 13-05-2026 10:00
# Horas transcurridas: 26 horas
# Quedan: 72 - 26 = 46 horas
```

## Estados de una brecha

```
Descubierta
    ↓
En curso (sin notificar)
    ↓
├── APDC notificada ✅
├── Titulares notificados ✅ (si aplica)
└── Brecha cerrada ✅
```

## Modelo de datos

```
SecurityBreach
├── id
├── company_id
├── descripcion
├── fecha_deteccion
├── rats_afectados (texto con IDs/nombres)
├── datos_comprometidos
├── medidas_adoptadas
├── notificado_apdc (bool)
├── fecha_notificacion_apdc
├── notificado_titulares (bool)
├── fecha_notificacion_titulares
├── creado_por
├── created_at
└── updated_at
```

## Endpoints de brechas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/brechas/?company_id=X` | Lista brechas de una empresa |
| POST | `/brechas/` | Crea una nueva brecha |
| PUT | `/brechas/{id}` | Actualiza una brecha |
| DELETE | `/brechas/{id}` | Elimina una brecha |

## Multas por incumplimiento (Art. 14 bis)

| Obligación | Multa |
|------------|-------|
| No notificar brecha a APDC (72h) | Hasta 20.000 UTM |
| No notificar a titulares (sin dilación) | Hasta 20.000 UTM |
| Remediation tardía | Gradual según gravedad |

## Qué logró el usuario

| Logro | Detalle |
|-------|---------|
| **Trazabilidad legal** | Registro documentado de todo el incidente |
| **Evidencia de reacción** | Timestamps de detección, notificación y medidas |
| **Cumplimiento del plazo** | Alertas para no superar las 72 horas |
| **Gestión del incidente** | Checklist de medidas correctivas |

## Diagrama de flujo

```
┌──────────────────────────┐
│  Nueva brecha            │
│  /breaches               │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Formulario:              │
│  - Descripción           │
│  - Fecha detección       │
│  - RATs afectados        │
│  - Datos comprometidos   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Sistema calcula:        │
│  - Horas transcurridas   │
│  - Plazo APDC (72h)     │
│  - Urgencia              │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Alertas en dashboard:   │
│  🚨 46h restantes APDC   │
│  ⚠️ Datos sensibles      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Usuario registra:        │
│  - notificado_apdc = true│
│  - Fecha notificación    │
│  - notificado_titulares  │
└──────────┬───────────────┘
           │
           ▼
     Brecha cerrada
```