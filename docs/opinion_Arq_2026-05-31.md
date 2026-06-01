# Opinion Arquitectónica — Custodio RAT Manager

**Fecha:** 2026-05-31
**Auditor:** architect-senior
**Versión analyzed:** develop (May 2026)

---

## Resumen Ejecutivo

Custodio RAT Manager es una aplicación funcional que implementa la gestión del Registro de Actividades de Tratamiento (RAT) conforme a la Ley 21.719 de Chile. El código funciona y cubre los casos de uso principales. Sin embargo, la deuda técnica acumulada y las inconsistencias arquitectónicas representan riesgos significativos para la escalabilidad, seguridad y mantenibilidad a mediano plazo.

El sistema se encuentra en un estado de **Producción Inicial** con rasgos de **Beta**. La arquitectura es aceptable para MVPs pero insuficiente para un producto empresarial que administre datos personales regulados.

---

## Riesgos Críticos

1. **Falta de autenticación en `GET /rats/auditoria/{company_id}`** — Este endpoint acepta `company_id` pero no verifica si el usuario tiene acceso a esa empresa. Un usuario podría acceder al historial de auditoría de cualquier empresa del sistema.

2. **Token en localStorage vulnerable a XSS** — El JWT se almacena en localStorage (`custodio_token`). Un ataque XSS podría extraer el token. La mejor práctica es usar httpOnly cookies, que ya se usan en el backend para setear el cookie, pero el token también se guarda en localStorage como fallback/confianza paralela.

3. **Falta de paginación en endpoints críticos** — `GET /auth/users`, `GET /companies`, `GET /brechas`, `GET /solicitudes-derecho` devuelven todos los registros sin límite. En producción con miles de registros, esto causa memory overflow y timeouts.

4. **Archivo binario en PostgreSQL** — `archivo_base_legal_datos` (LargeBinary) almacena archivos directamente en la BD. PostgreSQL no es un almacén de objetos; archivos >1MB degradan el rendimiento severamente.

5. **Falta de paginación en reportes** — `GET /rats/reportes` no tiene paginación en el backend, confiando en que el frontend limita a 20 resultados. Si el frontend no limita, la consulta puede devolver miles de filas.

---

## Riesgos Altos

1. **Lógica de negocio duplicada en `calcular_completitud`** — Existe en `RAT.calcular_completitud()` (modelo) Y en `rat_service._calcular_estado()` (servicio). Si uno cambia, el otro no se actualiza. Los modelos deben ser "skinny" en arquitectura por capas.

2. **`decode_access_token` hace query a BD en cada request autenticado** — El blacklist check consulta `token_blacklist` en cada decode. En producción con muchas requests por minuto, esto es un cuello de botella en el hot path.

3. **Validación de RUT en frontend sin servidor** — La validación del RUT chileno se hace solo en el frontend. No hay validación en el backend para `companies` al crear/actualizar. Un request directo por API podría crear una empresa con RUT inválido.

4. **AI queries sin audit logging** — `POST /ai/ask` no registra en `audit_logs`. En un sistema de compliance regulatorio, cada acción debería ser rastreable. Las preguntas a la IA podrían exponer datos sensibles de la empresa.

5. **Falta de índice en `audit_logs`** — `usuario` y `timestamp` son consultas comunes pero no tienen índice. Queries de auditoría serán lentas con volumen alto.

6. **Componente `solicitud_derecho.py` con lógica embebida** — Este archivo tiene routes, schemas, modelos y lógica de negocio todo junto (300+ líneas). Viola el principio de responsabilidad única.

7. **`is_admin` legacy column en `User`** — La columna `is_admin` es redundante con `rol_global`. Se mantiene por compatibilidad legacy pero causa confusión y potencial inconsistencia de datos.

---

## Riesgos Medios

1. **Raw `fetch()` vs `api.*` inconsistente** — `configuracion/page.tsx`, `conexion/page.tsx`, `ejercitar/page.tsx` usan `fetch()` directo en lugar de las funciones de `lib/api.ts`. Esto rompe la centralización del manejo de errores y autenticación.

2. **9 componentes > 300 líneas** — `companies/page.tsx` (717), `reportes/page.tsx` (866), `configuracion/page.tsx` (861), `RatWizard.tsx` (873), `RatEditForm.tsx` (445), `RatTable.tsx` (450), entre otros. Estos son inmantenibles y propensos a bugs.

3. **Rate limiting solo en 4 endpoints** — `/auth/login`, `/auth/logout`, `/auth/me/password`, `/ai/ask`. Los demás endpoints no tienen límite, incluyendo `POST /companies`, `POST /rats`, `POST /brechas` que podrían ser abused.

4. **Sin retry logic en conexión a BD** — `database.py` no tiene configuración de reconnect para fallos transitorios. En Neon (serverless), las conexiones pueden caerse entre requests.

5. **TZ inconsistente entre `export_service` y `get_dashboard_stats`** — `export_service` usa UTC-4 hardcodeado (fallback Chile), `get_dashboard_stats` usa `datetime.now(timezone.utc)`. Podría haber off-by-hours cerca de transiciones DST.

