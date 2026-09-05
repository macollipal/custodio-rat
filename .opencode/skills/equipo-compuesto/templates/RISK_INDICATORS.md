# Template: Matriz de Indicadores de Riesgo — Custodio RAT

Matriz completa de indicadores de riesgo por módulo con fórmulas SQL y thresholds calibrados.

---

## Cómo usar esta matriz

Para cada indicador:
1. Identificar la fuente de dato (tabla, columna)
2. Verificar la fórmula SQL
3. Ajustar thresholds según el contexto del cliente
4. Implementar como query en el dashboard backend
5. Configurar alertas en frontend

---

## Indicadores por Módulo

---

### MÓDULO: RAT (Registro de Actividades de Tratamiento)

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| R-01 | RATs totales | `COUNT(*) FROM rats WHERE company_id = ?` | — | — | — |
| R-02 | RATs vencidos | `COUNT(*) FROM rats WHERE company_id = ? AND fecha_vencimiento < NOW() AND estado != 'archivado'` | >0 | — | Plazo retención |
| R-03 | RATs por vencer (30d) | `COUNT(*) FROM rats WHERE company_id = ? AND fecha_vencimiento BETWEEN NOW() AND NOW() + INTERVAL '30 days' AND estado NOT IN ('archivado','aprobado')` | >3 | >1 | Plazo legal |
| R-04 | RATs por vencer (7d) | `COUNT(*) FROM rats WHERE company_id = ? AND fecha_vencimiento BETWEEN NOW() AND NOW() + INTERVAL '7 days'` | >0 | — | Urgencia |
| R-05 | Completitud promedio | `AVG(calcular_completitud(r.*)) FROM rats WHERE company_id = ?` | <50% | <75% | Score interno |
| R-06 | RATs en borrador | `COUNT(*) FROM rats WHERE company_id = ? AND estado = 'borrador'` | >5 | >2 | Progreso |
| R-07 | RATs completos | `COUNT(*) FROM rats WHERE company_id = ? AND estado = 'completo'` / total | <50% | <70% | Madurez |
| R-08 | RATs aprobados | `COUNT(*) FROM rats WHERE company_id = ? AND estado = 'aprobado'` / total | <30% | <50% | Calidad |
| R-09 | RATs con datos sensibles | `COUNT(*) FROM rats WHERE company_id = ? AND datos_sensibles = TRUE` | — | — | Exposición |
| R-10 | RATs con EIPD pendiente | `COUNT(*) FROM rats WHERE company_id = ? AND evaluacion_impacto = TRUE AND estado_eipd NOT IN ('completada','no_requerida')` | >0 | — | Art. 15 bis |
| R-11 | RATs con transferencias int. | `COUNT(*) FROM rats WHERE company_id = ? AND transferencia_internacional = TRUE` | — | — | Exposición |
| R-12 | Transferencias sin garantías | `COUNT(*) FROM rats WHERE company_id = ? AND transferencia_internacional = TRUE AND (garantias_transferencia_int IS NULL OR garantias_transferencia_int = '')` | >0 | — | Art. 14 quater |
| R-13 | RATs bloqueados | `COUNT(*) FROM rats WHERE company_id = ? AND bloqueado = TRUE` | >0 | — | Art. 8 ter |
| R-14 | RATs sin archivo (base legal ≠ "otra") | `COUNT(*) FROM rats WHERE company_id = ? AND base_legal != 'otra' AND archivo_base_legal_datos IS NULL` | >0 | — | Art. 16 |
| R-15 | Interés legítimo sin test | `COUNT(*) FROM rats WHERE company_id = ? AND base_legal = 'interes_legitimo' AND test_interes_legitimo IS NULL` | >0 | >0 | Validación |
| R-16 | RATs sin medida de seguridad | `COUNT(*) FROM rats WHERE company_id = ? AND (medidas_seguridad IS NULL OR medidas_seguridad = '')` | >3 | >0 | Riesgo |

