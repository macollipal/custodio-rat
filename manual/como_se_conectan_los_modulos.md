# Cómo se conectan los módulos — Vista panorámica

Esta es la vista "mapa" para entender cómo una acción en un módulo afecta a los demás. Útil cuando estás aprendiendo el sistema o cuando algo no queda claro en el flujo principal.

## Diagrama general

```
                            ┌─────────────────────┐
                            │     Dashboard       │
                            │  (resumen general   │
                            │   de cumplimiento)  │
                            └──────────┬──────────┘
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       │                               │                               │
       ▼                               ▼                               ▼
 ┌────────────┐               ┌────────────────┐               ┌────────────────┐
 │   RATs     │◄─────────────│    Brechas      │──────────────►│ Consentimientos│
 │ (tus       │  si ocurre   │  (incidentes   │  si hay      │ (registro de  │
 │ procesos)  │   incidente  │   seguridad)   │  datos       │  aceptacion)  │
 └─────┬──────┘   en estos    └────────┬───────┘  sensibles   └────────────────┘
       │            RATs                  │
       │                                  │
       ▼                                  ▼
 ┌────────────┐                  ┌────────────────┐
 │   EIPD     │                  │ Notificaciones │
 │ (eval.     │                  │ (APDC +        │
 │  impacto)  │                  │  titulares)    │
 └────────────┘                  └────────────────┘

        ┌────────────────────┐
        │       ARCO          │
        │ (solicitudes de     │
        │  derechos titulares)│
        └────────────────────┘
```

## Flujos típicos explicados

### Flujo 1: Crear un nuevo RAT con datos sensibles

```
1. Menu "Procesos RAT" → "+ Nuevo proceso"
2. Wizard 5 pasos con validación en cada paso
3. Si marco "datos sensibles = sí":
   ↓ AUTOMÁTICO
   • Custodio marca el RAT como "requiere EIPD"
   • Sugiere registrar consentimiento expreso por cada titular
   • El endpoint POST /consentimientos/ se vuelve obligatorio
4. Guardar → estado "Borrador" hasta tener EIPD completa
5. Cuando EIPD esté "completada", RAT puede pasar a "Completo"
```

### Flujo 2: Ocurre una brecha de seguridad

```
1. Menu "Brechas" → "+ Registrar brecha"
2. Completo:
   - Descripción del incidente
   - Fecha de detección (cuándo lo supiste, no cuándo pasó)
   - Naturaleza: confidencialidad / integridad / disponibilidad
3. Si marco:
   - "Incluye datos sensibles" o "menores" o "financieros":
     ↓ CUSTODIO ENCOLA TAREA para notificar titulares (sin dilación)
   - "Nivel_riesgo = alto/critico":
     ↓ CUSTODIO ENCOLA TAREA para notificar APDC (72h)
4. Las tareas se procesan vía scheduler (Vercel Cron cada 5min)
5. Cuando llegan las notificaciones, marco:
   - "Notificado APDC: sí" + fecha + folio
   - "Notificado titulares: sí" + fecha
```

### Flujo 3: Un titular pide un derecho ARCO

```
1. Titular contacta por email/presencial
2. Menu "ARCO" → "+ Nueva solicitud"
3. Selecciono tipo: acceso / rectificación / cancelación / oposición / portabilidad / bloqueo
4. La fecha de vencimiento se calcula automáticamente:
   - Hoy + 10 días hábiles (sin contar Sáb/Dom ni feriados Chile)
5. Mientras esté "abierto":
   - Aparece en el dashboard como "vencimiento próximo"
   - Si vencen los 10 días sin responder → estado "vencido"
6. Cuando respondo:
   - Cambio a "en_proceso"
   - Resuelvo con verificación de identidad (Art. 12):
     * Cédula
     * Firma digital
     * Video call
   - Genera hash SHA-256 probatorio de la respuesta (Art. 28)
7. Estado final: "resuelto" o "rechazado" (con causal fundada)
```

### Flujo 4: Auditoría APDC llega

```
1. APDC te notifica de fiscalización
2. Abres "Reportes"
3. Filtros: por empresa, por fecha, por estado
4. Exportas:
   - CSV para análisis en Excel
   - PDF para impresión
   - CNI (formato oficial APDC)
5. Custodio genera un paquete con:
   - Todos tus RATs
   - Historial de cambios (hash chain verificable)
   - Brechas y notificaciones
   - ARCO tickets
   - Consentimientos
6. Si APDC pide verificar integridad:
   - "Reportes → Verificar cadena de auditoría"
   - Muestra cada hash SHA-256 con timestamp
   - Cualquier modificación aparece explícitamente
```

---

## Glosario visual rápido

```
┌─────────────────────────────────────────────────────────┐
│ MÓDULO         │  AFECTA A                    │ CUÁNDO   │
├─────────────────────────────────────────────────────────┤
│ Crear RAT      │  Dashboard, Brechas          │ Al inicio│
│ Crear Brecha   │  Dashboard, ARCO, Notificaciones│ Al inci-│
│                │                              │ dente  │
│ Crear ARCO     │  Dashboard, Notificaciones   │ Cuando   │
│                │                              │ titular  │
│                │                              │ pide    │
│ Registrar      │  Dashboard, Brechas (si      │ Cuando   │
│ Consentimiento │  datos sensibles)            │ titular  │
│                │                              │ acepta  │
│ Crear EIPD     │  RAT (cambia estado)        │ Antes    │
│                │                              │ de trat. │
│ Aprobar RAT    │  Dashboard, Notificaciones   │ Cuando   │
│                │                              │ completo │
└─────────────────────────────────────────────────────────┘
```

---

¿Perdido? Volvé al **[README principal](README.md)**.