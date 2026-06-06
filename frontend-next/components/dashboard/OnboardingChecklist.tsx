'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApp } from '@/context/AppContext';
import { CheckCircle2, Circle, X } from 'lucide-react';

interface ChecklistItem {
  key: string;
  label: string;
  done: boolean;
  cta: string;
  href: string;
}

interface OnboardingChecklistProps {
  ratsCount: number;
  hasDpo: boolean;
  hasContratoEncargado: boolean;
  hasBrechaRegistrada: boolean;
  hasPoliticaTransparencia: boolean;
}

export default function OnboardingChecklist({
  ratsCount,
  hasDpo,
  hasContratoEncargado,
  hasBrechaRegistrada,
  hasPoliticaTransparencia,
}: OnboardingChecklistProps) {
  const router = useRouter();
  const { company } = useApp();
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  const items: ChecklistItem[] = [
    {
      key: 'empresa',
      label: 'Empresa creada',
      done: !!company,
      cta: 'Editar',
      href: '/companies',
    },
    {
      key: 'dpo',
      label: 'DPO definido (nombre + email)',
      done: hasDpo,
      cta: 'Definir',
      href: '/companies',
    },
    {
      key: 'primer_rat',
      label: 'Primer RAT creado',
      done: ratsCount > 0,
      cta: 'Crear RAT',
      href: '/rat',
    },
    {
      key: 'contrato_encargado',
      label: 'Contrato de encargado formalizado (si aplica)',
      done: hasContratoEncargado,
      cta: 'Crear contrato',
      href: '/encargados-contrato',
    },
    {
      key: 'politica',
      label: 'Política de transparencia publicada',
      done: hasPoliticaTransparencia,
      cta: 'Publicar',
      href: '/transparencia',
    },
    {
      key: 'brecha',
      label: 'Procedimiento de brechas revisado',
      done: hasBrechaRegistrada,
      cta: 'Revisar',
      href: '/breaches',
    },
  ];

  const done = items.filter(i => i.done).length;
  const total = items.length;
  const pct = Math.round((done / total) * 100);
  const allDone = done === total;

  if (allDone) return null;

  return (
    <div
      className="rounded-2xl p-5 mb-6"
      style={{
        background: 'white',
        border: '1px solid #E5E7EB',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
      }}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="text-base font-bold" style={{ color: '#111827' }}>
            Primeros pasos
          </h3>
          <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>
            Completa estos pasos para alinear tu empresa con la Ley 21.719.
          </p>
        </div>
        <button
          onClick={() => setDismissed(true)}
          aria-label="Cerrar checklist"
          className="p-1 rounded hover:bg-gray-100 transition"
          style={{ color: '#9CA3AF' }}
        >
          <X size={16} />
        </button>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-semibold" style={{ color: '#374151' }}>
            {done} de {total} completados
          </span>
          <span className="text-xs font-bold" style={{ color: '#2563EB' }}>{pct}%</span>
        </div>
        <div
          className="h-2 rounded-full overflow-hidden"
          style={{ background: '#E5E7EB' }}
        >
          <div
            className="h-full transition-all"
            style={{
              width: `${pct}%`,
              background: pct === 100 ? '#059669' : '#2563EB',
            }}
          />
        </div>
      </div>

      <ul className="space-y-1.5">
        {items.map(item => (
          <li
            key={item.key}
            className="flex items-center gap-3 px-2 py-1.5 rounded-lg"
            style={{ background: item.done ? '#F0FDF4' : 'transparent' }}
          >
            {item.done ? (
              <CheckCircle2 size={18} style={{ color: '#059669', flexShrink: 0 }} />
            ) : (
              <Circle size={18} style={{ color: '#D1D5DB', flexShrink: 0 }} />
            )}
            <span
              className="text-sm flex-1"
              style={{
                color: item.done ? '#6B7280' : '#111827',
                textDecoration: item.done ? 'line-through' : 'none',
              }}
            >
              {item.label}
            </span>
            {!item.done && (
              <button
                onClick={() => router.push(item.href)}
                className="text-xs font-semibold px-2.5 py-1 rounded-md transition"
                style={{ color: '#2563EB', background: '#EFF6FF' }}
              >
                {item.cta}
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
