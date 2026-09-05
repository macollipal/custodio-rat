'use client';

interface FieldLabelProps {
  label: string;
  required?: boolean;
  htmlFor?: string;
}

export function FieldLabel({ label, required, htmlFor }: FieldLabelProps) {
  return (
    <label htmlFor={htmlFor} className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
      {label}
      {required && <span style={{ color: '#DC2626' }}> *</span>}
    </label>
  );
}