**Query agregada para dashboard RAT:**
```sql
SELECT
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE estado = 'borrador') as en_borrador,
  COUNT(*) FILTER (WHERE estado = 'completo') as completos,
  COUNT(*) FILTER (WHERE estado = 'aprobado') as aprobados,
  COUNT(*) FILTER (WHERE datos_sensibles = TRUE) as con_datos_sensibles,
  COUNT(*) FILTER (WHERE evaluacion_impacto = TRUE AND estado_eipd NOT IN ('completada','no_requerida')) as eipd_pendientes,
  COUNT(*) FILTER (WHERE transferencia_internacional = TRUE) as transferencias_int,
  COUNT(*) FILTER (WHERE transferencia_internacional = TRUE AND (garantias_transferencia_int IS NULL OR garantias_transferencia_int = '')) as transferencias_sin_garantia,
  COUNT(*) FILTER (WHERE fecha_vencimiento < NOW()) as vencidos,
  COUNT(*) FILTER (WHERE fecha_vencimiento BETWEEN NOW() AND NOW() + INTERVAL '30 days') as por_vencer_30d,
  ROUND(AVG(completitud_porcentaje), 1) as completitud_promedio
FROM rats
WHERE company_id = ?;
```

---

### MÓDULO: ARCO (Solicitudes de Derechos)

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| A-01 | Solicitudes pendientes | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado IN ('abierto','en_proceso','pendiente')` | >5 | >2 | Art. 12 |
| A-02 | Solicitudes vencidas (SLA) | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado NOT IN ('resuelto','rechazado') AND fecha_vencimiento < NOW()` | >0 | — | Plazo 10 días hábiles |
| A-03 | Solicitudes por vencer (48h) | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado NOT IN ('resuelto','rechazado') AND fecha_vencimiento BETWEEN NOW() AND NOW() + INTERVAL '48 hours'` | >0 | >2 | Urgencia |
| A-04 | Tiempo promedio respuesta | `AVG(EXTRACT(EPOCH FROM (respuesta_fecha - fecha_recepcion)) / 3600) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado = 'resuelto'` | >240h (>10 días) | >180h | Eficiencia |
| A-05 | Tasa de rechazo | `COUNT(*) FILTER (WHERE estado = 'rechazado') / COUNT(*) FILTER (WHERE estado IN ('resuelto','rechazado'))` | >30% | >20% | Calidad proceso |
| A-06 | Solicitudes en subsanación | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado = 'subsanacion'` | >0 | >0 | Workflow |
| A-07 | Solicitudes con prorroga | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado = 'prorroga'` | >0 | >0 | Art. 12 bis |
| A-08 | Solicitudes bloqueadas | `COUNT(*) FROM tkt_solicitud_derecho WHERE company_id = ? AND estado = 'bloqueado'` | >0 | — | Art. 8 ter |
| A-09 | Cumplimiento SLA | `COUNT(*) FILTER (WHERE estado = 'resuelto' AND respuesta_fecha <= fecha_vencimiento) / NULLIF(COUNT(*) FILTER (WHERE estado = 'resuelto'), 0)` | <80% | <90% | KPI calidad |
| A-10 | RATs bloqueados desde ARCO | `COUNT(*) FROM rats WHERE company_id = ? AND bloqueado = TRUE` | >0 | — | Art. 8 ter |

**Query agregada para dashboard ARCO:**
```sql
SELECT
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE estado IN ('abierto','en_proceso','pendiente')) as pendientes,
  COUNT(*) FILTER (WHERE estado NOT IN ('resuelto','rechazado') AND fecha_vencimiento < NOW()) as vencidas,
  COUNT(*) FILTER (WHERE estado NOT IN ('resuelto','rechazado') AND fecha_vencimiento BETWEEN NOW() AND NOW() + INTERVAL '48 hours') as por_vencer_48h,
  COUNT(*) FILTER (WHERE estado = 'subsanacion') as en_subsanacion,
  COUNT(*) FILTER (WHERE estado = 'prorroga') as con_prorroga,
  COUNT(*) FILTER (WHERE estado = 'bloqueado') as bloqueadas,
  COUNT(*) FILTER (WHERE estado = 'resuelto') as resueltas,
  COUNT(*) FILTER (WHERE estado = 'rechazado') as rechazadas,
  ROUND(
    COUNT(*) FILTER (WHERE estado = 'resuelto' AND respuesta_fecha <= fecha_vencimiento) * 100.0 /
    NULLIF(COUNT(*) FILTER (WHERE estado = 'resuelto'), 0)
  , 1) as cumplimiento_sla_pct
