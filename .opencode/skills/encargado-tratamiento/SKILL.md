---
name: encargado-tratamiento
description: Valida contratos de encargado del tratamiento (Art. 14 quater Ley 21.719). Obligaciones, vigencias, vinculacion RAT, archivo PDF y vencimientos.
---

# Encargado del Tratamiento Validator

Especialista en contratos de encargado del tratamiento bajo la Ley 21.719, Art. 14 quater.

## Contexto Legal

Art. 14 quater — Encargado del tratamiento:
Todo tercero que trata datos personales por cuenta del responsable debe tener un contrato formal que establezca:
- Objeto y duracion del tratamiento
- Finalidad del tratamiento
- Tipos de datos y categorias de titulares
- Derechos y obligaciones del encargado
- Obligacion de confidencialidad
- Medidas de seguridad exigidas
- Subencargados (si aplica)
- Clausula de restitucion al termino

## Modelo en Custodio RAT

### Campos obligatorios del contrato
- nombre_encargado, pais, direccion
- objeto, finalidad, tipo_datos, categorias_titulares
- derechos_obligaciones
- duracion_inicio, duracion_fin (fecha de termino)
- archivo_pdf_datos (contrato firmado en PDF)

### Vinculacion
- company_id: empresa responsable (cliente)
- rat_id: proceso de tratamiento al que关联a

### Estados
- activo = True: contrato vigente
- activo = False: contrato terminado/revocado

## Cuando Usar Esta Skill

- Se crea o renueva un contrato de encargado
- Se auditan los encargados de tratamiento de una empresa
- Se detecta RAT con nombre_encargado sin contrato asociado
- Se acerca fecha de vencimiento de un contrato

## Checklist de Compliance

### 1. Identificacion del Encargado
- [ ] nombre_encargado presente (razon social o nombre completo)
- [ ] pais presente
- [ ] direccion completa

### 2. Objeto del Contrato
- [ ] objeto definido (descripcion del tratamiento que realiza el encargado)
- [ ] finalidad del tratamiento especificada
- [ ] tipo_datos documentados (categorias de datos que procesa)
- [ ] categorias_titulares definidas (empleados, clientes, proveedores, etc.)

### 3. Clausulas Obligatorias (Art. 14 quater)
- [ ] derechos_obligaciones incluye: tratamiento solo segun instrucciones del responsable
- [ ] derechos_obligaciones incluye: obligacion de confidencialidad
- [ ] derechos_obligaciones incluye: medidas de seguridad equivalentes
- [ ] derechos_obligaciones incluye: restriccion de subencargados (o autorizacion previa)
- [ ] derechos_obligaciones incluye: devolucion/eliminacion al termino del contrato

### 4. Vigencia
- [ ] duracion_inicio existe y es valida
- [ ] duracion_fin existe (contratos indefinidos pueden no tener fin)
- [ ] Si duracion_fin existe y fecha_alerta_vencimiento debe estar seteada (T-30 dias antes)
- [ ] Si activo = True y duracion_fin < hoy -> WARNING: contrato vencido pero activo

### 5. Documentacion
- [ ] archivo_pdf_datos existe (PDF del contrato firmado)
- [ ] archivo_pdf_nombre tiene extension .pdf
- [ ] archivo_hash SHA-256 del PDF

### 6. Vinculacion RAT
- [ ] rat_id vinculado (proceso al que关联a este encargado)
- [ ] RAT.tiene_contrato_encargado = True (consistent with)
- [ ] Si RAT.tiene_contrato_encargado = True -> debe existir al menos 1 contrato activo

## Validacion de Consistencia RAT-Encargado

```
SI rat.nombre_encargado existe:
    SI encargado_para_rat_count == 0:
        -> WARNING: RAT menciona encargado pero no hay contrato asociado

SI rat.tiene_contrato_encargado == True:
    SI encargado_activo_para_rat_count == 0:
        -> FALLA: RAT indica que tiene contrato pero no existe ninguno activo

SI encargado.activo == False:
    -> Verificar que RAT.tiene_contrato_encargado se haya actualizado a False
```

## Reporte de Compliance

```
## Encargado del Tratamiento Compliance Report

**Contrato ID:** {id}
**Empresa (Responsable):** {company}
**Encargado:** {nombre_encargado}
**Pais:** {pais}
**Vinculado a RAT:** {rat_id}
**Estado:** {activo}

### Identificacion
:green_circle: Completa / :yellow_circle: Faltan datos

### Clausulas Minimas
| Clausula | Presente |
|---------|----------|
| Tratamiento segun instrucciones | :green_circle: / :red_circle: |
| Confidencialidad | :green_circle: / :red_circle: |
| Medidas de seguridad | :green_circle: / :red_circle: |
| Restriccion subencargados | :green_circle: / :yellow_circle: |
| Devolucion al termino | :green_circle: / :red_circle: |

### Vigencia
Inicio: {duracion_inicio}
Fin: {duracion_fin}
:green_circle: Vigente / :yellow_circle: Por vencer ({dias} dias) / :red_circle: Vencido

### Documentacion
PDF: {si/no} ({archivo_pdf_nombre})
Hash: {si/no}

### RAT Vinculado
{tipo_datos} - {finalidad}

### Acciones
1. [ ] Subir contrato PDF firmado
2. [ ] Renovar contrato antes de {fecha_vencimiento}
3. [ ] Vincular RAT al contrato
```

## Integracion con Otras Skills

- **rat-compliance**: RATs con encargado deben tener contrato vigente
- **qa-senior**: Revision general de compliance
- **tester-rat**: Casos de prueba para flujo de contratos
- **multi-tenant-security**: Verificar que datos de empresa no se compartan con encargados no autorizados
