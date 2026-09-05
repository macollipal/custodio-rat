'use client';

/**
 * RatWizard - Orquestador modular.
 *
 * Estructura (H4.5):
 *   ./types.ts          — Constantes, tipos, props
 *   ./hooks/useDraftAutosave.ts     — Auto-save localStorage cada 30s
 *   ./hooks/useWizardNavigation.ts  — Navegacion entre pasos
 *   ./steps/Step*.tsx   — Pasos individuales (futuro)
 */

export { STEPS, DESCRIPCIONES_BASE, DRAFT_KEY } from './types';
export type { RatWizardProps, DraftSnapshot, WizardStepName } from './types';
export { useDraftAutosave } from './hooks/useDraftAutosave';
export { useWizardNavigation } from './hooks/useWizardNavigation';
export type { WizardNavigation } from './hooks/useWizardNavigation';
export { Step0, Step1, Step2, Step3, Step4, Step5 } from './steps';