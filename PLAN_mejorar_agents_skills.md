# Plan: Mejorar Agentes y Skills de Custodio RAT

## Estado Actual
Todos los agentes y skills son esqueletos genéricos (título + 1-2 líneas + sección "Hallazgos" vacía).
No tienen workflows, criterios de inspección, conocimiento del dominio, ni lógica de decisión.

---

## Propuesta de Mejora

### 1. AGENTES (5 archivos)

Cada agente expandido a 4 secciones:
- **Mission** — Rol y responsabilidad en el proyecto
- **Responsibilities** — Qué inspecciona, con qué criterios
- **KnowledgeBase** — Conceptos clave del dominio que debe conocer
- **OutputFormat** — Formato estructurado de sus hallazgos

#### A. `compliance-domain-expert/AGENT.md`
- Dominio: Ley 21.719 completa con énfasis en lo que Custodio implementa
- Artículos clave: 14, 14 bis, 14 quáter, 15 bis, 16, 16 bis, 28
- Flags específicos: datos_sensibles, EIPD, decisiones_automatizadas, transferencia_internacional, encargado_sin_contrato
- Plazos: 72h breach notification, ARCO workflow
- Conocimiento de fórmulas: completeness (7 obligatorios + 3 recomendados - penalización documento), risk score (5 factores con pesos)

#### B. `backend-principal-engineer/AGENT.md`
- Tech stack: FastAPI + SQLAlchemy + PostgreSQL + JWT
- Rutas reales del backend: `/auth`, `/companies`, `/rats`, `/brechas`, `/ai`, `/rubros`, `/solicitudes-derecho`
- Modelos: User, Company, RAT, SecurityBreach, EIPD, Consentimiento, SolicitudDerecho, AuditLog
- Servicios: rat_service, breach_service, export_service
- Reglas de negocio: approval requiere 100%, penalización por falta de documento, 72h deadline
- Revisa: APIs, migraciones, performance, integridad referencial, seguridad

#### C. `qa-compliance-director/AGENT.md`
- Funcional: flujos RAT (wizard 4 pasos), brechas, ARCO
- Límites: campos requeridos (7 obligatorios), umbrales (completitud >= 100 para aprobar), fechas (72h)
- Casos borde: base_legal "Otra" sin documento, EIPD incompleta,什么都没
- Alertas generadas automáticamente
- Revisa: flujos end-to-end, casos límite, auditoria

#### D. `software-architect/AGENT.md`
- Arquitectura: FastAPI → Next.js → Neon PostgreSQL
- Multi-tenant: UserCompany con roles ADMIN/EDITOR/VIEWER
- Clean Architecture: routes → services → models
- Escalabilidad: JWT httpOnly cookie, rate limiting, auditoría
- Revisa: modularidad, deuda técnica, evolución futura

#### E. `devsecops-platform-engineer/AGENT.md`
- Deployment: Vercel (frontend serverless) + Neon PostgreSQL
- CI/CD: flujos de build, secretos en entorno
- Monitoreo: health endpoints, logging
- Seguridad: secretos, tokens, rate limiting
- Revisa: pipeline, configuración, observabilidad

---

### 2. SKILLS DE DOMINIO (4 archivos)

Cada skill expandido a 5 secciones:
- **Purpose** — Qué valida y por qué es importante
- **KnowledgeBase** — Artículos relevantes + umbrales del sistema
- **InspectionCriteria** — Checklist específica de qué buscar
- **SeverityMatrix** — Qué constituye Critical/High/Medium/Low
- **ValidationRules** — Reglas específicas del dominio

#### A. `rat-compliance/SKILL.md`
- Knowledge: Art. 16 (7 campos obligatorios + 3 recomendados), completeness fórmula
- Inspection: campos requeridos, documento base legal, EIPD triggers, transferencia internacional
- Severity:
  - Critical: datos_sensibles sin EIPD, biométrico con consentimiento (no válido)
  - High: transferencia internacional sin garantías, encargado sin contrato
  - Medium: completeness < 80%, EIPD pendiente > 30 días
  - Low: campos recomendados faltantes, revisión > 6 meses

#### B. `arco-rights/SKILL.md`
- Knowledge: Art. 14 y 16 bis, workflow PENDIENTE→EN_PROCESO→RESUELTO/RECHAZADA
- Inspection: plazos de respuesta, canal_ejercicio_derechos configurado, historial completo
- Severity:
  - Critical: solicitud sin respuesta > 10 días hábiles
  - High: historial incompleto, cambio de estado sin timestamp
  - Medium: canal no configurado
  - Low: documentación insuficiente

