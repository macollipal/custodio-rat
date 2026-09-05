# A5/A6 — Arquitectura: Repository Pattern + Capa de Servicios

## Estado: EN PROGRESO (Ola 3) — Implementación parcial

---

## Hallazgo Original

| ID | Descripción | Esfuerzo | Estado |
|----|-------------|----------|--------|
| A5 | Sin patrón Repository — lógica acoplada | ALTO (1 semana) | 🟡 Parcial (A5 creado, no usado aún) |
| A6 | Sin capa de servicios | ALTO (1 semana) | ⚠️ Confirmado (106 instancias de db.query() en routes) |

---

## A5 — Repository Pattern (Parcial)

### Lo implementado en Ola 3

Estructura creada en `app/repositories/`:

```
app/repositories/
├── __init__.py
├── base.py              # Repository[T] genérico con CRUD
└── rat_repository.py    # RATRepository con eager loading
```

### Lo que falta (v1.3)
- `company_repository.py`
- `breach_repository.py`
- `user_repository.py`
- `audit_repository.py`
- Migración gradual de services/routes para usar repositories

### Estrategia de migración (aditiva)

**Fase 1 (v1.3):** Usar repositories en nuevo código
```python
# En lugar de:
rat = db.query(RAT).filter(RAT.id == rat_id).first()

# Usar:
repo = RATRepository(db)
rat = repo.get_with_relations(rat_id)
```

**Fase 2 (v1.4):** Migrar services existentes uno por uno
```python
# rat_service.py → usa RATRepository internamente
def get_rat(db, rat_id):
    repo = RATRepository(db)
    return repo.get_with_relations(rat_id)
```

**Fase 3 (v1.5):** Routes migradas a services → repositories

---

## A6 — Capa de Servicios (Confirmado, no resuelto)

### Situación actual

106 instancias de acceso directo a BD en `routes/`:
- `routes/rats.py` — 9 db.query(), db.add(), db.commit()
- `routes/consentimientos.py` — 7 db.query(), db.add(), db.commit()
- `routes/eipd.py` — 8 db.query(), db.add(), db.commit()
- `routes/solicitudes_derecho.py` — 15+ db.query(), db.add(), db.commit()
- `routes/tkt_solicitud_derecho.py` — 12+ db.query(), db.add(), db.commit()
- `routes/companies.py` — 5 db.query()
- `routes/feriados.py` — 4 db.query(), db.add(), db.commit()
- `routes/rubros.py` — 8 db.query(), db.add(), db.commit()
- `routes/encargados_contrato.py` — 6 db.query(), db.add(), db.commit()

### Lo que debería estar en services (y no está)

| Route | Lógica que debería estar en service |
|-------|-------------------------------------|
| `rats.py` | Creación de RAT con validaciones (`_validar_consentimiento_sensibles`, `_validar_contrato_encargado`) — YA están en `rat_service.py` ✅ |
| `solicitudes_derecho.py` | Lógica de workflow ARCO, generación de tokens, envío de emails |
| `tkt_solicitud_derecho.py` | Lógica de tickets con validaciones de SLA |
| `companies.py` | Creación de empresa con validaciones |
| `consentimientos.py` | CRUD de consentimientos — la mayor parte ya está en `consentimiento_service`? (no existe) |

### Servicios existentes

| Service | Cobertura |
|---------|-----------|
| `user_service.py` | ✅ Completo — auth, users |
| `rat_service.py` | ✅ bueno — CRUD + validaciones |
| `breach_service.py` | ✅ bueno — CRUD + enriquecimiento |
| `company_service.py` | ✅ básico — CRUD |
| `audit_service.py` | ✅ hash chain |
| `task_service.py` | ✅ cola de tareas |
| `ticket_service.py` | ✅ cálculo SLA + feriados |
| `export_service.py` | ✅ CSV/PDF export |
| `user_company_service.py` | ✅ gestión accesos |

### Servicios FALTANTES (para cerrar A6)

| Service faltante | Prioridad |
|-----------------|-----------|
| `consentimiento_service.py` | Alta |
| `solicitud_derecho_service.py` | Alta |
| `tkt_service.py` (ticket service ya existe pero no se usa consistentemente) | Media |

### Plan de cierre A6 (v1.3)

**Sprint 1:**
- Crear `consentimiento_service.py` (mover lógica de `routes/consentimientos.py`)
- Migrar `routes/consentimientos.py` a usar el service

**Sprint 2:**
- Crear `solicitud_derecho_service.py` (mover lógica de `routes/solicitudes_derecho.py`)
- Migrar `routes/solicitudes_derecho.py`

**Sprint 3:**
- Crear `tkt_service.py` (ya existe `ticket_service.py`, verificar uso en routes)
- Migrar `routes/tkt_solicitud_derecho.py`

---

## Recomendación de Cierre Ola 3

**A5:** Parcialmente cerrado — estructura creada, lista para usar en v1.3
**A6:** Documentado, plan creado, implementación en v1.3

El refactor completo de A6 (106 db.query() en routes) es un esfuerzo de 2-3 sprints que no debería hacerse en el mismo ciclo que los P0 de compliance.

---

*Documento generado: 08 Junio 2026*
*A5/A6 — Repository Pattern + Capa de Servicios — Custodio RAT Manager v1.2*