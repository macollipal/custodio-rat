'use client';

import React from 'react';
import { toast } from 'sonner';
import type { RATWizardData } from '@/types';
import FormField from '@/components/ui/FormField';
import AlertBanner from '@/components/dashboard/AlertBanner';
import Spinner from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';

interface Step4Props {
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

export function Step4({
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
}: Step4Props) {
  function cambiarStep(n: number) {
    onNext();
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 4 · Almacenamiento y transferencias</h3>
        <p className="text-sm mb-2" style={{ color: '#6B7280' }}>Por cuánto tiempo se conservan los datos y cómo se comparten.</p>
        {validation.requiredCount > 0 && (
          <p className="text-xs font-medium" style={{ color: validation.isValid ? '#059669' : '#DC2626' }}>
            {validation.completedCount} / {validation.requiredCount} obligatorios completos
          </p>
        )}
      </div>

      {/* Iter 10 fields — storage system and volume */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
            Sistema de almacenamiento
          </label>
          <input
            type="text"
            value={data.sistema_almacenamiento ?? ''}
            onChange={e => setData(d => ({ ...d, sistema_almacenamiento: e.target.value }))}
            placeholder="Ej: CRM Salesforce, Excel, Google Drive, Sistema clínico..."
            className={inputCls}
            style={inputStyle}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
            Volumen estimado de titulares
          </label>
          <input
            type="number"
            value={data.volumen_titulares_estimado ?? ''}
            onChange={e => setData(d => ({ ...d, volumen_titulares_estimado: e.target.value ? parseInt(e.target.value) : undefined }))}
            placeholder="Ej: 50000"
            className={inputCls}
            style={inputStyle}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-4">
          <FormField label="Plazo de retención" required htmlFor="rw-plazo_retencion" error={fieldErrors.plazo_retencion}>
            <input
              id="rw-plazo_retencion"
              type="text"
              value={data.plazo_retencion ?? ''}
              onChange={e => setData(d => ({ ...d, plazo_retencion: e.target.value }))}
              placeholder="Ej: 5 años desde el último contacto comercial"
              aria-required="true"
              aria-invalid={!!fieldErrors.plazo_retencion}
              className={inputCls}
              style={{
                ...inputStyle,
                borderColor: fieldErrors.plazo_retencion ? '#DC2626' : '#D1D5DB',
              }}
            />
          </FormField>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Medidas de seguridad implementadas
            </label>
            <textarea
              value={data.medidas_seguridad ?? ''}
              onChange={e => setData(d => ({ ...d, medidas_seguridad: e.target.value }))}
              rows={2}
              placeholder="Ej: Cifrado AES-256, acceso por roles, MFA..."
              className={inputCls}
              style={inputStyle}
            />
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Transferencias o comunicaciones de datos
            </label>
            <textarea
              value={data.transferencia_datos ?? ''}
              onChange={e => setData(d => ({ ...d, transferencia_datos: e.target.value }))}
              rows={2}
              placeholder="Ej: Compartidos con proveedor de nómina bajo contrato de encargo"
              className={inputCls}
              style={inputStyle}
            />
          </div>
          <div className="space-y-2">
            <label className="flex items-start gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={data.transferencia_internacional ?? false}
                onChange={e => setData(d => ({ ...d, transferencia_internacional: e.target.checked, pais_destino: e.target.checked ? d.pais_destino : undefined, evaluacion_impacto: e.target.checked ? true : (d.datos_sensibles ? true : d.evaluacion_impacto) }))}
                className="mt-0.5 rounded"
              />
              <span className="text-sm font-medium" style={{ color: '#374151' }}>
                🌐 Transferencia internacional de datos
              </span>
            </label>
            {data.transferencia_internacional && (
              <div className="space-y-2">
                <FormField label="País destino" required htmlFor="rw-pais_destino" error={fieldErrors.pais_destino}>
                  <input
                    id="rw-pais_destino"
                    type="text"
                    value={data.pais_destino ?? ''}
                    onChange={e => setData(d => ({ ...d, pais_destino: e.target.value }))}
                    placeholder="Ej: Estados Unidos, España, Brasil"
                    aria-required="true"
                    aria-invalid={!!fieldErrors.pais_destino}
                    className={inputCls}
                    style={{
                      ...inputStyle,
                      borderColor: fieldErrors.pais_destino ? '#DC2626' : '#D1D5DB',
                    }}
                  />
                </FormField>
                <FormField label="Garantías aplicables" required htmlFor="rw-garantias_transferencia_int" error={fieldErrors.garantias_transferencia_int}>
                  <select
                    id="rw-garantias_transferencia_int"
                    value={data.garantias_transferencia_int ?? ''}
                    onChange={e => setData(d => ({ ...d, garantias_transferencia_int: e.target.value }))}
                    aria-required="true"
                    aria-invalid={!!fieldErrors.garantias_transferencia_int}
                    className={inputCls}
                    style={{
                      ...inputStyle,
                      borderColor: fieldErrors.garantias_transferencia_int ? '#DC2626' : '#D1D5DB',
                    }}
                  >
                    <option value="">— Garantías aplicables (obligatorio) —</option>
                    <option value="Nivel adecuado de protección (decisión APDC o UE)">Nivel adecuado de protección (decisión APDC o UE)</option>
                    <option value="Cláusulas Contractuales Tipo (SCC)">Cláusulas Contractuales Tipo (SCC)</option>
                    <option value="Normas Corporativas Vinculantes (BCR)">Normas Corporativas Vinculantes (BCR)</option>
                    <option value="Consentimiento explícito del titular para la transferencia">Consentimiento explícito del titular para la transferencia</option>
                    <option value="Contrato con cláusulas de protección equivalentes">Contrato con cláusulas de protección equivalentes</option>
                    <option value="Otra garantía adecuada">Otra garantía adecuada (especificar en transferencia de datos)</option>
                  </select>
                </FormField>
                <AlertBanner
                  message="Chile NO está en la lista de adecuación de la UE. Si el destinatario es europeo, se requieren SCC u otras garantías. Documente siempre las garantías aplicadas (Art. 28 Ley 21.719)."
                  type="warning"
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resumen */}
      <details className="rounded-lg" style={{ border: '1px solid #E5E7EB' }}>
        <summary className="px-4 py-3 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>
          📋 Revisar resumen antes de guardar
        </summary>
        <div className="px-4 pb-4 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
          {[
            ['Proceso', data.nombre_proceso],
            ['Titulares', data.categoria_titulares],
            ['Fuente', data.fuente_datos],
            ['Finalidad', data.finalidad],
            ['Base legal', data.base_legal],
            ['Datos sensibles', data.datos_sensibles ? `Sí ⚠️ (${data.tipo_dato_sensible || 'tipo no especificado'})` : 'No'],
            ['Decisiones automatizadas', data.decisiones_automatizadas ? 'Sí 🤖' : 'No'],
            ['EIPD requerida', data.evaluacion_impacto ? 'Sí 📋' : 'No'],
            ['Transfer. internacional', data.transferencia_internacional ? `Sí 🌐 — ${data.garantias_transferencia_int || 'garantías pendientes'}` : 'No'],
          ].map(([k, v]) => (
            <div key={k} className="text-sm py-0.5">
              <span className="font-medium" style={{ color: '#374151' }}>{k}: </span>
              <span style={{ color: '#6B7280' }}>{v ?? '—'}</span>
            </div>
          ))}
        </div>
      </details>

      <div className="flex flex-col sm:flex-row gap-2 pt-2">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => cambiarStep(3)}
        >
          ← Anterior
        </Button>
        <Button
          variant="success"
          onClick={() => {
            if (!stepIsValid) {
              toast.error('Completa los campos obligatorios antes de guardar.');
              return;
            }
            cambiarStep(5);
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
