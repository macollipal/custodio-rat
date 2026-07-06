'use client';

import { useState, Dispatch, SetStateAction } from 'react';
import { RATWizardData } from '@/types';
import { useStepValidation, StepValidation } from '../../ratWizardValidation';

const MIN_STEP = 1;
const MAX_STEP = 5;

export interface WizardNavigation {
  step: number;
  setStep: Dispatch<SetStateAction<number>>;
  getValidation: (data: RATWizardData) => StepValidation;
  canGoNext: boolean;
  canGoPrev: boolean;
  next: () => boolean;
  prev: () => void;
  goTo: (n: number) => boolean;
}

export function useWizardNavigation(
  data: RATWizardData,
  initialStep: number = 1,
): WizardNavigation {
  const validation = useStepValidation(initialStep, data);
  const [step, setStep] = useState<number>(initialStep);

  const canGoPrev = step > MIN_STEP;
  const canGoNext = step < MAX_STEP && validation.isValid;

  const next = (): boolean => {
    if (!canGoNext) return false;
    setStep((s) => Math.min(s + 1, MAX_STEP));
    return true;
  };

  const prev = () => {
    setStep((s) => Math.max(s - 1, MIN_STEP));
  };

  const goTo = (n: number): boolean => {
    if (n < MIN_STEP || n > MAX_STEP) return false;
    if (n > step && !validation.isValid) return false;
    setStep(n);
    return true;
  };

  // Re-export validation getter
  const getValidation = (d: RATWizardData) => useStepValidation(step, d);

  return { step, setStep, getValidation, canGoNext, canGoPrev, next, prev, goTo };
}