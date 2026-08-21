'use client';

import React from 'react';
import { toast } from 'sonner';
import type { RATWizardData } from '@/types';
import FormField from '@/components/ui/FormField';
import AlertBanner from '@/components/dashboard/AlertBanner';
import { Button } from '@/components/ui/Button';
import { useApp } from '@/context/AppContext';

interface Step3Props {
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
  onAplicarSugerencias: () => Promise<void>;
}

export function Step3({
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
  onAplicarSugerencias,
}: Step3Props) {
  const { baseLegalOptions, baseLegalDescripciones } = useApp();
  const opciones = baseLegalOptions.length > 0 ? baseLegalOptions : [];
  const DESCRIPCIONES_BASE = baseLegalDescripciones;

  function cambiarStep(n: number) {
    onNext();
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 3 · Finalidad y base legal</h3>
        <p className="text-sm mb-2" style={{ color: '#6B7280' }}>Por qué y con qué fundamento jurídico se tratan los datos.</p>
        {validation.requiredCount > 0 && (
          <p className="text-xs font-medium" style={{ color: validation.isValid ? '#059669' : '#DC2626' }}>
            {validation.completedCount} / {validation.requiredCount} obligatorios completos
          </p>
        )}
      </div>

      <FormField label="Finalidad del tratamiento" required htmlFor="rw-finalidad" error={fieldErrors.finalidad}>
        <textarea
          id="rw-finalidad"
          value={data.finalidad ?? ''}
          onChange={e => setData(d => ({ ...d, finalidad: e.target.value }))}
          rows={3}
          placeholder="Ej: Gestión de la relación comercial, liquidación de remuneraciones..."
          aria-required="true"
          aria-invalid={!!fieldErrors.finalidad}
          className={inputCls}
          style={{
            ...inputStyle,
            borderColor: fieldErrors.finalidad ? '#DC2626' : '#D1D5DB',
          }}
        />
      </FormField>

      <FormField
        label="Base legal del tratamiento"
        required
        htmlFor="rw-base_legal"
        hint="Art. 13 Ley 21.719"
        error={fieldErrors.base_legal}
      >
        <select
          id="rw-base_legal"
          value={data.base_legal ?? opciones[0]}
          onChange={e => setData(d => ({ ...d, base_legal: e.target.value }))}
          aria-required="true"
          aria-invalid={!!fieldErrors.base_legal}
          className={inputCls}
          style={{
            ...inputStyle,
            borderColor: fieldErrors.base_legal ? '#DC2626' : '#D1D5DB',
          }}
        >
          {opciones.map(b => <option key={b} value={b}>{b}</option>)}
        </select>
      </FormField>

      <div className="space-y-3">
        {data.base_legal && DESCRIPCIONES_BASE[data.base_legal] && (
          <div className="mt-2">
            <AlertBanner
              message={DESCRIPCIONES_BASE[data.base_legal]}
              type={data.base_legal === 'Interés legítimo' || data.base_legal === 'Datos biométricos de identificación (Art. 16 BIS)' ? 'warning' : 'info'}
            />
          </div>
        )}
        {data.base_legal === 'Consentimiento del titular' && data.datos_sensibles && (
          <div className="mt-2">
            <AlertBanner
              message="⚠️ Consentimiento + datos sensibles: el consentimiento debe ser EXPRESO (no basta implícito o tácito). Documente el mecanismo de obtención y revocación."
              type="warning"
            />
          </div>
        )}

        {data.base_legal && data.base_legal !== 'Otra' && (
          <div className="mt-4 p-4 rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <label className="block text-sm font-semibold mb-2" style={{ color: '#374151' }}>
              📄 Documento que respalda la base legal *
            </label>
            <p className="text-xs mb-3" style={{ color: '#6B7280' }}>
              Adjunte el documento correspondiente: consentimiento firmado, contrato, norma legal, EIPD, etc. (PDF, imagen o Word, máx. 10MB).
            </p>
            {!data.archivo_base_legal_base64 ? (
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                onChange={e => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  if (file.size > 10 * 1024 * 1024) {
                    toast.error('El archivo excede el límite de 10MB.');
                    return;
                  }
                  const reader = new FileReader();
                  reader.onload = ev => {
                    const b64 = (ev.target?.result as string)?.split(',')[1] || '';
                    setData(d => ({
                      ...d,
                      archivo_base_legal_base64: b64,
                      archivo_base_legal_nombre: file.name,
                      archivo_base_legal_tipo: file.type,
                    }));
                  };
                  reader.readAsDataURL(file);
                }}
                className="block w-full text-sm border rounded-lg p-2"
                style={{ borderColor: '#D1D5DB' }}
              />
            ) : (
              <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: 'white', border: '1px solid #D1D5DB' }}>
                <span className="text-lg">📎</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>{data.archivo_base_legal_nombre}</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>{data.archivo_base_legal_tipo}</p>
                </div>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  onClick={() => setData(d => ({ ...d, archivo_base_legal_base64: undefined, archivo_base_legal_nombre: undefined, archivo_base_legal_tipo: undefined }))}
                  style={{ color: '#DC2626', background: '#FEE2E2' }}
                >
                  Eliminar
                </Button>
              </div>
            )}
          </div>
        )}

        {/* documento de base legal ahora es opcional */}
      </div>

      {data.base_legal === 'Interés legítimo' && (
        <details className="rounded-lg" style={{ border: '1px solid #E5E7EB' }}>
          <summary className="px-4 py-3 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>
            📋 Test de interés legítimo (3 pasos)
          </summary>
          <div className="px-4 pt-2 pb-4 space-y-3">
            <AlertBanner message="El test de interés legítimo es obligatorio (Art. 16 Ley 21.719). Sin este análisis documentado en los 3 pasos, la base legal no será válida como defensa ante la APDP." type="warning" />
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                Paso 1 — ¿Existe un interés legítimo real?
              </label>
              <textarea
                rows={2}
                value={data._testIL?.paso1 ?? ''}
                onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL!, paso1: e.target.value } }))}
                placeholder="Describa el interés legítimo: marketing directo, seguridad, prevención de fraude..."
                className={inputCls}
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                Paso 2 — ¿El tratamiento es necesario para ese interés?
              </label>
              <textarea
                rows={2}
                value={data._testIL?.paso2 ?? ''}
                onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL, paso2: e.target.value } }))}
                placeholder="Justifique por qué el tratamiento es necesario y no hay alternativa menos invasiva."
                className={inputCls}
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                Paso 3 — ¿Prevalece sobre los derechos del titular?
              </label>
              <textarea
                rows={3}
                value={data._testIL?.paso3 ?? ''}
                onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL, paso3: e.target.value } }))}
                placeholder="Considere expectativas razonables del titular, impacto en su privacidad, medidas mitigadoras..."
                className={inputCls}
                style={inputStyle}
              />
            </div>
          </div>
          {fieldErrors._testIL && (
            <p role="alert" className="text-xs flex items-center gap-1 mt-2" style={{ color: '#DC2626' }}>
              <span aria-hidden="true">⚠</span>
              {fieldErrors._testIL}
            </p>
          )}
        </details>
      )}

      <div className="flex flex-col sm:flex-row gap-2 pt-2">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => cambiarStep(2)}
        >
          ← Anterior
        </Button>
        <Button
          onClick={() => {
            if (!stepIsValid) {
              toast.error('Completa los campos obligatorios antes de continuar.');
              if (validation.firstErrorField) {
                const el = document.getElementById(`rw-${validation.firstErrorField}`);
                el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                el?.focus();
              }
              return;
            }
            if (!data.base_legal) setData(d => ({ ...d, base_legal: opciones[0] }));
            cambiarStep(4);
          }}
          disabled={!stepIsValid}
          className="flex-1"
        >
          Siguiente →
        </Button>
      </div>
    </div>
  );
}
