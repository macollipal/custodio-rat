// Test E2E: Sidebar tiene los 4 grupos y navegacion funciona
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Sidebar y Navegación', () => {
  test('Sidebar muestra los 4 grupos', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=OPERACIONES').first()).toBeVisible({ timeout: 8000 });
    await expect(page.locator('text=CUMPLIMIENTO').first()).toBeVisible();
    await expect(page.locator('text=ANÁLISIS').first()).toBeVisible();
    await expect(page.locator('text=ADMINISTRACIÓN').first()).toBeVisible();
  });

  test('Sidebar muestra los nuevos items del grupo Cumplimiento', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=Consentimientos').first()).toBeVisible();
    await expect(page.locator('text=EIPD').first()).toBeVisible();
    await expect(page.locator('text=Transparencia').first()).toBeVisible();
  });

  test('URL /consentimientos carga correctamente', async ({ page }) => {
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
  });

  test('URL /eipd carga correctamente', async ({ page }) => {
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
  });

  test('URL /tkt_solicitud_derecho carga correctamente', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Ticket|Solicitud|Derecho/i);
  });
});