6. **`suggestion_service` hardcodeado en memoria** — Agregar un nuevo tipo de proceso requiere cambiar código. Para un producto en producción, esto debería ser editable por admins desde la UI.

7. **`ALERTAS_AUDITORIA` hardcodeado en `rat_service`** — Las alertas de auditoría son un dict de Python, no configurable externamente.

8. **No hay tests de integración** — Los tests son unitarios con SQLite in-memory. No hay tests end-to-end que verifiquen el flujo completo login → crear RAT → exportar.

9. **`require_editor_or_admin_empresa` y `require_company_admin` no usan FastAPI Depends()** — Son funciones que reciben `db, current_user` como argumentos, inconsistente con `require_admin` que sí usa `Depends()`. No pueden reutilizarse como dependencies en otras rutas.

10. **Validación de email solo en frontend** — No hay validación de formato de email en schemas del backend para `email_dpo`.

---

## Fortalezas Detectadas

1. **Arquitectura de capas correcta** — La separación routes → services → models es coherente en la mayoría del código. Las dependencias van en la dirección correcta.

2. **Auditoría centralizada** — `audit_service.log_audit()` es un patrón sólido. El logging de acciones de usuarios está bien implementado.

3. **Tabla `token_blacklist` con cleanup** — El mecanismo de revocación de tokens JWT y la limpieza de tokens expirados al startup es una buena práctica.

4. **Rate limiting implementado** — slowapi está configurado para endpoints sensibles, lo cual es importante para un sistema de auth.

5. **Password hashing con bcrypt** — `passlib` + `bcrypt` es el estándar de la industria. La validación de longitud de secret key (64 chars = 256 bits) es correcta.

6. **Pydantic para validación de entrada/salida** — Los schemas están bien definidos y separan la validación de la lógica de negocio.

7. **Separación de responsabilidades en auth** — Login, logout, refresh token, cambio de password son operaciones separadas con endpoints distintos.

8. **Sistema de roles documentado** — La documentación en CLAUDE.md explica claramente los 3 roles y sus alcances. La implementación los respeta.

9. **Tests covering RAT CRUD** — 95+ tests cubren los casos de uso principales. La cobertura de RAT completo es buena.

10. **Documentación comprehensiva** — README, CLAUDE.md, VERCEL_DEPLOY_ERRORS.md, flujo_datos.md, casos_de_uso/README.md facilitan el onboarding.

---

## Deuda Técnica

| Ítem | Gravedad | Ubicación | Estimación |
|------|----------|-----------|------------|
| Paginar `GET /auth/users`, `GET /companies`, `GET /brechas`, `GET /solicitudes-derecho` | Alta | routes/ | 1 día |
| Mover `archivo_base_legal_datos` a almacenamiento de objetos (S3 o similar) | Alta | models/rat.py | 3 días |
| Eliminar columna `is_admin` de User, usar solo `rol_global` | Media | models/user.py | 0.5 día |
| Agregar índices en `audit_logs(usuario, timestamp)` | Media | migrate_to_neon.py | 0.5 día |
| Unificar `_calcular_estado` y `calcular_completitud` en el service | Media | rat_service.py, models/rat.py | 1 día |
| Reemplazar `fetch()` por `api.*` en configuracion, conexion, ejercitar | Media | frontend pages | 1 día |
| Extraer `solicitudes_derecho.py` en service + schemas | Alta | routes/solicitudes_derecho.py | 2 días |
| Implementar refresh tokens JWT | Alta | security.py, routes/auth.py | 3 días |
| Externalizar `ALERTAS_AUDITORIA` y `TIPOS_PROCESO` a DB | Media | rat_service.py, suggestion_service.py | 2 días |
| Splitear componentes > 300 líneas (RatWizard, RatTable, companies, reportes, configuracion) | Media | frontend | 5+ días |
| Agregar input validation en backend para RUT/email | Media | schemas | 0.5 día |
| Agregar audit logging a `POST /ai/ask` | Media | routes/ai.py | 0.5 día |
| Corregir dependencias de FastAPI (`require_editor_or_admin_empresa`, `require_company_admin`) | Media | routes/deps.py | 1 día |
| Reducir duplicación company switcher (Sidebar + Topbar) | Baja | frontend | 0.5 día |
| Unificar `DESCRIPCIONES_BASE` en un solo lugar | Baja | constants.ts, RatWizard.tsx | 0.5 día |

---

## Recomendaciones Arquitectónicas

### Corto plazo (1-2 semanas)

1. **Paginar endpoints críticos** — `GET /auth/users`, `GET /companies`, `GET /brechas`, `GET /solicitudes-derecho`. Sin paginación, el sistema no escala.

2. **Validación de RUT en backend** — Crear un schema validator o función `validar_rut_chile(rut)` y usarla en `CompanyCreate`, `CompanyUpdate`.

3. **Corregir `GET /rats/auditoria/{company_id}`** — Agregar verificación de que el usuario tiene acceso a la empresa antes de devolver logs de auditoría.

4. **Mover archivo_base_legal a object storage** — No almacenar archivos binarios grandes en PostgreSQL. Usar S3 o similar con firma de URL.

