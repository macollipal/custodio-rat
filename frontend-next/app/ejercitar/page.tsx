'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { crearSolicitudDerecho } from '@/lib/api';

const TIPOS_DERECHO = [
  { value: 'acceso', label: 'Acceso', desc: 'Quiero saber qué datos personales tu empresa tiene sobre mí.' },
  { value: 'rectificacion', label: 'Rectificación', desc: 'Quiero corregir datos personales incorrectos o incompletos.' },
  { value: 'cancelacion', label: 'Cancelación', desc: 'Quiero que se eliminen mis datos personales.' },
  { value: 'oposicion', label: 'Oposición', desc: 'Me opongo al tratamiento de mis datos por un motivo legítimo.' },
];

interface CompanyOption {
  id: number;
  nombre: string;
  rut: string;
  email_dpo?: string;
  contacto_dpo?: string;
  canal_ejercicio_derechos?: string;
}

export default function EjercitarPage() {
  const [companies, setCompanies] = useState<CompanyOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<CompanyOption | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const [form, setForm] = useState({
    tipo: 'acceso',
    nombre_titular: '',
    email_titular: '',
    rut_titular: '',
    descripcion: '',
  });

  useEffect(() => {
    fetch(`${API_BASE}/companies/publico`)
      .then(r => r.json())
      .then(data => { setCompanies(data); setLoading(false); })
      .catch(() => { toast.error('No se pudieron cargar las empresas.'); setLoading(false); });
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCompany) { toast.error('Selecciona una empresa.'); return; }
    if (!form.nombre_titular.trim()) { toast.error('El nombre es obligatorio.'); return; }
    if (!form.email_titular.trim()) { toast.error('El email es obligatorio.'); return; }
    if (!form.descripcion.trim()) { toast.error('La descripción es obligatoria.'); return; }

    setSubmitting(true);
    try {
      await crearSolicitudDerecho({
        company_id: selectedCompany.id,
        tipo: form.tipo,
        nombre_titular: form.nombre_titular.trim(),
        email_titular: form.email_titular.trim(),
        rut_titular: form.rut_titular.trim() || undefined,
        descripcion: form.descripcion.trim(),
      });
      setSubmitted(true);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Error al enviar la solicitud.');
    } finally {
      setSubmitting(false);
    }
  }

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#F9FAFB' }}>
        <div className="max-w-md w-full bg-white rounded-2xl p-8 shadow-lg text-center">
          <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style={{ background: '#DCFCE7' }}>
            <span className="text-3xl">✓</span>
          </div>
          <h1 className="text-xl font-bold mb-2" style={{ color: '#111827' }}>Solicitud enviada</h1>
          <p className="text-sm mb-4" style={{ color: '#6B7280' }}>
            Tu solicitud de <strong>{TIPOS_DERECHO.find(t => t.value === form.tipo)?.label}</strong> fue recibida por <strong>{selectedCompany?.nombre}</strong>.
          </p>
          <p className="text-xs mb-6" style={{ color: '#9CA3AF' }}>
            La empresa tiene un plazo razonable para responder conforme a la Ley 21.719.
            Recibirás una respuesta al email proporcionado.
          </p>
          {selectedCompany?.email_dpo && (
            <div className="rounded-lg p-3 mb-4 text-left" style={{ background: '#F3F4F6', border: '1px solid #E5E7EB' }}>
              <p className="text-xs font-medium mb-1" style={{ color: '#374151' }}>Contacto directo:</p>
              <p className="text-xs" style={{ color: '#6B7280' }}>{selectedCompany.contacto_dpo || 'DPO'} — {selectedCompany.email_dpo}</p>
            </div>
          )}
          <button
            onClick={() => setSubmitted(false)}
            className="px-4 py-2 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            Enviar otra solicitud
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#F9FAFB' }}>
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="p-6 text-center" style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}>
          <h1 className="text-xl font-bold text-white mb-1">Ejercé sus derechos ARCO</h1>
          <p className="text-xs text-white/70">
            Ley 21.719 — Acceso, Rectificación, Cancelación, Oposición
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Selección de empresa */}
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Empresa ante la cual ejerzo mis derechos *
            </label>
            {loading ? (
              <div className="h-10 rounded-lg animate-pulse" style={{ background: '#F3F4F6' }} />
            ) : (
              <select
                value={selectedCompany?.id ?? ''}
                onChange={e => {
                  const c = companies.find(c => c.id === Number(e.target.value));
                  setSelectedCompany(c ?? null);
                }}
                required
                className={inputCls}
                style={inputStyle}
              >
                <option value="">— Selecciona una empresa —</option>
                {companies.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre} ({c.rut})</option>
                ))}
              </select>
            )}
            {selectedCompany?.canal_ejercicio_derechos && (
              <div className="mt-2 p-3 rounded-lg" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                <p className="text-xs font-medium mb-0.5" style={{ color: '#1E40AF' }}>Canal informado por la empresa:</p>
                <p className="text-xs" style={{ color: '#3B82F6' }}>{selectedCompany.canal_ejercicio_derechos}</p>
              </div>
            )}
          </div>

          {/* Tipo de derecho */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: '#374151' }}>
              ¿Qué derecho desea ejercer? *
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {TIPOS_DERECHO.map(t => (
                <label
                  key={t.value}
                  className="flex items-start gap-2.5 p-3 rounded-lg border cursor-pointer transition-all"
                  style={{
                    borderColor: form.tipo === t.value ? '#2563EB' : '#E5E7EB',
                    background: form.tipo === t.value ? '#EFF6FF' : '#FFFFFF',
                  }}
                >
                  <input
                    type="radio"
                    name="tipo"
                    value={t.value}
                    checked={form.tipo === t.value}
                    onChange={() => setForm(f => ({ ...f, tipo: t.value }))}
                    className="mt-0.5"
                  />
                  <div>
                    <p className="text-sm font-semibold" style={{ color: '#111827' }}>{t.label}</p>
                    <p className="text-xs" style={{ color: '#9CA3AF' }}>{t.desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Datos del titular */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Nombre completo *
              </label>
              <input
                type="text"
                value={form.nombre_titular}
                onChange={e => setForm(f => ({ ...f, nombre_titular: e.target.value }))}
                placeholder="Tu nombre completo"
                className={inputCls}
                style={inputStyle}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                RUT (opcional)
              </label>
              <input
                type="text"
                value={form.rut_titular}
                onChange={e => setForm(f => ({ ...f, rut_titular: e.target.value }))}
                placeholder="12.345.678-9"
                className={inputCls}
                style={inputStyle}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Email de contacto *
            </label>
            <input
              type="email"
              value={form.email_titular}
              onChange={e => setForm(f => ({ ...f, email_titular: e.target.value }))}
              placeholder="tu@email.com"
              className={inputCls}
              style={inputStyle}
            />
            <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
              La empresa usará este email para responder a tu solicitud.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
              Detalle de la solicitud *
            </label>
            <textarea
              value={form.descripcion}
              onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
              rows={4}
              placeholder="Describa de forma clara y específica qué datos desea acceder, corregir, eliminar u oponerse..."
              className={inputCls}
              style={inputStyle}
            />
          </div>

          <div className="rounded-lg p-3" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs" style={{ color: '#6B7280' }}>
              <strong>Nota:</strong> La empresa tiene un plazo <strong>máximo de 10 días hábiles</strong> para responder a tu solicitud,
              conforme al Art. 12 y 14 de la Ley 21.719. Si no recibes respuesta o la respuesta es insatisfactoria,
              puedes presentar un reclamo ante la <strong>APDC</strong> (Agencia de Protección de Datos Personales).
            </p>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
            style={{ background: '#2563EB' }}
          >
            {submitting ? 'Enviando...' : 'Enviar solicitud'}
          </button>
        </form>
      </div>
    </div>
  );
}
