import { describe, it, expect } from 'vitest';
import {
  getDiagramaPorTipo,
  getNodosAnteriores,
  getIdNodoPorEstado,
  aplicarColores,
  getTituloPorTipo,
  getDescripcionPorTipo,
  TipoArco
} from './flujos-arco';

describe('getDiagramaPorTipo', () => {
  it('retorna diagrama para acceso', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('EN_PROCESO');
    expect(diagrama).toContain('RESUELTO');
    expect(diagrama).toContain('RECHAZADO');
    expect(diagrama).toContain('flowchart TD');
  });

  it('retorna diagrama para cancelacion', () => {
    const diagrama = getDiagramaPorTipo('cancelacion');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('RECHAZADO');
    expect(diagrama).toContain('Art. 8 c.ii');
  });

  it('retorna diagrama para rectificacion', () => {
    const diagrama = getDiagramaPorTipo('rectificacion');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('RESUELTO');
  });

  it('retorna diagrama para oposicion', () => {
    const diagrama = getDiagramaPorTipo('oposicion');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('RECHAZADO');
    expect(diagrama).toContain('interés legítimo');
  });

  it('retorna diagrama para bloqueo', () => {
    const diagrama = getDiagramaPorTipo('bloqueo');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('BLOQUEADO');
    expect(diagrama).toContain('Art. 8 ter');
  });

  it('retorna diagrama para portabilidad', () => {
    const diagrama = getDiagramaPorTipo('portabilidad');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('RESUELTO');
    expect(diagrama).toContain('portability_data');
  });

  it('fallback a acceso si tipo invalido', () => {
    const diagrama = getDiagramaPorTipo('invalid' as TipoArco);
    expect(diagrama).toContain('ABIERTO');
  });
});

describe('getNodosAnteriores', () => {
  it('estado resuelto retorna estados anteriores', () => {
    const nodos = getNodosAnteriores('resuelto', 'acceso');
    expect(nodos).toContain('en_proceso');
    expect(nodos).toContain('abierto');
    expect(nodos).not.toContain('resuelto');
  });

  it('estado abierto retorna array vacio', () => {
    const nodos = getNodosAnteriores('abierto', 'acceso');
    expect(nodos).toEqual([]);
  });

  it('estado en_proceso retorna solo abierto', () => {
    const nodos = getNodosAnteriores('en_proceso', 'acceso');
    expect(nodos).toEqual(['abierto']);
  });

  it('estado rechazado retorna nodos completados', () => {
    const nodos = getNodosAnteriores('rechazado', 'acceso');
    expect(nodos.length).toBeGreaterThan(0);
    expect(nodos).not.toContain('rechazado');
  });

  it('estado desconocido retorna array vacio', () => {
    const nodos = getNodosAnteriores('invalid', 'acceso');
    expect(nodos).toEqual([]);
  });

  it('subsanacion retorna estados anteriores', () => {
    const nodos = getNodosAnteriores('subsanacion', 'acceso');
    expect(nodos).toContain('en_proceso');
    expect(nodos).toContain('abierto');
    expect(nodos).not.toContain('subsanacion');
  });

  it('bloqueo tiene secuencia correcta', () => {
    const nodos = getNodosAnteriores('bloqueado', 'bloqueo');
    expect(nodos).toContain('en_proceso');
    expect(nodos).toContain('abierto');
  });
});

describe('getIdNodoPorEstado', () => {
  it('abierto mapea a A', () => {
    expect(getIdNodoPorEstado('abierto')).toBe('A');
  });

  it('en_proceso mapea a B', () => {
    expect(getIdNodoPorEstado('en_proceso')).toBe('B');
  });

  it('subsanacion mapea a D', () => {
    expect(getIdNodoPorEstado('subsanacion')).toBe('D');
  });

  it('prorroga mapea a F', () => {
    expect(getIdNodoPorEstado('prorroga')).toBe('F');
  });

  it('resuelto mapea a H', () => {
    expect(getIdNodoPorEstado('resuelto')).toBe('H');
  });

  it('rechazado mapea a I', () => {
    expect(getIdNodoPorEstado('rechazado')).toBe('I');
  });

  it('bloqueado mapea a E', () => {
    expect(getIdNodoPorEstado('bloqueado')).toBe('E');
  });

  it('estado desconocido fallback a A', () => {
    expect(getIdNodoPorEstado('invalid')).toBe('A');
  });
});

