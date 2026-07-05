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
  'En revision': 'en_revision',
  'Aprobado': 'aprobado',
};
export const ESTADO_OPTIONS = ['Borrador', 'Completo', 'En revision', 'Aprobado'] as const;
export const ESTADO_LABEL: Record<string, string> = {
  borrador: 'Borrador',
  completo: 'Completo',
  en_revision: 'En revisión',
  aprobado: 'Aprobado',
};
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

export const DATOS_NNA_OPCIONES = [
  { value: 'ninguno', label: 'Ninguno' },
  { value: 'ninos', label: 'Ninos (< 14 anos)' },
  { value: 'adolescentes', label: 'Adolescentes (14-17 anos)' },
  { value: 'ambos', label: 'Ambos' },
] as const;

export const NIVEL_CONFIDENCIALIDAD_OPCIONES = [
  { value: 'DC0', label: 'DC0 — Publico', tooltip: 'Informacion publicada o de dominio publico. Sin restricciones de privacidad.' },
  { value: 'DC1', label: 'DC1 — Uso Interno', tooltip: 'Informacion interna de la organizacion. Acceso restringido a empleados.' },
  { value: 'DC2', label: 'DC2 — Uso Restringido', tooltip: 'Informacion sensible internamente. Acceso solo a personal autorizado con necesidad de conocer.' },
  { value: 'DC3', label: 'DC3 — Confidencial', tooltip: 'Informacion altamente sensible. Requiere medidas de seguridad reforzadas. Incluye datos biometricos, de salud, NNA y financieros.' },
] as const;

export const ESTRUCTURA_DATO_OPCIONES = [
  { value: 'estructurado', label: 'Estructurado (DB, Excel, CSV)' },
  { value: 'semiestructurado', label: 'Semi-estructurado (JSON, XML, Emails)' },
  { value: 'no_estructurado', label: 'No estructurado (Documentos, imagenes, audio)' },
  { value: 'fisico', label: 'Fisico (papel, formularios)' },
] as const;

export const CICLO_PROCESAMIENTO_OPCIONES = [
  'recopilacion', 'almacenamiento', 'uso', 'comunicacion', 'eliminacion', 'archivo'
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