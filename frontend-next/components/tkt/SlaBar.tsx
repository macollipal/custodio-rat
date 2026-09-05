'use client';

interface SlaBarProps {
  cumplimiento: number;
}

export function SlaBar({ cumplimiento }: SlaBarProps) {
  const color = cumplimiento >= 80 ? '#059669' : cumplimiento >= 50 ? '#D97706' : '#DC2626';
  return (
    <div className="rounded-xl p-4" style={{ background: 'white', border: '1px solid #E5E7EB' }}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-medium" style={{ color: '#6B7280' }}>Cumplimiento SLA</p>
        <p className="text-sm font-bold" style={{ color }}>{cumplimiento}%</p>
      </div>
      <div className="w-full h-2 rounded-full" style={{ background: '#E5E7EB' }}>
        <div
          className="h-2 rounded-full transition-all"
          style={{ width: `${cumplimiento}%`, background: color }}
        />
      </div>
    </div>
  );
}
