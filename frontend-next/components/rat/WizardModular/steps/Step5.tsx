'use client';

import React from 'react';
import { toast } from 'sonner';
import type { RATWizardData } from '@/types';
import Spinner from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';

interface Step5Props {
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
}

export function Step5({
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
}: Step5Props) {
  function cambiarStep(n: number) {
    onPrev();
  }

  function guardar() {
    if (!data.plazo_retencion?.trim()) {
      toast.error('Vuelve al paso 4 y completa el plazo de retención.');
      return;
    }
    onNext();
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 5 · Compliance avanzado (Tier 1 + Tier 2)</h3>
        <p className="text-sm" style={{ color: '#6B7280' }}>Campos críticos y operativos del template ProBest para compliance total Ley 21.719.</p>
      </div>

      {/* Tier 2 — Operativos (ProBest template) */}
      <div className="rounded-lg p-4 space-y-4" style={{ border: '1px solid #E5E7EB' }}>
        <h4 className="text-sm font-bold" style={{ color: '#374151' }}>Tier 2 — Operativos (ProBest template)</h4>

        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={data.transferencia_nacional ?? false} onChange={e => setData(d => ({ ...d, transferencia_nacional: e.target.checked }))} className="mt-0.5 rounded" />
          <span className="text-sm font-medium" style={{ color: '#374151' }}>Existe transferencia de datos a nivel nacional (dentro de Chile)</span>
        </label>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Documentacion de clausulas</label>
            <textarea value={data.doc_clausulas ?? ''} onChange={e => setData(d => ({ ...d, doc_clausulas: e.target.value }))} rows={2} placeholder="Politica de privacidad, aviso de privacidad..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Medidas organizativas</label>
            <textarea value={data.medidas_organizativas ?? ''} onChange={e => setData(d => ({ ...d, medidas_organizativas: e.target.value }))} rows={2} placeholder="Designacion RAI, procedimientos de acceso..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Mecanismos de eliminación</label>
            <textarea value={data.mecanismos_eliminacion ?? ''} onChange={e => setData(d => ({ ...d, mecanismos_eliminacion: e.target.value }))} rows={2} placeholder="Borrado seguro NIST 800-88, destrucción física..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Técnica de anonimización</label>
            <input value={data.tecnica_anonimizacion ?? ''} onChange={e => setData(d => ({ ...d, tecnica_anonimizacion: e.target.value }))} placeholder="Pseudonimización, k-anonimidad..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Origen del dato (portabilidad)</label>
            <input value={data.origen_dato_portabilidad ?? ''} onChange={e => setData(d => ({ ...d, origen_dato_portabilidad: e.target.value }))} placeholder="Directamente del titular, de otro responsable..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fecha de levantamiento</label>
            <input type="date" value={data.fecha_levantamiento ?? ''} onChange={e => setData(d => ({ ...d, fecha_levantamiento: e.target.value }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-2">
        <Button variant="secondary" size="lg" onClick={() => cambiarStep(4)}>Anterior</Button>
        <Button
          variant="success"
          onClick={() => {
            if (!data.plazo_retencion?.trim()) {
              toast.error('Vuelve al paso 4 y completa el plazo de retención.');
              return;
            }
            onNext();
          }}
        >
          Guardar en el RAT
        </Button>
      </div>
    </div>
  );
}
