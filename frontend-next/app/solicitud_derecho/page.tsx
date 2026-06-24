'use client';
// QW10: Formulario público ARCO con representantes + archivos + tracking token

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { validarRUT } from '@/components/ui/validation';

const TIPOS_DERECHO = [
  { value: 'acceso', label: 'Acceso', desc: 'Quiero saber qué datos personales tu empresa tiene sobre mí.' },
  { value: 'rectificacion', label: 'Rectificación', desc: 'Quiero corregir datos personales incorrectos o incompletos.' },
  { value: 'cancelacion', label: 'Cancelación', desc: 'Quiero que se eliminen mis datos personales.' },
  { value: 'oposicion', label: 'Oposición', desc: 'Me opongo al tratamiento de mis datos por un motivo legítimo.' },
  { value: 'bloqueo', label: 'Bloqueo temporal', desc: 'Quiero suspender temporalmente el tratamiento de mis datos (Art. 8 ter).' },
  { value: 'portabilidad', label: 'Portabilidad', desc: 'Quiero recibir mis datos en un formato estructurado y de uso común.' },
];

const VALID_TIPOS = ['acceso', 'rectificacion', 'cancelacion', 'oposicion', 'bloqueo', 'portabilidad'];
const MAX_FILES = 5;
const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif'];

interface Company {
  id: number;
  nombre: string;
  rut: string;
}

interface FormErrors {
  companyId?: string;
  tipo?: string;
  nombre_titular?: string;
  rut_titular?: string;
  email_titular?: string;
  descripcion?: string;
  representante_nombre?: string;
  representante_rut?: string;
}

interface SubmitResponse {
  id: number;
  tracking_token: string;
  company_id: number;
  tipo: string;
  nombre_titular: string;
  rut_titular?: string;
  email_titular: string;
  descripcion?: string;
  estado: string;
  solicitud_fecha: string;
  created_at: string;
}

function validarEmail(email: string): boolean {
  return /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(email);
}

function validarNombre(nombre: string): string | undefined {
  if (!nombre.trim()) return 'El nombre es obligatorio.';
  if (nombre.trim().length < 3) return 'El nombre debe tener al menos 3 caracteres.';
  if (nombre.trim().length > 100) return 'El nombre no puede superar los 100 caracteres.';
  return undefined;
}

function validarEmailField(email: string): string | undefined {
  if (!email.trim()) return 'El email es obligatorio.';
  if (!validarEmail(email)) return 'El email no es válido. Ej: nombre@empresa.com';
  return undefined;
}

function validarCompanyId(id: string): string | undefined {
  if (!id) return 'Seleccioná una empresa.';
  if (Number(id) <= 0) return 'Empresa inválida.';
  return undefined;
}

function validarTipo(tipo: string): string | undefined {
  if (!tipo) return 'Seleccioná el tipo de solicitud.';
  if (!VALID_TIPOS.includes(tipo)) return 'Tipo de solicitud inválido.';
  return undefined;
}

