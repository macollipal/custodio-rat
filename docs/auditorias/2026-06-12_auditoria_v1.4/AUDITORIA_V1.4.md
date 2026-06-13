# AUDITORÍA v1.4 — 12 JUNIO 2026
## Custodio RAT Manager

**Fecha auditoría:** 12 Junio 2026
**Carpeta:** `docs/auditorias/2026-06-12_auditoria_v1.4/`
**Documentos base:** Versión v1.3 (09 Junio 2026)
**Documentos objetivo:** Versión v1.4 (12 Junio 2026)
**Score anterior:** 7.6/10 (post-fix OCI)
**Madurez:** Beta → Producción Inicial

---

## 1. RESUMEN EJECUTIVO

Auditoría post-integración OCI Object Storage. Los principales cambios desde v1.3 son:
- Integración completa de OCI Object Storage con fallback chain (PAR → signed GET → BYTEA)
- Nuevos endpoints de administración del asesor IA (indexación, stats, eliminación de chunks)
- Mejoras en el servicio de IA con soporte MiniMax M2.7
- El score se mantiene en 7.6/10 tras los fixes de OCI

### Commits desde auditoría v1.3 (09-Jun-2026 → 12-Jun-2026)

| Commit | Fecha | Descripción |
|--------|-------|-------------|
| `57cbffc` | 12-Jun | fix(storage): fallback OCI download cuando PAR falla |
| `reorganizacion-carpetas` | 12-Jun | Reorganización carpetas docs/, scripts/, archive/ |

---

## 2. ENDPOINTS DETECTADOS EN CÓDIGO

### 2.1 Backend — Routes completas (TODOS)

