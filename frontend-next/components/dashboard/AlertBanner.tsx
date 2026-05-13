type AlertType = 'success' | 'warning' | 'danger' | 'info';

interface AlertBannerProps {
  message: string;
  type: AlertType;
}

const STYLES: Record<AlertType, { bg: string; border: string; color: string }> = {
  success: { bg: '#D1FAE5', border: '#059669', color: '#065F46' },
  warning: { bg: '#FEF3C7', border: '#D97706', color: '#92400E' },
  danger:  { bg: '#FEE2E2', border: '#DC2626', color: '#7F1D1D' },
  info:    { bg: '#DBEAFE', border: '#2563EB', color: '#1E3A8A' },
};

export default function AlertBanner({ message, type }: AlertBannerProps) {
  const s = STYLES[type];
  return (
    <div
      className="rounded-lg px-4 py-3 text-sm mb-3"
      style={{ background: s.bg, borderLeft: `3px solid ${s.border}`, color: s.color }}
      dangerouslySetInnerHTML={{ __html: message }}
    />
  );
}

export function AlertCard({ title, value, type }: { title: string; value: number; type: AlertType }) {
  if (value <= 0) return null;
  const s = STYLES[type];
  return (
    <div
      className="rounded-lg px-4 py-3 flex items-center justify-between"
      style={{ background: s.bg, borderLeft: `3px solid ${s.border}`, color: s.color }}
    >
      <span className="text-sm font-medium">{title}</span>
      <span className="text-lg font-bold">{value}</span>
    </div>
  );
}
