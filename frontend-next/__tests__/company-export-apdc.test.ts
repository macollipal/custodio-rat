import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Test de regresion para QW2: boton Reporte APDC.
 *
 * Verifica que el boton esta presente en companies/page.tsx,
 * que usa el endpoint correcto (/rats/export/cni), y que
 * valida que la empresa tenga RATs antes de exportar.
 */

const ROOT = join(__dirname, '..');
const readFile = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('QW2: Boton Reporte APDC en companies/page.tsx', () => {
  const src = readFile('app/(app)/companies/page.tsx');

  it('existe el handler handleExportarApdc', () => {
    expect(src).toContain('async function handleExportarApdc');
  });

  it('el handler valida que la empresa tenga RATs antes de exportar', () => {
    expect(src).toMatch(/total_rats\s*\?\?\s*0\)\s*===\s*0/);
    expect(src).toContain('no tiene RATs para exportar');
  });

  it('el handler llama a api.exportarCni(emp.id)', () => {
    expect(src).toMatch(/api\.exportarCni\(\s*emp\.id\s*\)/);
  });

  it('el handler crea un <a> con download attribute', () => {
    expect(src).toMatch(/a\.download\s*=/);
  });

  it('el handler usa createObjectURL + revokeObjectURL para el Blob', () => {
    expect(src).toContain('createObjectURL');
    expect(src).toContain('revokeObjectURL');
  });

  it('el handler nombra el archivo con prefijo RAT_APDC_', () => {
    expect(src).toContain('RAT_APDC_');
  });

  it('el handler muestra toast de exito al completar', () => {
    expect(src).toMatch(/toast\.success\(`Reporte APDC/);
  });

  it('existe un boton visible con el label "Reporte APDC"', () => {
    expect(src).toContain('Reporte APDC');
  });

  it('el boton usa color violeta distintivo (#7C3AED)', () => {
    expect(src).toContain('#7C3AED');
  });

  it('el boton tiene title explicativo sobre el formato legal', () => {
    expect(src).toMatch(/title=.*APDC.*Ley 21\.719/);
  });
});

describe('QW2: API exportarCni existe y usa endpoint correcto', () => {
  const apiSrc = readFile('lib/api.ts');

  it('existe la funcion exportarCni en lib/api.ts', () => {
    expect(apiSrc).toMatch(/export\s+async\s+function\s+exportarCni/);
  });

  it('exportarCni usa el endpoint /rats/export/cni', () => {
    expect(apiSrc).toMatch(/\/rats\/export\/cni/);
  });

  it('exportarCni pasa company_id como query param', () => {
    expect(apiSrc).toMatch(/company_id=\$\{companyId\}/);
  });

  it('exportarCni retorna Blob', () => {
    expect(apiSrc).toMatch(/exportarCni\(companyId:\s*number\):\s*Promise<Blob>/);
  });
});