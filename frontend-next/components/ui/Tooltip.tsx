'use client';

import { useState, useRef, useEffect } from 'react';

interface TooltipProps {
  text: string;
  children?: React.ReactNode;
}

/**
 * Tooltip accesible con hover + focus.
 * Se muestra con un delay de 200ms para no ser intrusivo.
 */
export default function Tooltip({ text, children }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [pos, setPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const ref = useRef<HTMLSpanElement>(null);

  function show() {
    timer.current = setTimeout(() => {
      if (ref.current) {
        const rect = ref.current.getBoundingClientRect();
        setPos({
          top: rect.bottom + window.scrollY + 6,
          left: rect.left + window.scrollX,
        });
      }
      setVisible(true);
    }, 200);
  }

  function hide() {
    if (timer.current) clearTimeout(timer.current);
    setVisible(false);
  }

  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  return (
    <span
      ref={ref}
      className="inline-flex items-center"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
      tabIndex={0}
      role="button"
      aria-label={text}
    >
      {children ?? (
        <span
          className="inline-flex items-center justify-center w-4 h-4 rounded-full text-xs cursor-help"
          style={{ backgroundColor: '#E5E7EB', color: '#6B7280' }}
          aria-hidden="true"
        >
          ?
        </span>
      )}
      {visible && (
        <span
          role="tooltip"
          className="fixed z-50 max-w-xs px-3 py-2 rounded-lg text-xs leading-relaxed shadow-lg pointer-events-none"
          style={{
            top: pos.top,
            left: pos.left,
            backgroundColor: '#111827',
            color: 'white',
          }}
        >
          {text}
        </span>
      )}
    </span>
  );
}