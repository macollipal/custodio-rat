'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import { validarRUT, formatearRUT } from '@/components/ui/validation';
import type { Rubro } from '@/types';

export default function OnboardingPage() {
  const router = useRouter();
  const { setCompany, setCompanies } = useApp();
  const [form, setForm] = useState({
    nombre: '',
    rut: '',
    contacto_dpo: '',
    email_dpo: '',
    rubro_id: '' as string,
  });
  const [rutError, setRutError] = useState('');
  const [saving, setSaving] = useState(false);
  const [rubros, setRubros] = useState<Rubro[]>([]);
  const [loadingRubros, setLoadingRubros] = useState(true);

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  function set(k: keyof typeof form, v: string) {
    setForm(f => ({ ...f, [k]: v }));
  }

  function handleRutChange(v: string) {
    const fmt = formatearRUT(v);
    set('rut', fmt);
    if (fmt.replace(/[^0-9kK]/gi, '').length >= 8) {
      const result = validarRUT(fmt);
      setRutError(result.valido ? '' : result.mensaje);
    } else {
      setRutError('');
    }
  }

  useEffect(() => {
    api.listarRubros().then(setRubros).catch(() => {}).finally(() => setLoadingRubros(false));
  }, []);

  async function handleSubmit() {
    if (!form.nombre.trim()) { toast.error('La razón social es obligatoria.'); return; }
    if (!form.rut.trim()) { toast.error('El RUT es obligatorio.'); return; }
    const rutValid = validarRUT(form.rut);
    if (!rutValid.valido) { toast.error(rutValid.mensaje); return; }
    if (!form.email_dpo.trim()) { toast.error('El email del DPO es obligatorio.'); return; }
    const emailValid = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(form.email_dpo.trim());
    if (!emailValid) { toast.error('El email del DPO no es valido.'); return; }

    setSaving(true);
    try {
      const payload: Record<string, unknown> = {
        nombre: form.nombre.trim(),
        rut: form.rut.trim(),
        contacto_dpo: form.contacto_dpo.trim() || undefined,
        email_dpo: form.email_dpo.trim(),
      };
      if (form.rubro_id) payload.rubro_id = Number(form.rubro_id);
      const empresa = await api.crearEmpresa(payload);
      setCompany(empresa);
      setCompanies([empresa]);
      localStorage.setItem('custodio_tour_completed', 'false');
      toast.success(`Empresa "${empresa.nombre}" registrada. ¡Listo para comenzar!`);
      router.push('/dashboard');
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al crear empresa.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: 'linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%)' }}
    >
      <div className="w-full max-w-lg px-4">
        <div className="text-center mb-8">
          <div
            className="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center text-3xl shadow-lg"
            style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)' }}
          >
            🛡
          </div>
          <h1 className="text-white text-2xl font-bold tracking-tight mb-2">¡Bienvenido a Custodio!</h1>
          <p className="text-slate-400 text-sm">
            Configuremos juntos el Registro de Actividades de Tratamiento de tu organización.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="rounded-lg px-4 py-3 mb-6 text-sm" style={{ background: '#DBEAFE', borderLeft: '3px solid #2563EB', color: '#1E3A8A' }}>
            <strong>Ley 21.719</strong> — Todo responsable que trata datos personales debe mantener un registro que documente qué datos trata, para qué finalidad, con qué base legal y cuánto tiempo los conserva.
          </div>

          <h2 className="text-lg font-bold mb-1" style={{ color: '#111827' }}>Empresa responsable del tratamiento</h2>
          <p className="text-sm mb-5" style={{ color: '#6B7280' }}>
            Primero, define la empresa que será responsable de los registros RAT.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Razón social *
              </label>
              <input
                type="text"
                value={form.nombre}
                onChange={e => set('nombre', e.target.value)}
                placeholder="Ej: Mi Empresa SpA"
                className={inputCls}
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                RUT *
              </label>
              <input
                type="text"
                value={form.rut}
                onChange={e => handleRutChange(e.target.value)}
                placeholder="Ej: 76.123.456-7"
                className={inputCls}
                style={{ borderColor: rutError ? '#DC2626' : '#D1D5DB', backgroundColor: '#FFFFFF' }}
              />
              {rutError && <p className="text-xs mt-1" style={{ color: '#DC2626' }}>{rutError}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Nombre del DPO (opcional)
              </label>
              <input
                type="text"
                value={form.contacto_dpo}
                onChange={e => set('contacto_dpo', e.target.value)}
                placeholder="Ej: Juan Pérez"
                className={inputCls}
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Email del DPO *
              </label>
              <input
                type="email"
                value={form.email_dpo}
                onChange={e => set('email_dpo', e.target.value)}
                placeholder="dpo@empresa.cl"
                className={inputCls}
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Rubro de la empresa
              </label>
              {loadingRubros ? (
                <div className="h-10 rounded-lg animate-pulse" style={{ background: '#F3F4F6' }} />
              ) : (
                <select
                  value={form.rubro_id}
                  onChange={e => set('rubro_id', e.target.value)}
                  className={inputCls}
                  style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
                >
                  <option value="">— Selecciona un rubro —</option>
                  {rubros.map(r => (
                    <option key={r.id} value={String(r.id)}>{r.nombre}</option>
                  ))}
                </select>
              )}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={saving}
            className="w-full mt-6 py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold text-sm transition"
          >
            {saving ? 'Configurando...' : 'Comenzar con Custodio'}
          </button>
        </div>
      </div>
    </div>
  );
}