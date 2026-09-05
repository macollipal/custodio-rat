---
name: qa-rat
description: Suite de QA semanal para Custodio RAT Manager. Ejecuta un ciclo CRUD completo (crear → editar → exportar → eliminar) sobre RAT, Brechas y ARCOP+ en el ambiente QA, buscando bugs y regresiones activamente.
---

# QA Semanal — Custodio RAT Manager

## Contexto
- **Ambiente QA**: https://custodio-qa.vercel.app
- **Credenciales**: admin / admin1234
- **Empresa de prueba**: crear una empresa nueva `QA-Corp-<YYYY-MM-DD>` para aislar los datos de cada corrida
- **Objetivo**: ciclo CRUD completo en RAT, Brechas y ARCOP+. Documentar todos los bugs encontrados.

## Instrucciones de ejecución

Usa las herramientas de browser (Claude in Chrome) si están disponibles.
Si no, guía al usuario paso a paso con instrucciones exactas de qué hacer.

---

## FASE 1: Setup

1. Abrir https://custodio-qa.vercel.app y hacer login (admin / admin1234)
2. Crear empresa: `QA Corp <fecha-hoy>` — guarda el ID de la empresa
3. Activar módulos: BRECHAS, EIPD, ARCOP

---

## FASE 2: RAT — Ciclo CRUD

### Crear RATs de prueba (al menos 3 casos)

**Caso A — Riesgo Alto (datos sensibles + encargado sin contrato)**
- Nombre: `QA-RAT-A-DatosSensibles`
- Datos: salud, biometría
- Base legal: Consentimiento
- Encargado: SÍ, contrato: NO
- EIPD: requerida, estado: pendiente
- Decisiones automatizadas: SÍ
- Verificar: nivel_riesgo debería ser ALTO o CRÍTICO

**Caso B — Riesgo Bajo (datos básicos)**
- Nombre: `QA-RAT-B-DatosBásicos`
- Datos: nombre, RUT, email
- Base legal: Ejecución de contrato
- Sin encargado
- Verificar: nivel_riesgo BAJO

**Caso C — Interés Legítimo (test IL)**
- Nombre: `QA-RAT-C-InteresLegitimo`
- Base legal: Interés legítimo
- Verificar: que el test IL aparezca con badge "Obligatorio"
- Completar los 3 pasos del test

### Editar RAT
- Editar RAT-A: cambiar estado a "En revisión"
- Verificar que el drawer muestra los datos actualizados (BUG-03 fix)

### Exportar RAT
- Descargar PDF individual desde el drawer de RAT-A
- Ir a /reportes → exportar CSV masivo → verificar que RAT-A aparece

### Eliminar RAT
- Eliminar RAT-B con confirmación de nombre
- Verificar que el contador baja
- Verificar "Deshacer" si aplica

---

## FASE 3: Brechas — Ciclo CRUD

### Crear Brechas de prueba (al menos 2 casos)

**Caso A — Alto riesgo**
- Descripción: `QA Brecha prueba datos sensibles y NNA`
- Fecha: hoy
- Volumen: 5000 titulares
- Incluye datos sensibles: SÍ
- Incluye datos NNA: SÍ
- Verificar: nivel_riesgo debería ser CRÍTICO (score ≥6: +3+3+2=8 solo por flags)

**Caso B — Bajo riesgo**
- Descripción: `QA Brecha prueba sin flags`
- Volumen: 5 titulares
- Todos los flags: NO
- Verificar: nivel_riesgo BAJO

### Editar Brecha
- Editar Brecha-B: activar `incluye_datos_financieros`, volumen 1500
- Verificar: nivel_riesgo pasa a ALTO (score: +2+2=4)

### Eliminar Brechas
- Eliminar Brecha-A con confirmación
- Verificar que desaparece de la lista

---

## FASE 4: ARCOP+ — Ciclo CRUD

### Crear tickets ARCOP
- Crear ticket tipo ACCESO para el RAT-C
- Crear ticket tipo RECTIFICACIÓN
- Verificar SLA (30 días hábiles)

### Editar y cerrar ticket
- Cerrar un ticket como COMPLETADO
- Verificar estado final

### Verificar restricción
- Confirmar que NO existe botón "Eliminar" en tickets ARCOP (compliance Art. 12)

---

## FASE 5: Exportaciones masivas

1. Ir a /reportes
2. Exportar CSV → verificar que incluye los RATs creados
3. Exportar PDF reporte → verificar contenido
4. Exportar Reporte APDP → verificar formato
5. Verificar que los RATs eliminados NO aparecen en el export

---

## FASE 6: Verificaciones cross-cutting

- [ ] Navegar a /brechas → debe redirigir a /breaches (BUG-05)
- [ ] URL inválida /rat/999 → debe mostrar 404 o redirigir correctamente
- [ ] Cerrar sesión y reintentar → redirige a /login
- [ ] Como viewer (si existe): intentar crear RAT → debe dar 403

---

## FASE 7: Documentar hallazgos

Para cada bug encontrado, registrar:
- **ID**: BUG-<N>
- **Severidad**: CRÍTICO / ALTO / MEDIO / BAJO
- **Descripción**: qué pasó vs. qué se esperaba
- **Pasos para reproducir**
- **Archivo/línea probable**

Al final, generar un artifact HTML con el catastro de bugs usando el mismo formato del QA anterior.

---

## Checklist de regresión (bugs ya corregidos — verificar que siguen OK)

- [ ] BUG-01: nivel_riesgo brecha NO es siempre BAJO
- [ ] BUG-02: RAT con volumen alto refleja mayor riesgo
- [ ] BUG-03: Drawer RAT muestra datos actualizados tras editar
- [ ] BUG-04: Test IL tiene badge "Obligatorio" cuando colapsado
- [ ] BUG-05: /brechas redirige a /breaches (301)
- [ ] Audit global: superadmin NO ve error 403 en /auditoria
