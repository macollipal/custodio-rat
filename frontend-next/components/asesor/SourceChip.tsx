'use client';

import { useState } from 'react';
import type { AsesorSource } from '@/lib/asesor-api';

interface SourceChipProps {
  source: AsesorSource;
  onClick?: (source: AsesorSource) => void;
}

export default function SourceChip({ source, onClick }: SourceChipProps) {
  const [hover, setHover] = useState(false);
  const filename = source.source.split(/[\\\/]/).pop() || source.source;
  const pct = Math.round(source.score * 100);
  return (
    <button
      type="button"
      onClick={() => onClick?.(source)}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all"
      style={{
        background: hover ? '#0D4F3C' : '#EAF5EF',
        color: hover ? '#FFFFFF' : '#0D4F3C',
        border: '1px solid #0D4F3C',
      }}
      title={`${filename} — score: ${source.score} (${pct}%)`}
    >
      <span aria-hidden="true">📄</span>
      <span className="max-w-[160px] truncate">{filename}</span>
      <span
        className="px-1.5 py-0.5 rounded-full text-[10px] font-bold"
        style={{ background: hover ? 'rgba(255,255,255,0.2)' : '#C8A951', color: hover ? '#FFFFFF' : '#0D4F3C' }}
      >
        {pct}%
      </span>
    </button>
  );
}
