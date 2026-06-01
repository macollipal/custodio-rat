export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://custodio-api-qa-git-qa-marcelos-projects-3cc299e0.vercel.app';
export const STORAGE_KEYS = {
  TOKEN: 'custodio_token',
  USER: 'custodio_user',
  COMPANY: 'custodio_company',
} as const;
export const DRAFT_KEY_PREFIX = 'custodio_wizard_draft_';
export const DIAS_REVISION = 180;
export const ESTADO_MAP: Record<string, string> = {
  'Borrador': 'borrador',
  'Completo': 'completo',
  'En revision': 'en_revision',
  'Aprobado': 'aprobado',
};
export const ESTADO_OPTIONS = ['Borrador', 'Completo', 'En revision', 'Aprobado'] as const;
export const RIESGO_OPTIONS = ['Bajo', 'Medio', 'Alto', 'Critico'] as const;
export const EIPD_OPTIONS = ['Requerida', 'No requerida'] as const;
export const TIPOS_DATO_SENSIBLE = [
  'Origen racial o etnico',
  'Situacion socioeconomica',
  'Salud (fisica o mental)',
  'Vida sexual, orientacion sexual e identidad de genero',
  'Opiniones politicas, creencias religiosas o filosoficas',
  'Afiliacion sindical',
  'Datos biometricos de identificacion (Art. 16 BIS)',
] as const;
export const BASES_LEGALES = [
  'Consentimiento del titular',
  'Ejecucion de contrato',
  'Obligacion legal',
  'Interes legitimo',
  'Interes vital del titular',
  'Datos biometricos de identificacion (Art. 16 BIS)',
  'Otra',
] as const;
export const DESCRIPCIONES_BASE: Record<string, string> = {
  'Consentimiento del titular':
    'Art. 12 - Debe ser libre, previo, expreso, informado, especifico, revocable y sin condicion negocial. ' +
    'Para datos sensibles, el consentimiento debe ser EXPRESO.',
  'Ejecucion de contrato':
    'Art. 13 b) - El tratamiento es necesario para ejecutar un contrato en que el titular es parte.',
  'Obligacion legal':
    'Art. 13 a) - El tratamiento es requerido por una norma legal vigente.',
  'Interes legitimo':
    'Art. 16 - Requiere documentar el test de 3 pasos.',
  'Interes vital del titular':
    'Art. 13 c) - Proteger intereses vitales del titular u otra persona.',
  'Datos biometricos de identificacion (Art. 16 BIS)':
    'Art. 16 BIS - Base especifica para datos biometricos. Requiere EIPD previa.',
};