5. **Indexar `audit_logs`** — Agregar índice compuesto en `(usuario, timestamp)` para queries de auditoría.

### Mediano plazo (1-2 meses)

6. **Implementar refresh tokens** — Tokens de 8 horas sin refresh es malo para UX. Implementar refresh token flow con cookie httpOnly.

7. **Splitear componentes gigantes** — Especialmente RatWizard (873 líneas), reportes (866), configuracion (861). Extraer pasos del wizard en componentes separados.

8. **Reemplazar fetch() por api.*** — Unificar toda la comunicación HTTP en `lib/api.ts` con manejo de errores centralizado.

9. **Migrar lógica de negocio del modelo al service** — `RAT.calcular_completitud()` y `RAT.calcular_nivel_riesgo()` deben estar solo en `rat_service.py`. Los modelos deben ser "skinny".

10. **Externalizar knowledge bases** — `TIPOS_PROCESO` en suggestion_service y `ALERTAS_AUDITORIA` en rat_service deben ser editables desde la UI por admins.

11. **Implementar cache para decode_access_token** — El blacklist check en cada request autenticado puede cachearse con TTL corto (30s) para reducir load en la BD.

### Largo plazo (3-6 meses)

12. **Migrar a cookies httpOnly para JWT** — Eliminando localStorage se elimina el vector XSS para tokens. El backend ya soporta cookies; el frontend debe usar ese mecanismo.

13. **Microservicio de exportación** — PDF y CSV para datasets grandes bloquean el thread. Mover a workers asíncronos con cola de trabajos.

14. **Sistema de eventos/audit trail inmutable** — El `audit_logs` actual es mutable (UPDATE/DELETE). Para compliance regulatorio, debería ser inmutable (append-only, triggers preventivos).

15. **Dashboard de observabilidad** — Logs estructurados sin correlación ID, sin métricas de request/response times, sin alertas sobre errores de BD o timeouts.

16. **Tests E2E** — Agregar Playwright o Cypress para tests end-toend: login → crear empresa → crear RAT → exportar PDF.

---

## Roadmap Arquitectónico

### Fase 1: Estabilidad y Seguridad (Mes 1)
- Paginar todos los endpoints de listado
- Validación de input en backend (RUT, email)
- Índices en BD
- Fix auth en /rats/auditoria/{company_id}
- Mover archivos a object storage

### Fase 2: Refactoring Técnico (Mes 2)
- Splitear componentes > 300 líneas
- Unificar fetch → api.*
- Externalizar knowledge bases
- Corregir dependencias de FastAPI
- Reducir duplicación company switcher

### Fase 3: Escalabilidad (Mes 3-4)
- Refresh tokens JWT
- Cache para token blacklist
- Workers para exportaciones grandes
- Observabilidad (correlation IDs, métricas, alertas)

### Fase 4: Enterprise Readiness (Mes 5-6)
- Tests E2E
- Audit trail inmutable
- Migración a arquitectura de microservicios si el tráfico lo justifica
- Revisión completa de OWASP

---

## Score Arquitectónico

| Dimensión | Puntuación | Comentario |
|-----------|------------|-------------|
| **Escalabilidad** | 5/10 | Sin paginación en endpoints críticos, sin cache, archivos en BD. Limitado a cientos de empresas/RATs. |
| **Mantenibilidad** | 4/10 | Componentes gigantes, duplicación extensa, lógica de negocio en modelos, mix de responsabilidades en archivos. |
| **Seguridad** | 5/10 | JWT sólido pero en localStorage, falta CSRF, rate limiting parcial, no validación de input en backend, sin audit en AI. |
| **Rendimiento** | 6/10 | BD bien indexada ( Neon tiene.pooler), pero N+1 queries en companies, decode_access_token con DB por request, exportación blocking. |
| **Observabilidad** | 3/10 | Sin correlación ID en logs, sin métricas, sin dashboard, sin alertas. Cleanup de tokens solo al startup. |
| **Arquitectura General** | 5/10 | Capas correctas pero con fugas de responsabilidad. El código funciona pero la estructura necesita refactoring significativo. |

**Promedio:** 4.7/10

---

## Evaluación de Madurez del Producto

**Clasificación actual:** Producción Inicial / Beta

### Justificación
El sistema está en producción real (Neon Custodio_dev) con datos de usuarios reales. La funcionalidad core (CRUD RAT, auth, exportación) funciona. Sin embargo:

- Carece de paginación → no escala
- Carece de validación de input completa en backend
- Carece de tests E2E
- Carece de observabilidad
- UX tiene issues de accesibilidad

### Qué falta para Producción Empresarial

1. **Paginação y límites** — Manejo de miles de registros
2. **Observabilidad** — Logs estructurados, métricas, alertas
3. **Tests E2E** — Cover end-to-end flows
4. **Refresh tokens** — UX de sesión más robusta
5. **Seguridad completa** — CSRF, validación de input, audit en AI
6. **Object storage** — Para archivos grandes
7. **Accesibilidad** — WCAG 2.1 AA compliance para uso gubernamentales

---

*Generado por architect-senior skill — 2026-05-31*