# Runbook de DR Test — Custodio RAT

> **Objetivo**: Validar que el sistema puede recuperarse de un desastre (pérdida de BD, caída de Vercel, corrupción de datos) dentro de los objetivos RTO/RPO.

## Objetivos de recuperación

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| **RTO** (Recovery Time Objective) | < 4 horas | 🎯 Target |
| **RPO** (Recovery Point Objective) | < 1 hora | 🎯 Target |
| **Disponibilidad mensual** | ≥ 99.5% | 🎯 Target |

## Escenarios de desastre cubiertos

| # | Escenario | RPO esperado | RTO esperado |
|---|-----------|--------------|--------------|
| 1 | Pérdida total de Neon DB (drop accidental) | < 1h | < 2h |
| 2 | Corrupción de datos por bug en deploy | < 1h | < 4h |
| 3 | Caída de Vercel (region outage) | N/A | < 1h (failover) |
| 4 | Pérdida de archivos en OCI Object Storage | < 24h | < 4h |
| 5 | Brecha de seguridad con extracción de datos | N/A | < 24h (notif APDC) |

---

## Pre-requisitos

Antes de ejecutar el DR test, verificar:

- [ ] Acceso a Neon Console con rol admin
- [ ] Acceso a Vercel Dashboard (cuenta `macollipal-7370`)
- [ ] Acceso a OCI Object Storage (namespace `custodio-qa` o prod)
- [ ] Acceso al repo de GitHub (rama `qa`)
- [ ] Backup reciente en Neon (< 24h de antigüedad)
- [ ] Variables de entorno documentadas en `docs/despliegue/PLAN_DEPLOY.md`

---

## Procedimiento de DR test

### Escenario 1: Pérdida total de BD

**Objetivo**: Recuperar BD desde backup de Neon.

#### Paso 1: Notificar stakeholders (T+0)
```bash
# Slack/email al equipo:
# "DR Test en curso. Sistema puede estar intermitente durante ~30 min."
```

#### Paso 2: Verificar último backup (T+5min)
- Abrir Neon Console → seleccionar branch → "Restore" → ver backups disponibles
- Anotar el **PIT (Point In Time)** más reciente antes del test
- Confirmar que el backup está completo (no corrupto)

#### Paso 3: Crear BD de DR (T+10min)
```bash
# Opción A: Neon Console → "Create branch from..." → seleccionar PIT
# Opción B: psql con backup manual
psql "$DATABASE_URL_ORIGINAL" --file=backup_2026-07-13_1200.sql
```

#### Paso 4: Apuntar app a BD de DR (T+15min)
```bash
# En Vercel → Settings → Environment Variables → DATABASE_URL
# Cambiar al connection string de la BD de DR

# Trigger redeploy
vercel --prod --force
```

#### Paso 5: Smoke test (T+20min)
```bash
# Desde local con nueva DATABASE_URL
cd backend
python -m pytest tests/test_smoke.py -v
# Esperado: tests pasan contra BD restaurada
```

#### Paso 6: Validar datos críticos (T+25min)
- [ ] Login con usuario admin funciona
- [ ] Lista de empresas correcta
- [ ] Lista de RATs coincide con BD pre-test
- [ ] Hash chain de auditoría válido (`GET /admin/audit/verify`)
- [ ] Archivos en OCI storage accesibles (sample 5 archivos)

#### Paso 7: Documentar resultados (T+30min)
- Llenar tabla "Resultados del test" abajo
- Reportar a stakeholders
- Cerrar incidente

### Escenario 2: Corrupción de datos

**Objetivo**: Restaurar registros corruptos desde backup.

#### Paso 1: Identificar corrupción
```bash
# Query para detectar anomalías
psql "$DATABASE_URL" -c "
SELECT entity, entity_id, action, created_at 
FROM audit_log 
WHERE hash != encode(sha256(...), 'hex')
ORDER BY id DESC LIMIT 10;"
```

#### Paso 2: Determinar ventana de tiempo afectada
- Última transacción válida: `SELECT MAX(created_at) FROM audit_log WHERE hash_valid`
- Ventana corrupta: [último válido, momento de deploy]

#### Paso 3: Restaurar registros específicos (no toda la BD)
```bash
# Para cada registro corrupto:
psql "$DATABASE_URL" -c "
INSERT INTO rats (id, ...)
SELECT * FROM rats_backup
WHERE id = 123;
"
```

#### Paso 4: Verificar integridad
```bash
curl -X GET https://custodio-qa.vercel.app/api/v1/admin/audit/verify
```

---

## Resultados del test

| Test # | Fecha | Escenario | RTO medido | RPO medido | Resultado | Notas |
|--------|-------|-----------|------------|------------|------------|-------|
| 1 | YYYY-MM-DD | Pérdida total BD | _h | _h | ✅ / ❌ | |
| 2 | YYYY-MM-DD | Corrupción | _h | _h | ✅ / ❌ | |
| 3 | YYYY-MM-DD | Caída Vercel | _h | N/A | ✅ / ❌ | |
| 4 | YYYY-MM-DD | Pérdida OCI | _h | _h | ✅ / ❌ | |

---

## Post-mortem

Después de cada DR test, documentar:

1. **¿Qué funcionó bien?**
2. **¿Qué falló?**
3. **Tiempo total de recuperación real vs objetivo**
4. **Acciones correctivas** (con responsable + fecha)
5. **Lecciones aprendidas**

---

## Contactos de emergencia

| Rol | Persona | Canal |
|-----|---------|-------|
| DBA on-call | ver `docs/despliegue/RUNBOOKS/` (crear) | Slack #custodio-ops |
| Vercel admin | Cliente/Admin de Vercel | Dashboard Vercel |
| Neon admin | Cliente/Admin de Neon | Console Neon |
| Legal/DPO | DPO del cliente | Email |

---

## Frecuencia del test

- **Smoke test mensual**: verificar backups existen y son válidos
- **DR test completo trimestral**: ejecutar procedimiento completo
- **DR test anual**: simular pérdida total con stakeholders

---

*Documento vivo. Actualizar después de cada DR test.*

*Versión: 1.0 — 2026-07-13*
*Próximo test programado: Q4 2026*