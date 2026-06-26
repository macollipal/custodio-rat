'use client';

import { useEffect, useRef, useState } from 'react';

interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary';
  /** Para variant="danger": el usuario debe tipear este texto para habilitar el botón de confirmación */
  requireTyping?: string;
}

export default function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  variant = 'primary',
  requireTyping,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const [typed, setTyped] = useState('');

  useEffect(() => {
    if (open) {
      setTyped('');
      document.body.style.overflow = 'hidden';
      const t = setTimeout(() => {
        const first = dialogRef.current?.querySelector<HTMLElement>('button, input');
        first?.focus();
      }, 50);
      return () => {
        clearTimeout(t);
        document.body.style.overflow = '';
      };
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        const focusables = dialogRef.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled])'
        );
        if (!focusables || focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, onClose]);

  if (!open) return null;

  const confirmEnabled = !requireTyping || typed === requireTyping;

  const confirmBg = variant === 'danger' ? '#DC2626' : '#2563EB';
  const confirmBgHover = variant === 'danger' ? '#B91C1C' : '#1D4ED8';

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-message"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        ref={dialogRef}
        className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6"
        style={{ border: '1px solid #E5E7EB' }}
      >
        <h2
          id="confirm-dialog-title"
          className="text-lg font-bold mb-2"
          style={{ color: '#111827' }}
        >
          {title}
        </h2>
        <p
          id="confirm-dialog-message"
          className="text-sm whitespace-pre-line mb-5"
          style={{ color: '#6B7280' }}
        >
          {message}
        </p>

        {requireTyping && (
          <div className="mb-4">
            <label
              htmlFor="confirm-typing"
              className="block text-xs font-medium mb-1.5"
              style={{ color: '#374151' }}
            >
              Escribe <code className="px-1 py-0.5 rounded text-xs font-mono" style={{ backgroundColor: '#F3F4F6' }}>{requireTyping}</code> para confirmar:
            </label>
            <input
              id="confirm-typing"
              type="text"
              value={typed}
              onChange={e => setTyped(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ borderColor: '#D1D5DB' }}
              autoComplete="off"
            />
          </div>
        )}

        <div className="flex gap-2 justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
            style={{ color: '#374151', borderColor: '#E5E7EB' }}
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={!confirmEnabled}
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50"
            style={{ backgroundColor: confirmEnabled ? confirmBg : '#9CA3AF' }}
            onMouseEnter={e => { if (confirmEnabled) e.currentTarget.style.backgroundColor = confirmBgHover; }}
            onMouseLeave={e => { if (confirmEnabled) e.currentTarget.style.backgroundColor = confirmBg; }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
