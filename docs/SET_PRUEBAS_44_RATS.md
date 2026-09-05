# Set de Pruebas: 44 RATs para Custodio RAT Manager v1.6.5

> **Generado:** 2026-07-02  
> **Versión:** v1.6.5  
> **Propósito:** Validar manualmente todos los flujos legales de la Ley 21.719

## 📋 Índice

1. [Cómo usar esta guía](#cómo-usar-esta-guía)
2. [CRÍTICOS (C1-C8)](#críticos-c1-c8)
3. [NORMALES (N1-N6)](#normales-n1-n6)
4. [TIPOS DE DATO SENSIBLE (S1-S6)](#tipos-de-dato-sensible-s1-s6)
5. [ESTADOS EIPD (E1-E4)](#estados-eipd-e1-e4)
6. [BASES LEGALES (B1-B7)](#bases-legales-b1-b7)
7. [ENCARGADO (EN1-EN3)](#encargado-en1-en3)
8. [DECISIONES AUTOMATIZADAS (A1-A3)](#decisiones-automatizadas-a1-a3)
9. [FRONTERA (F1-F7)](#frontera-f1-f7)
10. [Auditoría (AUDIT-1)](#auditoría-audit-1)

---

## Cómo usar esta guía

Cada RAT tiene una ficha con:

- **Nombre**: nombre único para identificarlo
- **Objetivo**: qué error/comportamiento se está probando
- **Campos**: valores exactos a ingresar
- **Flujo esperado**: pasos y resultado esperado
- **Resultado esperado**: ✅ éxito / ❌ error / ⚠️ alerta

### Formas de crear los RATs

Tienes **3 opciones**:

| Opción | Cómo | Velocidad |
|--------|------|-----------|
| **A) Manual UI** | Usar el wizard de creación, un RAT a la vez | Lenta (~5 min/RAT) |
| **B) Script SQL** | Ejecutar `44_rats_prueba.sql` en Neon PostgreSQL | Rápida (~30 seg/insert, 41 RATs) |
| **C) Mixto** | SQL para normales + manual para críticos | Equilibrado |

### Pasos previos (Opción B)

```bash
# 1. Conectar a Neon QA
psql "postgresql://user:pass@ep-fragrant-...neon.tech/custodio_qa?sslmode=require"

# 2. Obtener IDs
SELECT id, nombre FROM companies LIMIT 5;
SELECT id, username FROM users LIMIT 5;

# 3. Editar 44_rats_prueba.sql y reemplazar :company_id y :user_id

# 4. Ejecutar
\i 44_rats_prueba.sql

# 5. Verificar
SELECT count(*) FROM rats WHERE nombre_proceso LIKE 'RAT-%';
```

---

## CRÍTICOS (C1-C8)

### C1: Biometría + Transferencia Internacional + EIPD Pendiente

**Objetivo:** Verificar flujo completo con EIPD + Consentimiento + Encargado

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C1-Biometrico-TransIntl` |
| **Tipo de proceso** | Control biométrico asistencia |
| **Categoría datos** | Datos biométricos de identificación (huella dactilar, facial o equivalente), registro de hora de entrada/salida |
| **Categoría titulares** | Trabajadores sujetos a control de asistencia |
| **Finalidad** | Control de horario y asistencia del personal para cumplimiento de jornada laboral |
| **Base legal** | Datos biométricos de identificación (Art. 16 BIS) |
| **Fuente datos** | Relojes biométricos de huella dactilar en todas las sedes |
| **Plazo retención** | 5 años desde último registro (según normativa laboral) |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Datos biométricos de identificación (Art. 16 BIS) |
| **EIPD** | ✅ Sí |
| **Estado EIPD** | Pendiente |
| **Transferencia internacional** | ✅ Sí |
| **País destino** | Estados Unidos |
| **Garantías transferencia** | Cláusulas Contractuales Tipo (SCC) |

**Flujo esperado:**
1. Crear RAT → Guardar → ✅ OK (backend acepta estado_eipd="pendiente")
2. En el wizard: completar campos de consentimiento (nombre, email)
3. Wizard guarda consentimiento automáticamente después de crear RAT
4. Ir al detalle del RAT → ver alerta de EIPD pendiente
5. Crear EIPD en `/eipd?rat_id=X` → debe redirigir al RAT

**Resultado esperado:** ✅ Rat con badges "⚠️ Datos sensibles" + "📋 EIPD · pendiente" + consentimiento activo

---

### C2: Biometría + Encargado SIN contrato

**Objetivo:** Verificar que el backend rechaza cuando hay encargado sin contrato

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C2-Biometrico-Encargado-Sin-Contrato` |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Datos biométricos de identificación (Art. 16 BIS) |
| **Nombre encargado** | CloudTech S.A. |
| **Tiene contrato encargado** | ❌ No |

**Flujo esperado:**
1. Crear RAT (con consentimiento y EIPD pendiente) → ✅ OK al crear
2. Editar el RAT guardando cambios → ❌ Error 422:
   > "Este RAT tiene un encargado del tratamiento registrado pero no tiene contrato de encargo activo"

**Resultado esperado:** ❌ Falla al editar. Solución: crear contrato primero en `/encargados-contrato`

---

### C3: Salud + Consentimiento (alerta expreso)

**Objetivo:** Verificar que el sistema alerta sobre consentimiento expreso requerido

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C3-Salud-Pacientes` |
| **Tipo de proceso** | Pacientes |
| **Categoría datos** | Datos de salud, datos identificativos, historial clínico, datos de tratamientos y medicamentos |
| **Categoría titulares** | Pacientes y beneficiarios del servicio de salud |
| **Finalidad** | Prestación de servicios de salud, medicina preventiva y seguimiento de tratamientos |
| **Base legal** | Obligación legal |
| **Fuente datos** | Sistema de historia clínica electrónica (HCE) |
| **Plazo retención** | 15 años desde última atención (Ley 20.584) |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Salud (física o mental) |
| **EIPD** | ✅ Sí |
| **Estado EIPD** | Pendiente |

**Flujo esperado:**
1. Crear RAT sin consentimiento en wizard → ✅ Crea OK
2. En detalle del RAT → ver alerta de consentimiento faltante
3. Click "Registrar consentimiento" → form inline
4. **Usar canal "verbal"** para probar alerta de expreso
5. En observaciones: "El tratamiento de datos sensibles basado en consentimiento requiere que sea EXPRESO"

**Resultado esperado:** ⚠️ Crea OK pero alerta en observaciones sobre canal del consentimiento

---

### C4: Datos sensibles SIN consentimiento (al crear)

**Objetivo:** Verificar que el wizard obliga a registrar consentimiento para datos sensibles

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C4-Sensible-Sin-Consentimiento` |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Situación socioeconómica |
| **Base legal** | Ejecución de contrato |
| **Consentimiento** | NO registrar (dejar campos vacíos) |

**Flujo esperado:**
1. Abrir wizard, marcar datos sensibles → ver sección de consentimiento
2. Dejar campos de nombre/email vacíos
3. Intentar guardar → wizard debe alertar "Debe registrar consentimiento"
4. Completar consentimiento → guardar → ✅ OK

**Resultado esperado:** ✅ Si consent registrado, ❌ si no

---

### C5: Transferencia Internacional SIN EIPD

**Objetivo:** Verificar que transferencia internacional requiere EIPD

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C5-TransIntl-Sin-EIPD` |
| **Datos sensibles** | ❌ No |
| **Transferencia internacional** | ✅ Sí |
| **País destino** | México |
| **Garantías transferencia** | Nivel adecuado de protección (decisión APDC o UE) |
| **EIPD** | ❌ No (forzado por backend al marcar trans_intl) |

**Flujo esperado:**
1. Marcar transferencia internacional en wizard
2. Wizard debe auto-forzar `evaluacion_impacto=true` y `estado_eipd=pendiente`
3. Guardar → ✅ OK (con la corrección automática)

**Nota:** Si se intenta guardar sin EIPD forzado (vía SQL directo sin pasar por wizard), falla con error 422.

**Resultado esperado:** ✅ Crea OK con EIPD forzado automáticamente

---

### C6: Transferencia Internacional + EIPD Pendiente + IL

**Objetivo:** Verificar que se puede crear con EIPD incompleta pero con alerta

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C6-TransIntl-EIPD-Pendiente-IL` |
| **Transferencia internacional** | ✅ Sí |
| **País destino** | España |
| **Garantías transferencia** | Cláusulas Contractuales Tipo (SCC) |
| **Base legal** | Interés legítimo |
| **Test IL** | (texto completo, ver SQL) |

**Flujo esperado:**
1. Wizard fuerza `evaluacion_impacto=true` y `estado_eipd=pendiente` por trans_intl
2. Crear con test_interes_legitimo completo
3. En detalle → ver alerta "EIPD PENDIENTE"
4. Crear EIPD para desbloquear

**Resultado esperado:** ✅ Crea OK con alerta EIPD pendiente

---

### C7: Biométrico + EIPD Completada (escenario ideal)

**Objetivo:** Verificar flujo completo exitoso

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C7-Biometrico-EIPD-Completa` |
| **Base legal** | Datos biométricos de identificación (Art. 16 BIS) |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Datos biométricos de identificación (Art. 16 BIS) |
| **EIPD** | ✅ Sí |
| **Estado EIPD** | Completada |
| **Fecha EIPD** | 2026-07-01 |
| **Decisiones automatizadas** | ✅ Sí |
| **Lógica automatizada** | "Identificación inequívoca del trabajador mediante huella dactilar para control de asistencia. Sistema compara 1:1 sin reconocimiento masivo." |

**Flujo esperado:**
1. Crear RAT + EIPD completada + consentimiento
2. Completitud debería ser 100% (todos los campos llenos)
3. En detalle → botón "Aprobar" habilitado
4. Aprobar → ✅ OK

**Resultado esperado:** ✅ Crea OK + aprobable inmediatamente

---

### C8: Sensibles + Consentimiento + EIPD Pendiente

**Objetivo:** Verificar flujo de registro diferido

| Campo | Valor |
|-------|-------|
| **Nombre** | `RAT-C8-Salud-ConSentimiento-EIPD-Pendiente` |
| **Datos sensibles** | ✅ Sí |
| **Tipo dato sensible** | Salud (física o mental) |
| **Base legal** | Consentimiento del titular |
| **EIPD** | ✅ Sí |
| **Estado EIPD** | Pendiente |
| **Consentimiento** | ✅ Registrar |

**Flujo esperado:**
1. Crear RAT + consentimiento → ✅ OK
2. Ir a detalle → badge "📋 EIPD · pendiente"
3. Ir a `/eipd?rat_id=X` → crear EIPD completada
4. Volver a RAT → ahora puede aprobarse

**Resultado esperado:** ✅ Crea OK + flujo EIPD diferido OK

---

## NORMALES (N1-N6)

### N1: Cliente Web Básico
- **Nombre**: `RAT-N1-Cliente-Web`
- **Tipo**: Clientes web
- **Datos**: identificativos, navegación
- **Base legal**: Consentimiento del titular
- **Resultado**: ✅ Crea OK, sin EIPD, sin consent (puede agregarse después)

### N2: Empleado (Ejecución Contrato)
- **Nombre**: `RAT-N2-Empleado`
- **Tipo**: Empleados
- **Datos**: identificativos, laborales, remuneracionales
- **Base legal**: Ejecución de contrato
- **Resultado**: ✅ Crea OK

### N3: Marketing
- **Nombre**: `RAT-N3-Marketing`
- **Tipo**: Marketing
- **Base legal**: Consentimiento del titular
- **Resultado**: ✅ Crea OK

### N4: Proveedores
- **Nombre**: `RAT-N4-Proveedores`
- **Tipo**: Proveedores
- **Base legal**: Ejecución de contrato
- **Resultado**: ✅ Crea OK

### N5: RRHH - Interés Legítimo
- **Nombre**: `RAT-N5-RRHH-InteresLegitimo`
- **Tipo**: Empleados
- **Base legal**: Interés legítimo
- **Test IL**: Requerido (3 pasos completos)
- **Resultado**: ✅ Crea OK con test IL completo

### N6: Contabilidad - Obligación Legal
- **Nombre**: `RAT-N6-Contabilidad`
- **Tipo**: Contabilidad y facturación
- **Base legal**: Obligación legal
- **Resultado**: ✅ Crea OK

---

## TIPOS DE DATO SENSIBLE (S1-S6)

> Las 7 categorías del Art. 2 letra g de la Ley 21.719. Cada una requiere EIPD + consentimiento.

| # | Nombre | Tipo sensible | Base legal | Test |
|---|--------|---------------|------------|------|
| **S1** | `RAT-S1-Origen-Racial` | Origen racial o étnico | Consentimiento | Verifica validación del enum |
| **S2** | (en C4) | Situación socioeconómica | Ejec. contrato | Ya cubierto |
| **S3** | (en C3, C7, C8) | Salud (física o mental) | Varios | Ya cubierto |
| **S4** | `RAT-S4-Vida-Sexual` | Vida sexual, orientación sexual | Consentimiento | EIPD completada |
| **S5** | `RAT-S5-Opiniones-Politicas` | Opiniones políticas, creencias | Consentimiento | EIPD completada |
| **S6** | `RAT-S6-Afiliacion-Sindical` | Afiliación sindical | Interés legítimo + test IL | Test IL obligatorio |
| **S7** | (en C1, C2, C7) | Biométricos Art. 16 BIS | Art. 16 BIS | Ya cubierto |

---

## ESTADOS EIPD (E1-E4)

| # | Nombre | Estado | Condición | Test |
|---|--------|--------|-----------|------|
| **E1** | `RAT-E1-EIPD-NoRequerida` | `no_requerida` | Sin sensibles ni trans | ✅ OK directo |
| **E2** | `RAT-E2-EIPD-Pendiente` | `pendiente` | Con sensibles | ✅ OK con alerta |
| **E3** | `RAT-E3-EIPD-EnProceso` | `en_proceso` | Con trans intl | ✅ OK con alerta |
| **E4** | `RAT-E4-EIPD-Completada` | `completada` | Con sensibles + EIPD completa | ✅ OK, aprobable |

---

## BASES LEGALES (B1-B7)

| # | Nombre | Base legal | Test |
|---|--------|-----------|------|
| **B1** | `RAT-B1-Interes-Legitimo-TestOK` | Interés legítimo | Con test IL ≥50 chars → ✅ |
| **B2** | `RAT-B2-Interes-Legitimo-SinTest` | Interés legítimo | Sin test IL → ⚠️ Alerta fuerte |
| **B3** | `RAT-B3-Ejecucion-Contrato` | Ejecución de contrato | ✅ Sin requisitos extra |
| **B4** | `RAT-B4-Obligacion-Legal` | Obligación legal | ✅ Sin requisitos extra |
| **B5** | `RAT-B5-Interes-Vital` | Interés vital del titular | ✅ Sin requisitos extra |
| **B6** | (en C1, C2, C7) | Datos biométricos Art. 16 BIS | Ya cubierto |
| **B7** | `RAT-B7-Otra` | Otra | ✅ Texto libre |

---

## ENCARGADO (EN1-EN3)

| # | Nombre | Encargado | Contrato | Test |
|---|--------|-----------|----------|------|
| **EN1** | `RAT-EN1-Sin-Encargado` | ❌ | ❌ | ✅ OK |
| **EN2** | `RAT-EN2-Encargado-Con-Contrato` | ✅ PayrollPro Chile SpA | ✅ | ✅ OK |
| **EN3** | `RAT-EN3-Encargado-Sin-Contrato` | ✅ ExternalPayrollServices | ❌ | ❌ Falla al editar |

---

## DECISIONES AUTOMATIZADAS (A1-A3)

| # | Nombre | Decisiones | Lógica | Test |
|---|--------|-----------|--------|------|
| **A1** | `RAT-A1-Sin-Decisiones` | ❌ | — | ✅ OK |
| **A2** | `RAT-A2-Con-Decisiones-Y-Logica` | ✅ | Score crediticio completo | ✅ OK + alerta en observaciones |
| **A3** | `RAT-A3-Con-Decisiones-Sin-Logica` | ✅ | (vacío) | ⚠️ Alerta "sin documentar" |

---

## FRONTERA (F1-F7)

| # | Nombre | Condición | Test |
|---|--------|-----------|------|
| **F1** | `RAT-F1-NoRequerida-Justificada` | `no_requerida_justificada` + justificación ≥20 chars | ✅ OK |
| **F2** | `RAT-F2-NoRequerida-Corta` | `no_requerida_justificada` + justificación <20 | ❌ Error 422 |
| **F3** | `RAT-F3-TransIntl-SinPais` | trans_intl=true, pais=NULL | ⚠️ OK + alerta |
| **F4** | `RAT-F4-TransIntl-SinGarantias` | trans_intl=true, garantias=NULL | ⚠️ OK + alerta |
| **F5** | `RAT-F5-NNA-Ninos` | datos_nna=`ninos` | ⚠️ OK + alerta NNA |
| **F6** | `RAT-F6-NNA-Adolescentes` | datos_nna=`adolescentes` | ⚠️ OK + alerta NNA |
| **F7** | `RAT-F7-NNA-Ambos` | datos_nna=`ambos` | ⚠️ OK + alerta NNA |

---

## Auditoría (AUDIT-1)

### AUDIT-1: RAT con muchos cambios

**Objetivo:** Probar log de auditoría

**Flujo esperado:**
1. Crear RAT-AUDIT-Cambios
2. Editar varias veces cambiando campos
3. En detalle → ver historial de auditoría con timestamps y usuarios

**Resultado esperado:** ✅ Cada cambio aparece en historial

---

## Resumen de cobertura

| Categoría | Total | Cubiertos aquí | Comentario |
|-----------|-------|----------------|------------|
| Críticos | 8 | 8 | C1-C8 |
| Normales | 6 | 6 | N1-N6 |
| Tipos sensible | 7 | 5 nuevos + 2 en C | S1, S4-S6, S2/S3/S7 ya en críticos |
| EIPD estados | 4 | 4 | E1-E4 |
| Bases legales | 7 | 6 nuevos + 1 en C | B1-B5, B7, B6 ya en críticos |
| Encargado | 3 | 3 | EN1-EN3 |
| Decisiones automatizadas | 3 | 3 | A1-A3 |
| Frontera | 7 | 7 | F1-F7 |
| Auditoría | 1 | 1 | AUDIT-1 |
| **TOTAL** | **44** | **41 RATs + 5 consentimientos** | |

---

## Próximos pasos

1. **Ejecutar el SQL** en Neon QA
2. **Recorrer la UI** manualmente validando cada caso
3. **Reportar bugs** encontrados
4. **Regenerar tests** si se descubre comportamiento inesperado
5. **Actualizar CHANGELOG** con los cierres de bugs encontrados

---

## Referencias

- Ley 21.719 - Protección de Datos Personales Chile
- Art. 12 - Consentimiento
- Art. 13 - Bases legales
- Art. 14 bis - Brechas de seguridad
- Art. 14 quater - Encargado del tratamiento
- Art. 14 ter - Política de transparencia
- Art. 15 bis - EIPD
- Art. 16 - RAT (9 campos mínimos)
- Art. 16 BIS - Datos biométricos