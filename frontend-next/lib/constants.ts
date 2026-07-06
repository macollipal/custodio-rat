const _apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8002';
export const API_BASE = _apiBase.startsWith('http') ? _apiBase : `https://${_apiBase}`;
export const DEPLOY_ENV = process.env.NEXT_PUBLIC_DEPLOY_ENV || 'local';
export const STORAGE_KEYS = {
  TOKEN: 'custodio_token',
  USER: 'custodio_user',
  COMPANY: 'custodio_company',
  COMPANIES: 'custodio_companies',
} as const;
export const DRAFT_KEY_PREFIX = 'custodio_wizard_draft_';
export const DIAS_REVISION = 180;
export const ESTADO_MAP: Record<string, string> = {
  'Borrador': 'borrador',
  'Completo': 'completo',
  'En revisión': 'en_revision',
  'Aprobado': 'aprobado',
};
export const ESTADO_OPTIONS = ['Borrador', 'Completo', 'En revisión', 'Aprobado'] as const;
export const ESTADO_LABEL: Record<string, string> = {
  borrador: 'Borrador',
  completo: 'Completo',
  en_revision: 'En revisión',
  aprobado: 'Aprobado',
};
export const RIESGO_OPTIONS = ['Bajo', 'Medio', 'Alto', 'Crítico'] as const;
export const EIPD_OPTIONS = ['Requerida', 'No requerida'] as const;
export const TIPOS_DATO_SENSIBLE = [
  'Origen racial o étnico',
  'Situación socioeconómica',
  'Salud (física o mental)',
  'Vida sexual, orientación sexual e identidad de género',
  'Opiniones políticas, creencias religiosas o filosóficas',
  'Afiliación sindical',
  'Datos biométricos de identificación (Art. 16 BIS)',
] as const;
export const BASES_LEGALES = [
  'Consentimiento del titular',
  'Ejecución de contrato',
  'Obligación legal',
  'Interés legítimo',
  'Interés vital del titular',
  'Datos biométricos de identificación (Art. 16 BIS)',
  'Otra',
] as const;
export const DESCRIPCIONES_BASE: Record<string, string> = {
  'Consentimiento del titular':
    'Art. 12 - Debe ser libre, previo, expreso, informado, específico, revocable y sin condición negocial. ' +
    'Para datos sensibles, el consentimiento debe ser EXPRESO.',
  'Ejecución de contrato':
    'Art. 13 b) - El tratamiento es necesario para ejecutar un contrato en que el titular es parte.',
  'Obligación legal':
    'Art. 13 a) - El tratamiento es requerido por una norma legal vigente.',
  'Interés legítimo':
    'Art. 16 - Requiere documentar el test de 3 pasos.',
  'Interés vital del titular':
    'Art. 13 c) - Proteger intereses vitales del titular u otra persona.',
  'Datos biométricos de identificación (Art. 16 BIS)':
    'Art. 16 BIS - Base específica para datos biométricos. Requiere EIPD previa.',
};

export const DATOS_NNA_OPCIONES = [
  { value: 'ninguno', label: 'Ninguno' },
  { value: 'ninos', label: 'Niños (< 14 años)' },
  { value: 'adolescentes', label: 'Adolescentes (14-17 años)' },
  { value: 'ambos', label: 'Ambos' },
] as const;

export const NIVEL_CONFIDENCIALIDAD_OPCIONES = [
  { value: 'DC0', label: 'DC0 — Público', tooltip: 'Información publicada o de dominio público. Sin restricciones de privacidad.' },
  { value: 'DC1', label: 'DC1 — Uso Interno', tooltip: 'Información interna de la organización. Acceso restringido a empleados.' },
  { value: 'DC2', label: 'DC2 — Uso Restringido', tooltip: 'Información sensible internamente. Acceso solo a personal autorizado con necesidad de conocer.' },
  { value: 'DC3', label: 'DC3 — Confidencial', tooltip: 'Información altamente sensible. Requiere medidas de seguridad reforzadas. Incluye datos biométricos, de salud, NNA y financieros.' },
] as const;

export const ESTRUCTURA_DATO_OPCIONES = [
  { value: 'estructurado', label: 'Estructurado (DB, Excel, CSV)' },
  { value: 'semiestructurado', label: 'Semi-estructurado (JSON, XML, Emails)' },
  { value: 'no_estructurado', label: 'No estructurado (Documentos, imágenes, audio)' },
  { value: 'fisico', label: 'Físico (papel, formularios)' },
] as const;

export const CICLO_PROCESAMIENTO_OPCIONES = [
  'recopilación', 'almacenamiento', 'uso', 'comunicación', 'eliminación', 'archivo'
] as const;

export const OPERACIONES_TRATAMIENTO_OPCIONES = [
  'recolección',
  'almacenamiento',
  'consulta',
  'uso',
  'comunicación',
  'cesión',
  'eliminación',
] as const;

export const AUTOMATIZACION_OPCIONES = [
  { value: '100% manual', label: '100% Manual' },
  { value: 'mayoritariamente manual', label: 'Mayoritariamente Manual' },
  { value: 'mayoritariamente automatizado', label: 'Mayoritariamente Automatizado' },
  { value: '100% automatizado', label: '100% Automatizado' },
] as const;

export const FRECUENCIA_OPCIONES = [
  { value: 'diaria', label: 'Diaria' },
  { value: 'semanal', label: 'Semanal' },
  { value: 'mensual', label: 'Mensual' },
  { value: 'trimestral', label: 'Trimestral' },
  { value: 'anual', label: 'Anual' },
  { value: 'puntual', label: 'Puntual / Eventual' },
] as const;