export default function SolicitudDerechoPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [tokenLoading, setTokenLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [step, setStep] = useState(1);
  const [rutError, setRutError] = useState('');
  const [repRutError, setRepRutError] = useState('');
  const [token, setToken] = useState('');
  const [tokenError, setTokenError] = useState('');
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<FormErrors>({});
  const [form, setForm] = useState({
    companyId: '',
    tipo: '',
    nombre_titular: '',
    rut_titular: '',
    email_titular: '',
    descripcion: '',
    actAsRepresentative: false,
    representante_nombre: '',
    representante_rut: '',
  });
  const [files, setFiles] = useState<FileList | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResponse | null>(null);

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

  useEffect(() => {
    if (touched.companyId) setErrors(e => ({ ...e, companyId: validarCompanyId(form.companyId) }));
  }, [form.companyId, touched.companyId]);

  useEffect(() => {
    if (touched.nombre_titular) setErrors(e => ({ ...e, nombre_titular: validarNombre(form.nombre_titular) }));
  }, [form.nombre_titular, touched.nombre_titular]);

  useEffect(() => {
    if (touched.email_titular) setErrors(e => ({ ...e, email_titular: validarEmailField(form.email_titular) }));
  }, [form.email_titular, touched.email_titular]);

  useEffect(() => {
    if (touched.descripcion) {
      const msg = form.descripcion.length > 2000 ? 'La descripción no puede superar los 2000 caracteres.' : undefined;
      setErrors(e => ({ ...e, descripcion: msg }));
    }
  }, [form.descripcion, touched.descripcion]);

  const selectedTipo = TIPOS_DERECHO.find(t => t.value === form.tipo);

  function validateAll(): FormErrors {
    return {
      companyId: validarCompanyId(form.companyId),
      tipo: validarTipo(form.tipo),
      nombre_titular: validarNombre(form.nombre_titular),
      rut_titular: form.rut_titular && form.rut_titular.length >= 8
        ? (validarRUT(form.rut_titular).valido ? undefined : 'El RUT no es válido.')
        : undefined,
      email_titular: validarEmailField(form.email_titular),
      descripcion: form.descripcion.length > 2000 ? 'La descripción no puede superar los 2000 caracteres.' : undefined,
      representante_nombre: form.actAsRepresentative && !form.representante_nombre.trim()
        ? 'El nombre del representante es obligatorio.'
        : form.actAsRepresentative && form.representante_nombre.trim().length < 3
          ? 'El nombre del representante debe tener al menos 3 caracteres.'
          : undefined,
      representante_rut: form.actAsRepresentative && form.representante_rut && form.representante_rut.length >= 8
        ? (validarRUT(form.representante_rut).valido ? undefined : 'El RUT del representante no es válido.')
        : undefined,
    };
  }

  function handleBlur(field: string) {
    setTouched(t => ({ ...t, [field]: true }));
    if (field === 'rut_titular' && form.rut_titular && form.rut_titular.length >= 8) {
      const result = validarRUT(form.rut_titular);
      setRutError(result.valido ? '' : result.mensaje);
    }
    if (field === 'representante_rut' && form.representante_rut && form.representante_rut.length >= 8) {
      const result = validarRUT(form.representante_rut);
      setRepRutError(result.valido ? '' : result.mensaje);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched({ companyId: true, tipo: true, nombre_titular: true, rut_titular: true, email_titular: true, descripcion: true, representante_nombre: true, representante_rut: true });
    const allErrors = validateAll();
    setErrors(allErrors);
    if (tokenLoading || !token) {
      toast.error('Esperá el token de seguridad antes de enviar.');
      return;
    }
    const hasErrors = Object.values(allErrors).some(e => e !== undefined);
    if (hasErrors) {
      toast.error('Completá todos los campos obligatorios correctamente.');
      return;
    }
    setSubmitting(true);

    const fd = new FormData();
    fd.append('company_id', String(form.companyId));
    fd.append('tipo', form.tipo);
    fd.append('nombre_titular', form.nombre_titular.trim());
    if (form.rut_titular) fd.append('rut_titular', form.rut_titular);
    fd.append('email_titular', form.email_titular.trim().toLowerCase());
    if (form.descripcion) fd.append('descripcion', form.descripcion);
    fd.append('token', token);
    if (form.actAsRepresentative) {
      fd.append('representante_nombre', form.representante_nombre.trim());
      if (form.representante_rut) fd.append('representante_rut', form.representante_rut);
    }
    if (files) {
      for (let i = 0; i < Math.min(files.length, MAX_FILES); i++) {
        fd.append('files', files[i]);
      }
    }

    fetch(`${API_BASE}/solicitudes-derecho/`, {
      method: 'POST',
      body: fd,
    })
      .then(async r => {
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.detail || 'Error al enviar la solicitud');
        }
        return r.json();
      })
      .then((data: SubmitResponse) => {
        setSubmitResult(data);
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
          {submitResult && (
            <div className="bg-gray-50 rounded-xl p-4 mb-4 text-left">
              <p className="text-xs font-semibold mb-1" style={{ color: '#6B7280' }}>Nº de seguimiento</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-sm font-mono break-all" style={{ color: '#111827' }}>
                  {submitResult.tracking_token}
                </code>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(submitResult.tracking_token).catch(() => {});
                    toast.success('Copiado al portapapeles');
                  }}
                  className="px-2 py-1 rounded text-xs font-medium text-white flex-shrink-0"
                  style={{ backgroundColor: '#2563EB' }}
                >
                  Copiar
                </button>
              </div>
              <p className="text-xs mt-2" style={{ color: '#9CA3AF' }}>
                Guardá este número para consultar el estado de tu solicitud.
              </p>
            </div>
          )}
          <button
            onClick={() => {
              setStep(1);
              setSubmitResult(null);
              setForm(f => ({
                ...f,
                companyId: '',
                tipo: '',
                nombre_titular: '',
                rut_titular: '',
                email_titular: '',
                descripcion: '',
                actAsRepresentative: false,
                representante_nombre: '',
                representante_rut: '',
              }));
              setFiles(null);
            }}
            className="px-6 py-2 rounded-lg text-white font-medium"
            style={{ backgroundColor: '#2563EB' }}
          >
            Hacer otra solicitud
          </button>
          {submitResult && (
            <a
              href={`/solicitud_derecho/consulta?token=${submitResult.tracking_token}`}
              className="block mt-3 text-sm font-medium"
              style={{ color: '#2563EB' }}
            >
              🔍 Consultar estado de mi solicitud
            </a>
          )}
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
          <div
            className="mt-4 rounded-lg p-3 text-xs text-left"
            style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', color: '#1E40AF' }}
            role="note"
            aria-label="Aviso de privacidad"
          >
            <p className="font-semibold mb-1">🔒 Aviso de privacidad</p>
            <p>
              Los datos personales que proporcionés serán tratados únicamente para gestionar tu solicitud de derechos ARCO (Acceso, Rectificación, Cancelación, Oposición, Bloqueo y Portabilidad) conforme a la Ley 21.719. No se compartirán con terceros sin tu consentimiento, salvo obligación legal.
            </p>
          </div>
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
              {touched.tipo && errors.tipo && (
                <p className="text-sm" style={{ color: '#DC2626' }}>{errors.tipo}</p>
              )}
              <button
                type="button"
                onClick={() => {
                  if (!form.tipo) {
                    setTouched(t => ({ ...t, tipo: true }));
                    setErrors(e => ({ ...e, tipo: validarTipo(form.tipo) }));
                    return;
                  }
                  setStep(2);
                }}
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
                    onBlur={() => handleBlur('companyId')}
                    className="w-full p-3 rounded-lg border"
                    style={{ borderColor: touched.companyId && errors.companyId ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                    required
                    aria-required="true"
                    aria-describedby={touched.companyId && errors.companyId ? 'company-error' : undefined}
                  >
                    <option value="">Seleccioná la empresa</option>
                    {companies.map(c => (
                      <option key={c.id} value={c.id}>{c.nombre} ({c.rut})</option>
                    ))}
                  </select>
                )}
                {touched.companyId && errors.companyId && (
                  <p id="company-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{errors.companyId}</p>
                )}
              </div>

              <div>
                <label htmlFor="nombre-titular" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>Tu nombre completo *</label>
                <input
                  id="nombre-titular"
                  type="text"
                  value={form.nombre_titular}
                  onChange={e => setForm(f => ({ ...f, nombre_titular: e.target.value }))}
                  onBlur={() => handleBlur('nombre_titular')}
                  placeholder="Ej: Juan Pérez González"
                  className="w-full p-3 rounded-lg border"
                  style={{ borderColor: touched.nombre_titular && errors.nombre_titular ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                  required
                  aria-required="true"
                  aria-describedby={touched.nombre_titular && errors.nombre_titular ? 'nombre-error' : undefined}
                />
                {touched.nombre_titular && errors.nombre_titular && (
                  <p id="nombre-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{errors.nombre_titular}</p>
                )}
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
                  onBlur={() => handleBlur('rut_titular')}
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
                  onBlur={() => handleBlur('email_titular')}
                  placeholder="Ej: juan@mail.com"
                  className="w-full p-3 rounded-lg border"
                  style={{ borderColor: touched.email_titular && errors.email_titular ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                  required
                  aria-required="true"
                  aria-describedby={touched.email_titular && errors.email_titular ? 'email-error' : undefined}
                />
                {touched.email_titular && errors.email_titular && (
                  <p id="email-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{errors.email_titular}</p>
                )}
              </div>

              <div>
                <label htmlFor="descripcion" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
                  Explicá tu solicitud
                </label>
                <textarea
                  id="descripcion"
                  value={form.descripcion}
                  onChange={e => setForm(f => ({ ...f, descripcion: e.target.value.slice(0, 2000) }))}
                  onBlur={() => handleBlur('descripcion')}
                  maxLength={2000}
                  placeholder="Ej: Quiero saber qué datos personales tienen sobre mí, en particular los relacionados con..."
                  rows={4}
                  className="w-full p-3 rounded-lg border resize-none"
                  style={{ borderColor: touched.descripcion && errors.descripcion ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                  aria-describedby={touched.descripcion && errors.descripcion ? 'descripcion-error' : 'descripcion-hint'}
                />
                {touched.descripcion && errors.descripcion ? (
                  <p id="descripcion-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{errors.descripcion}</p>
                ) : (
                  <p id="descripcion-hint" className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                    Opcional pero recomendable. ({form.descripcion.length}/2000)
                  </p>
                )}
              </div>

              <div className="border-t pt-4">
                <button
                  type="button"
                  onClick={() => setForm(f => ({ ...f, actAsRepresentative: !f.actAsRepresentative }))}
                  className="flex items-center gap-2 text-sm font-medium"
                  style={{ color: '#374151' }}
                >
                  <div
                    className="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: form.actAsRepresentative ? '#2563EB' : 'white', borderColor: form.actAsRepresentative ? '#2563EB' : '#D1D5DB' }}
                  >
                    {form.actAsRepresentative && (
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                  Estoy actuando en representación de un tercero
                </button>

                {form.actAsRepresentative && (
                  <div className="mt-3 pl-6 space-y-3 border-l-2 border-gray-200">
                    <div>
                      <label htmlFor="rep-nombre" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
                        Nombre del titular que represento *
                      </label>
                      <input
                        id="rep-nombre"
                        type="text"
                        value={form.representante_nombre}
                        onChange={e => setForm(f => ({ ...f, representante_nombre: e.target.value }))}
                        onBlur={() => handleBlur('representante_nombre')}
                        placeholder="Ej: Juan Pérez González"
                        className="w-full p-3 rounded-lg border"
                        style={{ borderColor: touched.representante_nombre && errors.representante_nombre ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                        aria-required="true"
                        aria-describedby={touched.representante_nombre && errors.representante_nombre ? 'rep-nombre-error' : undefined}
                      />
                      {touched.representante_nombre && errors.representante_nombre && (
                        <p id="rep-nombre-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{errors.representante_nombre}</p>
                      )}
                    </div>
                    <div>
                      <label htmlFor="rep-rut" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
                        RUT del titular (opcional)
                      </label>
                      <input
                        id="rep-rut"
                        type="text"
                        value={form.representante_rut}
                        onChange={e => {
                          const val = e.target.value;
                          setForm(f => ({ ...f, representante_rut: val }));
                          if (val && val.length >= 8) {
                            const result = validarRUT(val);
                            setRepRutError(result.valido ? '' : result.mensaje);
                          } else {
                            setRepRutError('');
                          }
                        }}
                        onBlur={() => handleBlur('representante_rut')}
                        placeholder="Ej: 12.345.678-5"
                        className="w-full p-3 rounded-lg border"
                        style={{ borderColor: repRutError ? '#DC2626' : '#E5E7EB', outline: 'none' }}
                        aria-describedby={repRutError ? 'rep-rut-error' : undefined}
                      />
                      {repRutError && <p id="rep-rut-error" className="text-xs mt-1" style={{ color: '#DC2626' }}>{repRutError}</p>}
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
                  Documentos adjuntos (opcional)
                </label>
                <label
                  className="flex flex-col items-center justify-center w-full p-4 rounded-lg border-2 border-dashed cursor-pointer transition-colors"
                  style={{ borderColor: '#D1D5DB', backgroundColor: '#FAFAFA' }}
                >
                  <svg className="w-6 h-6 mb-2" style={{ color: '#9CA3AF' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span className="text-sm" style={{ color: '#6B7280' }}>
                    {files && files.length > 0 ? `${files.length} archivo(s) seleccionado(s)` : 'Hacé click para adjuntar archivos'}
                  </span>
                  <span className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                    PDF, JPEG, PNG o GIF — máx 5 archivos de 5MB c/u
                  </span>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.jpg,.jpeg,.png,.gif"
                    className="hidden"
                    onChange={e => {
                      const selected = e.target.files;
                      if (selected) {
                        const valid: File[] = [];
                        let sizeError = false;
                        let typeError = false;
                        for (let i = 0; i < selected.length && valid.length < MAX_FILES; i++) {
                          if (selected[i].size > MAX_FILE_SIZE) sizeError = true;
                          else if (!['application/pdf', 'image/jpeg', 'image/png', 'image/gif'].includes(selected[i].type)) typeError = true;
                          else valid.push(selected[i]);
                        }
                        if (sizeError) toast.error('Uno o más archivos superan los 5MB.');
                        if (typeError) toast.error('Solo se permiten archivos PDF, JPEG, PNG o GIF.');
                        if (valid.length > 0) {
                          const dt = new DataTransfer();
                          valid.forEach(f => dt.items.add(f));
                          setFiles(dt.files);
                        }
                      }
                    }}
                  />
                </label>
                {files && files.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {Array.from(files).map((f, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs" style={{ color: '#374151' }}>
                        <svg className="w-3 h-3 flex-shrink-0" style={{ color: '#059669' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span className="truncate">{f.name}</span>
                        <span className="flex-shrink-0" style={{ color: '#9CA3AF' }}>{(f.size / 1024).toFixed(0)}KB</span>
                      </li>
                    ))}
                  </ul>
                )}
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
