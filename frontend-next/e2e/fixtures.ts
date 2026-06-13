// Fixtures compartidos para tests E2E
import { test as base, Page } from '@playwright/test';

export const TEST_USER = {
  username: process.env.E2E_USERNAME || 'admin',
  password: process.env.E2E_PASSWORD || 'Admin1234!',
};

export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[name="username"], input[placeholder*="usuario" i], input[type="text"]', TEST_USER.username);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(app)?\/?(dashboard|$)/, { timeout: 15000 });
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    // Cerrar modal "Sin empresa" si aparece bloqueando la UI
    const noCompanyModal = page.locator('text=/Sin empresas|Crea una primero|Sin empresa/i').first();
    if (await noCompanyModal.isVisible({ timeout: 3000 })) {
      // Press Escape to close modal backdrop
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }
    await use(page);
  },
});

export { expect } from '@playwright/test';
