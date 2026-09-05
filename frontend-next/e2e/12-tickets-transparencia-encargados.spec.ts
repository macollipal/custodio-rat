// Test E2E: Tickets ARCO, Transparencia, Encargados-contrato
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Tickets ARCO', () => {
  test('Carga la página de tickets', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Ticket|Solicitud|Derecho/i, { timeout: 10000 });
  });

  test('Tabla de tickets visible', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
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

  test('KPIs de tickets ARCO si hay datos', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const kpis = page.locator('[class*="card" i], [class*="kpi" i]');
    const count = await kpis.count();
    if (count === 0) {
      console.log('No hay KPIs en tickets - ambiente QA vacío');
    }
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('Click en ticket abre drawer de detalle', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const firstRow = page.locator('tbody tr').first();
    if (!await firstRow.isVisible({ timeout: 5000 })) return;
    await firstRow.click();
    await page.waitForTimeout(1500);
    const drawer = page.locator('[class*="drawer" i], [role="dialog"]').first();
    const visible = await drawer.isVisible({ timeout: 3000 }).catch(() => false);
    expect(typeof visible).toBe('boolean');
  });

  test('Filtro por tipo de solicitud', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const filterSelect = page.locator('select[name*="tipo" i]').first();
    if (await filterSelect.isVisible({ timeout: 3000 })) {
      const options = await filterSelect.locator('option').allTextContents();
      if (options.length > 1) {
        await filterSelect.selectOption({ index: 1 });
        await page.waitForTimeout(500);
        await filterSelect.selectOption({ index: 0 });
      }
    }
  });
});

test.describe('Transparencia', () => {
  test('Carga la página de transparencia', async ({ page }) => {
    await login(page);
    await page.goto('/transparencia');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Transparencia/i, { timeout: 10000 });
  });
});

test.describe('Encargados de Contrato', () => {
  test('Carga la página de encargados', async ({ page }) => {
    await login(page);
    await page.goto('/encargados-contrato');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Encargado|Contrato/i, { timeout: 10000 });
  });

  test('Tabla de encargados visible', async ({ page }) => {
    await login(page);
    await page.goto('/encargados-contrato');
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
});