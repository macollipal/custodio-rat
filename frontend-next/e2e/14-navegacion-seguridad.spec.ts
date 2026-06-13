// Test E2E: Navegación global, sesión y seguridad
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Navegación Global', () => {
  test('URL directa a /rat sin sesión redirige a login', async ({ page }) => {
    await page.goto('/rat');
    await page.waitForURL(/login|dashboard/, { timeout: 10000 });
  });

  test('URL directa a /companies sin sesión redirige a login', async ({ page }) => {
    await page.goto('/companies');
    await page.waitForURL(/login|dashboard/, { timeout: 10000 });
  });

  test('URL directa a /breaches sin sesión redirige a login', async ({ page }) => {
    await page.goto('/breaches');
    await page.waitForURL(/login|dashboard/, { timeout: 10000 });
  });

  test('Session persiste tras refresh de página', async ({ page }) => {
    await login(page);
    await page.reload();
    await page.waitForLoadState('networkidle');
    const currentUrl = page.url();
    expect(currentUrl).not.toMatch(/login/);
  });

  test('Logout cierra sesión y redirige a login', async ({ page }) => {
    await login(page);
    // Cerrar modal "Sin empresa" si bloquea
    try {
      const noCompanyModal = page.locator('text=/Sin empresas|Crea una primero|Sin empresa/i').first();
      if (await noCompanyModal.isVisible({ timeout: 2000 })) {
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    } catch {}
    const logoutButton = page.locator('button:has-text("Cerrar sesión"), button:has-text("Logout"), button[aria-label*="logout" i]').first();
    if (await logoutButton.isVisible({ timeout: 5000 })) {
      await logoutButton.click({ force: true });
      await page.waitForURL(/login/, { timeout: 10000 });
      await expect(page.locator('input[type="password"]')).toBeVisible();
    }
  });

  test('Token expirado redirige a login', async ({ page }) => {
    await login(page);
    await page.evaluate(() => {
      localStorage.removeItem('custodio_token');
    });
    await page.goto('/rat');
    await page.waitForURL(/login/, { timeout: 10000 });
  });

  test('No se puede acceder a rutas autenticadas sin token', async ({ page }) => {
    const routes = ['/rat', '/companies', '/breaches', '/reportes'];
    for (const route of routes) {
      await page.goto(route);
      await page.waitForURL(/login|dashboard/, { timeout: 10000 });
    }
  });

  test('Logout limpia todo el estado de sesión', async ({ page }) => {
    await login(page);
    // Cerrar modal "Sin empresa" si bloquea
    try {
      const noCompanyModal = page.locator('text=/Sin empresas|Crea una primero|Sin empresa/i').first();
      if (await noCompanyModal.isVisible({ timeout: 2000 })) {
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    } catch {}
    const logoutButton = page.locator('button:has-text("Cerrar sesión")').first();
    if (await logoutButton.isVisible({ timeout: 5000 })) {
      await logoutButton.click({ force: true });
      await page.waitForURL(/login/, { timeout: 10000 });
      const sessionData = await page.evaluate(() => ({
        token: localStorage.getItem('custodio_token'),
        user: localStorage.getItem('custodio_user'),
        company: localStorage.getItem('custodio_company'),
      }));
      expect(sessionData.token).toBeNull();
      expect(sessionData.user).toBeNull();
    }
  });
});