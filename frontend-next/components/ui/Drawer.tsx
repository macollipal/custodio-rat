'use client';

import { useEffect, useRef } from 'react';

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  width?: string;
  extraAction?: React.ReactNode;
}

export default function Drawer({ open, onClose, title, children, width = '640px', extraAction }: DrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
      const firstFocusable = drawerRef.current?.querySelector<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      firstFocusable?.focus();
    } else {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }
    return () => {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    };
  }, [open]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape' && open) {
        onClose();
      }
      if (open && e.key === 'Tab') {
        const focusable = drawerRef.current?.querySelectorAll<HTMLElement>('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (!focusable || focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start sm:items-center justify-center p-2 sm:p-6" onClick={onClose}>
      <div
        className="absolute inset-0 bg-black/40 sm:backdrop-blur-sm"
        style={{ animation: 'fadeIn 0.2s ease' }}
      />
      <div
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'drawer-title' : undefined}
        aria-label={title ? undefined : 'Diálogo'}
        className="relative flex flex-col shadow-2xl overflow-hidden rounded-2xl w-[95vw] max-w-[640px] sm:w-[60vw]"
        style={{
          maxHeight: '90vh',
          background: 'white',
          animation: 'scaleIn 0.2s ease',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div
          className="flex items-center justify-between px-6 py-4 flex-shrink-0 rounded-t-2xl"
          style={{ borderBottom: '1px solid #E5E7EB', background: '#F9FAFB' }}
        >
          <div className="flex items-center gap-3">
            {title ? <h2 id="drawer-title" className="text-base font-semibold" style={{ color: '#111827' }}>{title}</h2> : <div id="drawer-title" />}
            {extraAction}
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition hover:bg-gray-200 text-sm font-bold"
            style={{ color: '#6B7280' }}
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 sm:p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
