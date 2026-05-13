export const API_BASE = 'http://localhost:8002';
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