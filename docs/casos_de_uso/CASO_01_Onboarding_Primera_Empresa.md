# Caso de Uso 1: Onboarding — Primera Empresa

## Objetivo
Dejar configurada la empresa responsable del tratamiento para comenzar el cumplimiento de la Ley 21.719.

## Paso a paso

### Paso 1 — Login
- El usuario entra al sistema (`http://localhost:3000`)
- Ingresa usuario y contraseña
- **Resultado**: entra al sistema

### Paso 2 — Redirección a onboarding
- El sistema detecta que no hay empresas registradas
- Redirige automáticamente a `/onboarding`
- **Resultado**: el usuario ve la pantalla de configuración inicial

### Paso 3 — Crear empresa
- El usuario completa:
  - Razón social *(obligatorio)*
  - RUT con validación de dígito verificador *(obligatorio)*
  - Nombre del DPO *(opcional)*
  - Email del DPO *(obligatorio)*
- **Resultado**: empresa queda registrada en el sistema

### Paso 4 — Selección automática
- El sistema selecciona automáticamente la empresa recién creada como activa
- Redirige al dashboard
- **Resultado**: todos los RAT se asociarán a esa empresa

## Diagrama de flujo

```
┌─────────────┐
│  Login      │
│  /login     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ ¿Hay empresas?   │
└──────┬───────────┘
       │
   ┌───┴───┐
   │  SÍ   │          ┌───────────────┐
   └───┬───┘          │  Onboarding   │
       │              │  /onboarding  │
       ▼              └───────┬───────┘
┌─────────────┐              │
│  Dashboard  │◄─────────────┘
│  /dashboard │    (empresa creada)
└─────────────┘
```

## Endpoint involucrado

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/login` | Autenticación → obtiene JWT |
| GET | `/companies/` | Lista empresas del usuario |
| POST | `/companies/` | Crea nueva empresa |

## Campos del formulario onboarding

| Campo | Obligatorio | Validación |
|-------|:-----------:|------------|
| Razón social | ✅ | No vacío |
| RUT | ✅ | Algoritmo DV chileno |
| Nombre DPO | ❌ | — |
| Email DPO | ✅ | Formato email |

## Comportamiento post-creación

1. `setCompany(empresa)` → empresa queda como activa en el contexto
2. `setCompanies([empresa])` → se agrega a la lista
3. `router.push('/dashboard')` → redirige al dashboard
4. El sidebar mostrará la empresa en el selector

## Estados de error

| Escenario | Comportamiento |
|-----------|----------------|
| RUT inválido | Se muestra mensaje de error bajo el campo |
| Campos obligatorios vacíos | Toast de error por campo |
| Error de servidor | Toast con mensaje del servidor |
| Sesión expirada | Redirige a `/login` automáticamente |