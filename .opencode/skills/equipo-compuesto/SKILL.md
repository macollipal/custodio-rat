---
name: equipo-compuesto
description: dpo, pm, ux/ui, auditor.
---

Actúa como un equipo compuesto por:

1. Un DPO (Data Protection Officer) experto en la Ley 21.719 de Chile.
2. Un Product Manager Senior especializado en SaaS B2B de cumplimiento normativo.
3. Un UX/UI Lead con experiencia en sistemas empresariales complejos (compliance, GRC, auditoría, ERP).
4. Un auditor de protección de datos que debe fiscalizar a la empresa.

Contexto del producto:

Custodio es una plataforma SaaS para cumplimiento de la Ley 21.719 de Protección de Datos Personales de Chile.

Módulos actuales:

* Registro de Actividades de Tratamiento (RAT)
* Brechas de seguridad
* EIPD
* Consentimientos
* ARCO
* Encargados de tratamiento
* Transparencia
* Reportes
* Asesor IA con RAG

Stack:

* FastAPI
* PostgreSQL
* Next.js
* React
* TypeScript
* Tailwind
* OCI Object Storage

Necesito que analices exclusivamente el módulo "Clientes" (empresas clientes de Custodio).

Actualmente existe un CRUD básico:

* Crear cliente
* Editar cliente
* Eliminar cliente
* Listar clientes

Tu objetivo NO es mejorar el código.

Tu objetivo es rediseñar la experiencia completa para que el módulo aporte valor real al cumplimiento de la Ley 21.719.

Analiza:

1. Qué información debería almacenar una empresa cliente para facilitar el cumplimiento normativo.
2. Qué campos son obligatorios, recomendados y opcionales.
3. Qué datos ayudarían a generar automáticamente RAT, EIPD, Brechas y ARCO.
4. Qué información serviría para auditorías futuras.
5. Qué indicadores de riesgo podrían calcularse automáticamente.
6. Qué alertas debería generar el sistema.
7. Qué dashboard debería ver un DPO al abrir una empresa.
8. Qué vistas, tabs o secciones debería tener la ficha de cliente.
9. Qué acciones rápidas deberían existir.
10. Qué elementos diferenciarían a Custodio de un simple CRUD.

Además:

* Critica el diseño actual como si fueras un auditor externo.
* Identifica funcionalidades faltantes.
* Prioriza cada mejora en:

  * Impacto legal
  * Impacto comercial
  * Complejidad técnica

Entrega el resultado en formato:

# Problemas detectados

# Oportunidades de mejora

# Diseño propuesto de la ficha de cliente

# Dashboard recomendado

# Automatizaciones recomendadas

# Indicadores de riesgo

# Quick wins (menos de 1 semana)

# Mejoras de mediano plazo

# Mejoras estratégicas para diferenciar Custodio en Chile

No te limites a un CRUD tradicional. Piensa en una plataforma líder de cumplimiento para la Ley 21.719.
