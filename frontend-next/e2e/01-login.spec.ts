// Test E2E: Login y Dashboard
import { test, expect } from './fixtures';

test.describe('Authentication', () => {
  test('Login page carga correctamente', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveTitle(/Custodio/);
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('Login con credenciales inválidas muestra error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'usuario_inexistente');
    await page.fill('input[type="password"]', 'wrong_password');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=/credenciales|inv[áa]lidas|incorrectas/i').first()).toBeVisible({ timeout: 5000 });
  });

  test('Login exitoso redirige al dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="text"]', process.env.E2E_USERNAME || 'admin');
    await page.fill('input[type="password"]', process.env.E2E_PASSWORD || 'Admin1234!');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/, { timeout: 15000 });
    await expect(page.locator('text=/Dashboard/i').first()).toBeVisible();
  });
});
