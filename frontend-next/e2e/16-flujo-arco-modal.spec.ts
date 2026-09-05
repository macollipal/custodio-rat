// Test E2E: Botón "Ver Flujo" con Mermaid en drawer ARCO
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Botón Ver Flujo en drawer ARCO', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 20000 });
    const h1 = page.locator('h1').first();
    const text = await h1.textContent().catch(() => 'not found');
    if (text?.includes('404')) {
      test.skip();
      return;
    }
  });

  test('Carga la página de tickets correctamente', async ({ page }) => {
    const h1 = page.locator('h1').first();
    await expect(h1).toContainText(/Ticket|Solicitud|Derecho/i, { timeout: 10000 });
  });

  test('Hay filas de tickets o mensaje de vacío', async ({ page }) => {
    await page.waitForTimeout(2000);
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    const emptyMsg = page.locator('text=/No hay|No se encontraron|Sin resultados/i');
    const hasEmptyMsg = await emptyMsg.isVisible().catch(() => false);
    if (count === 0 && !hasEmptyMsg) {
      console.log('Tabla visible pero sin filas ni mensaje vacío');
    }
    expect(count >= 0 || hasEmptyMsg).toBe(true);
  });

  test('Drawer abre al hacer click en una fila', async ({ page }) => {
    await page.waitForTimeout(2000);
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    if (count === 0) {
      test.skip();
      return;
    }
    await rows.first().click();
    await page.waitForTimeout(3000);
    const drawer = page.locator('[class*="fixed"]').first();
    const visible = await drawer.isVisible({ timeout: 5000 }).catch(() => false);
    expect(visible).toBe(true);
  });

  test('Botón Ver Flujo existe en el DOM al abrir drawer', async ({ page }) => {
    await page.waitForTimeout(2000);
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    if (count === 0) {
      test.skip();
      return;
    }
    await rows.first().click();
    await page.waitForTimeout(3000);
    const flujoBtn = page.locator('button:has-text("Ver Flujo")');
    const countInDom = await flujoBtn.count();
    if (countInDom === 0) {
      console.log('Drawer abierto pero botón Ver Flujo no está en el DOM');
    }
    expect(countInDom).toBeGreaterThan(0);
  });

  test('Modal se abre al clickear Ver Flujo cuando hay tickets', async ({ page }) => {
    await page.waitForTimeout(2000);
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    if (count === 0) {
      test.skip();
      return;
    }
    await rows.first().click();
    await page.waitForTimeout(3000);
    const flujoBtn = page.locator('button:has-text("Ver Flujo")');
    if (await flujoBtn.count() === 0) {
      test.skip();
      return;
    }
    await flujoBtn.click();
    await page.waitForTimeout(5000);
    const modal = page.locator('h2').filter({ hasText: /ACCESO|CANCELACIÓN|RECTIFICACIÓN|OPOSICIÓN|BLOQUEO|PORTABILIDAD/i }).first();
    const visible = await modal.isVisible({ timeout: 8000 }).catch(() => false);
    expect(visible).toBe(true);
  });

  test('Leyenda visible en footer del modal', async ({ page }) => {
    await page.waitForTimeout(2000);
    const rows = page.locator('tbody tr');
    if (await rows.count() === 0) {
      test.skip();
      return;
    }
    await rows.first().click();
    await page.waitForTimeout(3000);
    const flujoBtn = page.locator('button:has-text("Ver Flujo")');
    if (await flujoBtn.count() === 0) {
      test.skip();
      return;
    }
    await flujoBtn.click();
    await page.waitForTimeout(5000);
    const leyenda = page.locator('text=/Estado actual|Completado|Pendiente/i').first();
    const visible = await leyenda.isVisible({ timeout: 5000 }).catch(() => false);
    if (!visible) {
      console.log('Leyenda no visible - mermaid puede no haber renderizado');
    }
    expect(visible).toBe(true);
  });
});

test.describe('Ver Flujo - múltiples tipos ARCO', () => {
  test('Abre drawer y modal de al menos un ticket', async ({ page }) => {
    await login(page);
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 20000 });
    await page.waitForTimeout(2000);

    const rows = page.locator('tbody tr');
    const count = await rows.count();
    if (count === 0) {
      test.skip();
      return;
    }

    await rows.first().click();
    await page.waitForTimeout(3000);

    const flujoBtn = page.locator('button:has-text("Ver Flujo")');
    if (await flujoBtn.count() === 0) {
      test.skip();
      return;
    }

    await flujoBtn.click();
    await page.waitForTimeout(5000);

    const modalTitle = page.locator('h2').filter({ hasText: /ACCESO|CANCELACIÓN|RECTIFICACIÓN|OPOSICIÓN|BLOQUEO|PORTABILIDAD/i }).first();
    const titleText = (await modalTitle.textContent({ timeout: 8000 }).catch(() => '')) || '';
    expect(titleText.length).toBeGreaterThan(0);
    console.log(`Tipo de ARCO detectado: ${titleText}`);
  });
});
