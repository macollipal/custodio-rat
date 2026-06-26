'use client';

interface ReadOnlyChipsProps {
  /** Lista separada por comas */
  value: string | null | undefined;
}

/**
 * Versión read-only de CategoryChips para vistas de detalle.
 * Muestra los items como chips no interactivos.
 */
export default function ReadOnlyChips({ value }: ReadOnlyChipsProps) {
  const items = (value ?? '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);

  if (items.length === 0) return <span style={{ color: '#9CA3AF' }}>—</span>;

  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item, i) => (
        <span
          key={`${item}-${i}`}
          className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
          style={{
            background: '#EFF6FF',
            color: '#1E40AF',
            border: '1px solid #BFDBFE',
          }}
        >
          {item}
        </span>
      ))}
    </div>
  );
}