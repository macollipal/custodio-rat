'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { validarRUT } from '@/components/ui/validation';

const TIPOS_DERECHO = [
  { value: 'acceso', label: 'Acceso', desc: 'Quiero saber qué datos personales tu empresa tiene sobre mí.' },
  { value: 'rectificacion', label: 'Rectificación', desc: 'Quiero corregir datos personales incorrectos o incompletos.' },
  { value: 'cancelacion', label: 'Cancelación', desc: 'Quiero que se eliminen mis datos personales.' },
  { value: 'oposicion', label: 'Oposición', desc: 'Me opongo al tratamiento de mis datos por un motivo legítimo.' },
];

interface Company {
  id: number;
  nombre: string;
  rut: string;
}

export default function SolicitudDerechoPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [tokenLoading, setTokenLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [step, setStep] = useState(1);
  const [rutError, setRutError] = useState('');
  const [token, setToken] = useState('');
  const [tokenError, setTokenError] = useState('');
  const [form, setForm] = useState({
    companyId: '',
    tipo: '',
    nombre_titular: '',
    rut_titular: '',
    email_titular: '',
    descripcion: '',
  });

  useEffect(() => {
    fetch(`${API_BASE}/companies/publico`)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setCompanies(data);
        else if (Array.isArray(data.companies)) setCompanies(data.companies);
      })
      .catch(() => toast.error('No se pudieron cargar las empresas.'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    setTokenLoading(true);
    setTokenError('');
    fetch(`${API_BASE}/solicitudes-derecho/token`)
      .then(r => {
        if (!r.ok) throw new Error('Failed to get token');
        return r.json();
      })
      .then(data => setToken(data.token))
      .catch(() => setTokenError('No se pudo obtener token de seguridad. Recargá la página.'))
      .finally(() => setTokenLoading(false));
  }, [step]);

  const selectedTipo = TIPOS_DERECHO.find(t => t.value === form.tipo);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (tokenLoading || !token) {
      toast.error('Esperá el token de seguridad antes de enviar.');
      return;
    }
    if (!form.companyId || !form.tipo || !form.nombre_titular || !form.email_titular) {
      toast.error('Completá todos los campos obligatorios.');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email_titular)) {
      toast.error('Ingresá un email válido.');
      return;
    }
    if (form.rut_titular && form.rut_titular.length >= 8) {
      const result = validarRUT(form.rut_titular);
      if (!result.valido) {
        toast.error('El RUT no es válido: ' + result.mensaje);
        return;
      }
    }
    if (form.descripcion && form.descripcion.length > 2000) {
      toast.error('La descripción no puede superar los 2000 caracteres.');
      return;
    }
    setSubmitting(true);
    fetch(`${API_BASE}/solicitudes-derecho/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_id: Number(form.companyId),
        tipo: form.tipo,
        nombre_titular: form.nombre_titular,
        rut_titular: form.rut_titular || undefined,
        email_titular: form.email_titular,
        descripcion: form.descripcion || undefined,
        token: token,
      }),
    })
      .then(async r => {
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.detail || 'Error al enviar la solicitud');
        }
        return r.json();
      })
      .then(() => {
        setStep(3);
      })
      .catch(err => {
        toast.error(err.message || 'Error al enviar la solicitud. Intentá de nuevo.');
      })
      .finally(() => setSubmitting(false));
  }

  if (step === 3) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F9FAFB' }}>
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#111827' }}>Solicitud enviada</h1>
          <p className="mb-4" style={{ color: '#6B7280' }}>
            Tu solicitud de {selectedTipo?.label} fue enviada correctamente. La empresa te responderá a tu email.
          </p>
          <button
            onClick={() => setStep(1)}
            className="px-6 py-2 rounded-lg text-white font-medium"
            style={{ backgroundColor: '#2563EB' }}
          >
            Hacer otra solicitud
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F9FAFB' }}>
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#111827' }}>Ejercé tus derechos ARCO</h1>
          <p className="text-base" style={{ color: '#6B7280' }}>
            Ley 21.719 — Protección de Datos Personales de Chile
          </p>
          <div className="mt-3 flex items-center justify-center gap-2">
            {['1', '2'].map(s => (
              <div key={s} className="flex items-center gap-2">
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold text-white"
                  style={{ backgroundColor: Number(s) <= step ? '#2563EB' : '#D1D5DB' }}
                >
                  {s}
                </div>
                <div className="w-8 h-0.5" style={{ backgroundColor: Number(s) < step ? '#2563EB' : '#D1D5DB' }} />
              </div>
            ))}
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold text-white"
              style={{ backgroundColor: Number(2) <= step ? '#2563EB' : '#D1D5DB' }}
            >
              {2}
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm p-8 space-y-6">
          {step === 1 && (
            <>
              <h2 className="text-xl font-semibold" style={{ color: '#111827' }}>¿Qué derecho querés ejercer?</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {TIPOS_DERECHO.map(tipo => (
                  <button
                    key={tipo.value}
                    type="button"
                    onClick={() => setForm(f => ({ ...f, tipo: tipo.value }))}
                    className="p-4 rounded-xl border-2 text-left transition-all"
                    style={{
                      borderColor: form.tipo === tipo.value ? '#2563EB' : '#E5E7EB',
                      backgroundColor: form.tipo === tipo.value ? '#EFF6FF' : 'white',
                    }}
                  >
                    <div className="font-semibold" style={{ color: '#111827' }}>{tipo.label}</div>
                    <div className="text-xs mt-1" style={{ color: '#6B7280' }}>{tipo.desc}</div>
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={() => form.tipo && setStep(2)}
                disabled={!form.tipo}
                className="w-full py-3 rounded-lg text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ backgroundColor: form.tipo ? '#2563EB' : '#9CA3AF' }}
              >
                Continuar
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="text-xl font-semibold" style={{ color: '#111827' }}>Tus datos</h2>

              {tokenError && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm" role="alert">
                  {tokenError}
                </div>
              )}

              <div>
                <label htmlFor="company-select" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>Empresa *</label>
                {loading ? (
                  <div className="p-3 rounded-lg" style={{ backgroundColor: '#F3F4F6' }}>Cargando empresas...</div>
                ) : (
                  <select
                    id="company-select"
                    value={form.companyId}
                    onChange={e => setForm(f => ({ ...f, companyId: e.target.value }))}
                    className="w-full p-3 rounded-lg border"
                    style={{ borderColor: '#E5E7EB', outline: 'none' }}
                    required
                    aria-required="true"
                  >
                    <option value="">Seleccioná la empresa</option>
                    {companies.map(c => (
                      <option key={c.id} value={c.id}>{c.nombre} ({c.rut})</option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <label htmlFor="nombre-titular" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>Tu nombre completo *</label>
                <input
                  id="nombre-titular"
                  type="text"
                  value={form.nombre_titular}
                  onChange={e => setForm(f => ({ ...f, nombre_titular: e.target.value }))}
                  placeholder="Ej: Juan Pérez González"
                  className="w-full p-3 rounded-lg border"
                  style={{ borderColor: '#E5E7EB', outline: 'none' }}
                  required
                  aria-required="true"
                />
              </div>

              <div>
                <label htmlFor="rut-titular" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>Tu RUT (opcional)</label>
                <input
                  id="rut-titular"
                  type="text"
                  value={form.rut_titular}
                  onChange={e => {
                    const val = e.target.value;
                    setForm(f => ({ ...f, rut_titular: val }));
                    if (val && val.length >= 8) {
                      const result = validarRUT(val);
                      setRutError(result.valido ? '' : result.mensaje);
                    } else {
                      setRutError('');
                    }
                  }}
                  onBlur={() => {
                    if (form.rut_titular && form.rut_titular.length >= 8) {
                      const result = validarRUT(form.rut_titular);
                      setRutError(result.valido ? '' : result.mensaje);
                    }
                  }}
                  placeholder="Ej: 12.345.678-5"
                  className="w-full p-3 rounded-lg border"
                  style={{ borderColor: rutError ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                  aria-describedby={rutError ? 'rut-error' : undefined}
                />
                {rutError && <p id="rut-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{rutError}</p>}
              </div>

              <div>
                <label htmlFor="email-titular" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>Tu email *</label>
                <input
                  id="email-titular"
                  type="email"
                  value={form.email_titular}
                  onChange={e => setForm(f => ({ ...f, email_titular: e.target.value }))}
                  placeholder="Ej: juan@mail.com"
                  className="w-full p-3 rounded-lg border"
                  style={{ borderColor: '#E5E7EB', outline: 'none' }}
                  required
                  aria-required="true"
                />
              </div>

              <div>
                <label htmlFor="descripcion" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
                  Explicá tu solicitud
                </label>
                <textarea
                  id="descripcion"
                  value={form.descripcion}
                  onChange={e => setForm(f => ({ ...f, descripcion: e.target.value.slice(0, 2000) }))}
                  maxLength={2000}
                  placeholder="Ej: Quiero saber qué datos personales tienen sobre mí, en particular los relacionados con..."
                  rows={4}
                  className="w-full p-3 rounded-lg border resize-none"
                  style={{ borderColor: '#E5E7EB', outline: 'none' }}
                  aria-describedby="descripcion-hint"
                />
                <p id="descripcion-hint" className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                  Opcional pero recomendable. ({form.descripcion.length}/2000)
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 rounded-lg border font-semibold"
                  style={{ borderColor: '#E5E7EB', color: '#374151' }}
                >
                  Volver
                </button>
                <button
                  type="submit"
                  disabled={submitting || tokenLoading || !token}
                  className="flex-1 py-3 rounded-lg text-white font-semibold disabled:opacity-50"
                  style={{ backgroundColor: '#059669' }}
                >
                  {submitting ? 'Enviando...' : 'Enviar solicitud'}
                </button>
              </div>
            </>
          )}
        </form>

        <div className="mt-6 text-center text-xs" style={{ color: '#9CA3AF' }}>
          <p>El responsable de tratamiento debe responder en un plazo máximo de <strong>10 días hábiles</strong> (Art. 14 Ley 21.719).</p>
        </div>
      </div>
    </div>
  );
}
