'use client';

import React from 'react';
import { toast } from 'sonner';
import type { RATWizardData } from '@/types';
import FormField from '@/components/ui/FormField';
import AlertBanner from '@/components/dashboard/AlertBanner';
import { TIPOS_DATO_SENSIBLE, DATOS_NNA_OPCIONES, NIVEL_CONFIDENCIALIDAD_OPCIONES, ESTRUCTURA_DATO_OPCIONES } from '@/lib/constants';
import { Button } from '@/components/ui/Button';

interface Step2Props {
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
}

export function Step2({
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
}: Step2Props) {
  function cambiarStep(n: number) {
    onNext();
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 2 · Datos personales tratados</h3>
        <p className="text-sm mb-2" style={{ color: '#6B7280' }}>Qué datos personales se tratan, su clasificación y si existen categorías especiales.</p>
        {validation.requiredCount > 0 && (
          <p className="text-xs font-medium" style={{ color: validation.isValid ? '#059669' : '#DC2626' }}>
            {validation.completedCount} / {validation.requiredCount} obligatorios completos
          </p>
        )}
      </div>

      <FormField label="Categoría de datos tratados" required htmlFor="rw-categoria_datos" error={fieldErrors.categoria_datos}>
        <textarea
          id="rw-categoria_datos"
          value={data.categoria_datos ?? ''}
          onChange={e => setData(d => ({ ...d, categoria_datos: e.target.value }))}
          rows={3}
          placeholder="Ej: Datos identificativos (nombre, RUT, email), datos laborales, datos de salud..."
          aria-required="true"
          aria-invalid={!!fieldErrors.categoria_datos}
          className={inputCls}
          style={{
            ...inputStyle,
            borderColor: fieldErrors.categoria_datos ? '#DC2626' : '#D1D5DB',
          }}
        />
      </FormField>

      <div className="space-y-4">
        <div className="space-y-2">
          <label className="flex items-start gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={data.datos_sensibles ?? false}
              onChange={e => setData(d => ({
                ...d,
                datos_sensibles: e.target.checked,
                tipo_dato_sensible: e.target.checked ? d.tipo_dato_sensible : '',
                evaluacion_impacto: e.target.checked ? true : d.evaluacion_impacto,
              }))}
              className="mt-0.5 rounded"
            />
            <span className="text-sm font-medium" style={{ color: '#374151' }}>
              ⚠️ El proceso trata datos sensibles (Art. 2 letra g)
            </span>
          </label>
          {data.datos_sensibles && (
            <div className="space-y-2 pl-6">
              <FormField label="Tipo de dato sensible (Art. 2 g)" required htmlFor="rw-tipo_dato_sensible" error={fieldErrors.tipo_dato_sensible}>
                <select
                  id="rw-tipo_dato_sensible"
                  value={data.tipo_dato_sensible ?? ''}
                  onChange={e => setData(d => ({ ...d, tipo_dato_sensible: e.target.value }))}
                  aria-required="true"
                  aria-invalid={!!fieldErrors.tipo_dato_sensible}
                  className={inputCls}
                  style={{
                    ...inputStyle,
                    borderColor: fieldErrors.tipo_dato_sensible ? '#DC2626' : '#D1D5DB',
                  }}
                >
                  <option value="">— Seleccione el tipo de dato sensible (Art. 2 g) —</option>
                  {TIPOS_DATO_SENSIBLE.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </FormField>
              <AlertBanner
                message="Dato sensible: requiere base legal expresa y medidas de seguridad reforzadas. Si es biometría, aplica Art. 16 BIS y la EIPD es obligatoria."
                type="warning"
              />
              <div className="rounded-lg p-3" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                <p className="text-xs font-semibold mb-2" style={{ color: '#1E40AF' }}>B-06: Consentimiento Expreso (Art. 12)</p>
                <p className="text-xs mb-2" style={{ color: '#374151' }}>Para datos sensibles, el consentimiento debe ser expreso. Registre el consentimiento del titular.</p>
                <div className="grid grid-cols-2 gap-2">
                  <input type="text" value={data.consentimiento_nombre ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_nombre: e.target.value }))} placeholder="Nombre del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                  <input type="email" value={data.consentimiento_email ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_email: e.target.value }))} placeholder="Email del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                </div>
                <textarea value={data.consentimiento_texto ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_texto: e.target.value }))} rows={2} placeholder="Texto del consentimiento expreso..." className="w-full mt-2 px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
              </div>
            </div>
          )}
        </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className={`flex items-start gap-2.5 ${data.datos_sensibles ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}>
              <input
                type="checkbox"
                checked={data.evaluacion_impacto ?? false}
                disabled={data.datos_sensibles}
                onChange={e => setData(d => ({ ...d, evaluacion_impacto: e.target.checked }))}
                className="mt-0.5 rounded"
              />
              <span className="text-sm font-medium" style={{ color: '#374151' }}>
                📋 Requiere Evaluación de Impacto (EIPD) {data.datos_sensibles ? '(obligatoria por datos sensibles — Art. 15 ter)' : ''}
              </span>
            </label>
            {data.datos_sensibles && (
              <AlertBanner
                message="EIPD obligatoria: el tratamiento de datos sensibles requiere evaluación de impacto documentada antes de iniciar (Art. 15 ter Ley 21.719)."
                type="warning"
              />
            )}
            {data.evaluacion_impacto && !data.datos_sensibles && (
              <AlertBanner
                message="La EIPD debe realizarse y documentarse antes de iniciar el tratamiento (Art. 15 ter)."
                type="info"
              />
            )}
          </div>
          <div className="space-y-2">
            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={data.decisiones_automatizadas ?? false}
                onChange={e => setData(d => ({ ...d, decisiones_automatizadas: e.target.checked }))}
                className="mt-0.5 rounded"
              />
              <span className="text-sm font-medium" style={{ color: '#374151' }}>
                🤖 Involucra decisiones automatizadas
              </span>
            </label>
            {data.decisiones_automatizadas && (
              <>
                <AlertBanner
                  message="Los titulares tienen derecho a solicitar revisión humana e impugnar la decisión (Art. 8). Documente la lógica del sistema."
                  type="info"
                />
                <textarea
                  value={data.logica_automatizada ?? ''}
                  onChange={e => setData(d => ({ ...d, logica_automatizada: e.target.value }))}
                  rows={3}
                  placeholder="Describa la lógica aplicada, consecuencias para el titular y posibilidad de revisión humana..."
                  className={inputCls}
                  style={inputStyle}
                />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Clasificación y NNA — canonical Step 2 */}
      <div className="rounded-lg p-4 space-y-4" style={{ border: '1px solid #E5E7EB' }}>
        <h4 className="text-sm font-bold" style={{ color: '#374151' }}>Clasificación y NNA</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Tratamiento de NNA
            </label>
            <select
              value={(data.datos_nna as string) ?? 'ninguno'}
              onChange={e => setData(d => ({ ...d, datos_nna: e.target.value as 'ninguno' | 'ninos' | 'adolescentes' | 'ambos' }))}
              className={inputCls}
              style={inputStyle}
            >
              {DATOS_NNA_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            {data.datos_nna && data.datos_nna !== 'ninguno' && (
              <AlertBanner
                message="Datos de menores de edad: la base legal debe ser Consentimiento del titular/apoderado, Interés vital u Obligación legal. No se admite Interés legítimo ni Contrato (Art. 16 Ley 21.719). El sistema bloqueará el guardado si la base legal no es compatible."
                type="warning"
              />
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Nivel de confidencialidad
            </label>
            <select
              value={(data.nivel_confidencialidad as string) ?? ''}
              onChange={e => setData(d => ({ ...d, nivel_confidencialidad: e.target.value as 'DC0' | 'DC1' | 'DC2' | 'DC3' }))}
              aria-describedby="nivel-conf-tooltip-wizard"
              className={inputCls}
              style={inputStyle}
            >
              <option value="">— Seleccionar —</option>
              {NIVEL_CONFIDENCIALIDAD_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            {(data.nivel_confidencialidad as string) && (() => {
              const opt = NIVEL_CONFIDENCIALIDAD_OPCIONES.find(o => o.value === data.nivel_confidencialidad);
              return opt?.tooltip ? <div role="tooltip" id="nivel-conf-tooltip-wizard" className="text-xs mt-1" style={{ color: '#6B7280' }}>{opt.tooltip}</div> : null;
            })()}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Estructura del dato
            </label>
            <select
              value={(data.estructura_dato as string) ?? ''}
              onChange={e => setData(d => ({ ...d, estructura_dato: e.target.value as 'estructurado' | 'semiestructurado' | 'no_estructurado' | 'fisico' }))}
              className={inputCls}
              style={inputStyle}
            >
              <option value="">— Seleccionar —</option>
              {ESTRUCTURA_DATO_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </div>
        <div className="flex gap-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={data.datos_anonimizados ?? false} onChange={e => setData(d => ({ ...d, datos_anonimizados: e.target.checked }))} className="mt-0.5 rounded" />
            <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos anonimizados</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={data.datos_seudonimizados ?? false} onChange={e => setData(d => ({ ...d, datos_seudonimizados: e.target.checked }))} className="mt-0.5 rounded" />
            <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos seudonimizados</span>
          </label>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 pt-2">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => cambiarStep(1)}
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
            cambiarStep(3);
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