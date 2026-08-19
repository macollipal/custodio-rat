export type TipoArco = 'acceso' | 'rectificacion' | 'cancelacion' | 'oposicion' | 'bloqueo' | 'portabilidad';

export type EstadoTicket = 'abierto' | 'en_proceso' | 'pendiente' | 'subsanacion' | 'prorroga' | 'bloqueado' | 'resuelto' | 'rechazado';

export const DIAGRAMAS: Record<TipoArco, string> = {
  acceso: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C{¿Subsanación?}
    C -->|Sí| D[SUBSANACIÓN]
    D -.->|Complementa| B
    C -->|No| E{¿Prórroga?}
    E -->|Sí| F[PRÓRROGA]
    F -.->|Vence| B
    E -->|No| G{Decisión DPO}
    G -->|Favorable| H[RESUELTO]
    G -->|Rechazado| I[RECHAZADO]
    H --> Z([FIN])
    I --> Z`,

  rectificacion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Evaluar datos inexactos]
    C --> D{¿Datos incorrectos?}
    D -->|Sí| E[RESUELTO<br/>Rectificar BD]
    D -->|No| F[RECHAZADO<br/>Fundamentado]
    E --> Z([FIN])
    F --> Z`,

  cancelacion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Evaluar excepciones<br/>Art. 8 c.ii]
    C --> D{¿Excepción aplica?}
    D -->|Sí| E[RECHAZADO<br/>Legal]
    D -->|No| F{¿Terceros involucrados?}
    F -->|Sí| G[Notificar terceros]
    F -->|No| H[RESUELTO<br/>Eliminar BD]
    G -.-> H
    H --> Z([FIN])
    E --> Z`,

  oposicion: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Evaluar base legal]
    C --> D{¿Legítimo interés<br/>o marketing?}
    D -->|No| E[RECHAZADO<br/>No aplica]
    D -->|Sí| F{¿Prevalece el interés?}
    F -->|Sí| G[RECHAZADO<br/>Prevalece interés]
    F -->|No| H[RESUELTO<br/>Cese tratamiento]
    H --> Z([FIN])
    G --> Z
    E --> Z`,

  bloqueo: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C{¿Causal Art. 8 ter<br/>acreditada?}
    C -->|No| D[RECHAZADO]
    C -->|Sí| E[BLOQUEADO]
    E --> F{¿Desbloqueo solicitado?}
    F -->|Sí| G[Evaluar desbloqueo]
    G --> H{¿Procede?}
    H -->|Sí| I[RESUELTO]
    H -->|No| E
    I --> Z([FIN])
    D --> Z`,

  portabilidad: `flowchart TD
    A([ABIERTO]) --> B[EN PROCESO]
    B --> C[Identificar datos a exportar]
    C --> D{Formato solicitado}
    D -->|JSON| E[Generar JSON]
    D -->|CSV| F[Generar CSV]
    D -->|Excel| G[Generar XLSX]
    E --> H[RESUELTO]
    F --> H
    G --> H
    H --> Z([FIN])
    B --> I{¿Prórroga?<br/>Art.12 bis}
    I -->|Sí| J[PRÓRROGA]
    J -.-> B
    I -->|No| D`,
};

const MAPEO_ESTADO_A_NODO_POR_TIPO: Record<TipoArco, Partial<Record<EstadoTicket, string>>> = {
  acceso: {
    abierto: 'A',
    en_proceso: 'B',
    pendiente: 'C',
    subsanacion: 'D',
    prorroga: 'F',
    resuelto: 'H',
    rechazado: 'I'
  },
  rectificacion: {
    abierto: 'A',
    en_proceso: 'C',
    pendiente: 'C',
    resuelto: 'E',
    rechazado: 'F'
  },
  cancelacion: {
    abierto: 'A',
    en_proceso: 'C',
    pendiente: 'C',
    subsanacion: 'D',
    resuelto: 'H',
    rechazado: 'E'
  },
  oposicion: {
    abierto: 'A',
    en_proceso: 'C',
    pendiente: 'C',
    subsanacion: 'D',
    resuelto: 'H',
    rechazado: 'G'
  },
  bloqueo: {
    abierto: 'A',
    en_proceso: 'C',
    pendiente: 'C',
    subsanacion: 'D',
    bloqueado: 'E',
    resuelto: 'I',
    rechazado: 'D'
  },
  portabilidad: {
    abierto: 'A',
    en_proceso: 'C',
    pendiente: 'C',
    subsanacion: 'D',
    prorroga: 'J',
    resuelto: 'H',
    rechazado: 'H'
  }
};

const SECUENCIA_ESTADOS: Record<TipoArco, string[]> = {
  acceso: ['abierto', 'en_proceso', 'subsanacion', 'prorroga', 'resuelto', 'rechazado'],
  rectificacion: ['abierto', 'en_proceso', 'resuelto', 'rechazado'],
  cancelacion: ['abierto', 'en_proceso', 'subsanacion', 'resuelto', 'rechazado'],
  oposicion: ['abierto', 'en_proceso', 'subsanacion', 'resuelto', 'rechazado'],
  bloqueo: ['abierto', 'en_proceso', 'subsanacion', 'bloqueado', 'resuelto', 'rechazado'],
  portabilidad: ['abierto', 'en_proceso', 'subsanacion', 'prorroga', 'resuelto', 'rechazado']
};

export function getDiagramaPorTipo(tipo: TipoArco): string {
  return DIAGRAMAS[tipo] || DIAGRAMAS.acceso;
}

export function getNodosAnteriores(estado: string, tipo: TipoArco): string[] {
  const secuencia = SECUENCIA_ESTADOS[tipo] || SECUENCIA_ESTADOS.acceso;
  const idx = secuencia.indexOf(estado);
  if (idx <= 0) return [];
  return secuencia.slice(0, idx);
}

export function getIdNodoPorEstado(tipo: TipoArco, estado: string): string {
  const mapeo = MAPEO_ESTADO_A_NODO_POR_TIPO[tipo];
  if (mapeo && mapeo[estado as EstadoTicket]) {
    return mapeo[estado as EstadoTicket]!;
  }
  if (mapeo && mapeo[estado as EstadoTicket] === undefined) {
    const secuencia = SECUENCIA_ESTADOS[tipo];
    const idx = secuencia.indexOf(estado);
    if (idx > 0) {
      const estadoAnterior = secuencia[idx - 1];
      return mapeo[estadoAnterior as EstadoTicket] || 'A';
    }
  }
  return 'A';
}

function marcarNodoActual(diagrama: string, nodoActual: string): string {
  // Rectangular: ID[label] → ID[★ label]
  let result = diagrama.replace(
    new RegExp(`\\b(${nodoActual})\\[(?!★)`, 'g'),
    '$1[★ '
  );
  // Stadium: ID([label]) → ID([★ label])
  result = result.replace(
    new RegExp(`\\b(${nodoActual})\\(\\[(?!★)`, 'g'),
    '$1([★ '
  );
  // Diamond: ID{label} → ID{★ label}
  result = result.replace(
    new RegExp(`\\b(${nodoActual})\\{(?!★)`, 'g'),
    `$1{★ `
  );
  return result;
}

// Paleta de colores del design system
const CLASSDEFS = [
  'classDef currentNode  fill:#4F46E5,color:#fff,stroke:#3730A3,stroke-width:3px,font-weight:bold',
  'classDef completedNode fill:#1E293B,color:#94A3B8,stroke:#334155,stroke-width:1px',
  'classDef pendingNode  fill:#F8FAFC,color:#94A3B8,stroke:#E2E8F0,stroke-width:1px,stroke-dasharray:4 2',
  'classDef finalNode    fill:#ECFDF5,color:#065F46,stroke:#10B981,stroke-width:2px',
  'classDef decisionNode fill:#FFFBEB,color:#92400E,stroke:#F59E0B,stroke-width:1.5px',
  'classDef rejectedNode fill:#FFF1F2,color:#9F1239,stroke:#FB7185,stroke-width:1.5px',
  'classDef resolvedNode fill:#ECFDF5,color:#065F46,stroke:#10B981,stroke-width:2px',
  'classDef startNode    fill:#EFF6FF,color:#1D4ED8,stroke:#93C5FD,stroke-width:1.5px',
].join('\n    ');

export function aplicarColores(
  diagrama: string,
  tipo: TipoArco,
  estadoActual: string,
  nodosAnteriores: string[]
): { codigo: string; nodoActual: string } {
  const nodoActual = getIdNodoPorEstado(tipo, estadoActual);
  const diagramaConMarca = marcarNodoActual(diagrama, nodoActual);

  // Extraer IDs de nodos presentes en el diagrama
  const nodoIdsEnDiagrama = new Set<string>();
  for (const linea of diagramaConMarca.split('\n')) {
    const matches = linea.match(/\b([A-Z]+)(?=[^w]|$)/g);
    if (matches) matches.forEach(m => { if (m.length > 0) nodoIdsEnDiagrama.add(m); });
  }

  // Mapa de prioridad: la asignación más reciente gana
  const nodeClasses = new Map<string, string>();

  // 1. Todos pendientes por defecto
  for (const id of nodoIdsEnDiagrama) nodeClasses.set(id, 'pendingNode');

  // 2. Nodo inicio
  if (nodoIdsEnDiagrama.has('A')) nodeClasses.set('A', 'startNode');

  // 3. Nodos de decisión (diamantes)
  const decPat = /\b([A-Z]+)\{/g;
  let dm: RegExpExecArray | null;
  while ((dm = decPat.exec(diagrama)) !== null) {
    if (nodoIdsEnDiagrama.has(dm[1])) nodeClasses.set(dm[1], 'decisionNode');
  }

  // 4. Nodos RECHAZADO
  const rejPat = /\b([A-Z]+)\[RECHAZADO/g;
  let rm: RegExpExecArray | null;
  while ((rm = rejPat.exec(diagrama)) !== null) {
    if (nodoIdsEnDiagrama.has(rm[1])) nodeClasses.set(rm[1], 'rejectedNode');
  }

  // 5. Nodos RESUELTO (excluyendo Z)
  const resPat = /\b([A-Z]+)\[RESUELTO/g;
  let resm: RegExpExecArray | null;
  while ((resm = resPat.exec(diagrama)) !== null) {
    if (nodoIdsEnDiagrama.has(resm[1]) && resm[1] !== 'Z') nodeClasses.set(resm[1], 'resolvedNode');
  }

  // 6. Nodo final Z
  if (nodoIdsEnDiagrama.has('Z')) nodeClasses.set('Z', 'finalNode');

  // 7. Nodos completados (mayor prioridad que los anteriores)
  for (const estado of nodosAnteriores) {
    const id = getIdNodoPorEstado(tipo, estado);
    if (nodoIdsEnDiagrama.has(id)) nodeClasses.set(id, 'completedNode');
  }

  // 8. Nodo actual (máxima prioridad)
  if (nodoIdsEnDiagrama.has(nodoActual)) nodeClasses.set(nodoActual, 'currentNode');

  // Construir resultado
  let resultado = diagramaConMarca.replace(
    'flowchart TD',
    `flowchart TD\n    ${CLASSDEFS}`
  );

  for (const [id, cls] of nodeClasses.entries()) {
    resultado += `\n    class ${id} ${cls}`;
  }

  return { codigo: resultado, nodoActual };
}

export function getTituloPorTipo(tipo: TipoArco): string {
  const titulos: Record<TipoArco, string> = {
    acceso: 'ACCESO — Art. 8 lit. (a)',
    rectificacion: 'RECTIFICACIÓN — Art. 9',
    cancelacion: 'CANCELACIÓN — Art. 8 lit. (c)',
    oposicion: 'OPOSICIÓN — Art. 13',
    bloqueo: 'BLOQUEO — Art. 8 ter',
    portabilidad: 'PORTABILIDAD — Art. 12'
  };
  return titulos[tipo] || tipo.toUpperCase();
}

export function getDescripcionPorTipo(tipo: TipoArco): string {
  const descripciones: Record<TipoArco, string> = {
    acceso: 'Derecho a conocer los datos personales almacenados',
    rectificacion: 'Derecho a corregir datos inexactos o incompletos',
    cancelacion: 'Derecho a eliminar datos personales con excepciones legales',
    oposicion: 'Derecho a oponerse al tratamiento basado en interés legítimo',
    bloqueo: 'Derecho a bloquear el tratamiento de datos personales',
    portabilidad: 'Derecho a recibir datos en formato estructurado'
  };
  return descripciones[tipo] || '';
}
