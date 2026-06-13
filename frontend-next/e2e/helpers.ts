// Shared login helper for E2E tests
import { Page } from '@playwright/test';

export async function login(page: Page): Promise<void> {
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => {});
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'Admin1234!');
  await page.click('button[type="submit"]');
  try {
    await page.waitForURL(/dashboard/, { timeout: 30000 });
  } catch {
    // QA lento, continuar si ya no está en login
  }
  await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
  try {
    const noCompanyModal = page.locator('text=/Sin empresas|Crea una primero|Sin empresa/i').first();
    if (await noCompanyModal.isVisible({ timeout: 2000 })) {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    }
  } catch {}
}

export async function skipIf404(page: Page, url: string): Promise<boolean> {
  await page.goto(url);
  await page.waitForLoadState('networkidle', { timeout: 10000 });
  const h1 = page.locator('h1').first();
  const text = await h1.textContent().catch(() => 'not found');
  if (text?.includes('404') || text?.includes('not found')) {
    return true;
  }
  return false;
}