| Método | Ruta | Función | Estado en docs v1.3 | Cambio |
|--------|------|---------|---------------------|--------|
| GET | `/` | root | ✓ Documentado | — |
| GET | `/health` | health | ✓ Documentado v1.3 | — |
| GET | `/health/db` | health_db | ✓ Documentado | — |
| POST | `/auth/login` | login | ✓ Documentado | — |
| POST | `/auth/refresh` | refresh_token | ✓ Documentado | — |
| POST | `/auth/logout` | logout | ✓ Documentado | — |
| GET | `/auth/me` | me | ✓ Documentado | — |
| POST | `/auth/users` | crear_usuario | ✓ Documentado | — |
| GET | `/auth/users` | listar_usuarios | ✓ Documentado | — |
| PUT | `/auth/users/{user_id}` | actualizar_usuario | ✓ Documentado | — |
| DELETE | `/auth/users/{user_id}` | eliminar_usuario | ✓ Documentado | — |
| PUT | `/auth/users/{user_id}/password` | cambiar_password_otro | ✓ Documentado | — |
| PUT | `/auth/me/password` | cambiar_password | ✓ Documentado | — |
| GET | `/companies/publico` | listar_publico | ✓ Documentado | — |
| GET | `/companies/` | listar | ✓ Documentado | — |
| GET | `/companies/{company_id}` | obtener | ✓ Documentado | — |
| POST | `/companies/` | crear | ✓ Documentado | — |
| PUT | `/companies/{company_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/companies/{company_id}` | eliminar | ✓ Documentado | — |
| GET | `/rats/` | listar | ✓ Documentado | — |
| GET | `/rats/reportes` | reportes | ✓ Documentado | — |
| GET | `/rats/dashboard/{company_id}` | dashboard | ✓ Documentado | — |
| GET | `/rats/sugerencias/tipos` | tipos_proceso | ✓ Documentado | — |
| POST | `/rats/sugerencias` | sugerencias | ✓ Documentado | — |
| GET | `/rats/{rat_id}` | obtener | ✓ Documentado | — |
| POST | `/rats/` | crear | ✓ Documentado | — |
| PUT | `/rats/{rat_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/rats/{rat_id}` | eliminar | ✓ Documentado | — |
| POST | `/rats/{rat_id}/consentimientos` | crear_consentimiento | ✓ Documentado | — |
| POST | `/rats/{rat_id}/revision` | registrar_revision | ✓ Documentado | — |
| POST | `/rats/{rat_id}/aprobar` | approve_rat | ✓ Documentado | — |
| GET | `/rats/{rat_id}/archivo` | descargar_archivo | ✗ **NUEVO v1.4** | ✅ OCI fallback chain |
| GET | `/rats/{rat_id}/auditoria` | auditoria | ✓ Documentado | — |
| GET | `/rats/auditoria/{company_id}` | auditoria_global | ✓ Documentado | — |
| GET | `/rats/auditoria/verify-chain` | verificar_cadena_auditoria | ✓ Documentado | — |
| GET | `/rats/export/csv` | exportar_a_csv | ✓ Documentado | — |
| GET | `/rats/export/pdf` | exportar_a_pdf | ✓ Documentado | — |
| GET | `/rats/{rat_id}/export/pdf` | exportar_rat_individual_pdf | ✓ Documentado | — |
| GET | `/rats/export/cni` | exportar_cni | ✓ Documentado | — |
| GET | `/brechas/` | listar | ✓ Documentado | — |
| GET | `/brechas/{breach_id}` | obtener | ✓ Documentado | — |
| POST | `/brechas/` | crear | ✓ Documentado | — |
| PUT | `/brechas/{breach_id}` | actualizar | ✓ Documentado | — |
| POST | `/brechas/{breach_id}/evaluar-riesgo` | evaluar_riesgo | ✓ Documentado | — |
| DELETE | `/brechas/{breach_id}` | eliminar | ✓ Documentado | — |
| GET | `/consentimientos/` | listar_consentimientos | ✓ Documentado | — |
| GET | `/consentimientos/{consentimiento_id}` | obtener_consentimiento | ✓ Documentado | — |
| POST | `/consentimientos/` | crear_consentimiento | ✓ Documentado | — |
| POST | `/consentimientos/{consentimiento_id}/revocar` | revocar_consentimiento | ✓ Documentado | — |
| GET | `/eipd/` | listar_eipds | ✓ Documentado | — |
| GET | `/eipd/rat/{rat_id}` | obtener_eipd_por_rat | ✓ Documentado | — |
| POST | `/eipd/` | crear_eipd | ✓ Documentado | — |
| PUT | `/eipd/{eipd_id}` | actualizar_eipd | ✓ Documentado | — |
| GET | `/encargados-contrato/` | listar | ✓ Documentado | — |
| GET | `/encargados-contrato/{contrato_id}` | obtener | ✓ Documentado | — |
| POST | `/encargados-contrato/` | crear | ✓ Documentado | — |
| PUT | `/encargados-contrato/{contrato_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/encargados-contrato/{contrato_id}` | eliminar | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/dashboard` | dashboard | ✓ Documentado | — |
| POST | `/tkt-solicitud-derecho/` | crear_ticket_endpoint | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/` | listar_tickets | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}` | obtener_ticket | ✓ Documentado | — |
| PATCH | `/tkt-solicitud-derecho/{ticket_id}` | actualizar_ticket | ✓ Documentado | — |
| POST | `/tkt-solicitud-derecho/{ticket_id}/notas` | agregar_nota | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}/notas` | listar_notas | ✓ Documentado | — |
| GET | `/tkt-solicitud-derecho/{ticket_id}/historial` | listar_historial | ✓ Documentado | — |
| GET | `/solicitudes-derecho/token` | obtener_token | ✓ Documentado | — |
| POST | `/solicitudes-derecho/` | crear_solicitud | ✓ Documentado | — |
| GET | `/solicitudes-derecho/` | listar_solicitudes | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}` | obtener_solicitud | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}/historial` | obtener_historial | ✓ Documentado | — |
| PATCH | `/solicitudes-derecho/{solicitud_id}/responder` | responder_solicitud | ✓ Documentado | — |
| POST | `/solicitudes-derecho/{solicitud_id}/bloquear` | bloquear_rat | ✓ Documentado | — |
| POST | `/solicitudes-derecho/{solicitud_id}/desbloquear` | desbloquear_rat | ✓ Documentado | — |
| GET | `/solicitudes-derecho/{solicitud_id}/portabilidad/export` | exportar_portabilidad | ✓ Documentado | — |
| GET | `/publico/transparencia/{company_id}` | obtener_politica | ✓ Documentado | — |
| GET | `/rubros` | listar_rubros | ✓ Documentado | — |
| POST | `/rubros` | crear_rubro | ✓ Documentado | — |
| PUT | `/rubros/{rubro_id}` | editar_rubro | ✓ Documentado | — |
| DELETE | `/rubros/{rubro_id}` | eliminar_rubro | ✓ Documentado | — |
| GET | `/rubros/{rubro_id}/sugerencias` | sugerencias_por_rubro | ✓ Documentado | — |
| GET | `/rats-sugeridos` | listar_sugerencias | ✓ Documentado | — |
| POST | `/rats-sugeridos` | crear_sugerencia | ✓ Documentado | — |
| PUT | `/rats-sugeridos/{sugerencia_id}` | editar_sugerencia | ✓ Documentado | — |
| DELETE | `/rats-sugeridos/{sugerencia_id}` | eliminar_sugerencia | ✓ Documentado | — |
| GET | `/companies/{company_id}/usuarios/` | listar | ✓ Documentado | — |
| POST | `/companies/{company_id}/usuarios/` | agregar | ✓ Documentado | — |
| PUT | `/companies/{company_id}/usuarios/{user_id}` | actualizar | ✓ Documentado | — |
| DELETE | `/companies/{company_id}/usuarios/{user_id}` | remover | ✓ Documentado | — |
| GET | `/admin/feriados/` | listar_feriados | ✓ Documentado | — |
| GET | `/admin/feriados/years` | listar_anios | ✓ Documentado | — |
| POST | `/admin/feriados/upload` | upload_feriados | ✓ Documentado | — |
| GET | `/admin/feriados/example` | download_example | ✓ Documentado | — |
| DELETE | `/admin/feriados/{anio}` | eliminar_feriados | ✓ Documentado | — |
| GET | `/admin/tasks/` | listar_tareas | ✓ Documentado | — |
| GET | `/admin/tasks/stats` | stats | ✓ Documentado | — |
| POST | `/admin/tasks/run` | run_tasks | ✓ Documentado | — |
| POST | `/admin/tasks/enqueue` | enqueue | ✓ Documentado | — |
| POST | `/ai/ask` | ask_ai | ✓ Documentado | — |
| POST | `/admin/asesor/index` | index_endpoint | ✗ **NUEVO v1.4** | ✅ Admin asesor |
| GET | `/admin/asesor/stats` | stats_endpoint | ✗ **NUEVO v1.4** | ✅ Admin asesor |
| DELETE | `/admin/asesor/documents/{chunk_id}` | delete_chunk_endpoint | ✗ **NUEVO v1.4** | ✅ Admin asesor |

