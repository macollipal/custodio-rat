import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Test de regresión WCAG AA para contraste de texto secundario.
 *
 * El color #9CA3AF (Tailwind gray-400) sobre fondo blanco da ratio
 * de contraste ~2.9:1, que NO cumple WCAG AA (mínimo 4.5:1).
 *
 * El color accesible es #6B7280 (Tailwind gray-500) con ratio ~4.5:1.
 *
 * Este test verifica que los archivos de UI visibles al usuario
 * ya no usan #9CA3AF para texto secundario (hints, labels, fechas).
 * Se permiten usos decorativos (iconos SVG) que no transmiten info.
 */

const ROOT = join(__dirname, '..');
const readRel = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('Contraste WCAG AA — texto secundario', () => {
  it('dashboard/page.tsx no usa #9CA3AF para texto', () => {
    const src = readRel('app/(app)/dashboard/page.tsx');
    const matches = (src.match(/#9CA3AF/g) || []).length;
    expect(matches).toBe(0);
  });

  it('Topbar.tsx no usa #9CA3AF para texto visible (max 1 decorativo)', () => {
    const src = readRel('components/layout/Topbar.tsx');
    const matches = (src.match(/#9CA3AF/g) || []).length;
    expect(matches).toBeLessThanOrEqual(1);
  });

  it('login/page.tsx no usa text-gray-400 (Tailwind gray-400)', () => {
    const src = readRel('app/login/page.tsx');
    expect(src).not.toContain('text-gray-400');
  });

  it('RatTable.tsx no usa #9CA3AF para texto', () => {
    const src = readRel('components/rat/RatTable.tsx');
    const matches = (src.match(/#9CA3AF/g) || []).length;
    expect(matches).toBe(0);
  });

  it('RatEditForm.tsx no usa #9CA3AF para texto de hints/labels', () => {
    const src = readRel('components/rat/RatEditForm.tsx');
    const matches = (src.match(/#9CA3AF/g) || []).length;
    expect(matches).toBe(0);
  });
});

describe('Contraste WCAG AA — colores accesibles presentes', () => {
  it('dashboard/page.tsx usa #6B7280 (gray-500)', () => {
    const src = readRel('app/(app)/dashboard/page.tsx');
    expect(src).toContain('#6B7280');
  });

  it('login/page.tsx usa text-gray-500', () => {
    const src = readRel('app/login/page.tsx');
    expect(src).toContain('text-gray-500');
  });
});