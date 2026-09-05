interface FieldProps {
  label: string;
  value?: string | null;
}

export function Field({ label, value }: FieldProps) {
  const isEmpty = !value || value.trim() === '';
  return (
    <div className="flex flex-col gap-1 p-2 sm:p-3 rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #F3F4F6' }}>
      <span className="text-xs font-semibold" style={{ color: '#6B7280' }}>{label}</span>
      <span className="text-sm break-words" style={{ color: isEmpty ? '#9CA3AF' : '#111827' }}>{isEmpty ? <em style={{ color: '#DC2626' }}>** {label}</em> : value}</span>
    </div>
  );
}
