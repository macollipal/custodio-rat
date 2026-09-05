'use client';

interface CategoryChipsProps {
  /** Lista separada por comas almacenada como string */
  value: string;
  /** Callback cuando se actualiza la lista */
  onChange: (newValue: string) => void;
  /** Chips predefinidos que se muestran como sugerencias */
  suggestions: string[];
  /** Texto placeholder del input */
  placeholder?: string;
  /** Label del input (mantener accesibilidad) */
  ariaLabel?: string;
  /** ID del input (asociado al FormField) */
  id?: string;
  /** Si está en estado de error */
  hasError?: boolean;
}

/**
 * Componente que muestra un campo de texto combinado con chips clickeables.
 * Las sugerencias son chips clickeables; el usuario puede tipear custom y separar con comas.
 *
 * Convención de almacenamiento: las categorías se guardan como string separado por comas
 * dentro del campo correspondiente.
 */
export default function CategoryChips({
  value,
  onChange,
  suggestions,
  placeholder,
  ariaLabel,
  id,
  hasError,
}: CategoryChipsProps) {
  // Parsear valor actual a lista
  const items = (value ?? '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);

  function toggle(item: string) {
    const has = items.includes(item);
    const next = has ? items.filter(i => i !== item) : [...items, item];
    onChange(next.join(', '));
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5">
        {suggestions.map(s => {
          const active = items.includes(s);
          return (
            <button
              key={s}
              type="button"
              onClick={() => toggle(s)}
              aria-pressed={active}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border transition hover:shadow-sm"
              style={{
                background: active ? '#2563EB' : 'white',
                color: active ? 'white' : '#374151',
                borderColor: active ? '#2563EB' : '#D1D5DB',
              }}
            >
              {active && <span aria-hidden="true">✓</span>}
              {s}
            </button>
          );
        })}
      </div>
      <input
        type="text"
        id={id}
        value={value ?? ''}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={ariaLabel}
        aria-invalid={hasError}
        className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
        style={{ borderColor: hasError ? '#DC2626' : '#D1D5DB', backgroundColor: '#FFFFFF' }}
      />
      {items.length > 0 && (
        <p className="text-xs" style={{ color: '#6B7280' }}>
          {items.length} categoría{items.length === 1 ? '' : 's'} seleccionada{items.length === 1 ? '' : 's'}
        </p>
      )}
    </div>
  );
}