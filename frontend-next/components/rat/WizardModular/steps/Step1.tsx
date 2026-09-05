'use client';

import React from 'react';
import { toast } from 'sonner';
import type { RATWizardData, RATSugerido } from '@/types';
import FormField from '@/components/ui/FormField';
import AlertBanner from '@/components/dashboard/AlertBanner';
import CategoryChips from '@/components/ui/CategoryChips';
import { Button } from '@/components/ui/Button';

interface Step1Props {
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
  tipos: string[];
  tipoSel: string;
  setTipoSel: (v: string) => void;
  sugerencias: RATSugerido[];
  usarSugerencia: (sug: RATSugerido) => void;
  aplicarSugerencias: () => Promise<void>;
}

export function Step1({
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
  tipos,
  tipoSel,
  setTipoSel,
  sugerencias,
  usarSugerencia,
  aplicarSugerencias,
}: Step1Props) {
  function cambiarStep(n: number) {
    onNext();
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 1 · Identificación del proceso</h3>
        <p className="text-sm mb-2" style={{ color: '#6B7280' }}>Nombre y tipo de actividad de tratamiento que deseas registrar.</p>
        {validation.requiredCount > 0 && (
          <p className="text-xs font-medium" style={{ color: validation.isValid ? '#059669' : '#DC2626' }}>
            {validation.completedCount} / {validation.requiredCount} obligatorios completos
          </p>
        )}
      </div>

      {/* Sugerencias */}
      <div className="rounded-xl p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
        <p className="text-sm font-semibold mb-1" style={{ color: '#111827' }}>🤖 Sugerencias inteligentes</p>
        <p className="text-xs mb-3" style={{ color: '#6B7280' }}>
          Selecciona el tipo de proceso y Custodio completará automáticamente los campos más relevantes.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={tipoSel}
            onChange={e => setTipoSel(e.target.value)}
            className={inputCls + ' flex-1'}
            style={inputStyle}
          >
            <option value="">— Selecciona para obtener sugerencias —</option>
            {tipos.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <Button
            onClick={aplicarSugerencias}
            disabled={!tipoSel || tipoSel.startsWith('—')}
            className="flex-shrink-0"
          >
            Aplicar
          </Button>
        </div>
        {data._sug_observacion && (
          <div className="mt-3">
            <AlertBanner message={data._sug_observacion} type="info" />
          </div>
        )}
      </div>

      <FormField label="Nombre del proceso" required htmlFor="rw-nombre_proceso" error={fieldErrors.nombre_proceso}>
        <input
          id="rw-nombre_proceso"
          type="text"
          value={data.nombre_proceso ?? ''}
          onChange={e => setData(d => ({ ...d, nombre_proceso: e.target.value }))}
          placeholder="Ej: Gestión de datos de clientes, Nómina de empleados"
          aria-required="true"
          aria-invalid={!!fieldErrors.nombre_proceso}
          className={inputCls}
          style={{
            ...inputStyle,
            borderColor: fieldErrors.nombre_proceso ? '#DC2626' : '#D1D5DB',
          }}
        />
      </FormField>

      <FormField
        label="Categorías de titulares"
        required
        htmlFor="rw-categoria_titulares"
        hint="Art. 16 Ley 21.719 — campo mínimo. Selecciona chips o escribe los tuyos separados por comas."
        error={fieldErrors.categoria_titulares}
      >
        <CategoryChips
          id="rw-categoria_titulares"
          value={data.categoria_titulares ?? ''}
          onChange={v => setData(d => ({ ...d, categoria_titulares: v }))}
          suggestions={['Clientes', 'Empleados', 'Proveedores', 'Pacientes', 'Postulantes', 'Estudiantes', 'Usuarios web', 'Menores de edad', 'Acreedores']}
          placeholder="Ej: Clientes, empleados, proveedores..."
          ariaLabel="Categorías de titulares"
          hasError={!!fieldErrors.categoria_titulares}
        />
      </FormField>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField label="Fuente de los datos" required htmlFor="rw-fuente_datos" error={fieldErrors.fuente_datos}>
          <input
            id="rw-fuente_datos"
            type="text"
            value={data.fuente_datos ?? ''}
            onChange={e => { setData(d => { const n = { ...d, fuente_datos: e.target.value }; guardarDraft(); return n; }); }}
            placeholder="Ej: Directamente del titular, base interna, terceros"
            aria-required="true"
            aria-invalid={!!fieldErrors.fuente_datos}
            className={inputCls}
            style={{
              ...inputStyle,
              borderColor: fieldErrors.fuente_datos ? '#DC2626' : '#D1D5DB',
            }}
          />
        </FormField>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
            Origen de los datos <span className="text-xs font-normal" style={{ color: '#6B7280' }}>(Art. 14 ter)</span>
          </label>
          <select
            value={data.origen_datos ?? ''}
            onChange={e => setData(d => ({ ...d, origen_datos: e.target.value as RATWizardData['origen_datos'] }))}
            className={inputCls}
            style={inputStyle}
            aria-label="Origen de los datos"
          >
            <option value="">— No especificado —</option>
            <option value="titular">Del propio titular</option>
            <option value="tercero">De un tercero</option>
            <option value="fuente_publica">Fuente pública</option>
            <option value="mixto">Mixto</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
          Destinatarios / Encargados del tratamiento
        </label>
        <input
          type="text"
          value={data.destinatarios ?? ''}
          onChange={e => setData(d => ({ ...d, destinatarios: e.target.value }))}
          placeholder="Ej: Proveedor CRM (encargado), área de RRHH, SII"
          className={inputCls}
          style={inputStyle}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
          Nombre del encargado del tratamiento
        </label>
        <input
          type="text"
          value={data.nombre_encargado ?? ''}
          onChange={e => setData(d => ({ ...d, nombre_encargado: e.target.value }))}
          placeholder="Ej: Proveedor CRM, asesora laboral..."
          className={inputCls}
          style={inputStyle}
        />
        <div className="mt-2">
          <label className="flex items-center gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={data.tiene_contrato_encargado ?? false}
              onChange={e => setData(d => ({ ...d, tiene_contrato_encargado: e.target.checked }))}
              className="mt-0.5 rounded"
            />
            <span className="text-sm font-medium" style={{ color: '#374151' }}>
              ✓ Tiene contrato de encargo (Art. 14 quáter Ley 21.719)
            </span>
          </label>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-2 pt-2">
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
            cambiarStep(2);
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
