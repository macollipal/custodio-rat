---
name: commit-helper
description: Guía para escribir mensajes de commit con formato conventional commits. Úsalo cuando el usuario vaya a commitear o pida ayuda con un mensaje.
---

# Asistente de commits conventional

Ayudá al usuario a escribir un mensaje de commit que siga el formato
conventional commits del proyecto (ver docs/desarrollo/COMMIT_POLICY.md).

## Cuándo invocarte

- Usuario dice "ayudame a commitear", "voy a commitear", "qué mensaje pongo"
- Usuario te pega un mensaje y pregunta "¿está bien?"
- Usuario pide revisar commits antes de hacer push

## Qué hacer paso a paso

1. Preguntale: ¿qué tipo de cambio es?
   - feat → funcionalidad nueva
   - fix → arreglo de bug
   - refactor → cambio interno sin cambio funcional
   - docs → solo documentación
   - chore → tareas menores (deps, configs, .gitignore)
   - test → solo tests
   - perf → mejora de performance

2. Preguntale: ¿en qué parte del código? (scope)
   Ejemplos del proyecto:
   - frontend, backend, auth, rats, companies, breaches
   - asesor, arco, tkt, ui, deploy, ci, docs, security

3. Escribí el mensaje en formato:
   `tipo(scope): descripción corta en imperativo`

   Reglas:
   - Descripción en IMPERATIVO ("agregar", NO "agregado" ni "agregando")
   - Sin punto final
   - Menos de 72 caracteres en la primera línea
   - En minúscula después del scope

4. Si el cambio es complejo, sugerí agregar un body:
   ```
   tipo(scope): título corto

   - Cambio 1 específico
   - Cambio 2 específico

   Por qué: explicación del motivo, no del qué.
   ```

5. Si el usuario te pega un mensaje existente, validá:
   - ¿Tiene tipo válido? (feat/fix/refactor/docs/chore/test/perf)
   - ¿Tiene scope entre paréntesis?
   - ¿Está en imperativo?
   - ¿Tiene menos de 72 caracteres?
   - ¿No tiene punto final?

   Si algo falla, marcale el problema y sugerí la corrección.

## Ejemplos de mensajes correctos del proyecto

Bien (estilo del repo):
- `feat(asesor): agregar timeout de 30s a MiniMax API`
- `fix(auth): aceptar ñ y @ en contraseñas`
- `refactor(rats): extraer useRatsData hook`
- `docs(ci): documentar workflow de GitHub Actions`
- `chore(deps): actualizar Next.js a 16.1`

Mal (antiestilo):
- `arregle bug` ❌ (no tiene tipo ni scope)
- `Added new feature` ❌ (en pasado, no imperativo)
- `feat(login): Agregué el botón de logout.` ❌ (mayúscula + punto final)

## Qué NO hacer

- No commitees vos. Solo ayudás con el mensaje.
- No asumas el tipo. Preguntá.
- No apruebes mensajes vagos como "cambios varios" o "fix cosas".
- Si el cambio toca más de un scope, sugerí dividir en 2 commits.
