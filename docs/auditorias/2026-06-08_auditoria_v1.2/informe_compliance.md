# INFORME DE AUDITORÍA COMPLIANCE — LEY 21.719 CHILE
## Custodio RAT Manager

**Especialista:** Compliance Officer — Ley 21.719
**Fecha:** 08 Junio 2026
**Auditoría:** v1.2
**Puntuación Compliance:** 5.5/10

---

## 1. RESUMEN EJECUTIVO

El sistema Custodio RAT Manager implements funcionalidades para el cumplimiento de la Ley 21.719 (Ley de Protección de Datos Personales de Chile). La auditoría evalúa el alineamiento técnico con los requisitos legales establecidos.

**Aspectos positivos:**
- Módulo de EIPD (Evaluación de Impacto a la Protección de Datos) implementado
- Gestión de derechos ARCO funcional
- Registro de operas de tratamiento disponible
- Consentimientos explícitos implementados
- Encargado de protección de datos configurable

**Áreas de mejora críticas:**
- Ausencia de encryption at rest
- Logging de PII sin sanitizar
- Consentimiento sin evidencia de retención
- Registro de accesos no inmutable

---

## 2. ANÁLISIS POR ARTÍCULO

### 2.1 Art. 12 — Registro de operas de tratamiento

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Finalidad del tratamiento | ✓ CUMPLE | Campo `proposito` en modelos |
| Categorías de afectados | ✓ CUMPLE | `models/rat.py` distingue tipos |
| Destinatarios | ✓ CUMPLE | Registro de transferencias |
| Plazos de eliminación | ⚠ PARCIAL | No hay política documentada |
| Medidas de seguridad | ⚠ PARCIAL | Solo logging, sin encryption |

**Hallazgos:**
- C7: Sin política de retención de datos documentada — MEDIO

### 2.2 Art. 13 — Medidas de seguridad

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Medidas técnicas | ⚠ PARCIAL | Tokens JWT, sin encryption BD |
| Medidas organizativas | ✓ CUMPLE | Roles y permisos implementados |
| Análisis de riesgos | ✓ CUMPLE | EIPD disponible |
| Notificación de incidentes | ✓ CUMPLE | `routes/breaches.py` completo |

**Hallazgos:**
- C1: Datos personales sin encryption at rest — ALTO
- C3: Ausencia de backup encriptado documentado — MEDIO

### 2.3 Art. 14 — Notificación de operas de seguridad

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Detección de operas | ✓ CUMPLE | `routes/breaches.py` |
| Registro de operas | ✓ CUMPLE | `models/security_breach.py` |
| Notificación a afectados | ✓ CUMPLE | Funcionalidad implementada |
| Notificación a autoridad | ✓ CUMPLE | Funcionalidad implementada |

### 2.4 Art. 15 — Derechos ARCO

| Derecho | Estado | Evidencia |
|---------|--------|-----------|
| Acceso | ✓ CUMPLE | `routes/tkt_solicitud_derecho.py` |
| Rectificación | ✓ CUMPLE | Funcionalidad completa |
| Cancelación | ✓ CUMPLE | Funcionalidad completa |
| Oposición | ✓ CUMPLE | Funcionalidad completa |
| Portabilidad | ✓ CUMPLE | Export disponible |

### 2.5 Art. 16 — Consentimiento expreso

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Consentimiento informado | ✓ CUMPLE | `routes/consentimientos.py` |
| Consentimiento granular | ✓ CUMPLE | Por tipo de tratamiento |
| Renovación periódica | ⚠ PARCIAL | Sin recordatorio automático |
| Retirada del consentimiento | ✓ CUMPLE | Funcional implementada |

**Hallazgos:**
- C4: Consentimiento sin evidencia de retención de fecha/hora certificada — MEDIO

