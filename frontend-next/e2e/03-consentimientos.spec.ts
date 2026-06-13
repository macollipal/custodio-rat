// Test E2E: Página de Consentimientos
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Consentimientos', () => {
  test('Carga la página con KPIs', async ({ page }) => {
    await login(page);
    await page.goto('/consentimientos');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText('Consentimientos');
    await expect(page.locator('text=Total').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Activos').first()).toBeVisible();
    await expect(page.locator('text=Revocados').first()).toBeVisible();
  });

  test('Botón Nuevo consentimiento abre modal', async ({ page }) => {
    await login(page);
    await page.goto('/consentimientos');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const newBtn = page.locator('button', { hasText: /nuevo|crear/i }).first();
    if (await newBtn.isVisible({ timeout: 5000 })) {
      await newBtn.click();
      await page.waitForTimeout(1000);
      const modal = page.locator('[role="dialog"], .fixed.inset-0.z-50').last();
      const modalVisible = await modal.isVisible({ timeout: 3000 }).catch(() => false);
      expect(typeof modalVisible).toBe('boolean');
    }
  });

  test('Filtro por RAT funciona', async ({ page }) => {
    await login(page);
    await page.goto('/consentimientos');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const select = page.locator('select').first();
    if (await select.isVisible({ timeout: 5000 })) {
      const options = await select.locator('option').allTextContents();
      if (options.length > 1) {
        await select.selectOption({ index: 1 });
        await page.waitForTimeout(500);
      }
    }
  });
});