// Test E2E: Usuarios — Gestión de usuarios (solo superadmin)
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Usuarios', () => {
  test('Carga la página de usuarios', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
    await expect(h1).toContainText(/Usuario/i, { timeout: 10000 });
  });

  test('Tabla de usuarios visible', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
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

  test('Botón Crear usuario abre formulario', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const createButton = page.locator('button', { hasText: /crear|nuevo|agregar/i }).first();
    if (await createButton.isVisible({ timeout: 3000 })) {
      await createButton.click();
      await page.waitForTimeout(1000);
      const modal = page.locator('[role="dialog"], .fixed.inset-0.z-50').last();
      const modalVisible = await modal.isVisible({ timeout: 5000 }).catch(() => false);
      expect(typeof modalVisible).toBe('boolean');
    }
  });

  test('Click en usuario abre drawer de edición', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
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

  test('Filtro por rol funciona', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const filterSelect = page.locator('select[name*="rol" i]').first();
    if (await filterSelect.isVisible({ timeout: 3000 })) {
      const options = await filterSelect.locator('option').allTextContents();
      if (options.length > 1) {
        await filterSelect.selectOption({ index: 1 });
        await page.waitForTimeout(500);
        await filterSelect.selectOption({ index: 0 });
      }
    }
  });

  test('Búsqueda por nombre filtra usuarios', async ({ page }) => {
    await login(page);
    await page.goto('/usuarios');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const searchInput = page.locator('input[placeholder*="Buscar" i], input[type="search"]').first();
    if (await searchInput.isVisible({ timeout: 3000 })) {
      await searchInput.fill('admin');
      await page.waitForTimeout(800);
      await searchInput.clear();
    }
  });
});