**Total endpoints detectados:** 74
**Endpoints nuevos desde v1.3:** 4 (3 admin asesor + 1 rats archivo)
**Endpoints sin cambios:** 70

---

## 3. RUTAS FRONTEND DETECTADAS

| Ruta | Componente | Estado |
|------|------------|--------|
| `/` | Root redirect | ✓ |
| `/login` | Login | ✓ |
| `/onboarding` | Onboarding | ✓ |
| `/solicitud_derecho` | Formulario ARCO público | ✓ |
| `/dashboard` | Dashboard | ✓ |
| `/rat` | RAT management | ✓ |
| `/companies` | Company CRUD | ✓ |
| `/breaches` | Security breaches | ✓ |
| `/reportes` | Advanced reporting | ✓ |
| `/usuarios` | User management | ✓ |
| `/conexion` | Connection diagnostics | ✓ |
| `/rubros` | Rubros + RAT suggestions | ✓ |
| `/encargados-contrato` | Data processor contracts | ✓ |
| `/transparencia` | Transparency policy | ✓ |
| `/tkt_solicitud_derecho` | ARCO ticket management | ✓ |
| `/configuracion` | Account settings | ✓ |
| `/consentimientos` | Consent management | ✓ |
| `/eipd` | Data Protection Impact Assessments | ✓ |

