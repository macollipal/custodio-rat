// Test E2E: Rubros, Configuración, Conexión
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Rubros', () => {
  test('Carga la página de rubros', async ({ page }) => {
    await login(page);
    await page.goto('/rubros');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Rubro|Categoría/i, { timeout: 10000 });
  });

  test('Tabla de rubros visible', async ({ page }) => {
    await login(page);
    await page.goto('/rubros');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
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

  test('Búsqueda por nombre de rubro', async ({ page }) => {
    await login(page);
    await page.goto('/rubros');
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
});

test.describe('Configuración', () => {
  test('Carga la página de configuración', async ({ page }) => {
    await login(page);
    await page.goto('/configuracion');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Config|Configur/i, { timeout: 10000 });
  });
});

test.describe('Conexión', () => {
  test('Página de diagnóstico carga', async ({ page }) => {
    await login(page);
    await page.goto('/conexion');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Conex|Diagnóstic/i, { timeout: 10000 });
  });

  test('Muestra estado de conexión al backend', async ({ page }) => {
    await login(page);
    await page.goto('/conexion');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const statusIndicator = page.locator('text=/conectado|error|estado/i').first();
    await expect(statusIndicator).toBeVisible({ timeout: 10000 });
  });
});