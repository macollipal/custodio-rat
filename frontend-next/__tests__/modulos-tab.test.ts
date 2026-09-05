import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

const ROOT = join(__dirname, '..');
const readFile = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('C2: ModulosTab existe y se integra', () => {
  it('ModulosTab.tsx existe', () => {
    const exists = (() => {
      try {
        readFile('components/configuracion/ModulosTab.tsx');
        return true;
      } catch {
        return false;
      }
    })();
    expect(exists).toBe(true);
  });

  it('exporta default ModulosTab', () => {
    const src = readFile('components/configuracion/ModulosTab.tsx');
    expect(src).toMatch(/export\s+default\s+function\s+ModulosTab/);
  });

  it('configuracion/page.tsx importa ModulosTab', () => {
    const src = readFile('app/(app)/configuracion/page.tsx');
    expect(src).toMatch(/import\s+ModulosTab\s+from\s+['"]@\/components\/configuracion\/ModulosTab['"]/);
  });

  it('configuracion/page.tsx tiene tab "modulos" en superadmin', () => {
    const src = readFile('app/(app)/configuracion/page.tsx');
    expect(src).toContain("key: 'modulos'");
    expect(src).toMatch(/label:\s*['"]M[óo]dulos['"]/);
  });

  it('configuracion/page.tsx renderiza ModulosTab solo si isSuperadmin', () => {
    const src = readFile('app/(app)/configuracion/page.tsx');
    expect(src).toMatch(/tab === ['"]modulos['"]\s*&&\s*isSuperadmin\s*&&/);
  });

  it('usa getCompanyModules para cargar estado inicial', () => {
    const src = readFile('components/configuracion/ModulosTab.tsx');
    expect(src).toMatch(/getCompanyModules\(/);
  });

  it('usa toggleCompanyModule para activar/desactivar', () => {
    const src = readFile('components/configuracion/ModulosTab.tsx');
    expect(src).toMatch(/toggleCompanyModule\(/);
  });

  it('incluye los 9 modulos en MODULE_INFO', () => {
    const src = readFile('components/configuracion/ModulosTab.tsx');
    const modulos = ['RAT', 'ARCO', 'BRECHAS', 'EIPD', 'CONSENTIMIENTOS', 'ENCARGADOS', 'TRANSPARENCIA', 'REPORTES', 'ASESOR'];
    for (const m of modulos) {
      expect(src).toContain(`${m}:`);
    }
  });

  it('toggle button usa role=switch + aria-checked (accesibilidad)', () => {
    const src = readFile('components/configuracion/ModulosTab.tsx');
    expect(src).toContain('role="switch"');
    expect(src).toContain('aria-checked');
  });
});

describe('C2: API functions en lib/api.ts', () => {
  const apiSrc = readFile('lib/api.ts');

  it('exporta getCompanyModules', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+getCompanyModules/);
  });

  it('exporta getActiveCompanyModules', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+getActiveCompanyModules/);
  });

  it('exporta toggleCompanyModule', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+toggleCompanyModule/);
  });

  it('exporta bulkUpdateCompanyModules', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+bulkUpdateCompanyModules/);
  });

  it('usa el endpoint /module-permissions/', () => {
    expect(apiSrc).toMatch(/\/module-permissions\/\$\{companyId\}/);
  });
});