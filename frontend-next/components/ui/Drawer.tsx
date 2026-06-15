'use client';

import { useEffect, useRef } from 'react';

export type DrawerSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

const SIZE_CLASSES: Record<DrawerSize, string> = {
  sm:    'w-[95vw] max-w-[400px] sm:w-[40vw]',
  md:    'w-[95vw] max-w-[540px] sm:w-[50vw]',
  lg:    'w-[95vw] max-w-[720px] sm:w-[65vw]',
  xl:    'w-[95vw] max-w-[900px] sm:w-[80vw]',
  full:  'w-[100vw] max-w-[100vw] sm:w-[100vw] rounded-none',
};

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  extraAction?: React.ReactNode;
  size?: DrawerSize;
}

export default function Drawer({
  open,
  onClose,
  title,
  children,
  extraAction,
  size = 'md',
}: DrawerProps) {
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = `${scrollbarWidth}px`;
      const firstFocusable = drawerRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
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
        const focusable = drawerRef.current?.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
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

  const hasHeader = !!(title || extraAction);
  const widthClass = SIZE_CLASSES[size];

  return (
    <div
      className="fixed inset-0 z-50 flex items-start sm:items-center justify-center p-2 sm:p-4 lg:p-6"
      onClick={onClose}
    >
      <div
        className="absolute inset-0 bg-black/40 sm:backdrop-blur-sm"
        style={{ animation: 'fadeIn 0.2s ease' }}
      />
      <div
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'drawer-title' : undefined}
        aria-label={title || 'Diálogo'}
        className={`relative flex flex-col shadow-2xl overflow-hidden ${widthClass}`}
        style={{
          maxHeight: '92vh',
          background: 'white',
          animation: 'scaleIn 0.2s ease',
        }}
        onClick={e => e.stopPropagation()}
      >
        {hasHeader && (
          <div
            className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 flex-shrink-0"
            style={{ borderBottom: '1px solid #E5E7EB', background: '#F9FAFB' }}
          >
            <div className="flex items-center gap-3 min-w-0">
              {title ? (
                <h2 id="drawer-title" className="text-sm sm:text-base font-semibold truncate" style={{ color: '#111827' }}>
                  {title}
                </h2>
              ) : (
                <div id="drawer-title" />
              )}
              {extraAction}
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg flex items-center justify-center transition hover:bg-gray-200 text-sm font-bold flex-shrink-0"
              style={{ color: '#6B7280' }}
              aria-label="Cerrar"
            >
              ✕
            </button>
          </div>
        )}
        <div className={`flex-1 overflow-y-auto ${hasHeader ? 'p-3 sm:p-5 lg:p-6' : 'p-4 sm:p-5 lg:p-6'}`}>
          {children}
        </div>
      </div>
    </div>
  );
}
