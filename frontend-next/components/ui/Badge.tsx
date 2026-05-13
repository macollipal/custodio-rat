type Estado = 'borrador' | 'completo' | 'en_revision' | 'aprobado';

const BADGE_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  borrador:    { bg: '#FEF3C7', color: '#92400E', label: 'Borrador' },
  completo:    { bg: '#D1FAE5', color: '#065F46', label: 'Completo' },
  en_revision: { bg: '#DBEAFE', color: '#1E3A8A', label: 'En revisión' },
  aprobado:    { bg: '#EDE9FE', color: '#4C1D95', label: 'Aprobado' },
};

export default function Badge({ estado }: { estado: string }) {
  const s = BADGE_STYLES[estado] ?? { bg: '#F3F4F6', color: '#374151', label: estado };
  return (
    <span
      className="inline-flex px-2 py-0.5 rounded-full text-xs font-semibold"
      style={{ background: s.bg, color: s.color }}
    >
      {s.label}
    </span>
  );
}