FROM tkt_solicitud_derecho
WHERE company_id = ?;
```

---

### MÓDULO: Brechas de Seguridad

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| B-01 | Brechas activas | `COUNT(*) FROM security_breaches WHERE company_id = ? AND estado_cierre != 'cerrada'` | >0 | — | Gestión |
| B-02 | Brechas no notificadas APDP | `COUNT(*) FROM security_breaches WHERE company_id = ? AND notificado_apdc = FALSE` | >0 | — | Art. 14 bis (72h) |
| B-03 | Brechas sin notificar titulares | `COUNT(*) FROM security_breaches WHERE company_id = ? AND notificado_apdc = TRUE AND notificado_titulares = FALSE` | >0 | — | Art. 14 bis |
| B-04 | Plazo APDP vencido | `COUNT(*) FROM security_breaches WHERE company_id = ? AND notificado_apdc = FALSE AND (NOW() - fecha_deteccion) > INTERVAL '72 hours'` | >0 | — | Urgencia 72h |
| B-05 | Brechas críticas | `COUNT(*) FROM security_breaches WHERE company_id = ? AND nivel_riesgo = 'CRITICO' AND estado_cierre != 'cerrada'` | >0 | — | Máximo riesgo |
| B-06 | Brechas con datos sensibles | `COUNT(*) FROM security_breaches WHERE company_id = ? AND incluye_datos_sensibles = TRUE AND estado_cierre != 'cerrada'` | >0 | >0 | Exposición |
| B-07 | Brechas con NNA | `COUNT(*) FROM security_breaches WHERE company_id = ? AND incluye_datos_nna = TRUE AND estado_cierre != 'cerrada'` | >0 | >0 | Protección especial |
| B-08 | Brechas último año | `COUNT(*) FROM security_breaches WHERE company_id = ? AND fecha_deteccion > NOW() - INTERVAL '1 year'` | >3 | >1 | Tendencia |
| B-09 | Tasa de breach por RAT | `COUNT(*) / NULLIF((SELECT COUNT(*) FROM rats WHERE company_id = ?), 0)` | >0.1 (>10%) | >0.05 | Eficiencia control |
| B-10 | Volumen promedio afectados | `AVG(volumen_titulares_afectados) FROM security_breaches WHERE company_id = ?` | >1000 | >100 | Impacto |

---

### MÓDULO: EIPD (Evaluaciones de Impacto)

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| E-01 | EIPDs en proceso | `COUNT(*) FROM eipds e JOIN rats r ON e.rat_id = r.id WHERE r.company_id = ? AND e.resultado = 'en_proceso'` | >0 | >0 | Plazo 90 días |
| E-02 | EIPDs vencidas (90d) | `COUNT(*) FROM eipds e JOIN rats r ON e.rat_id = r.id WHERE r.company_id = ? AND e.resultado = 'en_proceso' AND e.created_at < NOW() - INTERVAL '90 days'` | >0 | — | Mejor práctica |
| E-03 | RATs sin EIPD requerida | `COUNT(*) FROM rats WHERE company_id = ? AND (datos_sensibles = TRUE OR transferencia_internacional = TRUE) AND evaluacion_impacto = FALSE` | >0 | >0 | Art. 15 bis |
| E-04 | EIPDs completadas | `COUNT(*) FILTER (WHERE resultado = 'completada') / COUNT(*)` | <80% | <90% | Madurez |

---

### MÓDULO: Consentimientos

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| C-01 | Consentimientos activos | `COUNT(*) FROM consents WHERE company_id = ? AND activo = TRUE` | — | — | Exposición |
| C-02 | Consentimientos vencidos | `COUNT(*) FROM consents WHERE company_id = ? AND activo = TRUE AND fecha_vencimiento < NOW()` | >0 | >0 | Vigencia |
| C-03 | Consentimientos revocados | `COUNT(*) FILTER (WHERE activo = FALSE) / COUNT(*)` | >20% | >10% | Calidad |
| C-04 | RATs sin consentimiento (datos sensibles) | `COUNT(*) FROM rats WHERE company_id = ? AND datos_sensibles = TRUE AND id NOT IN (SELECT rat_id FROM consents WHERE activo = TRUE AND rat_id IS NOT NULL)` | >0 | >0 | Art. 12 |
| C-05 | Consentimientos por canal | `COUNT(*) FILTER (WHERE canal = 'web')`, etc. | — | Desequilibrio | Diversidad |

---

### MÓDULO: Encargados de Tratamiento

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| EN-01 | Contratos vigentes | `COUNT(*) FROM encargado_contrato WHERE company_id = ? AND activo = TRUE` | — | — | Cobertura |
| EN-02 | Contratos por vencer (60d) | `COUNT(*) FROM encargado_contrato WHERE company_id = ? AND activo = TRUE AND duracion_fin IS NOT NULL AND duracion_fin BETWEEN NOW() AND NOW() + INTERVAL '60 days'` | >0 | >2 | Art. 14 quater |
| EN-03 | Contratos vencidos | `COUNT(*) FROM encargado_contrato WHERE company_id = ? AND activo = TRUE AND duracion_fin < NOW()` | >0 | — | Compliance |
| EN-04 | Encargados sin contrato | `COUNT(*) FROM rats WHERE company_id = ? AND nombre_encargado IS NOT NULL AND tiene_contrato_encargado = FALSE` | >0 | — | Art. 14 quater |
| EN-05 | Transferencias int. sin encargado local | `COUNT(*) FROM rats WHERE company_id = ? AND transferencia_internacional = TRUE AND nombre_encargado IS NULL` | >0 | >0 | Riesgo |

---

### MÓDULO: Transparencia

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| T-01 | Política existe | `SELECT COUNT(*) FROM politicas_transparencia WHERE company_id = ?` | =0 | — | Art. 14 ter |
| T-02 | Política actualizada (1 año) | `SELECT COUNT(*) FROM politicas_transparencia WHERE company_id = ? AND fecha_generacion < NOW() - INTERVAL '1 year'` | >0 | — | Best practice |
| T-03 | RATs sin medida de seguridad (afecta política) | `COUNT(*) FROM rats WHERE company_id = ? AND (medidas_seguridad IS NULL OR medidas_seguridad = '')` | >3 | >0 | Completitud |
| T-04 | Items vacíos en política | `COUNT(*) FROM politicas_transparencia WHERE company_id = ? AND item_e_medidas IS NULL` | >0 | >0 | Compliance |

---

### MÓDULO: Company (Empresa)

| # | Indicador | Fórmula SQL | Umbral Rojo | Umbral Amarillo | Fuente |
|---|-----------|-------------|:---:|:---:|--------|
| CO-01 | Score compliance empresa | `(completitud_rats * 0.4) + (cumplimiento_sla * 0.3) + ((1 - rats_vencidos/total_rats) * 0.3) * 100` | <40 | <70 | Score agregado |
| CO-02 | DPO sin contacto | `COUNT(*) FROM companies WHERE id = ? AND (email_dpo IS NULL OR email_dpo = '')` | >0 | — | critical |
| CO-03 | Usuarios sin MFA | `COUNT(*) FROM users u JOIN user_companies uc ON u.id = uc.user_id WHERE uc.company_id = ? AND mfa_enabled = FALSE` / total | >30% | >10% | Security |
| CO-04 | Empresas sin RATs | `COUNT(*) FROM companies c LEFT JOIN rats r ON c.id = r.company_id WHERE c.id = ? GROUP BY c.id HAVING COUNT(r.id) = 0` | >0 | — | Onboarding |

---

## Score Aggregado de Compliance

Fórmula para score general de la empresa (0-100):

```sql
WITH
rat_score AS (
  SELECT
    company_id,
    COUNT(*) as total_rats,
    COUNT(*) FILTER (WHERE fecha_vencimiento < NOW()) as vencidos,
    ROUND(AVG(completitud_porcentaje), 1) as completitud_promedio
  FROM rats
  WHERE company_id = ?
  GROUP BY company_id
),
arco_score AS (
  SELECT
    company_id,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE estado NOT IN ('resuelto','rechazado') AND fecha_vencimiento < NOW()) as vencidas,
    ROUND(
      COUNT(*) FILTER (WHERE estado = 'resuelto' AND respuesta_fecha <= fecha_vencimiento) * 100.0 /
      NULLIF(COUNT(*) FILTER (WHERE estado = 'resuelto'), 0)
    , 1) as cumplimiento_sla
  FROM tkt_solicitud_derecho
  WHERE company_id = ?
  GROUP BY company_id
),
breach_score AS (
  SELECT
    company_id,
    COUNT(*) FILTER (WHERE notificado_apdc = FALSE AND estado_cierre != 'cerrada') as no_notificadas
  FROM security_breaches
  WHERE company_id = ?
  GROUP BY company_id
)

