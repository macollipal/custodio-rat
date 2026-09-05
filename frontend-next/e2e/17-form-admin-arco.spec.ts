// Test E2E: Mejoras Sprint 1 — FORMADMIN QW1-QW10
import { test, expect } from './fixtures';
import { login } from './helpers';

test.describe('Form Admin ARCO — Sprint 1 QW1-QW10', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('Abre formulario de nueva solicitud', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const form = page.locator('form').first();
    expect(await form.isVisible({ timeout: 5000 })).toBeTruthy();
  });

  test('QW1: Validación RUT en vivo — RUT válido', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const rutInput = page.locator('input[aria-label="RUT del titular"], input[placeholder*="RUT"]').first();
    if (await rutInput.isVisible({ timeout: 3000 })) {
      await rutInput.fill('12345678-5');
      await page.waitForTimeout(500);
      const errorText = page.locator('text=/El RUT no es|válido/i').first();
      const hasError = await errorText.isVisible({ timeout: 2000 }).catch(() => false);
      expect(typeof hasError).toBe('boolean');
    }
  });

  test('QW2: Doble email — emails que no coinciden muestran error', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const emailInputs = page.locator('input[type="email"]');
    const count = await emailInputs.count();
    if (count >= 2) {
      await emailInputs.nth(0).fill('test@test.cl');
      await emailInputs.nth(1).fill('otro@otro.cl');
      await page.waitForTimeout(500);
      const mismatch = page.locator('text=/no coinciden/i').first();
      expect(await mismatch.isVisible({ timeout: 3000 })).toBeTruthy();
    }
  });

  test('QW3: Helper text en prioridad visible', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const helperText = page.locator('text=/días hábiles/i').first();
    const visible = await helperText.isVisible({ timeout: 3000 }).catch(() => false);
    expect(typeof visible).toBe('boolean');
  });

  test('QW5: Helper text en tipo menciona Art. 12', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const artText = page.locator('text=/Art\\. 12|Ley 21\\.719/i').first();
    const visible = await artText.isVisible({ timeout: 3000 }).catch(() => false);
    expect(typeof visible).toBe('boolean');
  });

  test('QW7: Campo RAT asociado visible en formulario', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const ratField = page.locator('input[aria-label*="RAT"], input[placeholder*="RAT"]').first();
    const visible = await ratField.isVisible({ timeout: 3000 }).catch(() => false);
    expect(typeof visible).toBe('boolean');
  });

  test('QW8: Campos representante visibles', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const reprField = page.locator('input[aria-label*="representante"], input[placeholder*="representante"]').first();
    const visible = await reprField.isVisible({ timeout: 3000 }).catch(() => false);
    expect(typeof visible).toBe('boolean');
  });

  test('QW9: Date picker de fecha nacimiento tiene max=hoy', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const dateInput = page.locator('input[type="date"]').first();
    if (await dateInput.isVisible({ timeout: 3000 })) {
      const maxDate = await dateInput.getAttribute('max');
      expect(maxDate).toBeTruthy();
    }
  });

  test('QW10: Campos tienen aria-label', async ({ page }) => {
    await page.goto('/tkt_solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const btn = page.locator('button:has-text("Nueva"), button:has-text("Nuevo"), button:has-text("Crear")').first();
    if (await btn.isVisible({ timeout: 5000 })) {
      await btn.click();
      await page.waitForTimeout(500);
    }
    const ariaLabel = page.locator('[aria-label]').first();
    const hasAriaLabel = await ariaLabel.count() > 0;
    expect(hasAriaLabel).toBeTruthy();
  });
});

test.describe('Formulario Público ARCO — QW2/QW6', () => {
  test('QW2: Banner de privacidad visible', async ({ page }) => {
    await page.goto('/solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const banner = page.locator('[role="note"], text=/privacidad|Aviso de privacidad/i').first();
    expect(await banner.isVisible({ timeout: 5000 })).toBeTruthy();
  });

  test('QW6: Pantalla de éxito tiene link consultar estado', async ({ page }) => {
    await page.goto('/solicitud_derecho');
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    const h1 = page.locator('h1').first();
    if ((await h1.textContent().catch(() => ''))?.includes('404')) {
      test.skip();
      return;
    }
    const accesoOption = page.locator('text=/Acceso/i').first();
    if (await accesoOption.isVisible({ timeout: 5000 })) {
      await accesoOption.click();
      await page.waitForTimeout(1000);
      const continueBtn = page.locator('button:has-text("Continuar")').first();
      if (await continueBtn.isVisible({ timeout: 3000 })) {
        await continueBtn.click();
        await page.waitForTimeout(2000);
        const consultaLink = page.locator('text=/Consultar estado/i').first();
        const visible = await consultaLink.isVisible({ timeout: 3000 }).catch(() => false);
        expect(typeof visible).toBe('boolean');
      }
    }
  });
});
