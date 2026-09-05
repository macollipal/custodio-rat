export default function CompletitudBar({ pct }: { pct: number }) {
  // Colores WCAG AA-compliant (ratio >= 4.5:1 sobre fondo blanco)
  const color =
    pct >= 75 ? '#065F46' :
    pct >= 50 ? '#92400E' :
    '#991B1B';

  const bgColor =
    pct >= 75 ? '#10B981' :
    pct >= 50 ? '#F59E0B' :
    '#EF4444';

  return (
    <div
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Completitud del RAT: ${pct}%`}
      className="flex items-center gap-2 min-w-0"
    >
      <div className="flex-1 h-1.5 rounded-full" style={{ background: '#E5E7EB', minWidth: 40 }}>
        <div
          className="h-1.5 rounded-full transition-all"
          style={{ width: `${Math.min(pct, 100)}%`, background: bgColor }}
        />
      </div>
      <span className="text-xs font-bold flex-shrink-0 tabular-nums" style={{ color, minWidth: 32 }}>
        {pct}%
      </span>
    </div>
  );
}