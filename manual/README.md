# Manual de Custodio RAT — Para clientes

> **Bienvenido a Custodio.** Esta guía está escrita para personas que nunca han usado el sistema y no tienen conocimientos técnicos de cumplimiento legal.

## 📖 Contenido

1. **Antes de empezar** — qué es Custodio y por qué te lo piden
2. **Mi primer RAT** — crear tu primer registro paso a paso
3. **Los módulos principales** — qué hace cada parte del sistema
4. **[Cómo se conectan los módulos](como_se_conectan_los_modulos.md)** — vista panorámica
5. **Ejemplos reales** — casos prácticos
6. **Glosario** — términos explicados en lenguaje simple

---

## 1. Antes de empezar

### ¿Qué es Custodio?

Custodio es un sistema digital que te ayuda a **documentar y mantener actualizado el Registro de Actividades de Tratamiento (RAT)** de tu empresa, según lo exige la **Ley 21.719 de Protección de Datos Personales de Chile**.

**En resumen:** Custodio hace el trabajo pesado de crear y mantener tu RAT para que tú no tengas que hacerlo en una planilla de Excel.

### ¿Por qué existe?

Desde el **1 de diciembre de 2026**, la Ley 21.719 entra en vigencia total. Si no tienes un RAT bien hecho, puedes recibir multas de hasta **$1.550.000 USD**.

### ¿Qué hace Custodio por mí?

- 📋 Te guía paso a paso para crear cada RAT
- 🔍 Te dice qué información te falta
- 📊 Te muestra el estado de cumplimiento de tu empresa
- 📧 Te avisa cuando algo requiere tu atención (vencimientos, brechas, etc.)
- 📄 Genera reportes listos para presentar a la autoridad

### ¿Qué NO hace Custodio?

- ❌ No almacena los datos personales de tus clientes/empleados
- ❌ No reemplaza el consejo de un abogado
- ❌ No envía datos a la APDC automáticamente (tú decides cuándo)
- ❌ No te cobra — eso se acuerda con tu proveedor

---

## 2. Mi primer RAT

Esta es la pantalla más importante: el **Wizard de creación de RAT**.

### Paso a paso visual

Imagina que tienes una **tienda online** y guardas los emails de tus clientes para enviar promociones. Eso es un "tratamiento de datos personales" y necesitas documentarlo.

**Paso 1: Identificación**
- **Nombre del proceso**: "Marketing por email a clientes"
- **Categorías de titulares**: "Clientes"
- **Fuente de los datos**: "Formulario de registro en el sitio web"
- **Destinatarios**: "Equipo de marketing"

**Paso 2: Datos tratados**
- **Categoría de datos**: "Email, nombre"
- **¿Hay datos sensibles?** (salud, religión, etc.): NO
- **¿Decisiones automatizadas?** (algoritmo decide sin humanos): NO

**Paso 3: Finalidad y ley**
- **Finalidad**: "Envío de promociones y newsletters"
- **Base legal**: "Consentimiento del titular" (la persona se suscribió voluntariamente)
- **Adjuntar**: el formulario web donde aceptan (si tienes la URL, adjunta captura)

**Paso 4: Almacenamiento**
- **Plazo de retención**: "Hasta que se den de baja + 2 años"
- **Medidas de seguridad**: "Email marketing platform con TLS, base de datos cifrada"
- **¿Transferencia internacional?** (datos salen de Chile): NO

**Paso 5: Compliance avanzado** (opcional pero recomendado)
- **Operaciones**: "Recopilación, almacenamiento, envío"
- **Frecuencia**: "Continua"

### ¿Qué pasa después?

Tu RAT queda en estado **"Borrador"** con un **% de completitud**. Cuando llegues al 100%, puedes marcarlo como "Completo" o "En revisión" para que tu DPO lo apruebe.

---

## 3. Los módulos principales

### 📊 Dashboard (pantalla principal)

Es lo primero que ves al entrar. Te muestra:
- **Cuántos RATs** tienes registrados
- **Completitud promedio** (qué tan completos están tus RATs)
- **Datos sensibles** que estás tratando
- **RATs vencidos** que necesitan actualización
- **Alertas** (vencimientos, brechas, brechas a notificar)

**Analogía**: es el "tablero de control" de tu auto — te dice qué está bien y qué necesita atención.

### 📋 Procesos RAT

Aquí ves la lista de todos los RATs de tu empresa. Puedes:
- **Crear** un RAT nuevo (botón "+ Nuevo proceso")
- **Ver** el detalle (clic en un RAT)
- **Editar** (botón de lápiz)
- **Exportar** PDF individual
- **Aprobar** (cuando está completo)

### 🚨 Brechas de Seguridad

Si ocurre un incidente (hackeo, robo de laptop, email mal enviado, etc.):
1. **Regístralo inmediatamente** (botón "+ Registrar brecha")
2. **Describe** qué pasó
3. **Indica** qué datos fueron comprometidos
4. **Marca** si hay datos sensibles, menores o financieros
5. **El sistema calcula** si debe notificarse a APDC en 72h
6. **Marca cuando se notificó** a APDC y a titulares

**No esperes** a tener todos los detalles para registrar la brecha. Es mejor un registro parcial a tiempo que uno completo tarde.

### 📑 ARCO / Solicitudes de derechos

Cuando un titular (cliente, empleado, etc.) pide uno de sus derechos:
- **Acceso**: ver qué datos tienen de él
- **Rectificación**: corregir datos incorrectos
- **Cancelación**: eliminar sus datos
- **Oposición**: oponerse a un tratamiento
- **Portabilidad**: recibir sus datos en formato transferible
- **Bloqueo**: suspender temporalmente un tratamiento

**Plazo legal**: tienes **10 días hábiles** para responder. Custodio te avisa cuando vence el plazo.

