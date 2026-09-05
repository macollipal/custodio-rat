'use client';

import { forwardRef, type TextareaHTMLAttributes } from 'react';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  fullWidth?: boolean;
  showCount?: boolean;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  {
    label,
    hint,
    error,
    fullWidth = true,
    showCount = false,
    id,
    className = '',
    required,
    value,
    maxLength,
    ...rest
  },
  ref,
) {
  const taId = id || `ta-${Math.random().toString(36).slice(2, 9)}`;
  const describedBy = error ? `${taId}-err` : hint ? `${taId}-hint` : undefined;
  const currentLength = typeof value === 'string' ? value.length : 0;
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={taId}
          className="block text-sm font-medium mb-1.5"
          style={{ color: '#374151' }}
        >
          {label}{required && <span style={{ color: '#DC2626' }} className="ml-0.5">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        id={taId}
        required={required}
        value={value}
        maxLength={maxLength}
        aria-invalid={!!error || undefined}
        aria-describedby={describedBy}
        className={[
          'w-full px-3.5 py-2.5 rounded-lg text-sm border transition',
          'focus:outline-none focus:ring-2 focus:ring-blue-500',
          'disabled:opacity-60 disabled:cursor-not-allowed',
          'resize-y',
          error ? 'border-red-500' : 'border-gray-300',
          className,
        ].filter(Boolean).join(' ')}
        style={{
          backgroundColor: '#FFFFFF',
          color: '#111827',
        }}
        {...rest}
      />
      <div className="flex justify-between mt-1">
        {error ? (
          <p id={`${taId}-err`} className="text-xs" style={{ color: '#DC2626' }} role="alert">
            {error}
          </p>
        ) : hint ? (
          <p id={`${taId}-hint`} className="text-xs" style={{ color: '#6B7280' }}>
            {hint}
          </p>
        ) : <span />}
        {showCount && maxLength && (
          <span className="text-xs" style={{ color: '#9CA3AF' }}>
            {currentLength}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
});

export default Textarea;
export type { TextareaProps };