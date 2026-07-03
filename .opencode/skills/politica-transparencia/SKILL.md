---
name: politica-transparencia
description: Valida la politica de transparencia (Art. 14 ter Ley 21.719). Endpoint publico /publico/transparencia/{company_id}, contenido minimo y actualizacion.
---

# Politica de Transparencia Validator

Especialista en politicas de transparencia y acceso a la informacion bajo la Ley 21.719, Art. 14 ter.

## Contexto Legal

Art. 14 ter — Transparencia:
Todo responsable debe informar de manera clara y accesible:
- Identidad y datos de contacto del responsable
- Finalidades del tratamiento
- Base legal
- Categorias de datos tratados
- Plazos de conservacion
- Derechos de los titulares (ARCO)
- Informacion sobre transferencias internacionales (si aplica)

El endpoint `GET /publico/transparencia/{company_id}` es PUBLICO (sin autenticacion).

## Modelo de Company relevante

Campos requeridos para politica de transparencia:
- nombre, rut, rubro, direccion
- contacto_dpo, email_dpo
- descripcion (opcional pero recomendado)
- canal_ejercicio_derechos

## Cuando Usar Esta Skill

- Se audita la pagina de transparencia de una empresa
- Se modifica el modulo de transparencia en frontend
- Se prepara documentacion para una auditoria APDP
- Se valida que el endpoint /publico/transparencia/{company_id} retorne contenido completo

## Checklist de Contenido Minimo

### 1. Identificacion del Responsable
- [ ] Nombre de la empresa (company.nombre)
- [ ] RUT de la empresa (company.rut)
- [ ] Rubro/actividad economica (company.rubro)
- [ ] Direccion (company.direccion)

### 2. Datos del DPO
- [ ] Nombre del DPO (company.contacto_dpo)
- [ ] Email del DPO (company.email_dpo)
- [ ] Indicacion de canal para ejercer derechos (company.canal_ejercicio_derechos)

### 3. Informacion del Tratamiento
- [ ] Lista de procesos RAT activos de la empresa
- [ ] Para cada RAT: nombre, finalidad, base legal, categorias de datos

### 4. Derechos de los Titulares (ARCO)
- [ ] Informacion sobre como acceder a los datos
- [ ] Como rectificar datos inexactos
- [ ] Como cancelar/oponer el tratamiento
- [ ] Como ejercer portabilidad
- [ ] Plazo de respuesta: 10 dias habiles

### 5. Transferencias Internacionales
- [ ] Si la empresa tiene transferencias internacionales -> detallar paises y garantias
- [ ] Si no tiene -> indicar que no hay transferencias internacionales

### 6. Canales de Ejercicio de Derechos
- [ ] company.canal_ejercicio_derechos definido
- [ ] Es accesible (email, formulario web, direccion fisica)

## Validacion de Contenido

```
Politica completa SI:
  1. Todos los campos de identificacion del responsable
  2. Al menos 1 RAT activo con informacion de tratamiento
  3. Seccion de derechos ARCO
  4. Informacion de contacto del DPO

Politica MINIMA (Art. 14 ter):
  - Responsable e identificacion
  - Finalidades
  - Base legal
  - Categorias de datos
  - Plazos de conservacion
  - Derechos ARCO
  - Canal de ejercicio de derechos
```

## Reporte de Compliance

```
## Politica de Transparencia Report

**Empresa:** {company}
**RUT:** {rut}
**RATs activos:** {n}

### Identificacion del Responsable
:green_circle: / :yellow_circle: / :red_circle: Completa

### Datos DPO
DPO: {contacto_dpo}
Email: {email_dpo}
Canal: {canal_ejercicio_derechos}

### RATs Declarados
| RAT | Finalidad | Base Legal | Estado |
|-----|-----------|------------|--------|
| {nombre} | {finalidad} | {base_legal} | {estado} |

### Derechos ARCO
:green_circle: Informados / :yellow_circle: Incompletos

### Transferencias Internacionales
{si/no} - {detalle si aplica}

### Score de Completitud
{n}% ({completados}/12 items minimos)

### Acciones
1. [ ] Completar informacion de empresa (rut, direccion, rubro)
2. [ ] Definir email_dpo
3. [ ] Declarar RATs activos
4. [ ] Verificar seccion de derechos ARCO
```

## Consideraciones de Seguridad

- El endpoint `/publico/transparencia/{company_id}` es PUBLICO (sin auth)
- NO debe exponer: emails_dpo en texto plano si hay riesgo de spam
- NO debe exponer: hashes internos, IDs internos, datos sensibles no relacionados
- El contenido debe estar en espanol claro (accesible para cualquier persona)

## Integracion con Otras Skills

- **rat-compliance**: RATs declarados deben cumplir Art. 16
- **arco-rights**: Derechos ARCO informados deben coincidir con el workflow real
- **multi-tenant-security**: Endpoint publico no expone datos de otras empresas
