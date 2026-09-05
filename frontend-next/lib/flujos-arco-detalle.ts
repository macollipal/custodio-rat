import { TipoArco, EstadoTicket } from './flujos-arco';

export interface SubPaso {
  titulo: string;
  accion: string;
  opciones?: string[];
  proximos?: string[];
}

export type SubPasosMap = Record<TipoArco, Partial<Record<EstadoTicket, SubPaso>>>;

export const SUBPASOS: SubPasosMap = {
  acceso: {
    abierto: {
      titulo: 'Solicitud recibida',
      accion: 'El titular ha presentado una solicitud de acceso. El DPO debe verificar la identidad y asignar responsable.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Evaluación por el DPO',
      accion: 'El responsable evalúa la solicitud. Debe determinar si requiere subsanación de datos o proroga del plazo.',
      opciones: ['Solicitar subsanación al titular', 'Solicitar prorroga (máx. 10 días)', 'Proceder con la respuesta']
    },
    pendiente: {
      titulo: 'Información adicional requerida',
      accion: 'Se ha solicitado información adicional al titular para completar la solicitud.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe completar o corregir la información. Plazo suspendido hasta recibido los datos.',
      opciones: ['Recibir subsanación del titular', 'Cancelar solicitud si no responde']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se ha extendido el plazo por 10 días hábiles adicionales. La solicitud permanece en evaluación.',
      opciones: ['Responder al vencimiento de la prorroga']
    },
    resuelto: {
      titulo: 'Acceso entregado',
      accion: 'Se han entregado los datos solicitados al titular. Proceso completado.',
      proximos: []
    },
    rechazado: {
      titulo: 'Solicitud rechazada',
      accion: 'La solicitud fue rechazada. Se ha notificado al titular con el fundamento legal correspondiente.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Tratamiento bloqueado',
      accion: 'El tratamiento de los datos del titular ha sido bloqueado preventivamente.',
      proximos: ['en_proceso', 'resuelto']
    }
  },

  rectificacion: {
    abierto: {
      titulo: 'Solicitud de rectificación recibida',
      accion: 'El titular solicita corregir datos inexactos o incompletos. El DPO debe verificar la solicitud.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Evaluar datos inexactos',
      accion: 'El DPO debe verificar si los datos efectivamente son inexactos o incompletos.',
      opciones: ['Datos inexactos — proceder a corregir', 'Datos correctos — rechazar solicitud']
    },
    pendiente: {
      titulo: 'Verificación en curso',
      accion: 'Se está verificando la inexactitud de los datos reportados por el titular.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe proporcionar los datos correctos para completar la rectificación.',
      opciones: ['Recibir datos correctos', 'Cancelar si no hay respuesta']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se extendió el plazo por 10 días. La evaluación de la rectificación continúa.',
      opciones: ['Finalizar evaluación al vencer']
    },
    resuelto: {
      titulo: 'Datos rectificados',
      accion: 'Los datos han sido corregidos en el sistema. El titular ha sido notificado.',
      proximos: []
    },
    rechazado: {
      titulo: 'Rectificación rechazada',
      accion: 'Los datos eran correctos o la solicitud no tenía fundamento. Notificado al titular.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Datos bloqueados',
      accion: 'Los datos involucrados han sido bloqueados mientras se evalúa la rectificación.',
      proximos: ['en_proceso', 'resuelto']
    }
  },

  cancelacion: {
    abierto: {
      titulo: 'Solicitud de cancelación recibida',
      accion: 'El titular solicita la eliminación de sus datos personales. El DPO evalúa si aplica alguna excepción legal.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Evaluar excepciones legales',
      accion: 'Verificar si existe alguna excepción del Art. 8 c.ii que impida la eliminación (ej. obligación legal, litigio pendiente).',
      opciones: ['Aplica excepción — rechazar con fundamento', 'No aplica excepción — continuar']
    },
    pendiente: {
      titulo: 'Evaluando excepciones',
      accion: 'Se analizan las posibles excepciones legales que podrían impedir la cancelación.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe aclarar o complementar su solicitud de cancelación.',
      opciones: ['Recibir aclaración', 'Cancelar solicitud']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se extendió el plazo por 10 días hábiles. La evaluación de excepciones continúa.',
      opciones: ['Evaluar al vencimiento']
    },
    resuelto: {
      titulo: 'Datos eliminados',
      accion: 'Los datos personales han sido eliminados del sistema. Terceros han sido notificados si corresponde.',
      proximos: []
    },
    rechazado: {
      titulo: 'Cancelación rechazada',
      accion: 'Aplica excepción legal. Los datos se conservan según Art. 8 c.ii. Titular notificado.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Datos bloqueados',
      accion: 'Los datos fueron bloqueados mientras se evalúa la cancelación.',
      proximos: ['en_proceso', 'resuelto']
    }
  },

  oposicion: {
    abierto: {
      titulo: 'Solicitud de oposición recibida',
      accion: 'El titular se opone al tratamiento de sus datos. El DPO debe evaluar la base legal del tratamiento.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Evaluar base legal del tratamiento',
      accion: 'Determinar si el tratamiento se basa en interés legítimo o marketing directo (Art. 13). Si es otra base, la oposición no aplica.',
      opciones: ['✓ Legítimo interés o marketing — evaluar si prevalece', '✗ Otra base legal — rechazar oposición']
    },
    pendiente: {
      titulo: 'Evaluando oposición',
      accion: 'Se está evaluando si el interés legítimo o marketing prevalece sobre los derechos del titular.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe aclarar elobjecto de su oposición.',
      opciones: ['Recibir aclaración', 'Cancelar solicitud']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se extendió el plazo por 10 días. La evaluación de la oposición continúa.',
      opciones: ['Evaluar al vencimiento']
    },
    resuelto: {
      titulo: 'Oposición estimada — tratamiento cesado',
      accion: 'El tratamiento de los datos del titular ha cesado. Notificado al titular y equipos internos.',
      proximos: []
    },
    rechazado: {
      titulo: 'Oposición rechazada',
      accion: 'El interés legítimo o marketing prevalece sobre la oposición. El tratamiento continúa. Titular notificado.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Tratamiento bloqueado',
      accion: 'El tratamiento ha sido bloqueado mientras se evalúa la oposición.',
      proximos: ['en_proceso', 'resuelto']
    }
  },

  bloqueo: {
    abierto: {
      titulo: 'Solicitud de bloqueo recibida',
      accion: 'El titular solicita bloquear el tratamiento de sus datos. El DPO evalúa si existe causal del Art. 8 ter.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Evaluar causal Art. 8 ter',
      accion: 'Verificar si existe causal legal para bloquear el tratamiento (ej. tratamiento ilícito, datos sensibles sin base legal).',
      opciones: ['✓ Causal acreditada — bloquear', '✗ Sin causal — rechazar solicitud']
    },
    pendiente: {
      titulo: 'Verificación en curso',
      accion: 'Se está verificando la existencia de causal para el bloqueo.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe aportar antecedentes que sustenten la causal de bloqueo.',
      opciones: ['Recibir antecedentes', 'Cancelar solicitud']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se extendió el plazo por 10 días. La evaluación de la causal continúa.',
      opciones: ['Evaluar al vencimiento']
    },
    resuelto: {
      titulo: 'Bloqueo aplicado',
      accion: 'El tratamiento ha sido bloqueado exitosamente. Notificado al titular.',
      proximos: []
    },
    rechazado: {
      titulo: 'Bloqueo rechazado',
      accion: 'No se acreditó causal del Art. 8 ter. El tratamiento continúa normalmente.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Evaluando desbloqueo',
      accion: 'El titular ha solicitado desbloqueo. El DPO evalúa si procede reiniciar el tratamiento.',
      opciones: ['✓ Desbloquear — reanudar tratamiento', '✗ Mantener bloqueo']
    }
  },

  portabilidad: {
    abierto: {
      titulo: 'Solicitud de portabilidad recibida',
      accion: 'El titular solicita sus datos en formato estructurado. El DPO identifica los datos y el formato solicitado.',
      proximos: ['en_proceso']
    },
    en_proceso: {
      titulo: 'Identificar y exportar datos',
      accion: 'El DPO identifica los datos subject a portabilidad y genera el archivo en el formato solicitado.',
      opciones: ['Generar JSON', 'Generar CSV', 'Generar Excel']
    },
    pendiente: {
      titulo: 'Generando exportación',
      accion: 'Se está preparando la exportación de datos en el formato solicitado.',
      proximos: ['en_proceso']
    },
    subsanacion: {
      titulo: 'Subsanación en curso',
      accion: 'El titular debe aclarar qué datos o formato requiere para la portabilidad.',
      opciones: ['Recibir aclaración', 'Cancelar solicitud']
    },
    prorroga: {
      titulo: 'Prórroga activada',
      accion: 'Se extendió el plazo por 10 días. La preparación de la exportación continúa.',
      opciones: ['Generar exportación al vencimiento']
    },
    resuelto: {
      titulo: 'Datos exportados y entregados',
      accion: 'El archivo con los datos del titular ha sido generado y entregado.',
      proximos: []
    },
    rechazado: {
      titulo: 'Portabilidad rechazada',
      accion: 'No fue posible generar la exportación o la solicitud no cumplía los requisitos.',
      proximos: []
    },
    bloqueado: {
      titulo: 'Datos bloqueados',
      accion: 'Los datos están bloqueados y no se pueden exportar hasta resolver el bloqueo.',
      proximos: ['en_proceso', 'resuelto']
    }
  }
};

export function getSubPaso(tipo: TipoArco, estado: EstadoTicket): SubPaso | null {
  return SUBPASOS[tipo]?.[estado] ?? null;
}