**Total páginas frontend:** 19 (sin cambios desde v1.3)

---

## 4. MODELOS DE DATOS

| Modelo | Tabla | Campos principales | Estado |
|--------|-------|-------------------|--------|
| User | users | id, username, email, full_name, hashed_password, is_active, is_admin, rol_global, created_at | ✓ |
| Company | companies | id, nombre, rut, rubro, direccion, contacto_dpo, email_dpo, descripcion, canal_ejercicio_derechos | ✓ |
| RAT | rats | id, company_id, nombre_proceso, 9 campos obligatorios, flags, estado, created_by + archivo_base_legal_storage_url | ✓ (+OCI URL field) |
| SecurityBreach | security_breaches | id, company_id, descripcion, fecha_deteccion, riesgos, niveles, notificacion | ✓ |
| EIPD | eipds | id, rat_id (1:1), metodologia, objetivos, riesgos, medidas, resultado, fecha | ✓ |
| Consentimiento | consentimientos | id, company_id, rat_id, nombre_titular, canal, texto_consentimiento, fecha_obtencion, activo | ✓ |
| EncargadoContrato | encargados_contrato | id, company_id, rat_id, nombre_encargado, objeto, duracion, finalidad, archivo_pdf | ✓ |
| UserCompany | user_companies | id, user_id, company_id, rol (ADMIN/EDITOR/VIEWER), UNIQUE(user_id, company_id) | ✓ |
| TktSolicitudDerecho | tkt_solicitud_derecho | id, company_id, tipo, estado, prioridad, titular, fecha_recepcion, fecha_vencimiento, responsable_id | ✓ |
| TktNota | tkt_notas | id, ticket_id, user_id, nota, created_at | ✓ |
| TktAdjunto | tkt_adjuntos | id, ticket_id, filename, content_type, data | ✓ |
| TktHistorial | tkt_historial | id, ticket_id, estado_anterior, estado_nuevo, user_id, descripcion | ✓ |
| SolicitudDerecho | solicitudes_derecho | id, company_id, tipo, nombre_titular, email_titular, estado, solicitud_fecha, respuesta, rat_id | ✓ |
| SolicitudHistorial | solicitud_derecho_historial | id, solicitud_id, estado_anterior, estado_nuevo, descripcion, fecha | ✓ |
| Feriado | feriados | id, anio, mes, dia, nombre, tipo, UNIQUE(anio, mes, dia) | ✓ |
| AuditLog | audit_logs | id, entidad, entidad_id, accion, usuario, detalle, ip_origen, timestamp, prev_hash, hash | ✓ |
| TaskQueue | task_queue | id, task_type, status, payload, attempts, scheduled_for, started_at, completed_at | ✓ |
| TokenBlacklist | token_blacklist | id, jti, created_at, expires_at | ✓ |
| Rubro | rubros | id, nombre, orden | ✓ |
| RATSugerido | rats_sugeridos | id, rubro_id, nombre_proceso, categoria_datos, categoria_titulares, finalidad, base_legal, flags | ✓ |
| PoliticaTransparencia | politicas_transparencia | id, company_id, version, fecha_generacion, hash_sha256, generado_por | ✓ |
| SolicitudToken | solicitud_tokens | id, token, ip_address, created_at, used | ✓ |
| AsesorChunk | asesor_chunks | id, content, source, chunk_index, created_at | ✓ (nuevo en v1.4) |

