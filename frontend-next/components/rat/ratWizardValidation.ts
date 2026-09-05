'use client';

import { useMemo } from 'react';
import type { RATWizardData } from '@/types';

export interface FieldErrors {
  [field: string]: string | undefined;
}

export interface StepValidation {
  errors: FieldErrors;
  isValid: boolean;
  /** Total de campos obligatorios en este paso */
  requiredCount: number;
  /** Cuántos están completados correctamente */
  completedCount: number;
  /** ID del primer campo con error (para scroll-to-error) */
  firstErrorField: string | undefined;
}

const MIN_TEST_IL = 50;

/** Valida Step 1: Identificación del proceso */
export function validateStep1(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.nombre_proceso?.trim()) errors.nombre_proceso = 'El nombre del proceso es obligatorio.';
  if (!d.categoria_titulares?.trim()) errors.categoria_titulares = 'Las categorías de titulares son obligatorias (Art. 16 Ley 21.719).';
  if (!d.fuente_datos?.trim()) errors.fuente_datos = 'La fuente de datos es obligatoria.';
  const requiredCount = 3;
  const completedCount = requiredCount - Object.keys(errors).length;
  const firstErrorField = Object.keys(errors)[0];
  return { errors, isValid: Object.keys(errors).length === 0, requiredCount, completedCount, firstErrorField };
}

/** Valida Step 2: Datos personales tratados */
export function validateStep2(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.categoria_datos?.trim()) errors.categoria_datos = 'La categoría de datos es obligatoria.';
  if (d.datos_sensibles && !d.tipo_dato_sensible?.trim()) {
    errors.tipo_dato_sensible = 'Selecciona el tipo de dato sensible (Art. 2 letra g).';
  }
  if (d.datos_anonimizados && d.datos_seudonimizados) {
    errors.datos_anonimizados = 'Un dato no puede ser simultáneamente anonimizado y seudonimizado (son técnicas mutuamente excluyentes).';
  }
  const requiredCount = 1 + (d.datos_sensibles ? 1 : 0);
  const completedCount = requiredCount - Object.keys(errors).length;
  const firstErrorField = Object.keys(errors)[0];
  return { errors, isValid: Object.keys(errors).length === 0, requiredCount, completedCount, firstErrorField };
}

/** Valida Step 3: Finalidad y base legal */
export function validateStep3(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.finalidad?.trim()) errors.finalidad = 'La finalidad es obligatoria.';
  if (!d.base_legal?.trim()) errors.base_legal = 'La base legal es obligatoria.';
  if (d.base_legal === 'Interés legítimo') {
    if (!d._testIL?.paso1?.trim() || !d._testIL?.paso2?.trim() || !d._testIL?.paso3?.trim()) {
      errors._testIL = 'El test de interés legítimo es obligatorio (Art. 16). Complete los 3 pasos documentados.';
    }
  }
  const requiredCount = 2 + (d.base_legal === 'Interés legítimo' ? 1 : 0);
  const completedCount = requiredCount - Object.keys(errors).length;
  const firstErrorField = Object.keys(errors)[0];
  return { errors, isValid: Object.keys(errors).length === 0, requiredCount, completedCount, firstErrorField };
}

/** Valida Step 4: Almacenamiento y transferencias */
export function validateStep4(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.plazo_retencion?.trim()) errors.plazo_retencion = 'El plazo de retención es obligatorio.';
  if (d.transferencia_internacional && !d.pais_destino?.trim()) {
    errors.pais_destino = 'Especifica el país destino.';
  }
  if (d.transferencia_internacional && !d.garantias_transferencia_int?.trim()) {
    errors.garantias_transferencia_int = 'Selecciona las garantías aplicables.';
  }
  const requiredCount = 1 + (d.transferencia_internacional ? 2 : 0);
  const completedCount = requiredCount - Object.keys(errors).length;
  const firstErrorField = Object.keys(errors)[0];
  return { errors, isValid: Object.keys(errors).length === 0, requiredCount, completedCount, firstErrorField };
}

/** Hook que retorna la validación del paso actual */
export function useStepValidation(step: number, data: RATWizardData): StepValidation {
  return useMemo(() => {
    switch (step) {
      case 0: return { errors: {}, isValid: true, requiredCount: 0, completedCount: 0, firstErrorField: undefined };
      case 1: return validateStep1(data);
      case 2: return validateStep2(data);
      case 3: return validateStep3(data);
      case 4: return validateStep4(data);
      default: return { errors: {}, isValid: true, requiredCount: 0, completedCount: 0, firstErrorField: undefined };
    }
  }, [step, data]);
}