export type TipoArco = 'acceso' | 'rectificacion' | 'cancelacion' | 'oposicion' | 'bloqueo' | 'portabilidad';

export type EstadoTicket = 'abierto' | 'en_proceso' | 'pendiente' | 'subsanacion' | 'prorroga' | 'bloqueado' | 'resuelto' | 'rechazado';

// Diagramas limpios: etiquetas cortas y consistentes, sin <br/>, flechas normalizadas
export const DIAGRAMAS: Record<TipoArco, string> = {
  acceso: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C{¿Subsanación?}
    C -- Sí --> D[SUBSANACIÓN]
    D -.-> B
    C -- No --> E{¿Prórroga?}
    E -- Sí --> F[PRÓRROGA]
    F -.-> B
    E -- No --> G{Decisión DPO}
    G -- Favorable --> H[RESUELTO]
    G -- Rechazado --> I[RECHAZADO]
    H --> Z([FIN])
    I --> Z`,

  rectificacion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Evaluar datos inexactos]
    C --> D{¿Datos incorrectos?}
    D -- Sí --> E[RESUELTO]
    D -- No --> F[RECHAZADO]
    E --> Z([FIN])
    F --> Z`,

  cancelacion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Excepciones Art. 8 c.ii]
    C --> D{¿Excepción aplica?}
    D -- Sí --> E[RECHAZADO]
    D -- No --> F{¿Terceros involucrados?}
    F -- Sí --> G[Notificar terceros]
    F -- No --> H[RESUELTO]
    G -.-> H
    H --> Z([FIN])
    E --> Z`,

  oposicion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Evaluar base legal]
    C --> D{¿Legítimo interés?}
    D -- No --> E[RECHAZADO]
    D -- Sí --> F{¿Prevalece interés?}
    F -- Sí --> G[RECHAZADO]
    F -- No --> H[RESUELTO]
    H --> Z([FIN])
    G --> Z
    E --> Z`,

  bloqueo: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C{¿Causal Art. 8 ter?}
    C -- No --> D[RECHAZADO]
    C -- Sí --> E[BLOQUEADO]
    E --> F{¿Desbloqueo?}
    F -- Sí --> G[Evaluar desbloqueo]
    G --> H{¿Procede?}
    H -- Sí --> I[RESUELTO]
    H -- No --> E
    I --> Z([FIN])
    D --> Z`,

  portabilidad: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> I{¿Prórroga?}
    I -- Sí --> J[PRÓRROGA]
    J -.-> B
    I -- No --> C[Identificar datos a exportar]
    C --> D{Formato solicitado}
    D -- JSON --> E[Generar JSON]
    D -- CSV --> F[Generar CSV]
    D -- Excel --> G[Generar XLSX]
    E --> H[RESUELTO]
    F --> H
    G --> H
    H --> Z([FIN])`,
};

const MAPEO_ESTADO_A_NODO_POR_TIPO: Record<TipoArco, Partial<Record<EstadoTicket, string>>> = {
  acceso: {
    abierto: 'A', en_proceso: 'B', pendiente: 'C',
    subsanacion: 'D', prorroga: 'F', resuelto: 'H', rechazado: 'I',
  },
  rectificacion: {
    abierto: 'A', en_proceso: 'C', pendiente: 'C',
    resuelto: 'E', rechazado: 'F',
  },
  cancelacion: {
    abierto: 'A', en_proceso: 'C', pendiente: 'C',
    subsanacion: 'D', resuelto: 'H', rechazado: 'E',
  },
  oposicion: {
    abierto: 'A', en_proceso: 'C', pendiente: 'C',
    subsanacion: 'D', resuelto: 'H', rechazado: 'G',
  },
  bloqueo: {
    abierto: 'A', en_proceso: 'C', pendiente: 'C',
    subsanacion: 'D', bloqueado: 'E', resuelto: 'I', rechazado: 'D',
  },
  portabilidad: {
    abierto: 'A', en_proceso: 'C', pendiente: 'C',
    subsanacion: 'D', prorroga: 'J', resuelto: 'H', rechazado: 'H',
  },
};

const SECUENCIA_ESTADOS: Record<TipoArco, string[]> = {
  acceso:       ['abierto', 'en_proceso', 'subsanacion', 'prorroga', 'resuelto', 'rechazado'],
  rectificacion:['abierto', 'en_proceso', 'resuelto', 'rechazado'],
  cancelacion:  ['abierto', 'en_proceso', 'subsanacion', 'resuelto', 'rechazado'],
  oposicion:    ['abierto', 'en_proceso', 'subsanacion', 'resuelto', 'rechazado'],
  bloqueo:      ['abierto', 'en_proceso', 'subsanacion', 'bloqueado', 'resuelto', 'rechazado'],
  portabilidad: ['abierto', 'en_proceso', 'subsanacion', 'prorroga', 'resuelto', 'rechazado'],
};

export function getDiagramaPorTipo(tipo: TipoArco): string {
  return DIAGRAMAS[tipo] || DIAGRAMAS.acceso;
}

export function getNodosAnteriores(estado: string, tipo: TipoArco): string[] {
  const sec = SECUENCIA_ESTADOS[tipo] || SECUENCIA_ESTADOS.acceso;
  const idx = sec.indexOf(estado);
  if (idx <= 0) return [];
  return sec.slice(0, idx);
}

export function getIdNodoPorEstado(tipo: TipoArco, estado: string): string {
  const mapeo = MAPEO_ESTADO_A_NODO_POR_TIPO[tipo];
  if (mapeo?.[estado as EstadoTicket]) return mapeo[estado as EstadoTicket]!;
  const sec = SECUENCIA_ESTADOS[tipo];
  const idx = sec.indexOf(estado);
  if (idx > 0) return mapeo?.[sec[idx - 1] as EstadoTicket] || 'A';
  return 'A';
}

