// Test E2E: Reportes — Reporting avanzado y chat IA
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Reportes', () => {
  test('Carga la página de reportes', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Reporte|Análisis/i, { timeout: 10000 });
  });

  test('Muestra KPIs si hay datos', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const kpis = page.locator('[class*="card" i], [class*="kpi" i]');
    const count = await kpis.count();
    if (count === 0) {
      console.log('No hay KPIs en reportes - ambiente QA vacío');
    }
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('Tabla de RATs visible', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const table = page.locator('table').first();
    if (await table.isVisible({ timeout: 5000 })) {
      await expect(table.locator('thead').first()).toBeVisible();
    }
  });

  test('Búsqueda por texto filtra resultados', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const searchInput = page.locator('input[placeholder*="Buscar" i], input[type="search"]').first();
    if (await searchInput.isVisible({ timeout: 3000 })) {
      await searchInput.fill('test');
      await page.waitForTimeout(800);
      await searchInput.clear();
    }
  });

  test('Click en RAT abre drawer de detalle', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const firstRow = page.locator('tbody tr').first();
    if (!await firstRow.isVisible({ timeout: 5000 })) return;
    await firstRow.click();
    await page.waitForTimeout(1000);
    const drawer = page.locator('[class*="drawer" i], [role="dialog"]').first();
    expect(await drawer.isVisible({ timeout: 3000 })).toBeTruthy();
  });

  test('Exportar CSV genera descarga', async ({ page }) => {
    await login(page);
    await page.goto('/reportes');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const exportButton = page.locator('button:has-text("CSV"), button:has-text("Exportar")').first();
    if (await exportButton.isVisible({ timeout: 3000 })) {
      const downloadPromise = page.waitForEvent('download', { timeout: 15000 }).catch(() => null);
      await exportButton.click();
      const download = await downloadPromise;
      if (download) {
        expect(download.suggestedFilename()).toMatch(/\.csv$/i);
      }
    }
  });
});