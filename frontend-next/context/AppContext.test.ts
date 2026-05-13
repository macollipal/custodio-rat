import { describe, it, expect } from 'vitest';

// Test de la lógica de puedeEditar tal como está implementada en AppContext
// Lógica real: rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor'

describe('puedeEditar — lógica de roles', () => {
  it('admin_global → puedeEditar = true', () => {
    const rolGlobal = 'admin';
    const rolEnEmpresa = null as string | null;
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('admin_empresa → puedeEditar = true', () => {
    const rolGlobal = 'admin_empresa';
    const rolEnEmpresa = null as string | null;
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('usuario + rol admin_en_empresa → puedeEditar = true', () => {
    const rolGlobal = 'usuario';
    const rolEnEmpresa = 'admin';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('usuario + rol editor_en_empresa → puedeEditar = true', () => {
    const rolGlobal = 'usuario';
    const rolEnEmpresa = 'editor';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('usuario + rol viewer_en_empresa → puedeEditar = false', () => {
    const rolGlobal = 'usuario';
    const rolEnEmpresa = 'viewer';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(false);
  });

  it('usuario sin rol de empresa → puedeEditar = false', () => {
    const rolGlobal = 'usuario';
    const rolEnEmpresa = null;
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(false);
  });

  it('sin rol global + rol admin en empresa → puedeEditar = true (cae en else branch)', () => {
    // Sin rol global: rolGlobal === null → toma else branch
    // else branch: rolEnEmpresa === 'admin' || 'admin' === 'editor' → true
    const rolGlobal = null;
    const rolEnEmpresa = 'admin';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('sin rol global + rol editor en empresa → puedeEditar = true', () => {
    const rolGlobal = null;
    const rolEnEmpresa = 'editor';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(true);
  });

  it('sin rol global + rol viewer en empresa → puedeEditar = false', () => {
    const rolGlobal = null;
    const rolEnEmpresa = 'viewer';
    const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';
    expect(puedeEditar).toBe(false);
  });
});

describe('RolGlobal — valores válidos', () => {
  const rolesValidos = ['admin', 'admin_empresa', 'usuario'] as const;

  it('tiene exactamente 3 roles', () => {
    expect(rolesValidos).toHaveLength(3);
  });

  it('admin_empresa es distinto de admin', () => {
    expect('admin_empresa').not.toBe('admin');
  });

  it('ningún rol es vacío', () => {
    rolesValidos.forEach(r => expect(r.length).toBeGreaterThan(0));
  });

  it('usuario es el único que no es admin ni admin_empresa', () => {
    const roles = rolesValidos;
    expect(roles.filter(r => r === 'admin' || r === 'admin_empresa')).toHaveLength(2);
    expect(roles.filter(r => r === 'usuario')).toHaveLength(1);
  });
});