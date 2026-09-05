import type { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  children?: ReactNode;
}

const PADDING_CLASSES = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-6',
};

const VARIANT_CLASSES = {
  default:  'bg-white shadow-sm',
  bordered: 'bg-white',
  elevated: 'bg-white shadow-md',
};

export default function Card({
  variant = 'default',
  padding = 'md',
  className = '',
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={[
        'rounded-xl',
        VARIANT_CLASSES[variant],
        PADDING_CLASSES[padding],
        variant !== 'bordered' ? '' : 'border border-gray-200',
        className,
      ].filter(Boolean).join(' ')}
      style={variant === 'default' || variant === 'elevated' ? { border: '1px solid #E5E7EB' } : undefined}
      {...rest}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
}

function CardHeader({ title, description, action, className = '', children }: CardHeaderProps) {
  return (
    <div className={`flex items-start justify-between gap-3 mb-4 ${className}`}>
      <div>
        {title && (
          <h3 className="text-base font-bold" style={{ color: '#111827' }}>{title}</h3>
        )}
        {description && (
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>{description}</p>
        )}
        {children}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}

export { CardHeader };
export type { CardProps, CardHeaderProps };