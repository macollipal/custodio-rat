import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

const ROOT = join(__dirname, '..');
const readFile = (rel: string): string =>
  readFileSync(join(ROOT, rel), 'utf-8');

describe('Z-01: next.config.ts con headers de seguridad', () => {
  const src = readFile('next.config.ts');

  it('configura Content-Security-Policy', () => {
    expect(src).toContain('Content-Security-Policy');
  });

  it('CSP usa default-src self', () => {
    expect(src).toMatch(/default-src\s+['"]self['"]/);
  });

  it('CSP deshabilita frame-ancestors', () => {
    expect(src).toContain("frame-ancestors 'none'");
  });

  it('configura X-Content-Type-Options: nosniff', () => {
    expect(src).toContain('X-Content-Type-Options');
    expect(src).toContain('nosniff');
  });

  it('configura X-Frame-Options: DENY', () => {
    expect(src).toContain('X-Frame-Options');
    expect(src).toContain('DENY');
  });

  it('configura Referrer-Policy', () => {
    expect(src).toContain('Referrer-Policy');
    expect(src).toContain('strict-origin-when-cross-origin');
  });

  it('configura Permissions-Policy', () => {
    expect(src).toContain('Permissions-Policy');
  });

  it('configura HSTS (Strict-Transport-Security)', () => {
    expect(src).toContain('Strict-Transport-Security');
    expect(src).toContain('max-age=31536000');
  });

  it('CSP incluye connect-src a los backends QA y prod', () => {
    expect(src).toContain('custodio-qa.vercel.app');
    expect(src).toContain('custodio-api-prod.vercel.app');
  });

  it('headers se aplican a todas las rutas (source: /:path*)', () => {
    expect(src).toMatch(/source:\s*['"]\/:path\*['"]/);
  });
});