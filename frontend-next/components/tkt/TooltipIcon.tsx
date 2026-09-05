'use client';

import { useState } from 'react';

export function TooltipIcon({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-flex ml-1">
      <button
        type="button"
        aria-label={`Ayuda: ${text}`}
        onClick={() => setOpen(o => !o)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold transition-colors"
        style={{ background: '#E5E7EB', color: '#6B7280' }}
      >
        ⓘ
      </button>
      {open && (
        <span
          role="tooltip"
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 w-56 px-2.5 py-2 rounded-lg text-xs text-white z-50 shadow-lg"
          style={{ background: '#1F2937' }}
        >
          {text}
        </span>
      )}
    </span>
  );
}
