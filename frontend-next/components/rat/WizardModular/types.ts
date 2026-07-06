import { Company, RATWizardData, RATSugerido } from '@/types';

export const STEPS: string[] = ['Identificación', 'Datos tratados', 'Finalidad y ley', 'Transferencias', 'Compliance'];
export type WizardStepName = typeof STEPS[number];

export interface RatWizardProps {
  company: Company;
  onDone: () => void;
  onCancel: () => void;
}

export interface DraftSnapshot {
  data: RATWizardData;
  savedAt: number;
}

export interface StepValidation {
  errors: Record<string, string | undefined>;
  isValid: boolean;
  requiredCount: number;
  completedCount: number;
  firstErrorField?: string;
}

export interface StepProps {
  data: RATWizardData;
  setData: React.Dispatch<React.SetStateAction<RATWizardData>>;
  validation: StepValidation;
  stepIsValid: boolean;
  fieldErrors: Record<string, string | undefined>;
  inputCls: string;
  inputStyle: React.CSSProperties;
  onNext: () => void;
  onPrev: () => void;
  guardarDraft: () => void;
}

export interface Step0Props extends StepProps {
  mostrarPaso0: boolean;
  rubroNombre: string;
  sugerencias: RATSugerido[];
  usarSugerencia: (sug: RATSugerido) => void;
}

export interface Step1Props extends StepProps {
  tipos: string[];
  tipoSel: string;
  setTipoSel: (v: string) => void;
  sugerencias: RATSugerido[];
  usarSugerencia: (sug: RATSugerido) => void;
  aplicarSugerencias: () => Promise<void>;
}

export interface Step3Props extends StepProps {
  onAplicarSugerencias: () => Promise<void>;
}

export const DRAFT_KEY = (companyId: number): string => `custodio_rat_draft_${companyId}`;

export const DESCRIPCIONES_BASE: Record<string, string> = {
  'Consentimiento del titular':
    'Art. 12 — Debe ser libre, previo, expreso, informado, específico, revocable y sin condición negocial. ' +
    'Para datos sensibles, el consentimiento debe ser EXPRESO. En relaciones laborales jerárquicas, el consentimiento del empleado no es base válida.',
  'Ejecución de contrato':
    'Art. 13 b) — El tratamiento es necesario para ejecutar un contrato en que el titular es parte, o para aplicar medidas precontractuales a su solicitud.',
  'Obligación legal':
    'Art. 13 a) — El tratamiento es requerido por una norma legal vigente (ley, decreto, etc.). Identifique la norma específica que habilita el tratamiento.',
  'Interés legítimo':
    'Art. 16 — Requiere documentar el test de 3 pasos: (1) ¿existe interés legítimo real? (2) ¿el tratamiento es necesario para ese interés? ' +
    '(3) ¿prevalece sobre los derechos del titular? Sin este test documentado, la base no sirve como defensa ante la APDC.',
  'Interés vital del titular':
    'Art. 13 c) — Proteger intereses vitales del titular u otra persona (situaciones de riesgo para la vida o la integridad física).',
  'Datos biométricos de identificación (Art. 16 BIS)':
    'Art. 16 BIS — Base específica para datos biométricos destinados a identificar inequívocamente a una persona. ' +
    'Requiere EIPD previa. En contextos laborales, el consentimiento NO es base válida — use obligación legal y justifique la necesidad.',
};