import React from 'react';

interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
  height?: number;
}

export function Skeleton({ className = '', style = {}, height }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded ${className}`}
      style={{ background: '#E5E7EB', ...(height ? { height } : {}), ...style }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
      <div className="flex items-center gap-3 mb-4">
        <Skeleton className="w-10 h-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton height={14} className="w-3/4 rounded" />
          <Skeleton height={10} className="w-1/2 rounded" />
        </div>
      </div>
      <Skeleton height={40} className="w-full rounded-lg mb-3" />
      <Skeleton height={12} className="w-2/3 rounded" />
    </div>
  );
}

export function SkeletonTableRow() {
  return (
    <div
      className="grid items-center px-5 py-3.5"
      style={{ gridTemplateColumns: '3fr 2fr 1.5fr 1fr 120px 80px', borderTop: '1px solid #F3F4F6' }}
    >
      <div className="space-y-1.5">
        <Skeleton height={14} className="w-3/4 rounded" />
        <Skeleton height={10} className="w-1/3 rounded" />
      </div>
      <Skeleton height={12} className="w-full rounded" />
      <Skeleton height={12} className="w-3/4 rounded" />
      <Skeleton height={20} className="w-16 rounded-full" />
      <Skeleton height={8} className="w-full rounded" />
      <Skeleton height={20} className="w-12 rounded" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
      <div
        className="grid text-xs font-semibold uppercase tracking-wide px-5 py-3"
        style={{ gridTemplateColumns: '3fr 2fr 1.5fr 1fr 120px 80px', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}
      >
        {['Proceso', 'Categoría de datos', 'Base legal', 'Estado', 'Completitud', 'Riesgo'].map((h, i) => (
          <Skeleton key={i} height={10} className="w-3/4 rounded" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => <SkeletonTableRow key={i} />)}
    </div>
  );
}

export function SkeletonKPIGrid({ cols = 4 }: { cols?: number }) {
  return (
    <div className={`grid gap-4 grid-cols-${cols}`}>
      {Array.from({ length: cols }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  );
}

export function SkeletonList({ items = 4 }: { items?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl p-5 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
          <div className="flex items-start justify-between mb-3">
            <div className="space-y-1.5 flex-1">
              <Skeleton height={14} className="w-2/3 rounded" />
              <Skeleton height={10} className="w-1/3 rounded" />
            </div>
            <Skeleton height={24} className="w-20 rounded-full" />
          </div>
          <Skeleton height={12} className="w-full rounded mb-2" />
          <Skeleton height={12} className="w-3/4 rounded" />
        </div>
      ))}
    </div>
  );
}