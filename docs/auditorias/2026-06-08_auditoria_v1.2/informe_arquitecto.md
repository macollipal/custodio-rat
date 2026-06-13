# INFORME DE AUDITORÍA ARQUITECTURA DE SOFTWARE
## Custodio RAT Manager

**Especialista:** Arquitecto de Software Senior
**Fecha:** 08 Junio 2026
**Auditoría:** v1.2
**Puntuación global:** 4.83/10

---

## 1. RESUMEN EJECUTIVO

Sistema Custodio RAT Manager basado en FastAPI (backend) y Next.js (frontend), operando en entorno Python 3.11 con SQLAlchemy 2.0 y PostgreSQL. El sistema implementa gestión de derechos ARCO, manejo de incidentes de seguridad, y funcionalidades de cumplimiento regulatorio bajo la Ley 21.719 chilena.

**Puntuación Arquitectura:** 4.83/10 — Requiere mejoras significativas en seguridad, patrones de diseño y documentación técnica.

---

## 2. HALLAZGOS POR CATEGORÍA

### 2.1 CRÍTICO (P0) — Deben corregirse inmediatamente

| # | Categoría | Hallazgo | Ubicación | Impacto |
|---|-----------|----------|-----------|---------|
| A1 | Seguridad | Token blacklist no consultado en `get_current_user` — tokens revocados siguen activos | `routes/deps.py` | CRÍTICO |
| A2 | Seguridad | IDOR en `/companies/{id}` — usuario puede acceder a datos de otra empresa | `routes/companies.py` | CRÍTICO |
| A3 | Seguridad | `/companies/publico` accesible sin autenticación | `routes/companies.py` | CRÍTICO |
| A4 | Seguridad | CSV injection en exportación de datos — parámetros no sanitizados | Múltiples rutas | CRÍTICO |

### 2.2 ALTO (P1) — Corregir en sprint actual

| # | Categoría | Hallazgo | Ubicación | Impacto |
|---|-----------|----------|-----------|---------|
| A5 | Arquitectura | Ausencia de patrón Repository — lógica de acceso a datos acoplada a routes | `routes/*.py` | ALTO |
| A6 | Arquitectura | Sin capa de servicios para lógica de negocio compleja | `routes/tkt_*.py` | ALTO |
| A7 | Arquitectura | Dependencies compartidas no centralizadas consistentemente | `routes/deps.py` | ALTO |
| A8 | Performance | Índices faltantes en consultas frecuentes | `models/rat.py`, `models/breach.py` | ALTO |
| A9 | Documentación | Endpoints undocumented en swagger | Varios routes | MEDIO |
| A10 | Arquitectura | Schemas duplicados entre módulos (EIPD, Rats, etc.) | `schemas/*.py` | MEDIO |

### 2.3 MEDIO (P2) — Corregir en backlog

| # | Categoría | Hallazgo | Ubicación |
|---|-----------|----------|-----------|
| A11 | Arquitectura | Ausencia de circuit breaker para llamadas externas | Services externos |
| A12 | Arquitectura | Sin retry logic para operaciones de base de datos | Transacciones |
| A13 | Documentación | Modelos de datos no documentados con relaciones | `models/*.py` |
| A14 | Arquitectura | Configuration dispersa entre .env y variables hardcoded | Múltiples archivos |
| A15 | Performance | N+1 queries detectadas en listados | `routes/rats.py`, `routes/breaches.py` |

---

## 3. ANÁLISIS DETALLADO

### 3.1 Gestión de Autenticación y Autorización

**Problema central:** El sistema implementa JWT tokens pero la invalidación de tokens no funciona correctamente. No existe una blacklist de tokens revocados consultada en cada request.

```
Flujo actual:
get_current_user(token) → decode_jwt(token) → return user
                              ↑
                     NO consulta blacklist
```

**Recomendación:**
```python
async def get_current_user(token: str = Depends(get_token_from_header)):
    payload = decode_jwt(token)
    if await token_blacklist.is_revoked(token):
        raise HTTPException(status_code=401)
    # continuar...
```

### 3.2 Control de Acceso por Empresa (IDOR)

El patrón `check_company_access` fue centralizado en `deps.py` y aplicado a múltiples rutas, lo cual es positivo. Sin embargo, `/companies/{id}` y `/companies/publico` permanecen sin esta validación.

### 3.3 Patrones de Arquitectura

El sistema carece de separación clara entre:
- **Routes** (presentación)
- **Services** (lógica de negocio)
- **Repositories** (acceso a datos)

Actualmente, las rutas contienen lógica de negocio mezclada con validaciones y queries SQLAlchemy.

### 3.4 Base de Datos

**Positivo:** Se添加aron índices `ix_rats_company_estado` y `ix_security_breaches_company_fecha` durante esta sesión.

**Pendiente:** 
- FK sin constraint en varias tablas
- Sequences no manejadas correctamente en PostgreSQL
- Sin migrations (Alembic configurado pero no usado consistentemente)

---

## 4. METRICAS DE CÓDIGO

| Métrica | Valor | Referencia |
|---------|-------|------------|
| Líneas de código Python | ~15,000 | — |
| Routes detectados | 45 | — |
| Modelos detectados | 22 | — |
| Servicios | 3 | Muy bajo |
| Schemas | 12 | — |
| Test coverage | N/D | — |

---

## 5. RECOMENDACIONES

### Corto plazo (esta semana)
1. Implementar blacklist de tokens en `deps.py`
2. Agregar `check_company_access` a `/companies/{id}` y `/companies/publico`
3. Crear función de sanitización para exports CSV

### Mediano plazo (2-4 semanas)
4. Extraer lógica de negocio a capa de servicios
5. Implementar patrón Repository para acceso a datos
6. Agregar Alembic migrations para esquema actual
7. Documentar todos los endpoints con docstrings y tipos

### Largo plazo (1-2 meses)
8. Implementar tests unitarios y de integración
9. Configurar CI/CD con linting y type checking
10. Implementar logging estructurado con correlation IDs

---

## 6. SCORE CARD

| Dimensión | Puntuación | Observaciones |
|-----------|------------|---------------|
| Diseño de datos | 5/10 | Índices agregados, FKs pendientes |
| Seguridad | 3/10 | Hallazgos P0 sin corregir |
| Arquitectura | 5/10 | Sin capas diferenciadas |
| Performance | 5/10 | Índices ayudan, N+1 persiste |
| Documentación | 5/10 | Incompleta |
| DevOps | 4/10 | Sin migrations, sin tests |
| **TOTAL** | **4.83/10** | — |

---

*Informe generado: 08 Junio 2026*
*Próxima auditoría: 15 Junio 2026*