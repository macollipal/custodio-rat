'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import type { Company, Rubro } from '@/types';

const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

interface CompanyEditFormProps {
  empresa: Company;
  onDone: (updated: Company) => void;
  onCancel: () => void;
}

export function CompanyEditForm({ empresa, onDone, onCancel }: CompanyEditFormProps) {
  const [form, setFormState] = useState({
    nombre: empresa.nombre ?? '',
    rubro_id: empresa.rubro_id?.toString() ?? '',
    direccion: empresa.direccion ?? '',
    contacto_dpo: empresa.contacto_dpo ?? '',
    email_dpo: empresa.email_dpo ?? '',
    descripcion: empresa.descripcion ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [rubros, setRubros] = useState<Rubro[]>([]);

  useEffect(() => { api.listarRubros().then(setRubros).catch(() => {}); }, []);

  function set(k: string, v: string) { setFormState(f => ({ ...f, [k]: v })); }

  async function handleSave() {
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (k === 'rubro_id') payload[k] = v ? Number(v) : null;
        else payload[k] = v.trim ? (v.trim() || null) : v;
      }
      const result = await api.actualizarEmpresa(empresa.id, payload as Partial<Company>);
      toast.success('Empresa actualizada correctamente.');
      onDone(result);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al actualizar.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-xl p-5 mt-4 space-y-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
      <p className="text-sm font-semibold" style={{ color: '#111827' }}>Editar: {empresa.nombre}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Razón social</label>
          <input type="text" value={form.nombre} onChange={e => set('nombre', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Rubro</label>
          <select value={form.rubro_id} onChange={e => set('rubro_id', e.target.value)} className={inputCls} style={inputStyle}>
            <option value="">— Sin rubro —</option>
            {rubros.map(r => <option key={r.id} value={String(r.id)}>{r.nombre}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Dirección</label>
          <input type="text" value={form.direccion} onChange={e => set('direccion', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>DPO</label>
          <input type="text" value={form.contacto_dpo} onChange={e => set('contacto_dpo', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Email DPO</label>
          <input type="email" value={form.email_dpo} onChange={e => set('email_dpo', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div className="col-span-2">
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Descripción</label>
          <textarea value={form.descripcion} onChange={e => set('descripcion', e.target.value)} rows={2} className={inputCls} style={inputStyle} />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <button onClick={onCancel} className="px-4 py-1.5 rounded-lg text-xs font-semibold border hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#374151' }}>Cancelar</button>
        <button onClick={handleSave} disabled={saving} className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white disabled:opacity-60" style={{ background: '#2563EB' }}>
          {saving ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </div>
    </div>
  );
}
