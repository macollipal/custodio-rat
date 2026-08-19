// lib/styles.ts — Design System centralizado Custodio RAT
// Single source of truth para todos los estilos de formularios, modales, drawers y botones.
// Última actualización: 2026-07-02 (Track Fases 1-3)

// ── Inputs / Textareas / Selects ───────────────────────────────────────────
export const inputCls =
  'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition';

export const inputStyle: React.CSSProperties = {
  borderColor: '#D1D5DB',
  backgroundColor: '#FFFFFF',
  color: '#111827',
};

export const selectCls =
  'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition appearance-none bg-white';

export const textareaCls = inputCls;

// ── Labels ────────────────────────────────────────────────────────────────
export const labelCls = 'block text-sm font-medium mb-1.5';

export const labelStyle: React.CSSProperties = { color: '#374151' };

// ── Botones ───────────────────────────────────────────────────────────────
export const btnPrimaryCls =
  'px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50';

export const btnPrimaryStyle: React.CSSProperties = { background: '#2563EB' };

export const btnSecondaryCls =
  'px-5 py-2.5 rounded-lg text-sm font-medium border transition hover:bg-gray-50';

export const btnSecondaryStyle: React.CSSProperties = {
  color: '#6B7280',
  borderColor: '#E5E7EB',
};

export const btnDangerCls =
  'px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50';

export const btnDangerStyle: React.CSSProperties = { background: '#DC2626' };

export const btnSuccessCls =
  'px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50';

export const btnSuccessStyle: React.CSSProperties = { background: '#059669' };

export const btnWarningCls =
  'px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50';

export const btnWarningStyle: React.CSSProperties = { background: '#D97706' };

// Botones compactos (para tablas, listas, headers)
export const btnCompactPrimaryCls =
  'px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition disabled:opacity-50';

export const btnCompactSecondaryCls =
  'px-3 py-1.5 rounded-lg text-xs font-medium border transition hover:bg-gray-50';

// ── Paneles coloreados por sección ────────────────────────────────────────
export const panelStyles: Record<string, React.CSSProperties> = {
  gray: { background: '#F9FAFB', border: '1px solid #E5E7EB' },
  blue: { background: '#EFF6FF', border: '1px solid #BFDBFE' },
  red: { background: '#FEF2F2', border: '1px solid #FECACA' },
  green: { background: '#F0FDF4', border: '1px solid #BBF7D0' },
  amber: { background: '#FEF3C7', border: '1px solid #FCD34D' },
  purple: { background: '#FAF5FF', border: '1px solid #E9D5FF' },
};

export const panelTitleStyles: Record<string, React.CSSProperties> = {
  gray: { color: '#374151' },
  blue: { color: '#1E40AF' },
  red: { color: '#B91C1C' },
  green: { color: '#065F46' },
  amber: { color: '#92400E' },
  purple: { color: '#6B21A8' },
};

export const panelWrapperCls = 'rounded-xl p-5 space-y-4';

// ── Headers de modal/drawer con gradiente ─────────────────────────────────
export const modalHeaderStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)',
};

export const modalHeaderCls = 'rounded-t-xl px-6 py-4';

// ── Layout helpers ────────────────────────────────────────────────────────
export const modalContentCls = 'p-6 space-y-5';

export const formFooterCls =
  'flex flex-col sm:flex-row gap-3 justify-between pt-2';

// ── Grid responsive ───────────────────────────────────────────────────────
export const gridResponsive1to2 = 'grid grid-cols-1 sm:grid-cols-2 gap-4';
export const gridResponsive1to3 = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4';

// ── Badges base ───────────────────────────────────────────────────────────
export const badgeBaseCls = 'px-2 py-0.5 rounded text-xs font-medium';

// ── Alertas ───────────────────────────────────────────────────────────────
export const alertInfoStyle: React.CSSProperties = {
  background: '#EFF6FF',
  border: '1px solid #BFDBFE',
};

export const alertWarningStyle: React.CSSProperties = {
  background: '#FEF3C7',
  border: '1px solid #FCD34D',
};

export const alertErrorStyle: React.CSSProperties = {
  background: '#FEE2E2',
  border: '1px solid #FCA5A5',
};

export const alertSuccessStyle: React.CSSProperties = {
  background: '#D1FAE5',
  border: '1px solid #6EE7B7',
};

// ── Tablas ────────────────────────────────────────────────────────────────
export const tableHeaderStyle: React.CSSProperties = {
  background: '#F9FAFB',
};

export const tableBorderStyle: React.CSSProperties = {
  borderColor: '#E5E7EB',
};

// ── Cards ─────────────────────────────────────────────────────────────────
export const cardCls =
  'rounded-xl overflow-hidden';

export const cardBorderStyle: React.CSSProperties = {
  border: '1px solid #E5E7EB',
};

// ── KPI Cards ─────────────────────────────────────────────────────────────
export const kpiCardCls =
  'p-4 rounded-lg';

// ── Drawer ────────────────────────────────────────────────────────────────
export const drawerCls = 'w-[95vw] max-w-[640px] sm:w-[60vw]';

// ── Helper: combinar className con cls por defecto ────────────────────────
export function cx(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ');
}