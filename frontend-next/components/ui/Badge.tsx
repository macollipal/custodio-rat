import type { HTMLAttributes, ReactNode } from 'react';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'purple';
export type RatEstado = 'borrador' | 'completo' | 'en_revision' | 'aprobado';

interface CommonBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  icon?: ReactNode;
  children?: ReactNode;
}

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  success: 'bg-emerald-100 text-emerald-800',
  warning: 'bg-amber-100 text-amber-800',
  danger:  'bg-red-100 text-red-800',
  info:    'bg-blue-100 text-blue-800',
  neutral: 'bg-gray-100 text-gray-700',
  purple:  'bg-purple-100 text-purple-800',
};

const RAT_ESTADO_STYLES: Record<RatEstado, { bg: string; color: string; label: string }> = {
  borrador:    { bg: '#FEF3C7', color: '#92400E', label: 'Borrador' },
  completo:    { bg: '#D1FAE5', color: '#065F46', label: 'Completo' },
  en_revision: { bg: '#DBEAFE', color: '#1E3A8A', label: 'En revisión' },
  aprobado:    { bg: '#EDE9FE', color: '#4C1D95', label: 'Aprobado' },
};

interface GenericBadgeProps extends CommonBadgeProps {
  variant?: BadgeVariant;
  estado?: never;
}

interface EstadoBadgeProps extends CommonBadgeProps {
  estado: string;
  variant?: never;
}

type BadgeProps = GenericBadgeProps | EstadoBadgeProps;

export default function Badge(props: BadgeProps) {
  const { className = '', ...rest } = props;
  const { icon, children } = rest as CommonBadgeProps;

  if ('estado' in props && props.estado !== undefined) {
    const s = RAT_ESTADO_STYLES[props.estado as RatEstado] ?? {
      bg: '#F3F4F6', color: '#374151', label: props.estado,
    };
    return (
      <span
        role="status"
        aria-label={`Estado del RAT: ${s.label}`}
        className={['inline-flex px-2 py-0.5 rounded-full text-xs font-semibold', className].filter(Boolean).join(' ')}
        style={{ background: s.bg, color: s.color }}
      >
        {s.label}
      </span>
    );
  }

  const variant = (rest as GenericBadgeProps).variant ?? 'neutral';
  return (
    <span
      className={[
        'inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold',
        VARIANT_CLASSES[variant],
        className,
      ].filter(Boolean).join(' ')}
      {...(rest as HTMLAttributes<HTMLSpanElement>)}
    >
      {icon}
      {children}
    </span>
  );
}

export { VARIANT_CLASSES, RAT_ESTADO_STYLES };