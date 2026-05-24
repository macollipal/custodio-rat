'use client';

import { useEffect } from 'react';

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  width?: string;
  extraAction?: React.ReactNode;
}

export default function Drawer({ open, onClose, title, children, width = '640px', extraAction }: DrawerProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" onClick={onClose}>
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        style={{ animation: 'fadeIn 0.2s ease' }}
      />
      <div
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
            <h2 className="text-base font-semibold" style={{ color: '#111827' }}>{title}</h2>
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
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
