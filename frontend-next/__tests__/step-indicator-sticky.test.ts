import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Test de regresion para sticky StepIndicator en mobile.
 *
 * En mobile el StepIndicator debe permanecer visible al hacer scroll
 * (sticky top-0 con backdrop-blur) para que el usuario no pierda
 * contexto de en que paso esta.
 *
 * En desktop (sm:) el indicador es estatico (sm:static).
 */

const ROOT = join(__dirname, '..');
const readFile = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('StepIndicator sticky mobile', () => {
  it('StepIndicator.tsx tiene clase sticky en el contenedor raiz', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/sticky\s+top-0/);
  });

  it('StepIndicator.tsx usa sm:static para que en desktop no sea sticky', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toContain('sm:static');
  });

  it('StepIndicator.tsx usa backdrop-blur en mobile para legibilidad sobre contenido', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/backdrop-blur/);
  });

  it('StepIndicator.tsx tiene z-index alto para superponerse al contenido', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/z-2[0-9]/);
  });

  it('StepIndicator.tsx usa bg-white con opacidad (no solido) para efecto glass', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/bg-white\/95/);
  });
});

describe('StepIndicator - exportacion por default', () => {
  it('StepIndicator.tsx exporta default function', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/export\s+default\s+function\s+StepIndicator/);
  });

  it('StepIndicator.tsx acepta props steps y current', () => {
    const src = readFile('components/ui/StepIndicator.tsx');
    expect(src).toMatch(/steps:\s*string\[\]/);
    expect(src).toMatch(/current:\s*number/);
  });
});