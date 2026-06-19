export type TipoArco = 'acceso' | 'rectificacion' | 'cancelacion' | 'oposicion' | 'bloqueo' | 'portabilidad';

export type EstadoTicket = 'abierto' | 'en_proceso' | 'pendiente' | 'subsanacion' | 'prorroga' | 'bloqueado' | 'resuelto' | 'rechazado';

export const DIAGRAMAS: Record<TipoArco, string> = {
  acceso: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C{"<b>¿Subsanación?</b>"}
    C -->|Sí| D[<b>SUBSANACIÓN</b>]
    D -.->|Complementa| B
    C -->|No| E{"<b>¿Prórroga?</b>"}
    E -->|Sí| F[<b>PRÓRROGA</b>]
    F -.->|Vence| B
    E -->|No| G{"<b>Decisión DPO</b>"}
    G -->|Favorable| H[<b>RESUELTO</b>]
    G -->|Rechazado| I[<b>RECHAZADO</b>]
    H --> Z([<b>FIN</b>])
    I --> Z`,

  rectificacion: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C[<b>Evaluar datos<br/>inexactos</b>]
    C --> D{"<b>¿Datos incorrectos?</b>"}
    D -->|Sí| E[<b>RESUELTO</b><br/>Rectificar BD]
    D -->|No| F[<b>RECHAZADO</b><br/>Fundamentado]
    E --> Z([<b>FIN</b>])
    F --> Z`,

  cancelacion: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C[<b>Evaluar excepciones<br/>Art. 8 c.ii</b>]
    C --> D{"<b>¿Excepción<br/>aplica?</b>"}
    D -->|Sí| E[<b>RECHAZADO</b><br/>Legal]
    D -->|No| F{"<b>¿Terceros<br/>involucrados?</b>"}
    F -->|Sí| G[<b>Notificar<br/>terceros</b>]
    F -->|No| H[<b>RESUELTO</b><br/>Eliminar BD]
    G -.-> H
    H --> Z([<b>FIN</b>])
    E --> Z`,

  oposicion: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C[<b>Evaluar base legal</b>]
    C --> D{"<b>¿Legítimo interés<br/>o marketing?</b>"}
    D -->|No| E[<b>RECHAZADO</b><br/>No aplica]
    D -->|Sí| F{"<b>¿Prevalece<br/>interés?</b>"}
    F -->|Sí| G[<b>RECHAZADO</b><br/>Prevalece interés]
    F -->|No| H[<b>RESUELTO</b><br/>Cese tratamiento]
    H --> Z([<b>FIN</b>])
    G --> Z
    E --> Z`,

  bloqueo: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C{"<b>¿Causal Art. 8 ter<br/>acreditada?</b>"}
    C -->|No| D[<b>RECHAZADO</b>]
    C -->|Sí| E[<b>BLOQUEADO</b>]
    E --> F{"<b>¿Desbloqueo<br/>solicitado?</b>"}
    F -->|Sí| G[<b>Evaluar<br/>desbloqueo</b>]
    G --> H{"<b>¿Procede?</b>"}
    H -->|Sí| I[<b>EN PROCESO<br/>o RESUELTO</b>]
    H -->|No| E
    I --> Z([<b>FIN</b>])
    E --> F`,

  portabilidad: `flowchart TD
    A([<b>ABIERTO</b>]) --> B[<b>EN PROCESO</b>]
    B --> C[<b>Identificar datos<br/>a exportar</b>]
    C --> D{"<b>Formato<br/>solicitado</b>"}
    D -->|JSON| E[<b>Generar JSON</b>]
    D -->|CSV| F[<b>Generar CSV</b>]
    D -->|Excel| G[<b>Generar XLSX</b>]
    E --> H[<b>RESUELTO</b>]
    F --> H
    G --> H
    H --> Z([<b>FIN</b>])
    B --> I{"<b>¿Prórroga?<br/>Art.12 bis</b>"}
    I -->|Sí| J[<b>PRÓRROGA</b>]
    J -.-> B
    I -->|No| D`
};

const MAPEO_ESTADO_A_NODO: Record<string, string> = {
  abierto: 'A',
  en_proceso: 'B',
  pendiente: 'C',
  subsanacion: 'D',
  prorroga: 'F',
  bloqueado: 'E',
  resuelto: 'H',
  rechazado: 'I',
  evaluacion: 'C',
  evaluar_excepciones: 'C',
  evaluar_base_legal: 'C',
  notificar_terceros: 'G',
  generar_export: 'C',
  evaluacion_excepciones: 'C',
  evaluar_datos: 'C',
  evaluar_bloqueo: 'C'
};

const SECUENCIA_ESTADOS: Record<TipoArco, string[]> = {
  acceso: ['abierto', 'en_proceso', 'subsanacion', 'prorroga', 'resuelto', 'rechazado'],
  rectificacion: ['abierto', 'en_proceso', 'resuelto', 'rechazado'],
  cancelacion: ['abierto', 'en_proceso', 'evaluacion', 'resuelto', 'rechazado'],
  oposicion: ['abierto', 'en_proceso', 'evaluacion', 'resuelto', 'rechazado'],
  bloqueo: ['abierto', 'en_proceso', 'bloqueado', 'resuelto', 'rechazado'],
  portabilidad: ['abierto', 'en_proceso', 'evaluacion', 'resuelto', 'rechazado']
};

const MARCA_ACTUAL = '★';

export function getDiagramaPorTipo(tipo: TipoArco): string {
  return DIAGRAMAS[tipo] || DIAGRAMAS.acceso;
}

export function getNodosAnteriores(estado: string, tipo: TipoArco): string[] {
  const secuencia = SECUENCIA_ESTADOS[tipo] || SECUENCIA_ESTADOS.acceso;
  const idx = secuencia.indexOf(estado);
  if (idx <= 0) return [];
  return secuencia.slice(0, idx);
}

export function getIdNodoPorEstado(estado: string): string {
  return MAPEO_ESTADO_A_NODO[estado] || 'A';
}

function marcarNodoActual(diagrama: string, nodoActual: string): string {
  const patron = new RegExp(
    `(${nodoActual}(\\[[^\\[]*?<b>)|${nodoActual}(\\([^\\(]*?<b>)|${nodoActual}(\\{[^\\{]*?<b>))`,
    'g'
  );
  return diagrama.replace(patron, (match, grupo) => {
    return match.replace(/<b>/, `<b>${MARCA_ACTUAL} `);
  });
}

export function aplicarColores(diagrama: string, estadoActual: string, nodosAnteriores: string[]): { codigo: string; nodoActual: string } {
  const nodoActual = getIdNodoPorEstado(estadoActual);

  const diagramaConMarca = marcarNodoActual(diagrama, nodoActual);

  const estiloActual = 'classDef currentNode fill:#fef08a,color:#713f12,stroke:#ca8a04,stroke-width:3px,stroke-dasharray:5 2';
  const estiloCompletado = 'classDef completedNode fill:#1f2937,color:#fff,stroke:#000';
  const estiloPendiente = 'classDef pendingNode fill:#f9fafb,color:#6b7280,stroke:#d1d5db';
  const estiloFinal = 'classDef finalNode fill:#10b981,color:#fff,stroke:#059669';
  const estiloDecision = 'classDef decisionNode fill:#fed7aa,color:#9a3412,stroke:#ea580c';

  let resultado = diagramaConMarca;
  const lineas = resultado.split('\n');
  const nodoIdsEnDiagrama = new Set<string>();

  for (const linea of lineas) {
    const matches = linea.match(/([A-Z]+)(?=[^\w]|$)/g);
    if (matches) {
      for (const m of matches) {
        if (m.length > 0) nodoIdsEnDiagrama.add(m);
      }
    }
  }

  if (nodoIdsEnDiagrama.has(nodoActual)) {
    resultado += `\n    class ${nodoActual} currentNode`;
  }

  for (const nodo of nodosAnteriores) {
    const id = MAPEO_ESTADO_A_NODO[nodo] || nodo;
    if (nodoIdsEnDiagrama.has(id)) {
      resultado += `\n    class ${id} completedNode`;
    }
  }

  if (nodoIdsEnDiagrama.has('Z')) {
    resultado += `\n    class Z finalNode`;
  }

  if (resultado.includes('{"<b>')) {
    resultado += `\n    class C decisionNode`;
  }

  resultado = resultado.replace('flowchart TD',
    `flowchart TD\n    ${estiloActual}\n    ${estiloCompletado}\n    ${estiloPendiente}\n    ${estiloFinal}\n    ${estiloDecision}`
  );

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
    cancelacion: 'Derecho a eliminar datos personales (con excepciones)',
    oposicion: 'Derecho a oponerse al tratamiento basado en interés legítimo',
    bloqueo: 'Derecho a bloquear el tratamiento de datos personales',
    portabilidad: 'Derecho a recibir datos en formato estructurado'
  };
  return descripciones[tipo] || '';
}
