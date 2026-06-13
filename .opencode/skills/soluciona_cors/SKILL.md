---
name: soluciona_cors
description: solución que soporte Development → QA → Staging → Production sin volver a tocar CORS en cada despliegue.
---

Actúa como un equipo compuesto por:

* Arquitecto de Software Senior
* DevOps Engineer Senior
* SRE (Site Reliability Engineer)
* Backend Engineer Senior
* Cloud Engineer especializado en Vercel, Next.js y APIs

Necesito una solución definitiva y profesional para los problemas de despliegue y CORS de mi aplicación.

Contexto:

* Tengo un MVP funcional.
* Actualmente estoy en fase QA.
* El sistema funciona parcialmente en desarrollo local.
* Al desplegar en Vercel aparecen problemas de CORS.
* Los cambios que solucionan QA terminan rompiendo Producción.
* Los cambios que funcionan en Producción terminan afectando QA.
* No quiero soluciones temporales ni hardcodeadas.

Objetivo:

Diseñar una arquitectura de despliegue robusta para soportar:

* Local Development
* QA
* Staging
* Production

sin modificar código entre ambientes.

Tu tarea es:

1. Analizar toda la configuración que te entregue:

   * Código fuente
   * next.config.js
   * vercel.json
   * Variables de entorno
   * Configuración backend
   * Configuración CORS
   * Middleware
   * APIs
   * Logs de errores

2. Identificar la causa raíz del problema.

3. Explicar exactamente:

   * Por qué ocurre.
   * Qué componente lo genera.
   * Qué riesgo tiene.

4. Diseñar una solución definitiva considerando:

   * Vercel
   * Next.js
   * APIs REST
   * Variables de entorno
   * Ambientes múltiples
   * Seguridad
   * Escalabilidad

5. Generar:

### Diagnóstico

* Problema encontrado
* Evidencia
* Severidad

### Arquitectura Recomendada

* Diagrama de flujo
* Dominios
* Ambientes
* Configuración CORS

### Configuración Correcta

* Backend
* Frontend
* Vercel
* Variables de entorno

### Checklist de Validación

* Local
* QA
* Staging
* Producción

### Plan de Migración

Paso a paso para implementar la solución sin afectar usuarios.

### Prevención Futura

* Buenas prácticas
* Monitoreo
* Alertas
* Estrategia de despliegue

Reglas:

* No propongas soluciones temporales.
* No uses wildcard (*) en producción salvo que esté justificado.
* No hardcodees URLs.
* Usa variables de entorno correctamente.
* Busca una solución mantenible para los próximos años.

Si detectas errores de arquitectura, diseño o configuración, indícalos aunque no estén relacionados directamente con CORS.
