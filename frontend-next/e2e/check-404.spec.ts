// Quick check: are the pages loading now?
import { test } from '@playwright/test';

test('Check if consentimientos loads', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'Admin1234!');
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard/, { timeout: 20000 });
  await page.waitForLoadState('networkidle', { timeout: 10000 });

  await page.goto('/consentimientos');
  await page.waitForLoadState('networkidle', { timeout: 10000 });
  const h1 = await page.locator('h1').first().textContent();
  console.log('consentimientos h1:', h1);
});

test('Check if eipd loads', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'Admin1234!');
  await page.click('button[type="submit"]');
  await page.waitForURL(/dashboard/, { timeout: 20000 });
  await page.waitForLoadState('networkidle', { timeout: 10000 });

  await page.goto('/eipd');
  await page.waitForLoadState('networkidle', { timeout: 10000 });
  const h1 = await page.locator('h1').first().textContent();
  console.log('eipd h1:', h1);
});