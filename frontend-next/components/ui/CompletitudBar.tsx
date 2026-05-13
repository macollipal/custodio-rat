export default function CompletitudBar({ pct }: { pct: number }) {
  const color =
    pct >= 75 ? '#059669' :
    pct >= 50 ? '#D97706' :
    '#DC2626';

  return (
    <div className="flex items-center gap-2 min-w-0">
      <div className="flex-1 h-1.5 rounded-full" style={{ background: '#E5E7EB', minWidth: 40 }}>
        <div
          className="h-1.5 rounded-full transition-all"
          style={{ width: `${Math.min(pct, 100)}%`, background: color }}
        />
      </div>
      <span className="text-xs font-medium flex-shrink-0" style={{ color, minWidth: 28 }}>
        {pct}%
      </span>
    </div>
  );
}