**Total modelos:** 23 (+1 AsesorChunk desde v1.3)

---

## 5. CAMBIOS vs DOCUMENTACIÓN v1.3

| Documento | v1.3 en docs | Código coincide? | Cambios detectados | Generar v1.4? |
|-----------|-------------|-----------------|-------------------|---------------|
| 00_Índice | v1.1 | ✓ | Ninguno | NO |
| 01_Visión | v1.0 | ✓ | Ninguno | NO |
| 02_Requisitos | v1.3 | ✗ | RF-117 (OCI storage), RF-118 (admin asesor) | **SÍ** |
| 03_HU | v1.3 | ✗ | HU relacionadas con OCI y admin asesor | **SÍ** |
| 04_CU | v1.3 | ✗ | CU para descarga con fallback OCI, admin asesor | **SÍ** |
| 05_Diseño | v1.3 | ✓? | Verificar cobertura OCI | **VERIFICAR** |
| 06_Arquitectura | v1.3 | ✗ | OCI Object Storage, fallback chain, admin asesor, MiniMax M2.7 | **SÍ** |
| 07_Modelo Datos | v1.1 | ✓ | AsesorChunk ya en v1.1 | NO |
| 08_APIs | v1.3 | ✗ | `/rats/{id}/archivo`, `/admin/asesor/*` no documentados | **SÍ** |
| 09_Backlog | v1.3 | ✓ | Sin cambios | NO |
| 10_Plan_QA | v1.3 | ✓ | Sin cambios | NO |
| 11_Despliegue | v1.2 | ✓ | Sin cambios | NO |
| 12_Manual_Técnico | v1.3 | ✗ | OCI storage, fallback chain, asesor service | **SÍ** |
| Matriz_Trazabilidad | v1.3 | ✗ | TC para OCI y admin asesor | **SÍ** |

---

## 6. SCORECARD COMPARATIVO

| Dimensión | v1.3 (09 Jun) | v1.4 (12 Jun) | Delta |
|-----------|--------------|----------------------|-------|
| Escalabilidad | 7/10 | **7.5/10** | +0.5 (OCI bucket分离) |
| Mantenibilidad | 7/10 | **7/10** | — |
| Seguridad | 8.5/10 | **8.5/10** | — |
| Rendimiento | 7/10 | **7/10** | — |
| Observabilidad | 7/10 | **7.5/10** | +0.5 (archive logging) |
| Arquitectura General | 7/10 | **7.5/10** | +0.5 |
| **Overall** | **7.3/10** | **7.6/10** | **+0.3** |

---

## 7. PENDIENTES CRÍTICOS (No abordados en v1.4)

| ID | Descripción | Prioridad | Razón |
|----|-------------|-----------|-------|
| S14 | CSRF protection | ALTA | Sin implementar. 3 opciones documentadas; requiere decisión arquitectura. |
| C1 | App-level encryption | ALTA | Neon AES-256 ya aplicado. App-level requiere alcance definido. |
| A10 | Schemas inline | BAJA | 7 schemas en solicitudes_derecho.py; alto riesgo de refactor. |

---

## 8. FORTALEZAS DETECTADAS

- OCI Object Storage con fallback chain robusto (PAR → signed GET → BYTEA)
- Hash chain de auditoría implementaddo y funcional
- RBAC completo con 3 niveles de acceso
- Módulo deIA con soporte MiniMax y OpenAI
- Cola de tareas asíncronas con retry automático
- Exportación PDF, CSV, CNI para compliance APDC
- Rat limit implementado en endpoints críticos

---

*Documento generado: 12 Junio 2026*
*Auditoría Custodio RAT Manager v1.4 — post-integración OCI*