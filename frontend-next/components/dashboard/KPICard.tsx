interface KPICardProps {
  title: string;
  value: string | number;
  subtitle: string;
  icon: string;
  color: string;
}

export default function KPICard({ title, value, subtitle, icon, color }: KPICardProps) {
  return (
    <div
      className="bg-white rounded-xl p-5 shadow-sm"
      style={{ border: '1px solid #E5E7EB' }}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#6B7280' }}>
          {title}
        </span>
        <span className="text-xl">{icon}</span>
      </div>
      <div className="text-2xl font-bold mb-1" style={{ color }}>
        {value}
      </div>
      <div className="text-xs" style={{ color: '#9CA3AF' }}>{subtitle}</div>
    </div>
  );
}
