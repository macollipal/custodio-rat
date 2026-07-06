'use client';

import React from 'react';
import type { RATWizardData, RATSugerido } from '@/types';
import AlertBanner from '@/components/dashboard/AlertBanner';

interface Step0Props {
  data: RATWizardData;
  setData: React.Dispatch<React.SetStateAction<RATWizardData>>;
  validation: { errors: Record<string, string | undefined>; isValid: boolean; requiredCount: number; completedCount: number; firstErrorField?: string };
  stepIsValid: boolean;
  fieldErrors: Record<string, string | undefined>;
  inputCls: string;
  inputStyle: React.CSSProperties;
  onNext: () => void;
  onPrev: () => void;
  guardarDraft: () => void;
  mostrarPaso0: boolean;
  rubroNombre: string;
  sugerencias: RATSugerido[];
  usarSugerencia: (sug: RATSugerido) => void;
}

export function Step0({
  data,
  setData,
  validation,
  stepIsValid,
  fieldErrors,
  inputCls,
  inputStyle,
  onNext,
  onPrev,
  guardarDraft,
  mostrarPaso0,
  rubroNombre,
  sugerencias,
  usarSugerencia,
}: Step0Props) {
  function crearPersonalizado() {
    onNext();
  }

  if (!mostrarPaso0) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl p-5" style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>Rat sugeridos para tu rubro</p>
        <h3 className="text-lg font-bold text-white">{rubroNombre || '...'}</h3>
        <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.6)' }}>Selecciona un proceso predefinido o crea uno personalizado</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sugerencias.map(sug => (
          <div
            key={sug.id}
            className="rounded-xl p-4 cursor-pointer transition hover:shadow-md"
            style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}
            onClick={() => usarSugerencia(sug)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-semibold text-sm" style={{ color: '#111827' }}>{sug.nombre_proceso}</p>
                <p className="text-xs mt-1" style={{ color: '#6B7280' }}>{sug.categoria_datos}</p>
                {sug.categoria_titulares && (
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Titulares: {sug.categoria_titulares}</p>
                )}
                <div className="flex gap-1 flex-wrap mt-2">
                  {sug.datos_sensibles && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEF3C7', color: '#92400E' }}>⚠️ Datos sensibles</span>}
                  {sug.evaluacion_impacto && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#DBEAFE', color: '#1E3A8A' }}>📋 EIPD</span>}
                  {sug.decisiones_automatizadas && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#F3F4F6', color: '#374151' }}>🤖 Dec. auto</span>}
                </div>
              </div>
              <button
                className="ml-3 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition flex-shrink-0"
                style={{ background: '#2563EB' }}
                onClick={e => { e.stopPropagation(); usarSugerencia(sug); }}
              >
                Usar
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={crearPersonalizado}
          className="px-6 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
          style={{ color: '#374151', borderColor: '#E5E7EB' }}
        >
          + Crear proceso personalizado
        </button>
      </div>
    </div>
  );
}