#### C. `breach-management/SKILL.md`
- Knowledge: Art. 14 bis, 72h deadline APDC, notificación inmediata a titulares si datos sensibles
- Inspection: fecha_deteccion, countdown, notificación APDC, notificación titulares, rats_afectados
- Severity:
  - Critical: > 72h sin notificar APDC, datos sensibles sin notificar titulares
  - High: 48-72h restantes sin confirmar notificación
  - Medium: rats_afectados no documentados
  - Low: medidas_adoptadas incompletas

#### D. `multi-tenant-security/SKILL.md`
- Knowledge: UserCompany, roles ADMIN/EDITOR/VIEWER, JWT httpOnly cookie
- Inspection: aislamiento de datos por company_id, autorización de endpoints, logout/blacklist
- Severity:
  - Critical: acceso cross-tenant, falta de company_id en queries
  - High: rol elevado sin auditoría, token sin blacklist
  - Medium: permisos no verificados en todas las rutas
  - Low: logging insuficiente de acceso

---

### 3. SKILLS TÉCNICOS (7 archivos)

Cada skill expandido a 4 secciones:
- **Purpose** — Qué revisa
- **CodeReferences** — Archivos y endpoints específicos del proyecto
- **CheckList** — Qué inspeccionar
- **SeverityMatrix** — Clasificación de hallazgos

#### A. `security-review/SKILL.md`
- CodeRefs: backend/app/models/user.py (JWT), backend/app/routes/auth.py, rate limiting
- CheckList: OWASP Top 10, bcrypt, httpOnly cookie, JTI blacklist, input validation, SQL injection, XSS
- Severity: Critical (auth bypass, SQL injection), High (weak password, no rate limit), Medium (missing headers), Low (info disclosure)

