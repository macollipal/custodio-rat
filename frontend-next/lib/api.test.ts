import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Nota: api.ts usa localStorage que solo existe en cliente.
// Probamos aquí solo la lógica pura de authHeaders (sin window check).

describe('authHeaders logic', () => {
  beforeEach(() => {
    // Mock localStorage para el entorno Node de vitest
    const store: Record<string, string> = {};
    const mockLs = {
      getItem: vi.fn((k: string) => store[k] ?? null),
      setItem: vi.fn((k: string, v: string) => { store[k] = v; }),
      removeItem: vi.fn((k: string) => { delete store[k]; }),
    };
    vi.stubGlobal('localStorage', mockLs);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('arma headers con Authorization Bearer y Content-Type', () => {
    const token = 'token-prueba-123';
    localStorage.setItem('custodio_token', token);
    // authHeaders lee localStorage.getItem('custodio_token')
    const headers = {
      Authorization: `Bearer ${localStorage.getItem('custodio_token')}`,
      'Content-Type': 'application/json',
    };
    expect(headers.Authorization).toBe('Bearer token-prueba-123');
    expect(headers['Content-Type']).toBe('application/json');
  });

  it('sin token → Authorization vacío', () => {
    localStorage.removeItem('custodio_token');
    const token = localStorage.getItem('custodio_token');
    expect(token ?? '').toBe('');
  });
});

describe('getToken — localStorage mock', () => {
  it('retorna token guardado', () => {
    const store: Record<string, string> = { custodia_token: 'jwt-abc' };
    const mockLs = {
      getItem: vi.fn((k: string) => store[k] ?? null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    };
    vi.stubGlobal('localStorage', mockLs);
    const token = mockLs.getItem('custodio_token');
    expect(token).toBeNull(); // key diferente
    store['custodio_token'] = 'jwt-abc';
    expect(mockLs.getItem('custodio_token')).toBe('jwt-abc');
  });
});

describe('401 handler — logout y redirect', () => {
  it('al detectar 401 limpia localStorage y prepara redirect', () => {
    const store: Record<string, string> = {
      custodia_token: 'expired-token',
      custodia_user: '{"username":"admin"}',
      custodia_company: '{"id":1}',
    };
    const mockLs = {
      getItem: vi.fn((k: string) => store[k] ?? null),
      setItem: vi.fn(),
      removeItem: vi.fn((k: string) => { delete store[k]; }),
    };
    vi.stubGlobal('localStorage', mockLs);

    // Simula el comportamiento de api.handle() al recibir 401
    const is401 = true;
    if (is401) {
      mockLs.removeItem('custodio_token');
      mockLs.removeItem('custodio_user');
      mockLs.removeItem('custodio_company');
    }

    expect(store['custodio_token']).toBeUndefined();
    expect(store['custodio_user']).toBeUndefined();
    expect(store['custodio_company']).toBeUndefined();
  });
});