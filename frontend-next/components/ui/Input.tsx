'use client';

import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  {
    label,
    hint,
    error,
    iconLeft,
    iconRight,
    fullWidth = true,
    id,
    className = '',
    required,
    ...rest
  },
  ref,
) {
  const inputId = id || `inp-${Math.random().toString(36).slice(2, 9)}`;
  const describedBy = error ? `${inputId}-err` : hint ? `${inputId}-hint` : undefined;
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium mb-1.5"
          style={{ color: '#374151' }}
        >
          {label}{required && <span style={{ color: '#DC2626' }} className="ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        {iconLeft && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            {iconLeft}
          </span>
        )}
        <input
          ref={ref}
          id={inputId}
          required={required}
          aria-invalid={!!error || undefined}
          aria-describedby={describedBy}
          className={[
            'w-full px-3.5 py-2.5 rounded-lg text-sm border transition',
            'focus:outline-none focus:ring-2 focus:ring-blue-500',
            'disabled:opacity-60 disabled:cursor-not-allowed',
            error ? 'border-red-500' : 'border-gray-300',
            iconLeft ? 'pl-10' : '',
            iconRight ? 'pr-10' : '',
            className,
          ].filter(Boolean).join(' ')}
          style={{
            backgroundColor: '#FFFFFF',
            color: '#111827',
          }}
          {...rest}
        />
        {iconRight && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
            {iconRight}
          </span>
        )}
      </div>
      {error && (
        <p id={`${inputId}-err`} className="text-xs mt-1" style={{ color: '#DC2626' }} role="alert">
          {error}
        </p>
      )}
      {!error && hint && (
        <p id={`${inputId}-hint`} className="text-xs mt-1" style={{ color: '#6B7280' }}>
          {hint}
        </p>
      )}
    </div>
  );
});

export default Input;
export type { InputProps };