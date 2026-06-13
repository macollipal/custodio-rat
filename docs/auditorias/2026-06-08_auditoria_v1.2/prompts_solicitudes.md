# REGISTRO DE PROMPTS — AUDITORÍA v1.2
## Custodio RAT Manager

**Fecha:** 08 Junio 2026
**Auditoría:** v1.2

---

## 1. PROMPTS DE INICIO DE SESIÓN

### Prompt 1: Contexto inicial
```
We are auditing Custodio RAT Manager codebase.
- Backend: FastAPI + SQLAlchemy 2.0 + PostgreSQL
- Frontend: Next.js 14 + Tailwind + TypeScript
- Stack: Python 3.11, Node 20+
- Features: RAT management, derechos ARCO, security breaches, EIPD, consentimientos
- Regulatory: Ley 21.719 (Chile data protection law)
- Backend running at http://localhost:8002

Goal: 3-specialist parallel audit (Arquitecto Senior, QA Lead, Compliance Ley 21.719)
```

### Prompt 2: Plan de trabajo
```
## Plan de Auditoría v1.2

### Sistema de auditoría existente (AUDIT_GUIDE.md)
- Ubicación docs: docs/documentacion_oficial/
- Scripts: paso/desarrollo_de_software_estandar/_build/
- Tema: _theme_custodio.py
- Auditorías previas: auditorias/[FECHA]_auditoria_vX/
- Docs v1.1 ya generados para: 02, 03, 04, 05, 09

### Lo que NO existe aún
- Registro de auditoría de HOY (08-Jun-2026) en el sistema
- Excel de hallazgos
- Informe consolidado
- Scripts v1.2 para docs

### Plan propuesto
1. Crear carpeta auditorias/2026-06-08_auditoria_v1.2/
2. Generar informes de 3 especialistas en paralelo
3. Crear AUDITORIA_V1.2.md (matriz de diferencias)
4. Crear Excel hallazgos_especialistas.xlsx
5. Crear script_actualizar_docs_v1.2.py
6. Ejecutar y verificar .docx
```

---

## 2. PROMPTS DE AUDITORÍA — ESPECIALISTAS

### Prompt Arquitecto Senior
```
# Rol: Arquitecto de Software Senior — 20+ años experiencia

## Tarea
Auditar codebase Custodio RAT Manager en dimensión ARQUITECTURA.

## Scope
- backend/app/routes/ → TODOS los endpoints
- backend/app/models/ → TODAS las entidades
- backend/app/services/ → servicios existentes
- backend/app/schemas/ → schemas
- backend/app/core/ → configuración, security
- frontend-next/app/ → rutas de página
- frontend-next/components/ → componentes
- frontend-next/lib/api.ts → funciones API

## Evaluar
1. Patrones de diseño (Repository, Service Layer, etc.)
2. Gestión de dependencias
3. Diseño de datos (índices, FKs, constraints)
4. Separación de responsabilidades
5. Seguridad en arquitectura (auth, authorization, validation)
6. Performance (N+1, índices, caching)
7. Escalabilidad
8. Documentación técnica

## Output
Generar informe completo en markdown con:
- Puntuación por dimensión (1-10)
- Hallazgos críticos (P0) listados con ubicación exacta
- Hallazgos altos (P1) con ubicación
- Recomendaciones priorizadas
- Score card final

## Contexto regulatorio
Ley 21.719 — Chile data protection (GDPR-like)
```

### Prompt QA Lead
```
# Rol: QA Lead Senior — Seguridad, Testing y Compliance

## Tarea
Auditar codebase Custodio RAT Manager en dimensión QA.

## Scope
- backend/app/routes/ → endpoints y seguridad
- frontend-next/ → componentes y forms
- backend/app/models/ → validación de datos
- Tests existentes

## Evaluar
1. **Seguridad** (OWASP Top 10):
   - A01:2021 Broken Access Control
   - A02:2021 Cryptographic Failures
   - A03:2021 Injection
   - A05:2021 Security Misconfiguration
   - A07:2021 Identification and Authentication Failures
   - A09:2021 Security Logging and Monitoring Failures

2. **Testing**:
   - Cobertura de tests unitarios
   - Tests de integración
   - E2E tests
   - Tests de seguridad

3. **Compliance Ley 21.719**:
   - Art. 12: Registro de operas
   - Art. 13: Medidas de seguridad
   - Art. 14: Notificación de breach
   - Art. 15: Derechos ARCO
   - Art. 16: Consentimiento expreso
   - Art. 17: Delegado DPD
   - Art. 19: EIPD
   - Art. 46: Secreto profesional
   - Art. 47: Sigilo profesional

## Output
Generar informe completo en markdown con:
- Puntuación seguridad (1-10)
- Puntuación testing (1-10)
- Puntuación compliance (1-10)
- Matriz de hallazgos P0/P1/P2
- Recomendaciones priorizadas
- Score card final
```

