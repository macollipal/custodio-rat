# Diff Código vs Documentos v1.8 — 2026-06-26

## Resumen

| Aspecto | Estado |
|---------|--------|
| Código modificado | ✅ Coherente con docs |
| Docs regenerados | ✅ 9/9 documentos |
| Inconsistencias | ninguna |

## Comparación Código ↔ Documentos

### 02 — Requisitos Funcionales
| Requisito | Código | Doc | Estado |
|-----------|--------|-----|--------|
| RF-141 | `LargeBinary(10_000_000)` en `rat.py` + CHECK constraint | BYTEA 10MB limit | ✅ |
| RF-142-149 | 15 campos Tier 1+Tier 2 en RAT | 15 campos RAT en doc | ✅ |
| RF-156 | `LargeBinary(10_000_000)` en `tkt_adjunto.py` | BYTEA 10MB limit | ✅ |
| RF-157 | `Field(min_length=50)` en `test_interes_legitimo` | Test IL min 50 chars | ✅ |
| RF-158 | `hashlib.sha256()` en PATCH TKT | Hash SHA-256 auto ARCO | ✅ |
| RF-159 | `CausalRechazoEnum` con 7 valores | causal_rechazo enum 7 valores | ✅ |
| RF-160 | `w-11 h-11` en toggle ARCO | Toggle 44x44px mobile | ✅ |
| RF-161 | `notificar_nueva_brecha()` en `actualizar_brecha()` | Notificación APDC auto | ✅ |
| RF-162 | `Log.info` en `actualizar_brecha()` (titulares) | Notificación titulares | ✅ |

### 03 — Historias de Usuario
| HU | Código | Doc | Estado |
|----|--------|-----|--------|
| HU-086 | `LargeBinary(10_000_000)` + CHECK | HU-086 en doc | ✅ |
| HU-087 | 15 campos en schema/model | HU-087 en doc | ✅ |
| HU-090 | `LargeBinary(10_000_000)` tkt_adjunto | HU-090 en doc | ✅ |
| HU-091 | `Field(min_length=50)` | HU-091 en doc | ✅ |
| HU-092 | `hashlib.sha256()` auto | HU-092 en doc | ✅ |
| HU-093 | `CausalRechazoEnum` | HU-093 en doc | ✅ |
| HU-094 | `w-11 h-11` toggle | HU-094 en doc | ✅ |
| HU-095 | `notificar_nueva_brecha()` | HU-095 en doc | ✅ |
| HU-096 | `Log.info` titulares | HU-096 en doc | ✅ |

### 04 — Casos de Uso
| CU | Código | Doc | Estado |
|----|--------|-----|--------|
| CU-069 | BYTEA 10MB | CU-069 en doc | ✅ |
| CU-070 | BYTEA 10MB tkt_adjunto | CU-070 en doc | ✅ |
| CU-071 | Test IL min 50 | CU-071 en doc | ✅ |
| CU-072 | Hash SHA-256 auto | CU-072 en doc | ✅ |
| CU-073 | CausalRechazoEnum | CU-073 en doc | ✅ |
| CU-074 | Toggle 44px | CU-074 en doc | ✅ |
| CU-075 | Notificación APDC | CU-075 en doc | ✅ |
| CU-076 | Notificación titulares | CU-076 en doc | ✅ |

### 06 — Arquitectura
| Componente | Código | Doc | Estado |
|------------|--------|-----|--------|
| Model RAT | 15 campos + BYTEA 10MB | Arquitectura doc | ✅ |
| Model TKT | CausalRechazo enum + BYTEA | Arquitectura doc | ✅ |
| Route TKT | Hash SHA-256 auto + HTTP 400 | Arquitectura doc | ✅ |
| Service Breach | Notificaciones APDC + titulares | Arquitectura doc | ✅ |

### 08 — API REST
| Endpoint | Código | Doc | Estado |
|----------|--------|-----|--------|
| PATCH /tkt-solicitud-derecho/{id} | SHA-256 + HTTP 400 | Endpoint en doc | ✅ |
| /tkt-solicitud-derecho/{id}/adjuntos | BYTEA 10MB | Endpoint en doc | ✅ |
| /rats | 15 campos + Field(min_length=50) | Endpoint en doc | ✅ |

### 10 — Plan QA
| Test Case | Código | Doc | Estado |
|-----------|--------|-----|--------|
| TC-030 | CHECK constraint 10MB | TC-030 en doc | ✅ |
| TC-031 | BYTEA tkt_adjunto 10MB | TC-031 en doc | ✅ |
| TC-032 | Test IL min 50 | TC-032 en doc | ✅ |
| TC-033 | Hash SHA-256 | TC-033 en doc | ✅ |
| TC-035 | CausalRechazoEnum | TC-035 en doc | ✅ |
| TC-037 | Notificación APDC | TC-037 en doc | ✅ |

### 12 — Manual Técnico
| Sección | Código | Doc | Estado |
|---------|--------|-----|--------|
| Flujo BYTEA 10MB | CHECK constraint + migration | Manual técnico | ✅ |
| Flujo Test IL 50 | Field(min_length=50) + UI | Manual técnico | ✅ |
| Flujo Hash SHA-256 | hashlib.sha256() en PATCH | Manual técnico | ✅ |
| Flujo causal_rechazo | Enum + dropdown + toast | Manual técnico | ✅ |
| Toggle ARCO mobile | w-11 h-11 | Manual técnico | ✅ |
| Notificaciones | notificar_nueva_brecha() | Manual técnico | ✅ |

## Conclusión

**Código y documentación 100% coherentes.** Ninguna inconsistencia detectada.
