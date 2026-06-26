'use client';

import { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
  /** ID del input para asociar label/htmlFor/error via aria-describedby */
  htmlFor: string;
  children: ReactNode;
  /** Asterisco visual para campos obligatorios */
  requiredMark?: boolean;
}

export default function FormField({
  label,
  required,
  hint,
  error,
  htmlFor,
  children,
  requiredMark = true,
}: FormFieldProps) {
  const errorId = error ? `${htmlFor}-error` : undefined;
  const hintId = hint ? `${htmlFor}-hint` : undefined;
  const describedBy = [errorId, hintId].filter(Boolean).join(' ') || undefined;

  return (
    <div className="space-y-1.5">
      <label
        htmlFor={htmlFor}
        className="block text-sm font-medium"
        style={{ color: '#374151' }}
      >
        {label}
        {required && requiredMark && (
          <span aria-hidden="true" style={{ color: '#DC2626' }}> *</span>
        )}
      </label>
      {hint && (
        <p
          id={hintId}
          className="text-xs"
          style={{ color: '#9CA3AF' }}
        >
          {hint}
        </p>
      )}
      {/* Children receives aria-describedby via React.cloneElement? Better: pass it via props */}
      <div data-describedby={describedBy}>
        {children}
      </div>
      {error && (
        <p
          id={errorId}
          role="alert"
          className="text-xs flex items-center gap-1"
          style={{ color: '#DC2626' }}
        >
          <span aria-hidden="true">⚠</span>
          {error}
        </p>
      )}
    </div>
  );
}