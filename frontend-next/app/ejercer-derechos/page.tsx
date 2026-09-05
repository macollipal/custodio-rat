'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  getEmpresasPublicas,
  ejercerDerechoPublico,
  verificarTitularPublico,
  type EmpresaPublica,
  type EjercerDerechosPayload,
} from '@/lib/api';
import { useEffect } from 'react';

// ── Tipos ARCOP+ ──────────────────────────────────────────────────────────────

const TIPOS = [
  {
    value: 'acceso',
    label: 'Acceso',
    icon: '👁️',
    desc: 'Conocer qué datos tiene la empresa sobre ti',
    art: 'Art. 8 lit. a',
  },
  {
    value: 'rectificacion',
    label: 'Rectificación',
    icon: '✏️',
    desc: 'Corregir datos incorrectos o desactualizados',
    art: 'Art. 9',
  },
  {
    value: 'cancelacion',
    label: 'Cancelación',
    icon: '🗑️',
    desc: 'Solicitar la eliminación o supresión de tus datos',
    art: 'Art. 8 lit. c',
  },
  {
    value: 'oposicion',
    label: 'Oposición',
    icon: '🚫',
    desc: 'Oponerte a un tratamiento específico de tus datos',
    art: 'Art. 13',
  },
  {
    value: 'bloqueo',
    label: 'Bloqueo',
    icon: '🔒',
    desc: 'Suspender temporalmente el uso de tus datos',
    art: 'Art. 8 ter',
  },
  {
    value: 'portabilidad',
    label: 'Portabilidad',
    icon: '📦',
    desc: 'Recibir tus datos en formato estructurado',
    art: 'Art. 12',
  },
] as const;

type TipoArco = (typeof TIPOS)[number]['value'];

// ── Estado del formulario ─────────────────────────────────────────────────────

interface FormState {
  company_id: string;
  tipo: TipoArco | '';
  titular_nombre: string;
  titular_email: string;
  titular_email_confirm: string;
  titular_rut: string;
  descripcion: string;
  telefono: string;
  con_representante: boolean;
  representante_nombre: string;
  representante_rut: string;
  representante_poder_notarial_notas: string;
}

const INITIAL: FormState = {
  company_id: '',
  tipo: '',
  titular_nombre: '',
  titular_email: '',
  titular_email_confirm: '',
  titular_rut: '',
  descripcion: '',
  telefono: '',
  con_representante: false,
  representante_nombre: '',
  representante_rut: '',
  representante_poder_notarial_notas: '',
};

// ── Validación RUT chileno (QW1) ──────────────────────────────────────────────

