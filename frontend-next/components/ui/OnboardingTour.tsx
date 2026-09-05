'use client';

import { useEffect, useState } from 'react';

interface OnboardingTourProps {
  open: boolean;
  onClose: () => void;
  steps: Array<{ title: string; description: string; icon?: string }>;
  /** Key en localStorage para no mostrar de nuevo */
  storageKey: string;
}

export default function OnboardingTour({ open, onClose, steps, storageKey }: OnboardingTourProps) {
  const [step, setStep] = useState(0);
  const current = steps[step];

  useEffect(() => {
    if (open) {
      setStep(0);
    }
  }, [open]);

  // Cerrar con ESC
  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, onClose]);

  function handleClose(dismiss = true) {
    if (dismiss) {
      try { localStorage.setItem(storageKey, '1'); } catch {}
    }
    onClose();
  }

  function next() {
    if (step < steps.length - 1) setStep(s => s + 1);
    else handleClose(true);
  }

  function prev() {
    if (step > 0) setStep(s => s - 1);
  }

  if (!open || !current) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
      aria-describedby="onboarding-description"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}
      onClick={e => { if (e.target === e.currentTarget) handleClose(false); }}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
        style={{ border: '1px solid #E5E7EB' }}
      >
        {/* Header gradiente */}
        <div
          className="px-6 pt-6 pb-5"
          style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}
        >
          <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: 'rgba(255,255,255,0.7)' }}>
            Paso {step + 1} de {steps.length}
          </p>
          <h2 id="onboarding-title" className="text-xl font-bold text-white flex items-center gap-2">
            {current.icon && <span aria-hidden="true">{current.icon}</span>}
            {current.title}
          </h2>
        </div>

        {/* Body */}
        <div className="px-6 py-5">
          <p id="onboarding-description" className="text-sm leading-relaxed whitespace-pre-line" style={{ color: '#374151' }}>
            {current.description}
          </p>
        </div>

        {/* Indicadores */}
        <div className="px-6 pb-3 flex items-center gap-1.5">
          {steps.map((_, i) => (
            <div
              key={i}
              className="h-1 rounded-full flex-1 transition-all"
              style={{ background: i === step ? '#2563EB' : '#E5E7EB' }}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 pb-5 flex items-center justify-between gap-2">
          <button
            type="button"
            onClick={() => handleClose(false)}
            className="text-xs font-medium underline"
            style={{ color: '#6B7280' }}
          >
            No volver a mostrar
          </button>
          <div className="flex items-center gap-2">
            {step > 0 && (
              <button
                type="button"
                onClick={prev}
                className="px-3 py-1.5 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                ← Atrás
              </button>
            )}
            <button
              type="button"
              onClick={next}
              autoFocus
              className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white transition"
              style={{ background: '#2563EB' }}
            >
              {step < steps.length - 1 ? 'Siguiente →' : '✓ Empezar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}