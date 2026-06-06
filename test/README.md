# Test Flujo Completo - Custodio RAT Manager

## Objetivo

Validar el flujo completo de funcionalidades de Custodio RAT Manager en un ambiente determinado (QA o Produccion).

## Flujo de 12 pasos

| Paso | Accion | Detalle |
|------|--------|---------|
| 0 | Login | Admin con JWT |
| 1 | Crear empresa | 1 empresa con prefijo unico |
| 2 | Crear usuario | 1 usuario admin_empresa |
| 3 | Crear 2 RATs | 2 registros RAT completos |
| 4 | Crear 2 brechas | 2 brechas de seguridad |
| 5 | Crear 3 ARCO | Solicitudes: acceso, rectificacion, cancelacion |
| 6 | Modificar empresa | Cambiar nombre a _MODIFICADA |
| 7 | Modificar 1 RAT | Actualizar nombre y categoria_datos |
| 8 | Modificar1 brecha | 2 cambios: notificar APDC + notificar titulares |
| 9 | Eliminar no modificados | 1 RAT + 1 brecha + 3 ARCO |
| 10 | Cleanup final | Eliminar RAT modificado + brecha modificada + usuario + empresa |
| 11 | Verificacion | Confirmar que la BD esta limpia |

## Estructura de archivos

```
test/
├── README.md                     # Este archivo
├── config.py                     # Configuracion por entorno
├── test_flujo_completo.py        # Script principal (12 pasos)
├── verificar_estado_final.py     # Verificacion post-test
├── cleanup_emergencia.py         # Cleanup por BD directa (fallback)
└── logs/                         # Logs de cada ejecucion
    └── test_TEST_FLUIDO_DEMO_*.log
```

## Entornos

| Entorno | Base URL | Rate Limit |
|---------|----------|------------|
| QA (default) | https://custodio-qa.vercel.app | 1.1s |
| Produccion | https://custodio-api-prod.vercel.app | 1.5s |

## Uso

### 1. Ejecutar en QA (default)

```bash
cd RAT_opencode
python test/test_flujo_completo.py
```

### 2. Ejecutar en Produccion

```bash
TEST_ENV=prod python test/test_flujo_completo.py
```

### 3. Verificar estado post-test

```bash
python test/verificar_estado_final.py TEST_FLUIDO_DEMO_20260608_143022
```

### 4. Cleanup de emergencia (si la API falla)

```bash
python test/cleanup_emergencia.py TEST_FLUIDO_DEMO_20260608_143022
```

## Archivos generados

- **Log de ejecucion:** `test/logs/test_TEST_FLUIDO_DEMO_<timestamp>.log`
- Cada ID creado/elimininado queda registrado en el log

## ARCO (Solicitudes de Derecho)

El endpoint `/solicitudes-derecho/` requiere un flujo de 2 pasos:

1. **GET** `/solicitudes-derecho/token` → Obtiene token UUID (5 min validez, rate limit 5/min)
2. **POST** `/solicitudes-derecho/` → Crea solicitud incluyendo el token en el body

**Rate limit:** El POST tiene limite de 3 solicitudes por hora por IP.

El test crea 3 ARCO (`acceso`, `rectificacion`, `cancelacion`) para evitar el rate limit.

## Precauciones

1. **Produccion es irreversible** - Los datos de prueba quedan visibles para usuarios reales
2. **Audit logs contaminados** - Quedan entradas de auditoria con datos de prueba
3. **Sequences consumen IDs** - Los IDs reales se incrementan aunque los datos se eliminen
4. **Cleanup puede fallar** - Usar `cleanup_emergencia.py` como fallback

## Para desarrollo

El test esta disenado para ejecutarse primero en QA, iterar hasta que pase100%, y solo entonces ejecutar en Produccion para la demo.

## Dependencias

```
requests
psycopg2
python-docx (solo si se regenera documentacion)
```