function formatRut(raw: string): string {
  const v = raw.replace(/[^0-9kK]/g, '').toUpperCase();
  if (v.length <= 1) return v;
  const dv = v.slice(-1);
  const num = v.slice(0, -1).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${num}-${dv}`;
}

function validarRut(rut: string): boolean {
  if (!rut.trim()) return true; // campo opcional
  const clean = rut.replace(/[^0-9kK]/g, '').toUpperCase();
  if (clean.length < 2) return false;
  const dv = clean.slice(-1);
  const num = parseInt(clean.slice(0, -1), 10);
  if (isNaN(num)) return false;
  let sum = 0, factor = 2, n = num;
  while (n > 0) {
    sum += (n % 10) * factor;
    n = Math.floor(n / 10);
    factor = factor === 7 ? 2 : factor + 1;
  }
  const rem = 11 - (sum % 11);
  const expected = rem === 11 ? '0' : rem === 10 ? 'K' : String(rem);
  return dv === expected;
}

// ── Stepper ───────────────────────────────────────────────────────────────────

const STEPS = ['Tu derecho', 'Tus datos', 'Enviar'];

function Stepper({ step }: { step: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 32, justifyContent: 'center' }}>
      {STEPS.map((label, i) => {
        const done = i < step;
        const active = i === step;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
              <div style={{
                width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: done ? '#059669' : active ? '#1E40AF' : '#E5E7EB',
                color: done || active ? 'white' : '#9CA3AF',
                fontSize: 13, fontWeight: 700, transition: 'all 0.2s',
              }}>
                {done ? '✓' : i + 1}
              </div>
              <span style={{ fontSize: 11, color: active ? '#1E40AF' : done ? '#059669' : '#9CA3AF', fontWeight: active ? 700 : 400, whiteSpace: 'nowrap' }}>
                {label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ width: 60, height: 2, background: done ? '#059669' : '#E5E7EB', margin: '0 4px', marginBottom: 20, transition: 'background 0.2s' }} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Pantalla intro (QW3) ──────────────────────────────────────────────────────

function IntroScreen({ onContinuar }: { onContinuar: () => void }) {
  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB', padding: '32px 16px' }}>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'linear-gradient(135deg, #1E40AF, #3730A3)',
            borderRadius: 12, padding: '10px 20px', marginBottom: 20,
          }}>
            <span style={{ color: 'white', fontWeight: 700, fontSize: 13 }}>Ley 21.719 — Art. 12</span>
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#111827', marginBottom: 8 }}>
            Tus derechos sobre tus datos personales
          </h1>
          <p style={{ color: '#6B7280', fontSize: 15, maxWidth: 500, margin: '0 auto' }}>
            La Ley 21.719 de Chile te otorga derechos sobre cómo las empresas tratan tu información personal.
            Puedes ejercerlos de forma gratuita.
          </p>
        </div>

        {/* Glosario de derechos */}
        <div style={{ background: 'white', borderRadius: 16, padding: 28, border: '1px solid #E5E7EB', marginBottom: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
          <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1E40AF', marginBottom: 20 }}>¿Qué puedes solicitar?</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
            {TIPOS.map(t => (
              <div key={t.value} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '12px 14px', borderRadius: 10, background: '#F9FAFB', border: '1px solid #F3F4F6' }}>
                <span style={{ fontSize: 22, lineHeight: 1 }}>{t.icon}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#111827' }}>{t.label}</div>
                  <div style={{ fontSize: 12, color: '#6B7280', marginTop: 2 }}>{t.desc}</div>
                  <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 4 }}>{t.art} Ley 21.719</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Info del proceso */}
        <div style={{ background: '#EFF6FF', borderRadius: 12, padding: '16px 20px', marginBottom: 28, border: '1px solid #BFDBFE' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 16 }}>
            {[
              { icon: '⏱️', title: '10 días hábiles', desc: 'Plazo máximo de respuesta' },
              { icon: '🆓', title: 'Sin costo', desc: 'El trámite es completamente gratuito' },
              { icon: '🔒', title: 'Privado y seguro', desc: 'Tus datos están protegidos' },
              { icon: '📧', title: 'Seguimiento', desc: 'Recibirás un código para rastrear tu solicitud' },
            ].map((item, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 24, marginBottom: 6 }}>{item.icon}</div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#1E40AF' }}>{item.title}</div>
                <div style={{ fontSize: 12, color: '#6B7280' }}>{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={onContinuar}
          style={{
            width: '100%', padding: '14px 32px', borderRadius: 10, fontWeight: 700, fontSize: 15,
            background: '#1E40AF', color: 'white', border: 'none', cursor: 'pointer',
          }}
        >
          Continuar con mi solicitud →
        </button>
        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 12, color: '#9CA3AF' }}>
          Al continuar, confirmas haber leído la información sobre el proceso
        </p>
      </div>
    </div>
  );
}

// ── Componente principal ──────────────────────────────────────────────────────

export default function EjercerDerechosPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: '100vh', background: '#F9FAFB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><span style={{ color: '#6B7280' }}>Cargando…</span></div>}>
      <EjercerDerechosInner />
    </Suspense>
  );
}

function EjercerDerechosInner() {
  const searchParams = useSearchParams();
  const [view, setView] = useState<'intro' | 'step0' | 'step1' | 'step2'>('intro');
  const [empresas, setEmpresas] = useState<EmpresaPublica[]>([]);
  const [form, setForm] = useState<FormState>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ token: string; mensaje: string } | null>(null);
  const [globalError, setGlobalError] = useState('');
  const [ticketsAbiertos, setTicketsAbiertos] = useState<number | null>(null);

  useEffect(() => {
    getEmpresasPublicas()
      .then(setEmpresas)
      .catch(() => setGlobalError('No se pudo cargar la lista de empresas. Intente más tarde.'));
    const empresaParam = searchParams.get('empresa');
    if (empresaParam) setForm(f => ({ ...f, company_id: empresaParam }));
  }, [searchParams]);

  function set(field: keyof FormState, value: string | boolean) {
    setForm(f => ({ ...f, [field]: value }));
    setErrors(e => { const n = { ...e }; delete n[field]; return n; });
  }

  function handleRutChange(field: 'titular_rut' | 'representante_rut', raw: string) {
    const formatted = formatRut(raw);
    set(field, formatted);
  }

  async function handleEmailBlur() {
    const email = form.titular_email.trim();
    const companyId = Number(form.company_id);
    if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/) || !companyId) return;
    try {
      const res = await verificarTitularPublico(companyId, email);
      setTicketsAbiertos(res.tiene_tickets_abiertos ? res.cantidad : null);
    } catch {
      // silencioso — no bloquear el flujo por un check informativo
    }
  }

  function handleRutBlur(field: 'titular_rut' | 'representante_rut') {
    const val = form[field];
    if (val && !validarRut(val)) {
      setErrors(e => ({ ...e, [field]: 'RUN inválido — verifica el dígito verificador' }));
    }
  }

  // Validación por paso
  function validateStep0(): boolean {
    const e: Partial<Record<keyof FormState, string>> = {};
    if (!form.company_id) e.company_id = 'Selecciona una empresa';
    if (!form.tipo) e.tipo = 'Selecciona el tipo de solicitud';
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  function validateStep1(): boolean {
    const e: Partial<Record<keyof FormState, string>> = {};
    if (!form.titular_nombre.trim() || form.titular_nombre.trim().length < 2)
      e.titular_nombre = 'Nombre requerido (mín. 2 caracteres)';
    if (!form.titular_email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/))
      e.titular_email = 'Email inválido';
    if (!form.titular_email_confirm.trim())
      e.titular_email_confirm = 'Confirma tu email';
    else if (form.titular_email !== form.titular_email_confirm)
      e.titular_email_confirm = 'Los emails no coinciden';
    if (form.titular_rut && !validarRut(form.titular_rut))
      e.titular_rut = 'RUN inválido — verifica el dígito verificador';
    if (!form.descripcion.trim() || form.descripcion.trim().length < 10)
      e.descripcion = 'Describe tu solicitud (mín. 10 caracteres)';
    if (form.con_representante) {
      if (!form.representante_nombre.trim()) e.representante_nombre = 'Nombre del representante requerido';
      if (form.representante_rut && !validarRut(form.representante_rut))
        e.representante_rut = 'RUN del representante inválido';
      if (!form.representante_poder_notarial_notas.trim())
        e.representante_poder_notarial_notas = 'Indica la referencia del poder notarial';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  function handleNext0() {
    if (validateStep0()) setView('step1');
  }

  function handleNext1() {
    if (validateStep1()) setView('step2');
  }

  async function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault();
    setSubmitting(true);
    setGlobalError('');
    try {
      const payload: EjercerDerechosPayload = {
        company_id: Number(form.company_id),
        tipo: form.tipo as TipoArco,
        titular_nombre: form.titular_nombre.trim(),
        titular_email: form.titular_email.trim(),
        descripcion: form.descripcion.trim(),
        ...(form.titular_rut.trim() && { titular_rut: form.titular_rut.trim() }),
        ...(form.telefono.trim() && { telefono: form.telefono.trim() }),
        ...(form.con_representante && {
          representante_nombre: form.representante_nombre.trim(),
          representante_rut: form.representante_rut.trim() || undefined,
          representante_poder_notarial_notas: form.representante_poder_notarial_notas.trim(),
        }),
      };
      const res = await ejercerDerechoPublico(payload);
      setResult({ token: res.tracking_token, mensaje: res.mensaje });
    } catch (err) {
      setGlobalError(err instanceof Error ? err.message : 'Error al enviar la solicitud. Intente nuevamente.');
      setView('step1');
    } finally {
      setSubmitting(false);
    }
  }

  const empresaSeleccionada = empresas.find(e => String(e.id) === form.company_id);
  const tipoSeleccionado = TIPOS.find(t => t.value === form.tipo);

  // ── Pantalla intro ──
  if (view === 'intro') return <IntroScreen onContinuar={() => setView('step0')} />;

  // ── Pantalla de éxito ──
  if (result) {
    return (
      <div style={{ minHeight: '100vh', background: '#F9FAFB', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
        <div style={{ maxWidth: 560, width: '100%', background: 'white', borderRadius: 16, padding: 40, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', textAlign: 'center' }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#D1FAE5', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', fontSize: 28 }}>✓</div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', marginBottom: 12 }}>Solicitud Enviada</h1>
          <p style={{ color: '#6B7280', fontSize: 15, lineHeight: 1.6, marginBottom: 28 }}>{result.mensaje}</p>
          <div style={{ background: '#F3F4F6', borderRadius: 12, padding: '16px 20px', marginBottom: 12 }}>
            <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Código de seguimiento</p>
            <p style={{ fontFamily: 'monospace', fontSize: 16, fontWeight: 700, color: '#111827', wordBreak: 'break-all' }}>{result.token}</p>
          </div>
          <p style={{ fontSize: 12, color: '#9CA3AF', marginBottom: 24 }}>
            Guarda este código. Lo necesitarás para consultar el estado de tu solicitud.
          </p>
          <a
            href={`/seguimiento?token=${result.token}`}
            style={{
              display: 'inline-block', padding: '12px 28px', borderRadius: 8,
              background: '#1E40AF', color: 'white', fontWeight: 600, fontSize: 14, textDecoration: 'none',
            }}
          >
            Ver estado de mi solicitud
          </a>
          <p style={{ marginTop: 20, fontSize: 12, color: '#9CA3AF' }}>
            Plazo máximo de respuesta: <strong>10 días hábiles</strong> · Ley 21.719 Art. 12
          </p>
        </div>
      </div>
    );
  }

  const stepNumber = view === 'step0' ? 0 : view === 'step1' ? 1 : 2;

  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB', padding: '32px 16px' }}>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: 28, textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'linear-gradient(135deg, #1E40AF, #3730A3)', borderRadius: 12, padding: '10px 20px', marginBottom: 16 }}>
            <span style={{ color: 'white', fontWeight: 700, fontSize: 13 }}>Ley 21.719 — Art. 12</span>
          </div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#111827', marginBottom: 4 }}>Ejercer mis Derechos ARCOP+</h1>
        </div>

        {/* Stepper (QW9) */}
        <Stepper step={stepNumber} />

        {/* ── PASO 0: Empresa + Tipo ── */}
        {view === 'step0' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <Section title="¿A qué empresa diriges tu solicitud?">
              <select
                value={form.company_id}
                onChange={e => set('company_id', e.target.value)}
                style={selectStyle(!!errors.company_id)}
                aria-label="Empresa"
              >
                <option value="">— Elige la empresa —</option>
                {empresas.map(emp => (
                  <option key={emp.id} value={String(emp.id)}>{emp.nombre}</option>
                ))}
              </select>
              {errors.company_id && <p style={errorStyle}>{errors.company_id}</p>}
              {empresaSeleccionada && (
                <p style={{ fontSize: 13, color: '#059669', fontWeight: 600, marginTop: 6 }}>
                  ✓ {empresaSeleccionada.nombre}
                </p>
              )}
            </Section>

            <Section title="¿Qué derecho quieres ejercer?">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10 }}>
                {TIPOS.map(t => (
                  <button
                    key={t.value}
                    type="button"
                    onClick={() => set('tipo', t.value)}
                    style={{
                      padding: '12px 14px', borderRadius: 10, textAlign: 'left', cursor: 'pointer',
                      border: `2px solid ${form.tipo === t.value ? '#1E40AF' : '#E5E7EB'}`,
                      background: form.tipo === t.value ? '#EFF6FF' : 'white',
                      transition: 'all 0.15s',
                    }}
                  >
                    <div style={{ fontSize: 20, marginBottom: 4 }}>{t.icon}</div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: form.tipo === t.value ? '#1E40AF' : '#111827' }}>{t.label}</div>
                    <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 2 }}>{t.desc}</div>
                    <div style={{ fontSize: 10, color: '#D1D5DB', marginTop: 3 }}>{t.art}</div>
                  </button>
                ))}
              </div>
              {errors.tipo && <p style={errorStyle}>{errors.tipo}</p>}
            </Section>

            {globalError && <ErrorBanner msg={globalError} />}

            <div style={{ display: 'flex', gap: 12 }}>
              <button
                type="button"
                onClick={() => setView('intro')}
                style={{ padding: '12px 20px', borderRadius: 10, fontWeight: 600, fontSize: 14, background: 'white', color: '#374151', border: '1px solid #D1D5DB', cursor: 'pointer' }}
              >
                ← Volver
              </button>
              <button
                type="button"
                onClick={handleNext0}
                style={{ flex: 1, padding: '13px 20px', borderRadius: 10, fontWeight: 700, fontSize: 15, background: '#1E40AF', color: 'white', border: 'none', cursor: 'pointer' }}
              >
                Continuar →
              </button>
            </div>
          </div>
        )}

        {/* ── PASO 1: Datos personales + Descripción ── */}
        {view === 'step1' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {tipoSeleccionado && (
              <div style={{ background: '#EFF6FF', borderRadius: 10, padding: '10px 16px', border: '1px solid #BFDBFE', fontSize: 13, color: '#1E40AF', fontWeight: 600 }}>
                {tipoSeleccionado.icon} Solicitud de <strong>{tipoSeleccionado.label}</strong> — {tipoSeleccionado.art}
              </div>
            )}

            <Section title="Tus datos de contacto">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <Field label="Nombre completo *" error={errors.titular_nombre} style={{ gridColumn: '1 / -1' }}>
                  <input
                    value={form.titular_nombre}
                    onChange={e => set('titular_nombre', e.target.value)}
                    placeholder="Ej: María González Pérez"
                    style={inputStyle(!!errors.titular_nombre)}
                    autoComplete="name"
                  />
                </Field>

                <Field label="Email *" error={errors.titular_email}>
                  <input
                    type="email"
                    value={form.titular_email}
                    onChange={e => { set('titular_email', e.target.value); setTicketsAbiertos(null); }}
                    onBlur={handleEmailBlur}
                    placeholder="tu@email.com"
                    style={inputStyle(!!errors.titular_email)}
                    autoComplete="email"
                  />
                </Field>

                {/* QW4: confirmación de email */}
                <Field label="Confirmar email *" error={errors.titular_email_confirm}>
                  <input
                    type="email"
                    value={form.titular_email_confirm}
                    onChange={e => set('titular_email_confirm', e.target.value)}
                    placeholder="Repite tu email"
                    style={inputStyle(!!errors.titular_email_confirm)}
                    autoComplete="off"
                    onPaste={e => e.preventDefault()}
                  />
                </Field>

                {/* QW1: RUT con formateo automático */}
                <Field label="RUN (opcional)" error={errors.titular_rut} hint="Ej: 12.345.678-9">
                  <input
                    value={form.titular_rut}
                    onChange={e => handleRutChange('titular_rut', e.target.value)}
                    onBlur={() => handleRutBlur('titular_rut')}
                    placeholder="12.345.678-9"
                    style={inputStyle(!!errors.titular_rut)}
                    maxLength={12}
                    autoComplete="off"
                  />
                </Field>

                <Field label="Teléfono (opcional)" error={errors.telefono} hint="Ej: +56 9 1234 5678">
                  <input
                    value={form.telefono}
                    onChange={e => set('telefono', e.target.value)}
                    placeholder="+56 9 1234 5678"
                    style={inputStyle(false)}
                    autoComplete="tel"
                  />
                </Field>
              </div>
            </Section>

            <Section title="Describe tu solicitud">
              <Field label="¿Qué solicitas exactamente? *" error={errors.descripcion} hint="Sé específico/a: menciona el sistema, la campaña o el dato concreto al que te refieres.">
                <textarea
                  value={form.descripcion}
                  onChange={e => set('descripcion', e.target.value)}
                  rows={5}
                  placeholder={
                    form.tipo === 'acceso' ? 'Ej: Solicito conocer qué datos personales tienen registrados sobre mí en su sistema de clientes.' :
                    form.tipo === 'rectificacion' ? 'Ej: Mi dirección registrada es incorrecta. La correcta es...' :
                    form.tipo === 'cancelacion' ? 'Ej: Solicito eliminar todos mis datos de su base de datos de marketing.' :
                    form.tipo === 'oposicion' ? 'Ej: Me opongo a que usen mis datos para el envío de publicidad.' :
                    'Explica con detalle qué solicitas...'
                  }
                  style={{ ...inputStyle(!!errors.descripcion), resize: 'vertical' }}
                  maxLength={2000}
                />
              </Field>
              <p style={{ fontSize: 12, color: form.descripcion.length > 1800 ? '#DC2626' : '#9CA3AF', marginTop: 4 }}>
                {form.descripcion.length}/2000 caracteres
              </p>
            </Section>

            <Section title="Representante (opcional)">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', marginBottom: 12 }}>
                <input type="checkbox" checked={form.con_representante} onChange={e => set('con_representante', e.target.checked)} style={{ width: 18, height: 18 }} />
                <span style={{ fontSize: 14, color: '#374151' }}>Actúo como representante de otra persona</span>
              </label>
              {form.con_representante && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, paddingTop: 8 }}>
                  <Field label="Nombre del representante *" error={errors.representante_nombre} style={{ gridColumn: '1 / -1' }}>
                    <input value={form.representante_nombre} onChange={e => set('representante_nombre', e.target.value)} placeholder="Nombre completo" style={inputStyle(!!errors.representante_nombre)} />
                  </Field>
                  <Field label="RUN del representante" error={errors.representante_rut} hint="Ej: 12.345.678-9">
                    <input
                      value={form.representante_rut}
                      onChange={e => handleRutChange('representante_rut', e.target.value)}
                      onBlur={() => handleRutBlur('representante_rut')}
                      placeholder="12.345.678-9"
                      style={inputStyle(!!errors.representante_rut)}
                      maxLength={12}
                    />
                  </Field>
                  <Field label="Referencia del poder notarial *" error={errors.representante_poder_notarial_notas} style={{ gridColumn: '1 / -1' }} hint="Indica número de escritura, notaría y fecha (Art. 14 quater Ley 21.719)">
                    <textarea value={form.representante_poder_notarial_notas} onChange={e => set('representante_poder_notarial_notas', e.target.value)} rows={3} placeholder="Ej: Escritura N° 1234 de fecha 01/01/2026 ante Notario Juan Pérez de Santiago" style={{ ...inputStyle(!!errors.representante_poder_notarial_notas), resize: 'vertical' }} />
                  </Field>
                </div>
              )}
            </Section>

            {ticketsAbiertos !== null && (
              <div style={{ padding: '12px 16px', borderRadius: 8, background: '#FFFBEB', border: '1px solid #FCD34D', color: '#92400E', fontSize: 14, display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <span style={{ fontSize: 18, lineHeight: 1 }}>⚠️</span>
                <div>
                  <strong>Ya tienes {ticketsAbiertos === 1 ? 'una solicitud abierta' : `${ticketsAbiertos} solicitudes abiertas`} para esta empresa.</strong>
                  <p style={{ margin: '4px 0 0', fontSize: 13 }}>
                    Puedes continuar de todos modos si tu nueva solicitud es diferente. Revisa el estado de tu solicitud anterior usando el código de seguimiento que recibiste.
                  </p>
                </div>
              </div>
            )}

            {globalError && <ErrorBanner msg={globalError} />}

            <div style={{ display: 'flex', gap: 12 }}>
              <button type="button" onClick={() => setView('step0')} style={{ padding: '12px 20px', borderRadius: 10, fontWeight: 600, fontSize: 14, background: 'white', color: '#374151', border: '1px solid #D1D5DB', cursor: 'pointer' }}>
                ← Volver
              </button>
              <button type="button" onClick={handleNext1} style={{ flex: 1, padding: '13px 20px', borderRadius: 10, fontWeight: 700, fontSize: 15, background: '#1E40AF', color: 'white', border: 'none', cursor: 'pointer' }}>
                Revisar solicitud →
              </button>
            </div>
          </div>
        )}

        {/* ── PASO 2: Revisión + Envío ── */}
        {view === 'step2' && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <Section title="Resumen de tu solicitud">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <ResumenRow label="Empresa" value={empresaSeleccionada?.nombre ?? form.company_id} />
                <ResumenRow label="Tipo" value={tipoSeleccionado ? `${tipoSeleccionado.icon} ${tipoSeleccionado.label} (${tipoSeleccionado.art})` : form.tipo} />
                <ResumenRow label="Nombre" value={form.titular_nombre} />
                <ResumenRow label="Email" value={form.titular_email} />
                {form.titular_rut && <ResumenRow label="RUN" value={form.titular_rut} />}
                {form.telefono && <ResumenRow label="Teléfono" value={form.telefono} />}
                <div style={{ borderTop: '1px solid #F3F4F6', paddingTop: 12 }}>
                  <p style={{ fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 4 }}>DESCRIPCIÓN</p>
                  <p style={{ fontSize: 14, color: '#111827', lineHeight: 1.6 }}>{form.descripcion}</p>
                </div>
                {form.con_representante && (
                  <div style={{ borderTop: '1px solid #F3F4F6', paddingTop: 12 }}>
                    <p style={{ fontSize: 12, fontWeight: 600, color: '#6B7280', marginBottom: 4 }}>REPRESENTANTE</p>
                    <ResumenRow label="Nombre" value={form.representante_nombre} />
                    {form.representante_rut && <ResumenRow label="RUN" value={form.representante_rut} />}
                  </div>
                )}
              </div>
            </Section>

            <div style={{ background: '#FFFBEB', border: '1px solid #FCD34D', borderRadius: 10, padding: '12px 16px', fontSize: 13, color: '#92400E' }}>
              ⚠️ Al enviar confirmas que la información es verdadera y que autorizas su uso para procesar tu solicitud conforme a la Ley 21.719.
            </div>

            {globalError && <ErrorBanner msg={globalError} />}

            <div style={{ display: 'flex', gap: 12 }}>
              <button type="button" onClick={() => setView('step1')} style={{ padding: '12px 20px', borderRadius: 10, fontWeight: 600, fontSize: 14, background: 'white', color: '#374151', border: '1px solid #D1D5DB', cursor: 'pointer' }}>
                ← Editar
              </button>
              <button
                type="submit"
                disabled={submitting}
                style={{
                  flex: 1, padding: '13px 20px', borderRadius: 10, fontWeight: 700, fontSize: 15,
                  background: submitting ? '#93C5FD' : '#059669', color: 'white',
                  border: 'none', cursor: submitting ? 'not-allowed' : 'pointer', transition: 'background 0.15s',
                }}
              >
                {submitting ? 'Enviando…' : '✓ Confirmar y enviar solicitud'}
              </button>
            </div>

            <p style={{ textAlign: 'center', fontSize: 12, color: '#9CA3AF' }}>
              Recibirás un código de seguimiento al completar el envío · Plazo: 10 días hábiles (Art. 12 Ley 21.719)
            </p>
          </form>
        )}

        <div style={{ marginTop: 40, textAlign: 'center', fontSize: 12, color: '#D1D5DB' }}>
          Custodio RAT Manager · Ley 21.719 de Chile
        </div>
      </div>
    </div>
  );
}

// ── Componentes auxiliares ────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: 'white', borderRadius: 12, padding: '24px', border: '1px solid #E5E7EB', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
      <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1E40AF', marginBottom: 16 }}>{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, error, hint, children, style }: { label: string; error?: string; hint?: string; children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={style}>
      <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 6 }}>{label}</label>
      {children}
      {hint && !error && <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{hint}</p>}
      {error && <p style={errorStyle}>{error}</p>}
    </div>
  );
}

function ResumenRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'baseline' }}>
      <span style={{ fontSize: 12, fontWeight: 600, color: '#6B7280', minWidth: 80 }}>{label}</span>
      <span style={{ fontSize: 14, color: '#111827' }}>{value || '—'}</span>
    </div>
  );
}

function ErrorBanner({ msg }: { msg: string }) {
  return (
    <div style={{ padding: '12px 16px', borderRadius: 8, background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626', fontSize: 14 }}>
      {msg}
    </div>
  );
}

const errorStyle: React.CSSProperties = { fontSize: 12, color: '#DC2626', marginTop: 4 };

function inputStyle(hasError: boolean): React.CSSProperties {
  return {
    width: '100%', padding: '10px 12px', borderRadius: 8, fontSize: 14,
    border: `1px solid ${hasError ? '#FCA5A5' : '#D1D5DB'}`,
    outline: 'none', background: 'white', color: '#111827', boxSizing: 'border-box',
  };
}

function selectStyle(hasError: boolean): React.CSSProperties {
  return { ...inputStyle(hasError), cursor: 'pointer', appearance: 'auto' };
}
