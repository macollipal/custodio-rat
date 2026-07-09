import type { ReactNode } from 'react';

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger';

interface AlertProps {
  variant?: AlertVariant;
  title?: ReactNode;
  children: ReactNode;
  icon?: ReactNode;
  className?: string;
}

const VARIANT_STYLES: Record<AlertVariant, { bg: string; border: string; color: string; defaultIcon: string }> = {
  info:    { bg: '#EFF6FF', border: '#BFDBFE', color: '#1E3A8A', defaultIcon: 'ℹ️' },
  success: { bg: '#ECFDF5', border: '#A7F3D0', color: '#065F46', defaultIcon: '✓' },
  warning: { bg: '#FFFBEB', border: '#FCD34D', color: '#92400E', defaultIcon: '⚠️' },
  danger:  { bg: '#FEF2F2', border: '#FCA5A5', color: '#991B1B', defaultIcon: '🛑' },
};

export default function Alert({
  variant = 'info',
  title,
  children,
  icon,
  className = '',
}: AlertProps) {
  const s = VARIANT_STYLES[variant];
  const displayIcon = icon ?? s.defaultIcon;
  return (
    <div
      role={variant === 'danger' || variant === 'warning' ? 'alert' : 'status'}
      className={`rounded-lg p-3 flex items-start gap-2 ${className}`}
      style={{ background: s.bg, border: `1px solid ${s.border}`, color: s.color }}
    >
      {displayIcon && <span className="flex-shrink-0">{displayIcon}</span>}
      <div className="flex-1 text-sm">
        {title && <div className="font-semibold mb-0.5">{title}</div>}
        <div>{children}</div>
      </div>
    </div>
  );
}

export { VARIANT_STYLES };
export type { AlertProps };