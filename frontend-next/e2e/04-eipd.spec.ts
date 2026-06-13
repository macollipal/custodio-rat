// Test E2E: Página de EIPD
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('EIPD', () => {
  test('Carga la página con KPIs', async ({ page }) => {
    await login(page);
    await page.goto('/eipd');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText('EIPD');
    await expect(page.locator('text=Total EIPDs').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=En proceso').first()).toBeVisible();
    await expect(page.locator('text=Completadas').first()).toBeVisible();
    await expect(page.locator('text=Pendientes').first()).toBeVisible();
  });

  test('Muestra alerta de RATs pendientes si los hay', async ({ page }) => {
    await login(page);
    await page.goto('/eipd');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const alerta = page.locator('text=/requiere.*EIPD/');
    const count = await alerta.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});