SELECT
  COALESCE(rat_score.total_rats, 0) as total_rats,
  COALESCE(rat_score.vencidos, 0) as rats_vencidos,
  COALESCE(rat_score.completitud_promedio, 0) as rat_completitud,
  COALESCE(arco_score.total, 0) as total_arco,
  COALESCE(arco_score.vencidas, 0) as arco_vencidas,
  COALESCE(arco_score.cumplimiento_sla, 0) as arco_sla,
  COALESCE(breach_score.no_notificadas, 0) as breaches_no_notif,

  -- Score components
  COALESCE(rat_score.completitud_promedio, 0) * 0.30 as rat_component,
  COALESCE(arco_score.cumplimiento_sla, 0) * 0.25 as arco_component,
  CASE WHEN COALESCE(rat_score.total_rats, 0) > 0
    THEN (1 - COALESCE(rat_score.vencidos, 0)::float / NULLIF(COALESCE(rat_score.total_rats, 0), 0)) * 100 * 0.20
    ELSE 100 * 0.20
  END as rat_venc_component,
  CASE WHEN COALESCE(arco_score.total, 0) > 0
    THEN (1 - COALESCE(arco_score.vencidas, 0)::float / NULLIF(COALESCE(arco_score.total, 0), 0)) * 100 * 0.15
    ELSE 100 * 0.15
  END as arco_venc_component,
  CASE WHEN COALESCE(breach_score.no_notificadas, 0) = 0
    THEN 100 * 0.10
    ELSE 0
  END as breach_component

