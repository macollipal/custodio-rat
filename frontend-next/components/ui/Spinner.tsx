'use client';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const sizes = { sm: 14, md: 18, lg: 24 };
  const px = sizes[size];
  return (
    <span
      role="status"
      aria-label="Cargando"
      className={`inline-block ${className}`}
      style={{
        width: px,
        height: px,
        border: '2px solid currentColor',
        borderRightColor: 'transparent',
        borderRadius: '50%',
        animation: 'spinner-spin 0.7s linear infinite',
      }}
    />
  );
}