### ✅ Consentimientos

Registro de consentimientos individuales (ej: para datos sensibles como salud, biométricos, etc.).

**Cuándo es obligatorio**:
- Datos sensibles (Art. 12)
- Transferencias internacionales
- Decisiones automatizadas con efectos legales

### 📄 Reportes

Genera reportes filtrados para:
- Presentar a la APDC en una fiscalización
- Auditorías internas
- Reportes a tu directorio
- Análisis de cumplimiento

**Formatos**: CSV, PDF, CNI (formato oficial APDC)

---

## 4. Cómo se conectan los módulos

Esta vista te ayuda a entender qué pasa cuando algo cambia:

```
                            ┌─────────────────┐
                            │   Dashboard     │
                            │  (vista general) │
                            └────────┬────────┘
                                     │
        ┌────────────────────────────┼────────────────────────┐
        │                            │                        │
        ▼                            ▼                        ▼
   ┌─────────┐              ┌──────────────┐         ┌──────────────┐
   │  RATs   │◄────────────│  Brechas     │────────►│  Consentim.  │
   │(tus    │  si hay      │  (incidentes)│  si hay │ (registro de │
   │procesos)│ incidente   │              │ datos    │  aceptacion) │
   └────┬────┘  afecta     └──────┬───────┘ sensibles└──────────────┘
        │            estos RATs        │
        │                  │              ┌──────────────┐
        ▼                  ▼             │  ARCO        │
   ┌──────────┐      ┌──────────┐       │ (solicitudes │
   │  EIPD    │      │ Notifica-│       │  de titulares)│
   │(evaluac.)│      │ ciones   │       └──────────────┘
   └──────────┘      └──────────┘
```

### Ejemplo de flujo real

1. **Creas un RAT** para "Nómina de empleados" (datos sensibles: salud)
2. **Custodio detecta** que requiere EIPD (Evaluación de Impacto)
3. **Registras** el consentimiento de cada empleado
4. **Ocurre una brecha**: roban una laptop con la nómina
5. **Creas** la brecha en Custodio con los datos comprometidos
6. **Custodio calcula**: 72h para notificar a APDC + sin dilación a titulares
7. **Un empleado pide acceso** a sus datos (ARCO)
8. **Creas** el ticket, respondes en 10 días hábiles

**Todo queda registrado** en el historial de auditoría inmutable.

---

## 5. Ejemplos reales

### Caso 1: Pyme retail (tienda de ropa)

**Empresa**: "Boutique María", 3 empleados, vende online y en local.
**RATs típicos**:
1. **Clientes web**: email, nombre, dirección de envío. Base legal: consentimiento.
2. **Nómina**: nombre, RUT, sueldo, AFP, salud (licencias). Base legal: obligación legal.
3. **Proveedores**: datos bancarios, contacto. Base legal: ejecución de contrato.

**Brechas que le podrían ocurrir**:
- Hackeo del sistema de e-commerce
- Pérdida de celular de un empleado con datos de clientes

### Caso 2: Clínica dental

**Empresa**: "Clínica Sonrisa", 5 dentistas, 2000 pacientes.
**RATs típicos**:
1. **Historia clínica**: nombre, RUT, diagnóstico, radiografías. Base legal: consentimiento (datos de salud son sensibles).
2. **Citas y agenda**: nombre, teléfono, email. Base legal: consentimiento.
3. **Facturación**: RUT, datos bancarios. Base legal: obligación legal (SII).

**Caso especial**: los datos de salud son **sensibles** (Art. 12 Ley 21.719). Requieren:
- EIPD (Evaluación de Impacto en Protección de Datos)
- Consentimiento expreso individual
- Medidas de seguridad reforzadas

### Caso 3: Empresa de software (B2B)

**Empresa**: "TechCorp", 50 empleados, 20 clientes empresariales.
**RATs típicos**:
1. **Gestión de clientes**: razón social, contacto, contratos. Base legal: ejecución de contrato.
2. **Recursos humanos**: nombre, RUT, sueldo, evaluaciones. Base legal: obligación legal.
3. **Marketing B2B**: emails corporativos. Base legal: interés legítimo.
4. **Logs de sistema**: IPs, user agents. Base legal: interés legítimo (requiere test de 3 pasos).

---

## 6. Glosario en lenguaje simple

| Término técnico | En palabras simples |
|---|---|
| **RAT** | Lista de "qué datos personales uso y para qué" |
| **APDC** | La agencia del gobierno que te puede fiscalizar |
| **DPO** | La persona en tu empresa responsable del cumplimiento |
| **EIPD** | Un análisis de "¿qué tan riesgoso es este tratamiento y cómo lo protejo?" |
| **Datos sensibles** | Datos que requieren protección extra: salud, religión, política, biométricos, etc. |
| **ARCO** | Los derechos que tienen las personas sobre sus datos: ver, corregir, borrar, oponerse |
| **Base legal** | La razón legal por la que puedes tratar esos datos (consentimiento, contrato, ley) |
| **Titular** | La persona cuyos datos estás tratando (cliente, empleado, etc.) |
| **Brecha** | Un incidente donde los datos se vieron comprometidos |
| **Cifrado** | Convertir datos en código ilegible para protegerlos |
| **72 horas** | Plazo legal para notificar una brecha a la APDC |
| **10 días hábiles** | Plazo legal para responder una solicitud ARCO |

---

## ¿Necesitas ayuda?

Si te trabas con algo:
1. **Busca en este manual** (Ctrl+F)
2. **Pregunta al Asesor IA** (botón 🤚 en la esquina inferior derecha)
3. **Contacta al administrador** de tu instancia Custodio

---

*Manual de Custodio RAT Manager · v1.0 · 2026-07-13 · Ley 21.719*