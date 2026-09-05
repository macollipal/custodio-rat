'use client';

export function SectionHeader({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color: '#6B7280', letterSpacing: '0.08em' }}>
        ▸ {label}
      </span>
      <div className="flex-1 h-px" style={{ background: '#E5E7EB' }} />
    </div>
  );
}