describe('aplicarColores', () => {
  it('estado en_proceso aplica currentNode al nodo B', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'en_proceso', ['abierto']);
    expect(codigo).toContain('class B currentNode');
    expect(codigo).toContain('class A completedNode');
  });

  it('agrega classDef de estilos', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'resuelto', ['en_proceso', 'abierto']);
    expect(codigo).toContain('classDef currentNode');
    expect(codigo).toContain('classDef completedNode');
    expect(codigo).toContain('classDef pendingNode');
  });

  it('marca nodo Z como finalNode', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'resuelto', ['en_proceso', 'abierto']);
    expect(codigo).toContain('class Z finalNode');
  });

  it('retorna nodo actual correcto', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { nodoActual } = aplicarColores(diagrama, 'resuelto', ['en_proceso']);
    expect(nodoActual).toBe('H');
  });

  it('funciona con cancelacion', () => {
    const diagrama = getDiagramaPorTipo('cancelacion');
    const { codigo, nodoActual } = aplicarColores(diagrama, 'en_proceso', ['abierto']);
    expect(nodoActual).toBe('B');
    expect(codigo).toContain('classDef');
  });

  it('funciona con bloqueo', () => {
    const diagrama = getDiagramaPorTipo('bloqueo');
    const { codigo, nodoActual } = aplicarColores(diagrama, 'bloqueado', ['abierto', 'en_proceso']);
    expect(nodoActual).toBe('E');
    expect(codigo).toContain('class E currentNode');
    expect(codigo).toContain('class A completedNode');
    expect(codigo).toContain('class B completedNode');
  });
});

describe('getTituloPorTipo', () => {
  it('acceso retorna titulo legal', () => {
    expect(getTituloPorTipo('acceso')).toContain('ACCESO');
    expect(getTituloPorTipo('acceso')).toContain('Art. 8');
  });

  it('rectificacion retorna titulo legal', () => {
    expect(getTituloPorTipo('rectificacion')).toContain('RECTIFICACIÓN');
    expect(getTituloPorTipo('rectificacion')).toContain('Art. 9');
  });

  it('cancelacion retorna titulo legal', () => {
    expect(getTituloPorTipo('cancelacion')).toContain('CANCELACIÓN');
    expect(getTituloPorTipo('cancelacion')).toContain('Art. 8');
  });

  it('oposicion retorna titulo legal', () => {
    expect(getTituloPorTipo('oposicion')).toContain('OPOSICIÓN');
    expect(getTituloPorTipo('oposicion')).toContain('Art. 13');
  });

  it('bloqueo retorna titulo legal', () => {
    expect(getTituloPorTipo('bloqueo')).toContain('BLOQUEO');
    expect(getTituloPorTipo('bloqueo')).toContain('Art. 8 ter');
  });

  it('portabilidad retorna titulo legal', () => {
    expect(getTituloPorTipo('portabilidad')).toContain('PORTABILIDAD');
    expect(getTituloPorTipo('portabilidad')).toContain('Art. 12');
  });
});

describe('getDescripcionPorTipo', () => {
  it('acceso describe el derecho', () => {
    expect(getDescripcionPorTipo('acceso')).toContain('conocer');
    expect(getDescripcionPorTipo('acceso')).toContain('datos personales');
  });

  it('rectificacion describe el derecho', () => {
    expect(getDescripcionPorTipo('rectificacion')).toContain('corregir');
  });

  it('cancelacion menciona excepciones', () => {
    expect(getDescripcionPorTipo('cancelacion')).toContain('excepciones');
  });

  it('oposicion menciona interes legitimo', () => {
    expect(getDescripcionPorTipo('oposicion')).toContain('interés legítimo');
  });

  it('bloqueo menciona Art. 8 ter implicitamente', () => {
    expect(getDescripcionPorTipo('bloqueo')).toContain('bloquear');
  });

  it('portabilidad menciona formato estructurado', () => {
    expect(getDescripcionPorTipo('portabilidad')).toContain('formato estructurado');
  });
});
