'use client';

import { useState } from 'react';

interface KpiCardProps {
  label: string;
  value: number;
  color: string;
  icon: string;
}

export function KpiCard({ label, value, color, icon }: KpiCardProps) {
  return (
    <div
      className="rounded-xl p-3 flex items-center gap-2.5"
      style={{ background: 'white', border: '1px solid #E5E7EB' }}
    >
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center text-base flex-shrink-0"
        style={{ background: `${color}15` }}
      >
        <span style={{ color }}>{icon}</span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium truncate" style={{ color: '#6B7280' }}>{label}</p>
        <p className="text-base font-bold" style={{ color: '#111827' }}>{value}</p>
      </div>
    </div>
  );
}
