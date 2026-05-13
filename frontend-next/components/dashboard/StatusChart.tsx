'use client';

interface StatusChartProps {
  data: Record<string, number>;
}

const COLORS: Record<string, string> = {
  borrador:    '#D97706',
  completo:    '#059669',
  en_revision: '#2563EB',
  aprobado:    '#7C3AED',
};

export default function StatusChart({ data }: StatusChartProps) {
  const entries = Object.entries(data).filter(([, v]) => v > 0);
  if (entries.length === 0) {
    return (
      <p className="text-center py-10 text-sm" style={{ color: '#9CA3AF' }}>
        Sin datos aún
      </p>
    );
  }

  const maxVal = Math.max(...entries.map(([, v]) => v));
  const barH = 160;
  const barW = 48;
  const gap = 24;
  const svgW = entries.length * (barW + gap);

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg width={svgW} height={barH + 40} style={{ display: 'block', margin: '0 auto' }}>
        {entries.map(([key, val], i) => {
          const h = maxVal > 0 ? Math.max(4, (val / maxVal) * barH) : 4;
          const x = i * (barW + gap);
          const y = barH - h;
          const color = COLORS[key] ?? '#6B7280';
          const label = key.replace('_', ' ');
          return (
            <g key={key}>
              <rect x={x} y={y} width={barW} height={h} rx={4} fill={color} opacity={0.85} />
              <text x={x + barW / 2} y={y - 6} textAnchor="middle" fontSize={11} fill={color} fontWeight={600}>
                {val}
              </text>
              <text x={x + barW / 2} y={barH + 16} textAnchor="middle" fontSize={10} fill="#6B7280">
                {label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
