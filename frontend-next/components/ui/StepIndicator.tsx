'use client';

interface StepIndicatorProps {
  steps: string[];
  current: number;
}

export default function StepIndicator({ steps, current }: StepIndicatorProps) {
  const total = steps.length;
  const pct = total > 0 ? Math.round(((current - 1) / total) * 100) : 0;
  const currentLabel = steps[current - 1] || '';

  return (
    <div className="mb-6">
      {/* Mobile: solo numeritos en círculos + label del paso actual + barra de progreso */}
      <div className="sm:hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium" style={{ color: '#2563EB' }}>
            Paso {current} de {total}
          </span>
          <span className="text-xs font-bold" style={{ color: '#2563EB' }}>{pct}%</span>
        </div>
        <div className="h-1.5 rounded-full mb-2" style={{ background: '#E5E7EB' }}>
          <div
            className="h-1.5 rounded-full transition-all"
            style={{ width: `${pct}%`, background: '#2563EB' }}
          />
        </div>
        <div className="flex items-center gap-1.5">
          {steps.map((s, i) => {
            const stepNum = i + 1;
            const done = stepNum < current;
            const active = stepNum === current;
            return (
              <div
                key={s}
                aria-current={active ? 'step' : undefined}
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                style={{
                  background: active ? '#2563EB' : done ? '#059669' : '#E5E7EB',
                  color: active || done ? 'white' : '#9CA3AF',
                }}
              >
                {done ? '✓' : stepNum}
              </div>
            );
          })}
        </div>
        <p className="text-sm font-semibold mt-2" style={{ color: '#111827' }}>
          {currentLabel}
        </p>
      </div>

      {/* Desktop: layout original con labels inline */}
      <div className="hidden sm:flex items-center gap-0 overflow-x-auto pb-1">
        {steps.map((s, i) => {
          const stepNum = i + 1;
          const done = stepNum < current;
          const active = stepNum === current;
          return (
            <div key={s} className="flex items-center flex-shrink-0">
              <div
                aria-current={active ? 'step' : undefined}
                className="flex items-center gap-2"
              >
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                  style={{
                    background: active ? '#2563EB' : done ? '#059669' : '#E5E7EB',
                    color: active || done ? 'white' : '#9CA3AF',
                  }}
                >
                  {done ? '✓' : stepNum}
                </div>
                <span
                  className="text-xs font-medium whitespace-nowrap"
                  style={{ color: active ? '#2563EB' : done ? '#059669' : '#9CA3AF' }}
                >
                  {s}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className="h-px mx-2 w-8 flex-shrink-0" style={{ background: done ? '#059669' : '#E5E7EB' }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}