### Prompt Compliance
```
# Rol: Compliance Officer — Ley 21.719 Chile

## Tarea
Auditar codebase Custodio RAT Manager en dimensión COMPLIANCE LEGAL.

## Scope
- backend/app/routes/ → funcionalidades legal-relevant
- backend/app/models/ → datos personales y sensibles
- backend/app/services/ → lógica de negocio legal
- frontend-next/ → flujos de usuario

## Evaluar — Artículos clave Ley 21.719
- Art. 12: Registro de operas de tratamiento
- Art. 13: Medidas de seguridad técnicas y organizativas
- Art. 14: Notificación de operas de seguridad
- Art. 15: Derechos del afectado (ARCO)
- Art. 16: Consentimiento expreso
- Art. 17: Designación de encargado de protección de datos
- Art. 19: Evaluación de impacto (EIPD) — obligatorio para tratamientos de alto riesgo
- Art. 46: Deber de secreto y confidencialidad
- Art. 47: Sigilo profesional

## Para cada artículo
- ¿El código implementa el requisito?
- ¿Hay gaps técnicos?
- ¿Qué hallazgos hay?
- ¿Qué severidad tiene?

## Output
Generar informe completo en markdown con:
- Tabla de cumplimiento por artículo (CUMPLE/PARCIAL/NO CUMPLE)
- Hallazgos por artículo
- Puntuación compliance (1-10)
- Recomendaciones legal-técnicas
- Score card final
- Próxima auditoría compliance

## Contexto
Sistema Custodio RAT Manager — gestión de derechos ARCO bajo Ley 21.719 chilena
```

---

## 3. PROMPTS DE REGISTRO

### Prompt para crear carpeta
```
Crear carpeta auditorias/2026-06-08_auditoria_v1.2/
```

### Prompt para consolidar informes
```
Consolidar los 3 informes de los especialistas en un solo informe_consolidado.md con:
- Hallazgos corregidos durante la sesión (10 items)
- Scorecard consolidado
- Matriz de hallazgos pendientes P0/P1/P2
- Cambios en código vs documentación
- Próxima auditoría
```

---

## 4. CRONOLOGÍA

| Hora | Acción | Prompt / Descripción |
|------|--------|----------------------|
| 11:00 | Inicio sesión | Contexto inicial del proyecto |
| 11:05 | Plan de auditoría | Explicado sistema existente AUDIT_GUIDE |
| 11:10 | Confirmación usuario | Decisiones 1-4 confirmadas |
| 11:15 | Creación carpeta | `New-Item auditorias/2026-08-06_auditoria_v1.2` |
| 11:16 | Informe Arquitecto | Generado informe_arquitecto.md |
| 11:17 | Informe QA | Generado informe_qa.md |
| 11:18 | Informe Compliance | Generado informe_compliance.md |
| 11:20 | Informe Consolidado | Generado informe_consolidado.md |
| 11:21 | Matriz Diferencias | Generado AUDITORIA_V1.2.md |
| 11:22 | Excel Hallazgos | Generado con openpyxl |
| 11:23 | Prompts Registro | Este archivo prompts_solicitudes.md |
| 11:24 | Script v1.2 docs | Pendiente: script_actualizar_docs_v1.2.py |

---

## 5. DECISIONES DEL USUARIO

| # | Decisión | Opción elegida |
|---|----------|----------------|
| 1 | Sistema auditoría | **Seguir existente** (auditorias/[FECHA]_vX/) |
| 2 | Generar docs | **Completo** (08, 09, 10, 12, Matriz) |
| 3 | Próxima auditoría | **1 semana o menos** (15-Jun-2026) |
| 4 | Hallazgos en docs | **Sí, como Apéndice B** |

---

## 6. HALLAZGOS CLAVE DETECTADOS

### Seguridad (CRÍTICO — 8 hallazgos P0)
1. Token blacklist no consultado (S1)
2. IDOR en /companies/{id} (S2)
3. /companies/publico sin auth (S3)
4. CSV injection en exports (S4)
5. XSS en tkt_solicitud_derecho (S5) → **CORREGIDO**
6. Credenciales en logs DEBUG (S6) → **CORREGIDO**
7. /debug/env expuesto (S7) → **CORREGIDO**
8. 401 silencioso (S8) → **CORREGIDO**

### Compliance (2 hallazgos P0)
1. Encryption at rest faltante (C1)
2. Audit trail no inmutable (C6)

### Funcional (3 hallazgos P0)
1. Feriados solo hasta 2030 (F1) → **CORREGIDO**
2. CSV injection en exports (F2) → mismo que S4
3. Pérdida datos en estado RAT (F3)

---

*Registro generado: 08 Junio 2026*
*Auditoría Custodio RAT Manager v1.2*