'use client';

import { useMemo } from 'react';
import type { RATWizardData } from '@/types';

export interface FieldErrors {
  [field: string]: string | undefined;
}

export interface StepValidation {
  errors: FieldErrors;
  isValid: boolean;
}

const MIN_TEST_IL = 50;

/** Valida Step 1: Identificación del proceso */
export function validateStep1(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.nombre_proceso?.trim()) errors.nombre_proceso = 'El nombre del proceso es obligatorio.';
  if (!d.categoria_titulares?.trim()) errors.categoria_titulares = 'Las categorías de titulares son obligatorias (Art. 16 Ley 21.719).';
  if (!d.fuente_datos?.trim()) errors.fuente_datos = 'La fuente de datos es obligatoria.';
  return { errors, isValid: Object.keys(errors).length === 0 };
}

/** Valida Step 2: Datos personales tratados */
export function validateStep2(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.categoria_datos?.trim()) errors.categoria_datos = 'La categoría de datos es obligatoria.';
  if (d.datos_sensibles && !d.tipo_dato_sensible?.trim()) {
    errors.tipo_dato_sensible = 'Selecciona el tipo de dato sensible (Art. 2 letra g).';
  }
  return { errors, isValid: Object.keys(errors).length === 0 };
}

/** Valida Step 3: Finalidad y base legal */
export function validateStep3(d: RATWizardData): StepValidation {
  const errors: FieldErrors = {};
  if (!d.finalidad?.trim()) errors.finalidad = 'La finalidad es obligatoria.';
  if (!d.base_legal?.trim()) errors.base_legal = 'La base legal es obligatoria.';
  if (d.base_legal === 'Interés legítimo') {
    const total = [d._testIL?.paso1, d._testIL?.paso2, d._testIL?.paso3].join(' ').trim();
    if (!total) {
      errors._testIL = 'Complete los 3 pasos del test de interés legítimo.';
    } else if (total.length < MIN_TEST_IL) {
      errors._testIL = `El test debe tener al menos ${MIN_TEST_IL} caracteres (actual: ${total.length}).`;
    }
  }
  return { errors, isValid: Object.keys(errors).length === 0 };
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
  return { errors, isValid: Object.keys(errors).length === 0 };
}

/** Hook que retorna la validación del paso actual */
export function useStepValidation(step: number, data: RATWizardData): StepValidation {
  return useMemo(() => {
    switch (step) {
      case 1: return validateStep1(data);
      case 2: return validateStep2(data);
      case 3: return validateStep3(data);
      case 4: return validateStep4(data);
      default: return { errors: {}, isValid: true };
    }
  }, [step, data]);
}