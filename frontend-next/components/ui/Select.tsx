'use client';

import { forwardRef, type SelectHTMLAttributes, type ReactNode } from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: string;
  hint?: string;
  error?: string;
  options?: SelectOption[];
  children?: ReactNode;
  fullWidth?: boolean;
  placeholder?: string;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  {
    label,
    hint,
    error,
    options,
    children,
    fullWidth = true,
    placeholder,
    id,
    className = '',
    required,
    ...rest
  },
  ref,
) {
  const selId = id || `sel-${Math.random().toString(36).slice(2, 9)}`;
  const describedBy = error ? `${selId}-err` : hint ? `${selId}-hint` : undefined;
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={selId}
          className="block text-sm font-medium mb-1.5"
          style={{ color: '#374151' }}
        >
          {label}{required && <span style={{ color: '#DC2626' }} className="ml-0.5">*</span>}
        </label>
      )}
      <select
        ref={ref}
        id={selId}
        required={required}
        aria-invalid={!!error || undefined}
        aria-describedby={describedBy}
        className={[
          'w-full px-3.5 py-2.5 rounded-lg text-sm border transition min-h-[44px]',
          'focus:outline-none focus:ring-2 focus:ring-blue-500',
          'disabled:opacity-60 disabled:cursor-not-allowed',
          error ? 'border-red-500' : 'border-gray-300',
          className,
        ].filter(Boolean).join(' ')}
        style={{
          backgroundColor: '#FFFFFF',
          color: '#111827',
        }}
        {...rest}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options?.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
        {children}
      </select>
      {error && (
        <p id={`${selId}-err`} className="text-xs mt-1" style={{ color: '#DC2626' }} role="alert">
          {error}
        </p>
      )}
      {!error && hint && (
        <p id={`${selId}-hint`} className="text-xs mt-1" style={{ color: '#6B7280' }}>
          {hint}
        </p>
      )}
    </div>
  );
});

export default Select;
export type { SelectProps, SelectOption };