function marcarNodoActual(diagrama: string, nodoActual: string): string {
  let r = diagrama.replace(new RegExp(`\\b(${nodoActual})\\[(?!★)`, 'g'), '$1[★ ');
  r = r.replace(new RegExp(`\\b(${nodoActual})\\(\\[(?!★)`, 'g'), '$1([★ ');
  r = r.replace(new RegExp(`\\b(${nodoActual})\\{(?!★)`, 'g'), `$1{★ `);
  return r;
}

// Design system: 5 colores semánticos + 3 de estado
const CLASSDEFS = [
  'classDef startNode    fill:#EFF6FF,color:#1D4ED8,stroke:#BFDBFE,stroke-width:1.5px',
  'classDef currentNode  fill:#4F46E5,color:#fff,stroke:#3730A3,stroke-width:2.5px,font-weight:bold',
  'classDef completedNode fill:#0F172A,color:#94A3B8,stroke:#1E293B,stroke-width:1px',
  'classDef pendingNode  fill:#F8FAFC,color:#94A3B8,stroke:#E2E8F0,stroke-width:1px,stroke-dasharray:5 3',
  'classDef decisionNode fill:#FFFBEB,color:#78350F,stroke:#D97706,stroke-width:1.5px',
  'classDef resolvedNode fill:#ECFDF5,color:#065F46,stroke:#059669,stroke-width:1.5px',
  'classDef rejectedNode fill:#FFF1F2,color:#881337,stroke:#E11D48,stroke-width:1.5px',
  'classDef finalNode    fill:#D1FAE5,color:#064E3B,stroke:#10B981,stroke-width:1.5px',
].join('\n    ');

export function aplicarColores(
  diagrama: string,
  tipo: TipoArco,
  estadoActual: string,
  nodosAnteriores: string[],
): { codigo: string; nodoActual: string } {
  const nodoActual = getIdNodoPorEstado(tipo, estadoActual);
  const conMarca = marcarNodoActual(diagrama, nodoActual);

  // Extraer todos los IDs de nodos del diagrama
  const ids = new Set<string>();
  for (const linea of conMarca.split('\n')) {
    const ms = linea.match(/\b([A-Z]+)(?=[^w]|$)/g);
    if (ms) ms.forEach(m => { if (m.length > 0) ids.add(m); });
  }

  // Mapa de clases con prioridad ascendente (última asignación gana)
  const cls = new Map<string, string>();
  for (const id of ids)           cls.set(id, 'pendingNode');     // 1. todo pendiente
  if (ids.has('A'))                cls.set('A', 'startNode');      // 2. inicio
  if (ids.has('Z'))                cls.set('Z', 'finalNode');      // 3. final

  // 4. Nodos de decisión (diamantes)
  const decPat = /\b([A-Z]+)\{/g; let dm: RegExpExecArray | null;
  while ((dm = decPat.exec(diagrama)) !== null)
    if (ids.has(dm[1])) cls.set(dm[1], 'decisionNode');

  // 5. Nodos RECHAZADO
  const rejPat = /\b([A-Z]+)\[RECHAZADO/g; let rm: RegExpExecArray | null;
  while ((rm = rejPat.exec(diagrama)) !== null)
    if (ids.has(rm[1])) cls.set(rm[1], 'rejectedNode');

  // 6. Nodos RESUELTO
  const resPat = /\b([A-Z]+)\[RESUELTO/g; let rsm: RegExpExecArray | null;
  while ((rsm = resPat.exec(diagrama)) !== null)
    if (ids.has(rsm[1]) && rsm[1] !== 'Z') cls.set(rsm[1], 'resolvedNode');

  // 7. Completados (mayor prioridad)
  for (const e of nodosAnteriores) {
    const id = getIdNodoPorEstado(tipo, e);
    if (ids.has(id)) cls.set(id, 'completedNode');
  }

  // 8. Nodo actual (máxima prioridad)
  if (ids.has(nodoActual)) cls.set(nodoActual, 'currentNode');

  let resultado = conMarca.replace(
    'flowchart TD',
    `flowchart TD\n    ${CLASSDEFS}`,
  );
  for (const [id, c] of cls.entries()) resultado += `\n    class ${id} ${c}`;
  resultado += '\n    linkStyle default stroke:#CBD5E1,stroke-width:1.5px,fill:none';

  return { codigo: resultado, nodoActual };
}

export function getTituloPorTipo(tipo: TipoArco): string {
  return {
    acceso:       'ACCESO — Art. 8 lit. (a)',
    rectificacion:'RECTIFICACIÓN — Art. 9',
    cancelacion:  'CANCELACIÓN — Art. 8 lit. (c)',
    oposicion:    'OPOSICIÓN — Art. 13',
    bloqueo:      'BLOQUEO — Art. 8 ter',
    portabilidad: 'PORTABILIDAD — Art. 12',
  }[tipo] ?? tipo.toUpperCase();
}

export function getDescripcionPorTipo(tipo: TipoArco): string {
  return {
    acceso:       'Derecho a conocer los datos personales almacenados',
    rectificacion:'Derecho a corregir datos inexactos o incompletos',
    cancelacion:  'Derecho a eliminar datos personales con excepciones legales',
    oposicion:    'Derecho a oponerse al tratamiento basado en interés legítimo',
    bloqueo:      'Derecho a bloquear el tratamiento de datos personales',
    portabilidad: 'Derecho a recibir datos en formato estructurado',
  }[tipo] ?? '';
}
