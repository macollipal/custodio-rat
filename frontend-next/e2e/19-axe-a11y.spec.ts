// E2E test: auditoria de accesibilidad WCAG 2.1 AA via axe-core
// Verifica que las paginas publicas no tengan violaciones criticas/serias
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const PUBLIC_PAGES = [
  { name: 'login', url: '/login' },
];

const TEST_USER = {
  username: process.env.E2E_USERNAME || 'admin',
  password: process.env.E2E_PASSWORD || 'Admin1234!',
};

async function tryLogin(page: import('@playwright/test').Page): Promise<boolean> {
  try {
    await page.goto('/login', { timeout: 5000 });
    await page.fill('input[type="text"]', TEST_USER.username);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(app)?\/?(dashboard|$)/, { timeout: 8000 });
    return true;
  } catch {
    return false;
  }
}

test.describe('Accesibilidad WCAG 2.1 AA (axe-core)', () => {
  test('Login page - sin violaciones criticas/serias', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    const critical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    if (critical.length > 0) {
      console.log('Violations criticas/serias en /login:');
      critical.forEach(v => console.log(`  - ${v.id} (${v.impact}): ${v.help}`));
    }
    expect(critical).toEqual([]);
  });

  test('Login page - axe completo (reporte)', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('domcontentloaded');
    const results = await new AxeBuilder({ page }).analyze();
    const serious = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
    const moderate = results.violations.filter(v => v.impact === 'moderate');
    const minor = results.violations.filter(v => v.impact === 'minor');
    console.log(`Login page axe: ${serious.length} criticas/serias, ${moderate.length} moderadas, ${minor.length} menores`);
    if (moderate.length > 0) {
      console.log('Moderate violations en /login:');
      moderate.forEach(v => {
        console.log(`  - ${v.id}: ${v.help} (${v.nodes.length} nodos)`);
        v.nodes.slice(0, 2).forEach(n => console.log(`      target: ${n.target.join(', ')}, html: ${n.html.slice(0, 100)}`));
      });
    }
    if (minor.length > 0) {
      console.log('Minor violations en /login:');
      minor.forEach(v => console.log(`  - ${v.id}: ${v.help} (${v.nodes.length} nodos)`));
    }
    expect(serious).toEqual([]);
  });

  test('Pages autenticadas - sin violaciones criticas/serias (si auth disponible)', async ({ page }) => {
    const loggedIn = await tryLogin(page);
    test.skip(!loggedIn, 'No hay credenciales validas para tests autenticados');

    const protectedPages = ['/dashboard', '/rat', '/breaches', '/reportes', '/companies', '/consentimientos'];
    for (const path of protectedPages) {
      await page.goto(path);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();
      const critical = results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
      if (critical.length > 0) {
        console.log(`Violations criticas/serias en ${path}:`);
        critical.forEach(v => console.log(`  - ${v.id} (${v.impact}): ${v.help}`));
      }
      expect.soft(critical, `${path} debe estar libre de violaciones criticas/serias`).toEqual([]);
    }
  });
});