export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ||
  'https://custodio-api-git-qa-marcelos-projects-3cc299e0.vercel.app';
export const STORAGE_KEYS = {
  TOKEN: 'custodio_token',
  USER: 'custodio_user',
  COMPANY: 'custodio_company',
} as const;
export const DRAFT_KEY_PREFIX = 'custodio_wizard_draft_';
export const DIAS_REVISION = 180; // 6 months
export const ESTADO_MAP: Record<string, string> = {
  'Borrador': 'borrador',
  'Completo': 'completo',
  'En revisión': 'en_revision',
  'Aprobado': 'aprobado',
};
export const ESTADO_OPTIONS = ['Borrador', 'Completo', 'En revisión', 'Aprobado'] as const;
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
    'Art. 12 — Debe ser libre, previo, expreso, informado, específico, revocable y sin condición negocial. ' +
    'Para datos sensibles, el consentimiento debe ser EXPRESO.',
  'Ejecución de contrato':
    'Art. 13 b) — El tratamiento es necesario para ejecutar un contrato en que el titular es parte.',
  'Obligación legal':
    'Art. 13 a) — El tratamiento es requerido por una norma legal vigente.',
  'Interés legítimo':
    'Art. 16 — Requiere documentar el test de 3 pasos: (1) ¿existe interés legítimo real? (2) ¿el tratamiento es necesario? (3) ¿prevalece sobre los derechos del titular?',
  'Interés vital del titular':
    'Art. 13 c) — Proteger intereses vitales del titular u otra persona.',
  'Datos biométricos de identificación (Art. 16 BIS)':
    'Art. 16 BIS — Base específica para datos biométricos. Requiere EIPD previa.',
};