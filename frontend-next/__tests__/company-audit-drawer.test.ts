import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

const ROOT = join(__dirname, '..');
const readFile = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('QW1: CompanyAuditDrawer existe y se integra', () => {
  it('CompanyAuditDrawer.tsx existe', () => {
    const exists = (() => {
      try {
        readFile('components/companies/CompanyAuditDrawer.tsx');
        return true;
      } catch {
        return false;
      }
    })();
    expect(exists).toBe(true);
  });

  it('exporta default CompanyAuditDrawer', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toMatch(/export\s+default\s+function\s+CompanyAuditDrawer/);
  });

  it('index.ts exporta CompanyAuditDrawer', () => {
    const src = readFile('components/companies/index.ts');
    expect(src).toContain('CompanyAuditDrawer');
  });

  it('companies/page.tsx importa CompanyAuditDrawer', () => {
    const src = readFile('app/(app)/companies/page.tsx');
    expect(src).toMatch(/import[\s\S]*CompanyAuditDrawer[\s\S]*from\s+['"]@\/components\/companies['"]/);
  });

  it('companies/page.tsx tiene un state auditCompany', () => {
    const src = readFile('app/(app)/companies/page.tsx');
    expect(src).toMatch(/useState<Company\s*\|\s*null>/);
  });

  it('existe boton Auditoria con emoji y title explicativo', () => {
    const src = readFile('app/(app)/companies/page.tsx');
    expect(src).toContain('Auditoría');
    expect(src).toMatch(/title=.*auditoría/i);
  });

  it('usa api.getAuditoriaGlobal() para cargar el historial', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toMatch(/getAuditoriaGlobal\(\s*company\.id\s*\)/);
  });

  it('muestra empty state cuando no hay eventos', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toContain('Sin eventos de auditoría');
  });

  it('usa Skeleton para estado de carga', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toMatch(/<Skeleton[\s\S]*\/>/);
  });

  it('referencia al Art. 28 Ley 21.719 (cadena hash verificable)', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toContain('Art. 28');
    expect(src).toContain('hash chain');
  });

  it('filtra por accion usando botones toggle', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toContain('filterAccion');
    expect(src).toMatch(/setFilterAccion/);
  });

  it('mapea acciones a colores (crear=azul, eliminar=rojo, etc)', () => {
    const src = readFile('components/companies/CompanyAuditDrawer.tsx');
    expect(src).toContain('ACCION_COLORS');
    expect(src).toMatch(/crear:\s*\{/);
    expect(src).toMatch(/eliminar:\s*\{/);
  });
});

describe('QW1: API getAuditoriaGlobal existe', () => {
  const apiSrc = readFile('lib/api.ts');

  it('lib/api.ts tiene getAuditoriaGlobal', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+getAuditoriaGlobal/);
  });

  it('usa endpoint /rats/auditoria/', () => {
    expect(apiSrc).toMatch(/\/rats\/auditoria\/\$\{companyId\}/);
  });
});

describe('QW1: Backend endpoint existe', () => {
  it('rats.py tiene ruta /auditoria/{company_id}', () => {
    const src = readFile('../backend/app/routes/rats.py');
    expect(src).toMatch(/@router\.get\(['"]\/auditoria\/\{company_id\}['"]/);
  });
});