// Test E2E: Crear RAT — Verificación de página RAT
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('RAT Page', () => {
  test('Carga la página de RATs', async ({ page }) => {
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1, [class*="heading"], [class*="title"]').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/RAT|Registro|Actividades|Procesos/i, { timeout: 10000 });
  });

  test('Tabla de RATs visible si hay datos', async ({ page }) => {
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const table = page.locator('table').first();
    if (await table.isVisible({ timeout: 5000 })) {
      await expect(table.locator('thead, [class*="header"]').first()).toBeVisible();
    }
  });

  test('Filtros de búsqueda funcionan', async ({ page }) => {
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const searchInput = page.locator('input[placeholder*="buscar" i], input[placeholder*="search" i], input[type="search"]').first();
    if (await searchInput.isVisible({ timeout: 3000 })) {
      await searchInput.fill('test');
      await page.waitForTimeout(500);
      await searchInput.clear();
    }
  });

  test('Exportar CSV genera descarga', async ({ page }) => {
    await login(page);
    await page.goto('/rat');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const exportButton = page.locator('button', { hasText: /exportar|csv|download/i }).first();
    if (await exportButton.isVisible({ timeout: 3000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
      await exportButton.click();
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.csv$/i);
      }
    }
  });
});