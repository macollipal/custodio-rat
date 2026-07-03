'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import { validarRUT, formatearRUT } from '@/components/ui/validation';
import type { Company } from '@/types';

import { inputCls, inputStyle, labelCls, labelStyle, panelStyles, panelWrapperCls, panelTitleStyles, btnPrimaryCls, btnPrimaryStyle, btnSecondaryCls, btnSecondaryStyle, gridResponsive1to2, modalHeaderStyle, modalHeaderCls, modalContentCls, formFooterCls } from '@/lib/styles';

interface CompanyFormProps {
  onDone: () => void;
  onCancel: () => void;
}

export function CompanyForm({ onDone, onCancel }: CompanyFormProps) {
  const { setCompany, setCompanies, companies } = useApp();
  const [form, setForm] = useState({
    nombre: '', rut: '', rubro: '', direccion: '', contacto_dpo: '', email_dpo: '', descripcion: '',
  });
  const [rutError, setRutError] = useState('');
  const [saving, setSaving] = useState(false);

  function set(k: string, v: string) { setForm(f => ({ ...f, [k]: v })); }

  function handleRutChange(v: string) {
    const fmt = formatearRUT(v);
    setForm(f => ({ ...f, rut: fmt }));
    if (fmt.replace(/[^0-9kK]/gi, '').length >= 8) {
      const result = validarRUT(fmt);
      setRutError(result.valido ? '' : result.mensaje);
    } else {
      setRutError('');
    }
  }

  async function handleSave() {
    if (!form.nombre.trim()) { toast.error('La razón social es obligatoria.'); return; }
    if (!form.rut.trim()) { toast.error('El RUT es obligatorio.'); return; }
    const rutValid = validarRUT(form.rut);
    if (!rutValid.valido) { toast.error(rutValid.mensaje); return; }
    if (form.email_dpo.trim()) {
      const emailValid = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(form.email_dpo.trim());
      if (!emailValid) { toast.error('El email del DPO no es valido.'); return; }
    }
    setSaving(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v.trim() || null])
      );
      const result = await api.crearEmpresa(payload);
      setCompany(result);
      setCompanies([...companies, result]);
      toast.success(`Empresa "${result.nombre}" registrada correctamente.`);
      onDone();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al crear empresa.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button onClick={onCancel} className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50" style={{ color: '#6B7280', borderColor: '#E5E7EB' }}>
          ← Volver al listado
        </button>
        <h2 className="text-lg font-bold" style={{ color: '#111827' }}>Nueva empresa responsable del tratamiento</h2>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm space-y-5" style={{ border: '1px solid #E5E7EB' }}>
        <p className="text-sm" style={{ color: '#6B7280' }}>
          Complete los datos del responsable conforme al Art. 5 de la Ley 21.719.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Razón social *</label>
            <input type="text" value={form.nombre} onChange={e => set('nombre', e.target.value)} placeholder="Ej: Empresa Ejemplo SpA" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>RUT *</label>
            <input
              type="text"
              value={form.rut}
              onChange={e => handleRutChange(e.target.value)}
              placeholder="Ej: 76.123.456-7"
              className={inputCls}
              style={{ borderColor: rutError ? '#DC2626' : '#E5E7EB' }}
            />
            {rutError && <p className="text-xs mt-1" style={{ color: '#DC2626' }}>{rutError}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Rubro / Sector</label>
            <input type="text" value={form.rubro} onChange={e => set('rubro', e.target.value)} placeholder="Ej: Retail, Salud, Tecnología" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Dirección</label>
            <input type="text" value={form.direccion} onChange={e => set('direccion', e.target.value)} placeholder="Ej: Av. Providencia 1234, Santiago" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nombre del DPO (opcional)</label>
            <input type="text" value={form.contacto_dpo} onChange={e => set('contacto_dpo', e.target.value)} placeholder="Ej: Juan Pérez" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Email del DPO</label>
            <input type="email" value={form.email_dpo} onChange={e => set('email_dpo', e.target.value)} placeholder="dpo@empresa.cl" className={inputCls} style={inputStyle} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Descripción (opcional)</label>
          <textarea value={form.descripcion} onChange={e => set('descripcion', e.target.value)} rows={2} placeholder="Breve descripción de la empresa y sus actividades principales." className={inputCls} style={inputStyle} />
        </div>

        <div className="rounded-lg px-4 py-3 text-sm" style={{ background: '#DBEAFE', borderLeft: '3px solid #2563EB', color: '#1E3A8A' }}>
          El DPO es la persona responsable de velar por el cumplimiento de la normativa de protección de datos al interior de la organización.
        </div>

        <div className="flex justify-end">
          <button onClick={handleSave} disabled={saving} className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60" style={{ background: '#2563EB' }}>
            {saving ? 'Registrando...' : 'Registrar empresa'}
          </button>
        </div>
      </div>
    </div>
  );
}



