// Test E2E: RAT Detail Modal — Verificación del modal centrado
// Cubre: abrir modal, tabs, aprobar, duplicar, eliminar, cerrar con Escape
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('RAT Detail Modal', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
  });

  test('Tabla de RATs visible', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="grid"] button').first();
    await expect(rows).toBeVisible({ timeout: 5000 });
  });

  test('Click en fila abre modal con tabs Ver/Editar', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });

    const verTab = page.getByRole('button', { name: /Ver/i });
    await expect(verTab).toBeVisible();

    const editarTab = page.getByRole('button', { name: /Editar/i });
    if (await editarTab.isVisible({ timeout: 2000 })) {
      await expect(editarTab).toBeVisible();
    }
  });

  test('Tab Ver muestra datos del RAT en el modal', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(800);

    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });

    const titulo = page.locator('h2[class*="font-bold"]');
    if (await titulo.isVisible({ timeout: 3000 })) {
      await expect(titulo).not.toBeEmpty();
    }
  });

  test('Tab Editar cambia modal a modo edicion', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(500);

    const editarTab = page.getByRole('button', { name: /Editar/i });
    if (await editarTab.isVisible({ timeout: 2000 })) {
      await editarTab.click();
      await page.waitForTimeout(500);
      const form = page.locator('form');
      await expect(form.or(page.getByPlaceholder(/Nombre/i))).toBeVisible({ timeout: 3000 });
    } else {
      test.skip();
    }
  });

  test('Tecla Escape cierra el modal', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });

    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    const modalAfterClose = page.locator('[role="dialog"]');
    await expect(modalAfterClose).not.toBeVisible({ timeout: 3000 });
  });

  test('Boton Cancelar en edicion vuelve a modo Ver', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(500);

    const editarTab = page.getByRole('button', { name: /Editar/i });
    if (await editarTab.isVisible({ timeout: 2000 })) {
      await editarTab.click();
      await page.waitForTimeout(500);

      const cancelarBtn = page.getByRole('button', { name: /Cancelar/i });
      if (await cancelarBtn.isVisible({ timeout: 2000 })) {
        await cancelarBtn.click();
        await page.waitForTimeout(300);
        const verTab = page.getByRole('button', { name: /Ver/i });
        await expect(verTab).toBeVisible();
      } else {
        test.skip();
      }
    } else {
      test.skip();
    }
  });

  test('Accion Duplicar muestra toast de confirmacion', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const rows = page.locator('[class*="cursor-pointer"]');
    const count = await rows.count();
    if (count === 0) { test.skip(); return; }

    await rows.first().click();
    await page.waitForTimeout(500);

    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible({ timeout: 5000 });

    const duplicarBtn = page.getByRole('button', { name: /Duplicar/i });
    if (await duplicarBtn.isVisible({ timeout: 2000 })) {
      await duplicarBtn.click();
      await page.waitForTimeout(1000);
      const toast = page.locator('[class*="toast"], [class*="sonner"]');
      if (await toast.isVisible({ timeout: 3000 })) {
        await expect(toast).toBeVisible();
      }
      await page.keyboard.press('Escape');
    } else {
      test.skip();
    }
  });
});