#### B. `database-review/SKILL.md`
- CodeRefs: backend/app/models/*.py, migrations/
- CheckList: índices en company_id, estado, created_at; foreign keys; unique constraints; ON DELETE CASCADE
- Severity: Critical (missing FK, orphan data), High (missing index en query frecuente), Medium (tipo dato incorrecto), Low (naming inconsistency)

#### C. `api-review/SKILL.md`
- CodeRefs: backend/app/routes/*.py, schemas/
- CheckList: REST compliance, validación Pydantic, errores apropiados (4xx/5xx), paginación, filtros
- Severity: Critical (endpoint inseguro, datos sensibles en response), High (validación faltante), Medium (error handling inconsistente), Low (documentación incompleta)

#### D. `frontend-review/SKILL.md`
- CodeRefs: frontend-next/components/rat/*, frontend-next/app/(app)/*
- CheckList: React 19 best practices, accessibility (WCAG), responsive, forms validation, error handling, dark mode
- Severity: Critical (XSS, broken auth flow), High (missing validation, inaccessible), Medium (UX issues), Low (code style)

#### E. `audit-trail-review/SKILL.md`
- CodeRefs: backend/app/models/audit_logs.py, audit_service.py, todas las rutas con log_audit
- CheckList: logging en crear/editar/eliminar, IPs capturadas, timestamps, historial de cambios
- Severity: Critical (operación sin auditoría), High (datos insuficientes), Medium (formato inconsistente), Low (logging parcial)

#### F. `reporting-review/SKILL.md`
- CodeRefs: backend/app/services/export_service.py, frontend-next/lib/api.ts (export functions)
- CheckList: PDF layout, CSV encoding (UTF-8 BOM), CNI formato APDC, datos completos
- Severity: Critical (datos incorrectos en export), High (encoding error, formato APDC incorrecto), Medium (campos faltantes), Low (layout mejorable)

#### G. `ai-assistant-review/SKILL.md`
- CodeRefs: backend/app/routes/ai.py, frontend-next/app/(app)/reportes/page.tsx (AI chat)
- CheckList: respuestas correctas sobre Ley 21.719, contexto apropiado, rate limiting
- Severity: Critical (respuesta con error legal), High (falta de contexto), Medium (rate limit no respetado), Low (UX de chat)

---

### 4. SKILLS ADICIONALES (3 archivos)

#### A. `dashboard-kpi-review/SKILL.md`
- CodeRefs: frontend-next/app/(app)/dashboard/page.tsx, backend/app/routes/rats.py (dashboard endpoint)
- CheckList: KPIs correctos, fórmulas de cálculo, alertas configuradas, gráficos actualizados
- Severity: High (KPI incorrecto), Medium (dato stale), Low (UX mejorable)

#### B. `performance-review/SKILL.md`
- CodeRefs: Queries en services, índices en modelos, frontend data fetching
- CheckList: N+1 queries, missing índices, carga innecesaria de datos, cache effectiveness
- Severity: Critical (> 2s response), High (N+1 queries), Medium (cache no usado), Low (optimización menor)

#### C. `code-quality/SKILL.md`
- CodeRefs: Todo el codebase
- CheckList: DRY, naming conventions, imports organizados, comments (solo cuando necesario), tests coverage
- Severity: High (duplicación masiva), Medium (naming poor), Low (estilo inconsistente)

---

## Resumen de Archivos a Crear/Modificar

| Tipo | Archivo | Cambios |
|------|---------|---------|
| Agent (actualizar) | agents/compliance-domain-expert/AGENT.md | Expandir a 4 secciones con Ley 21.719 |
| Agent (actualizar) | agents/backend-principal-engineer/AGENT.md | Agregar endpoints y modelos reales |
| Agent (actualizar) | agents/qa-compliance-director/AGENT.md | Agregar flujos y casos borde |
| Agent (actualizar) | agents/software-architect/AGENT.md | Agregar arquitectura real |
| Agent (actualizar) | agents/devsecops-platform-engineer/AGENT.md | Agregar stack de deployment |
| Skill (actualizar) | skills/rat-compliance/SKILL.md | Agregar Art. 16, completeness, severity |
| Skill (actualizar) | skills/arco-rights/SKILL.md | Agregar workflow y plazos |
| Skill (actualizar) | skills/breach-management/SKILL.md | Agregar 72h y notificaciones |
| Skill (actualizar) | skills/multi-tenant-security/SKILL.md | Agregar roles y aislamiento |
| Skill (actualizar) | skills/security-review/SKILL.md | Agregar OWASP y code refs |
| Skill (actualizar) | skills/database-review/SKILL.md | Agregar índices y FK |
| Skill (actualizar) | skills/api-review/SKILL.md | Agregar endpoints y validación |
| Skill (actualizar) | skills/frontend-review/SKILL.md | Agregar componentes y check |
| Skill (actualizar) | skills/audit-trail-review/SKILL.md | Agregar modelo de auditoría |
| Skill (actualizar) | skills/reporting-review/SKILL.md | Agregar exports y CNI |
| Skill (actualizar) | skills/ai-assistant-review/SKILL.md | Agregar contexto y rate limit |
| Skill (actualizar) | skills/dashboard-kpi-review/SKILL.md | Agregar KPIs y fórmulas |
| Skill (nuevo) | skills/performance-review/SKILL.md | Crear con checklist de performance |
| Skill (nuevo) | skills/code-quality/SKILL.md | Crear con checklist de calidad |
| README | .opencode/README.md | Expandir con contexto del proyecto |

**Total: 21 archivos** (1 README + 5 agents + 15 skills)

---

## Consideraciones de Implementación

1. **Orden sugerido:**
   - Primero agentes de dominio (compliance-domain-expert, qa-compliance-director)
   - Luego skills de dominio (rat-compliance, breach-management, arco-rights)
   - Luego skills técnicos referencing archivos reales
   - Finalmente skills nuevos (performance-review, code-quality)

2. **Referencias cruzadas:** Los skills referencian archivos reales del proyecto para que sean accionables

3. **Severity alineado:** Todos usan Critical/High/Medium/Low consistentemente con la terminología de la ley y riesgos del sistema

4. **Contexto de negocio:** Cada skill incluye conocimiento del dominio (artículos, plazos, umbrales) no solo review técnico

---

## Preguntas Pendientes

1. ¿Quieres que incluya también un agent especializado en **asesor de RAT** que sugiera mejoras específicas basadas en el contexto de la empresa?

2. ¿Los skills técnicos deben también verificar que el código esté alineado con las **políticas de privacidad** específicas por rubro?

3. ¿Quieres agregar un skill para **generación de documentación** legal (políticas, avisos) como capability?