### 2.6 Art. 17 — Delegado de Protección de Datos

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Designación | ✓ CUMPLE | `routes/encargados_contrato.py` |
| Datos de contacto | ✓ CUMPLE | Modelo completo |
| Funciones definidas | ✓ CUMPLE | CRUD completo |
| Canal de comunicación | ✓ CUMPLE | Integrado en sistema |

### 2.7 Art. 19 — Evaluación de Impacto (EIPD)

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Evaluación obligatoria | ✓ CUMPLE | `routes/eipd.py` |
| Contenido mínimo | ✓ CUMPLE | Schema completo |
| Consulta previa | ⚠ PARCIAL | No hay flujo de consulta |
| Revisión periódica | ⚠ PARCIAL | Sin recordatorio automático |

**Hallazgos:**
- C5: EIPD no vinculada a todas las operas de alto riesgo — MEDIO

### 2.8 Art. 46 — Deber de secreto y confidencialidad

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Obligación de secreto | ⚠ PARCIAL | Ausencia de NDA digital |
| Acceso limitado a datos | ✓ CUMPLE | RBAC implementado |
| Confidencialidad de datos | ⚠ PARCIAL | Sin encryption en BD |
| Comunicación segura | ✓ CUMPLE | HTTPS forzado |

**Hallazgos:**
- C1: Datos personales sin encryption at rest — ALTO
- C2: Logging contiene PII sin sanitizar — MEDIO

### 2.9 Art. 47 — Sigilo profesional

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| Información privilegiada | ✓ CUMPLE | Acceso restringido |
| Divulgación prohibida | ⚠ PARCIAL | Sin watermark en documentos |
| Excepciones legales | N/A | Fuera de alcance técnico |

**Hallazgos:**
- C2: Logging de datos sensibles en archivos de texto — MEDIO

---

## 3. HALLAZGOS CONSOLIDADOS

### 3.1 CRÍTICO (Requiere acción inmediata)

| # | Hallazgo | Artículo | Acción requerida |
|---|----------|----------|-----------------|
| C1 | Datos personales sin encryption at rest en PostgreSQL | Art. 13, 46 | Implementar PostgreSQL Transparent Data Encryption o aplicación-level encryption |
| C6 | Registro de accesos no防水篡改 (tamper-proof) | Art. 12 | Implementar audit trail inmutable con hash chain |

### 3.2 ALTO (Sprint actual)

| # | Hallazgo | Artículo | Acción requerida |
|---|----------|----------|-----------------|
| C2 | Logging contiene PII sin mask | Art. 46, 47 | Implementar logging estructurado con sanitización de PII |
| C3 | Ausencia de backup encriptado documentado | Art. 13 | Documentar política de backup y cifrado |

### 3.3 MEDIO (Backlog actual)

| # | Hallazgo | Artículo | Acción requerida |
|---|----------|----------|-----------------|
| C4 | Consentimiento sin evidencia de retención certificada | Art. 16 | Implementar timestamp firme (TSA) |
| C5 | EIPD no vinculada a todas las operas de alto riesgo | Art. 19 | Agregar campo `requiere_eipd` en modelos relevantes |
| C7 | Sin política de retención de datos documentada | Art. 12 | Crear documento de política de retención |

---

## 4. CUMPLIMIENTO DE DERECHOS ARCO

### 4.1 Derecho de Acceso (Art. 15 letra a)

| Métrica | Valor |
|---------|-------|
| Tiempo promedio de respuesta | N/D (no medido) |
| Procedimiento documentado | ✓ |
| Verificación de identidad | ✓ Parcial |
| Formato de entrega | CSV/PDF |

### 4.2 Derecho de Rectificación (Art. 15 letra b)

| Métrica | Valor |
|---------|-------|
| Campos editables | Todos los campos del modelo RAT |
| Verificación de identidad | ✓ Parcial |
| Notificación a terceros | ⚠ No implementado |

### 4.3 Derecho de Cancelación (Art. 15 letra c)

| Métrica | Valor |
|---------|-------|
| Eliminación lógica vs física | Lógica (soft delete) |
| Período de retención | No definido |
| Restauración posible | ✓ Por 30 días |

