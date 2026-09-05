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
import { getSubPaso } from './flujos-arco-detalle';

describe('getDiagramaPorTipo', () => {
  it('retorna diagrama para acceso', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    expect(diagrama).toContain('ABIERTO');
    expect(diagrama).toContain('EN PROCESO');
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
    expect(diagrama).toContain('Legítimo interés');
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
    expect(diagrama).toContain('Generar JSON');
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

  it('portabilidad en_proceso retorna abierto', () => {
    const nodos = getNodosAnteriores('en_proceso', 'portabilidad');
    expect(nodos).toEqual(['abierto']);
  });
});

describe('getIdNodoPorEstado', () => {
  it('abierto siempre es A', () => {
    expect(getIdNodoPorEstado('acceso', 'abierto')).toBe('A');
    expect(getIdNodoPorEstado('rectificacion', 'abierto')).toBe('A');
    expect(getIdNodoPorEstado('cancelacion', 'abierto')).toBe('A');
  });

  it('acceso en_proceso es B', () => {
    expect(getIdNodoPorEstado('acceso', 'en_proceso')).toBe('B');
  });

  it('rectificacion en_proceso es C (Evaluar datos)', () => {
    expect(getIdNodoPorEstado('rectificacion', 'en_proceso')).toBe('C');
  });

  it('oposicion en_proceso es C (Evaluar base legal)', () => {
    expect(getIdNodoPorEstado('oposicion', 'en_proceso')).toBe('C');
  });

  it('bloqueo en_proceso es C (¿Causal Art.8 ter?)', () => {
    expect(getIdNodoPorEstado('bloqueo', 'en_proceso')).toBe('C');
  });

  it('cancelacion en_proceso es C (Evaluar excepciones)', () => {
    expect(getIdNodoPorEstado('cancelacion', 'en_proceso')).toBe('C');
  });

  it('portabilidad en_proceso es C (Identificar datos)', () => {
    expect(getIdNodoPorEstado('portabilidad', 'en_proceso')).toBe('C');
  });

  it('acceso subsanacion es D', () => {
    expect(getIdNodoPorEstado('acceso', 'subsanacion')).toBe('D');
  });

  it('acceso prorroga es F', () => {
    expect(getIdNodoPorEstado('acceso', 'prorroga')).toBe('F');
  });

  it('acceso resuelto es H', () => {
    expect(getIdNodoPorEstado('acceso', 'resuelto')).toBe('H');
  });

  it('acceso rechazado es I', () => {
    expect(getIdNodoPorEstado('acceso', 'rechazado')).toBe('I');
  });

  it('bloqueo bloqueado es E', () => {
    expect(getIdNodoPorEstado('bloqueo', 'bloqueado')).toBe('E');
  });

  it('rectificacion resuelto es E (Rectificar BD)', () => {
    expect(getIdNodoPorEstado('rectificacion', 'resuelto')).toBe('E');
  });

  it('rectificacion rechazado es F (Fundamentado)', () => {
    expect(getIdNodoPorEstado('rectificacion', 'rechazado')).toBe('F');
  });

  it('estado desconocido fallback a A', () => {
    expect(getIdNodoPorEstado('acceso', 'invalid')).toBe('A');
  });
});

describe('aplicarColores', () => {
  it('estado en_proceso aplica currentNode al nodo B en acceso', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'acceso', 'en_proceso', ['abierto']);
    expect(codigo).toContain('class B currentNode');
    expect(codigo).toContain('class A completedNode');
  });

  it('estado en_proceso aplica currentNode al nodo C en oposicion', () => {
    const diagrama = getDiagramaPorTipo('oposicion');
    const { codigo } = aplicarColores(diagrama, 'oposicion', 'en_proceso', ['abierto']);
    expect(codigo).toContain('class C currentNode');
    expect(codigo).toContain('class A completedNode');
  });

  it('agrega classDef de estilos', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'acceso', 'resuelto', ['en_proceso', 'abierto']);
    expect(codigo).toContain('classDef currentNode');
    expect(codigo).toContain('classDef completedNode');
    expect(codigo).toContain('classDef pendingNode');
  });

  it('marca nodo Z como finalNode', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { codigo } = aplicarColores(diagrama, 'acceso', 'resuelto', ['en_proceso', 'abierto']);
    expect(codigo).toContain('class Z finalNode');
  });

  it('retorna nodo actual correcto para acceso resuelto', () => {
    const diagrama = getDiagramaPorTipo('acceso');
    const { nodoActual } = aplicarColores(diagrama, 'acceso', 'resuelto', ['en_proceso']);
    expect(nodoActual).toBe('H');
  });

  it('funciona con cancelacion', () => {
    const diagrama = getDiagramaPorTipo('cancelacion');
    const { codigo, nodoActual } = aplicarColores(diagrama, 'cancelacion', 'en_proceso', ['abierto']);
    expect(nodoActual).toBe('C');
    expect(codigo).toContain('classDef');
  });

  it('funciona con bloqueo', () => {
    const diagrama = getDiagramaPorTipo('bloqueo');
    const { codigo, nodoActual } = aplicarColores(diagrama, 'bloqueo', 'bloqueado', ['abierto', 'en_proceso']);
    expect(nodoActual).toBe('E');
    expect(codigo).toContain('class E currentNode');
    expect(codigo).toContain('class A completedNode');
  });

  it('rectificacion en_proceso pinta nodo C', () => {
    const diagrama = getDiagramaPorTipo('rectificacion');
    const { codigo, nodoActual } = aplicarColores(diagrama, 'rectificacion', 'en_proceso', ['abierto']);
    expect(nodoActual).toBe('C');
    expect(codigo).toContain('class C currentNode');
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

describe('getSubPaso', () => {
  it('oposicion en_proceso tiene titulo de evaluar base legal', () => {
    const sub = getSubPaso('oposicion', 'en_proceso');
    expect(sub).not.toBeNull();
    expect(sub!.titulo).toContain('Evaluar base legal');
  });

  it('rectificacion en_proceso tiene opciones', () => {
    const sub = getSubPaso('rectificacion', 'en_proceso');
    expect(sub).not.toBeNull();
    expect(sub!.opciones).toBeDefined();
    expect(sub!.opciones!.length).toBeGreaterThan(0);
  });

  it('acceso resuelto no tiene opciones', () => {
    const sub = getSubPaso('acceso', 'resuelto');
    expect(sub).not.toBeNull();
    expect(sub!.opciones).toBeUndefined();
  });

  it('bloqueo en_proceso menciona Art. 8 ter', () => {
    const sub = getSubPaso('bloqueo', 'en_proceso');
    expect(sub).not.toBeNull();
    expect(sub!.titulo).toContain('Art. 8 ter');
  });

  it('portabilidad en_proceso menciona exportar', () => {
    const sub = getSubPaso('portabilidad', 'en_proceso');
    expect(sub).not.toBeNull();
    expect(sub!.opciones).toContain('Generar JSON');
    expect(sub!.opciones).toContain('Generar CSV');
    expect(sub!.opciones).toContain('Generar Excel');
  });

  it('cancelacion en_proceso menciona excepciones', () => {
    const sub = getSubPaso('cancelacion', 'en_proceso');
    expect(sub).not.toBeNull();
    expect(sub!.accion).toContain('excepción');
  });

  it('todos los 6 tipos tienen subpaso para en_proceso', () => {
    const tipos: TipoArco[] = ['acceso', 'rectificacion', 'cancelacion', 'oposicion', 'bloqueo', 'portabilidad'];
    for (const tipo of tipos) {
      const sub = getSubPaso(tipo, 'en_proceso');
      expect(sub).not.toBeNull();
    }
  });

  it('estado inexistente retorna null', () => {
    const sub = getSubPaso('acceso', 'invalid' as any);  // eslint-disable-line @typescript-eslint/no-explicit-any
    expect(sub).toBeNull();
  });
});