FROM rat_score
FULL OUTER JOIN arco_score ON rat_score.company_id = arco_score.company_id
FULL OUTER JOIN breach_score ON rat_score.company_id = breach_score.company_id;
```

---

## Thresholds Configurables por Cliente

Cada cliente puede ajustar thresholds según su perfil de riesgo:

| Perfil | Descripción | Multiplicador thresholds |
|--------|-------------|------------------------|
| **Crítico** | Salud, banca, seguros | ×0.5 (más estricto) |
| **Alto** | Retail grande, telco | ×0.75 |
| **Standard** | Default | ×1.0 |
| **Bajo** | PYME, microempresas | ×1.5 (más permisivo) |

---

## Alerts Actionable

Cada indicador rojo debe generar una alerta accionable:

| Alerta | Indicador trigger | Acción recomendada |
|--------|-------------------|-------------------|
| RAT_VENCIó | R-02 > 0 | Contactar DPO, iniciar renovación |
| RAT_POR_VENCER | R-03 > 3 | Alertar DPO, planificar renovación |
| ARCO_VENCIÓ | A-02 > 0 | Escalar a DPO, riesgo legal APDP |
| ARCO_POR_VENCER | A-03 > 0 | Recordatorio urgente DPO |
| BREACH_SIN_NOTIFICAR | B-02 > 0 | Notificar DPO 72h imminent |
| BREACH_CRITICO | B-05 > 0 | Escalación inmediata DPO + legal |
| EIPD_PENDIENTE | E-02 > 0 | Completa EIPD o justifica |
| ENCARGADO_SIN_CONTRATO | EN-04 > 0 | Formalizar contrato urgentemente |
| POLITICA_VENCIDA | T-02 > 0 | Regenerar política transparencia |