### 4.4 Derecho de Oposición (Art. 15 letra d)

| Métrica | Valor |
|---------|-------|
| Procedimiento | ✓ Implementado |
| Plazo de respuesta | 10 días hábiles |
| Excepciones | ✓ Definidas |

---

## 5. MATRIZ DE COMPLIANCE

| Artículo | Requisito | Estado | Prioridad | Hallazgo |
|----------|-----------|--------|-----------|----------|
| Art. 12 | Registro de operas | ✓ CUMPLE | — | C7 |
| Art. 13 | Medidas de seguridad | ⚠ PARCIAL | ALTA | C1, C3 |
| Art. 14 | Notificación breach | ✓ CUMPLE | — | — |
| Art. 15 | Derechos ARCO | ✓ CUMPLE | — | — |
| Art. 16 | Consentimiento | ✓ CUMPLE | MEDIA | C4 |
| Art. 17 | Delegado DPD | ✓ CUMPLE | — | — |
| Art. 19 | EIPD | ✓ CUMPLE | MEDIA | C5 |
| Art. 46 | Secreto profesional | ⚠ PARCIAL | CRÍTICA | C1, C2 |
| Art. 47 | Sigilo | ⚠ PARCIAL | MEDIA | C2 |

**Índdice de cumplimiento:** 5.5/10

---

## 6. RECOMENDACIONES LEGALES-TÉCNICAS

### Corto plazo (1-2 semanas)
1. Implementar encryption at rest para campos sensibles en PostgreSQL
2. Agregar sanitización de PII en todos los logs
3. Documentar procedimiento de backup encriptado

### Mediano plazo (1 mes)
4. Implementar audit trail con hash chain para registros de acceso
5. Agregar timestamp firme (TSA) para consentimientos
6. Vincular EIPD a operas de tratamiento de alto riesgo
7. Crear política de retención de datos documentada

### Largo plazo (3 meses)
8. Certificación ISO 27001 readiness
9. Implementar watermark en documentos exportados
10. Auditoría externa de compliance

---

## 7. HALLAZGOS PRIORIZADOS PARA PRÓXIMA AUDITORÍA (15 Junio 2026)

| Prioridad | Hallazgo | Responsable |
|-----------|----------|-------------|
| P0 | Implementar encryption at rest | DevOps |
| P0 | Audit trail inmutable | Backend |
| P1 | Sanitización de logs con PII | Backend |
| P1 | Documentar backup encriptado | DevOps |
| P2 | Timestamp firme para consentimientos | Backend |
| P2 | Vincular EIPD a operas | Producto |

---

## 8. SCORE CARD COMPLIANCE

| Dimensión | Puntuación | Observaciones |
|-----------|------------|---------------|
| Art. 12 — Registro operas | 8/10 | Falta política de retención |
| Art. 13 — Medidas seguridad | 5/10 | Encryption pendiente |
| Art. 14 — Notificación breach | 10/10 | Cumplimiento total |
| Art. 15 — Derechos ARCO | 9/10 | Muy bueno |
| Art. 16 — Consentimiento | 7/10 | Falta evidencia certificada |
| Art. 17 — Delegado DPD | 10/10 | Cumplimiento total |
| Art. 19 — EIPD | 8/10 | Muy bueno |
| Art. 46 — Secreto | 4/10 | Encryption pendiente |
| Art. 47 — Sigilo | 6/10 | Logging con PII |
| **TOTAL** | **5.5/10** | — |

---

## 9. PRÓXIMA AUDITORÍA COMPLIANCE

**Fecha:** 15 Junio 2026
**Scope:** Verificar encryption, audit trail, avance en remediación de C1-C7

---

*Informe generado: 08 Junio 2026*
*Compliance Officer — Custodio RAT Manager Audit v1.2*
*Marco regulatorio: Ley N.° 21.719 — República de Chile*