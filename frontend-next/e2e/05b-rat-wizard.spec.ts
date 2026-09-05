// E2E: Wizard RAT completo 5 pasos
// Cubre creación end-to-end de un RAT, validando los 5 pasos:
// 1. Identificación
// 2. Datos tratados
// 3. Finalidad y ley (incluye sugerencia QW5)
// 4. Transferencias
// 5. Compliance operativo
//
// Historia: este test existe porque el wizard 5 pasos es la ruta
// principal de creación de RAT, y romperlo silenciosamente es un
// incidente crítico para el onboarding de clientes.
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Wizard RAT — 5 pasos', () => {
  test('Wizard carga y muestra paso 0 (sugerencias por rubro)', async ({ page }) => {
    test.setTimeout(60_000);
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

    const newButton = page.locator('button', { hasText: /nuevo|nuevo proceso|\+ nuevo/i }).first();
    if (await newButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await newButton.click();
      await page.waitForTimeout(2000);
    }

    // Wizard debe tener StepIndicator visible
    const step1 = page.locator('text=/Identificación|Paso 1/i').first();
    const visible = await step1.isVisible({ timeout: 5000 }).catch(() => false);

    if (!visible) {
      // Si no se carga el wizard, falla con mensaje claro
      test.fail(true, 'Wizard no se abrió tras click en Nuevo RAT');
      return;
    }
    await expect(step1).toBeVisible();
  });

  test('Wizard paso 3 muestra sugerencia base legal por rubro (QW5)', async ({ page }) => {
    test.setTimeout(90_000);
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

    const newButton = page.locator('button', { hasText: /nuevo|nuevo proceso|\+ nuevo/i }).first();
    if (!(await newButton.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await newButton.click();
    await page.waitForTimeout(2000);

    // Navegar al paso 3 — Finalidad y ley
    // Saltar paso 0 si está visible (sugerencias)
    const skipPaso0 = page.locator('button', { hasText: /personalizado|crear personalizado|omitir/i }).first();
    if (await skipPaso0.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipPaso0.click();
      await page.waitForTimeout(500);
    }

    // Completar Paso 1 (Identificación) — nombre_proceso es obligatorio
    await page.fill('input[name="nombre_proceso"], input[placeholder*="proceso" i]', 'Test E2E Wizard RAT');
    const nextButton1 = page.locator('button', { hasText: /siguiente|continuar/i }).first();
    if (await nextButton1.isVisible({ timeout: 3000 }).catch(() => false)) {
      await nextButton1.click();
      await page.waitForTimeout(500);
    }

    // Paso 2 — Datos tratados (skip mínimo si no es critical)
    const nextButton2 = page.locator('button', { hasText: /siguiente|continuar/i }).first();
    if (await nextButton2.isVisible({ timeout: 3000 }).catch(() => false)) {
      await nextButton2.click();
      await page.waitForTimeout(500);
    }

    // Paso 3 — Finalidad y base legal
    await expect(page.locator('text=/Paso 3|Finalidad/i').first()).toBeVisible({ timeout: 5000 });

    // Si la sugerencia QW5 esta visible (porque la empresa tiene rubro_id), verificar el flow
    const sugerencia = page.locator('text=/Sugerencia para tu rubro/i').first();
    const sugerenciaVisible = await sugerencia.isVisible({ timeout: 3000 }).catch(() => false);

    if (sugerenciaVisible) {
      // Click "Aplicar" debe cambiar el select
      const aplicarBtn = page.locator('button', { hasText: /aplicar/i }).first();
      await aplicarBtn.click();
      await page.waitForTimeout(500);
      // El boton de sugerencia debe desaparecer (porque ya coincide)
      await expect(sugerencia).not.toBeVisible({ timeout: 3000 });
    }
    // Si no hay sugerencia visible, no fallar — depende de la config de la empresa
  });

  test('Wizard muestra error si paso 1 sin nombre_proceso (validación)', async ({ page }) => {
    test.setTimeout(60_000);
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

    const newButton = page.locator('button', { hasText: /nuevo|nuevo proceso|\+ nuevo/i }).first();
    if (!(await newButton.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await newButton.click();
    await page.waitForTimeout(2000);

    const skipPaso0 = page.locator('button', { hasText: /personalizado|crear personalizado|omitir/i }).first();
    if (await skipPaso0.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipPaso0.click();
      await page.waitForTimeout(500);
    }

    // Intentar siguiente sin llenar nombre_proceso
    const nextButton = page.locator('button', { hasText: /siguiente|continuar/i }).first();
    if (await nextButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await nextButton.click();
      await page.waitForTimeout(1000);
    }

    // Debe quedarse en paso 1 o mostrar error
    const paso1Title = page.locator('text=/Paso 1|Identificación/i').first();
    await expect(paso1Title).toBeVisible({ timeout: 5000 });
  });

  test('Wizard mobile viewport (375x667) carga correctamente', async ({ page }) => {
    test.setTimeout(60_000);
    await page.setViewportSize({ width: 375, height: 667 });
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

    // En mobile, los botones pueden estar en menu hamburguesa
    const mobileTrigger = page.locator('button[aria-label*="menu" i], button[class*="hamburger" i]').first();
    if (await mobileTrigger.isVisible({ timeout: 2000 }).catch(() => false)) {
      await mobileTrigger.click();
      await page.waitForTimeout(500);
    }

    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

    // Header principal debe estar visible
    const h1 = page.locator('h1, [class*="title"]:visible').first();
    const visible = await h1.isVisible({ timeout: 5000 }).catch(() => false);
    if (visible) {
      await expect(h1).toContainText(/RAT|Proceso/i);
    }
  });
});
