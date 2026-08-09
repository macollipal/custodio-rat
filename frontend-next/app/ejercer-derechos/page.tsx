'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  getEmpresasPublicas,
  ejercerDerechoPublico,
  type EmpresaPublica,
  type EjercerDerechosPayload,
} from '@/lib/api';

const TIPOS = [
  { value: 'acceso', label: 'Acceso — Conocer mis datos', desc: 'Art. 8 lit. a' },
  { value: 'rectificacion', label: 'Rectificación — Corregir datos', desc: 'Art. 9' },
  { value: 'cancelacion', label: 'Cancelación / Supresión', desc: 'Art. 8 lit. c' },
  { value: 'oposicion', label: 'Oposición al tratamiento', desc: 'Art. 13' },
  { value: 'bloqueo', label: 'Bloqueo temporal', desc: 'Art. 8 ter' },
  { value: 'portabilidad', label: 'Portabilidad de datos', desc: 'Art. 12' },
] as const;

type TipoArco = (typeof TIPOS)[number]['value'];

interface FormState {
  company_id: string;
  tipo: TipoArco | '';
  titular_nombre: string;
  titular_email: string;
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
  titular_rut: '',
  descripcion: '',
  telefono: '',
  con_representante: false,
  representante_nombre: '',
  representante_rut: '',
  representante_poder_notarial_notas: '',
};

export default function EjercerDerechosPage() {
  const searchParams = useSearchParams();
  const [empresas, setEmpresas] = useState<EmpresaPublica[]>([]);
  const [form, setForm] = useState<FormState>(INITIAL);
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ token: string; mensaje: string } | null>(null);
  const [globalError, setGlobalError] = useState('');

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

  function validate(): boolean {
    const e: Partial<Record<keyof FormState, string>> = {};
    if (!form.company_id) e.company_id = 'Seleccione una empresa';
    if (!form.tipo) e.tipo = 'Seleccione el tipo de solicitud';
    if (!form.titular_nombre.trim() || form.titular_nombre.trim().length < 2)
      e.titular_nombre = 'Nombre requerido (mín. 2 caracteres)';
    if (!form.titular_email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/))
      e.titular_email = 'Email inválido';
    if (!form.descripcion.trim() || form.descripcion.trim().length < 10)
      e.descripcion = 'Describa su solicitud (mín. 10 caracteres)';
    if (form.con_representante) {
      if (!form.representante_nombre.trim()) e.representante_nombre = 'Nombre del representante requerido';
      if (!form.representante_poder_notarial_notas.trim())
        e.representante_poder_notarial_notas = 'Debe indicar la referencia del poder notarial';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault();
    if (!validate()) return;
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
      setGlobalError(err instanceof Error ? err.message : 'Error al enviar la solicitud');
    } finally {
      setSubmitting(false);
    }
  }

  const empresaSeleccionada = empresas.find(e => String(e.id) === form.company_id);

  if (result) {
    return (
      <div style={{ minHeight: '100vh', background: '#F9FAFB', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
        <div style={{ maxWidth: 560, width: '100%', background: 'white', borderRadius: 16, padding: 40, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', textAlign: 'center' }}>
          <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#D1FAE5', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px', fontSize: 28 }}>✓</div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', marginBottom: 12 }}>Solicitud Recibida</h1>
          <p style={{ color: '#6B7280', fontSize: 15, lineHeight: 1.6, marginBottom: 28 }}>{result.mensaje}</p>
          <div style={{ background: '#F3F4F6', borderRadius: 12, padding: '16px 20px', marginBottom: 28 }}>
            <p style={{ fontSize: 12, color: '#6B7280', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Código de seguimiento</p>
            <p style={{ fontFamily: 'monospace', fontSize: 15, fontWeight: 700, color: '#111827', wordBreak: 'break-all' }}>{result.token}</p>
          </div>
          <a
            href={`/seguimiento?token=${result.token}`}
            style={{
              display: 'inline-block', padding: '12px 28px', borderRadius: 8,
              background: '#1E40AF', color: 'white', fontWeight: 600, fontSize: 14, textDecoration: 'none',
            }}
          >
            Consultar estado de mi solicitud
          </a>
          <p style={{ marginTop: 20, fontSize: 13, color: '#9CA3AF' }}>
            Ley 21.719 — Art. 12 · Protección de Datos Personales
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB', padding: '32px 16px' }}>
      <div style={{ maxWidth: 680, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: 32, textAlign: 'center' }}>
          <div
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'linear-gradient(135deg, #1E40AF, #3730A3)',
              borderRadius: 12, padding: '10px 20px', marginBottom: 20,
            }}
          >
            <span style={{ color: 'white', fontWeight: 700, fontSize: 13 }}>Ley 21.719 — Art. 12</span>
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#111827', marginBottom: 8 }}>
            Ejercer mis Derechos ARCO
          </h1>
          <p style={{ color: '#6B7280', fontSize: 15, maxWidth: 480, margin: '0 auto' }}>
            Acceso, Rectificación, Cancelación, Oposición y derechos adicionales sobre tus datos personales
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

            {/* Empresa */}
            <Section title="1. Empresa">
              <Field label="¿A qué empresa diriges tu solicitud?" error={errors.company_id}>
                <select
                  value={form.company_id}
                  onChange={e => set('company_id', e.target.value)}
                  style={selectStyle(!!errors.company_id)}
                >
                  <option value="">— Selecciona una empresa —</option>
                  {empresas.map(emp => (
                    <option key={emp.id} value={String(emp.id)}>{emp.nombre}</option>
                  ))}
                </select>
              </Field>
              {empresaSeleccionada && (
                <p style={{ fontSize: 13, color: '#059669', fontWeight: 600, marginTop: 4 }}>
                  Empresa seleccionada: {empresaSeleccionada.nombre}
                </p>
              )}
            </Section>

            {/* Tipo de solicitud */}
            <Section title="2. Tipo de solicitud">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 10 }}>
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
                    <div style={{ fontSize: 13, fontWeight: 700, color: form.tipo === t.value ? '#1E40AF' : '#111827' }}>{t.label}</div>
                    <div style={{ fontSize: 11, color: '#9CA3AF', marginTop: 2 }}>{t.desc}</div>
                  </button>
                ))}
              </div>
              {errors.tipo && <p style={errorStyle}>{errors.tipo}</p>}
            </Section>

            {/* Datos personales */}
            <Section title="3. Tus datos">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <Field label="Nombre completo *" error={errors.titular_nombre} style={{ gridColumn: '1 / -1' }}>
                  <input
                    value={form.titular_nombre}
                    onChange={e => set('titular_nombre', e.target.value)}
                    placeholder="Ej: María González Pérez"
                    style={inputStyle(!!errors.titular_nombre)}
                  />
                </Field>
                <Field label="Email *" error={errors.titular_email}>
                  <input
                    type="email"
                    value={form.titular_email}
                    onChange={e => set('titular_email', e.target.value)}
                    placeholder="tu@email.com"
                    style={inputStyle(!!errors.titular_email)}
                  />
                </Field>
                <Field label="RUN (opcional)" error={errors.titular_rut}>
                  <input
                    value={form.titular_rut}
                    onChange={e => set('titular_rut', e.target.value)}
                    placeholder="12345678-9"
                    style={inputStyle(false)}
                  />
                </Field>
                <Field label="Teléfono (opcional)" error={errors.telefono}>
                  <input
                    value={form.telefono}
                    onChange={e => set('telefono', e.target.value)}
                    placeholder="+56 9 1234 5678"
                    style={inputStyle(false)}
                  />
                </Field>
              </div>
            </Section>

            {/* Descripción */}
            <Section title="4. Descripción de la solicitud">
              <Field label="Describe tu solicitud *" error={errors.descripcion}>
                <textarea
                  value={form.descripcion}
                  onChange={e => set('descripcion', e.target.value)}
                  rows={5}
                  placeholder="Explica con detalle qué datos solicitas acceder, corregir o eliminar, o en qué tratamiento te opones..."
                  style={{ ...inputStyle(!!errors.descripcion), resize: 'vertical' }}
                />
              </Field>
              <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{form.descripcion.length}/2000 caracteres</p>
            </Section>

            {/* Representante */}
            <Section title="5. Representante (opcional)">
              <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', marginBottom: 12 }}>
                <input
                  type="checkbox"
                  checked={form.con_representante}
                  onChange={e => set('con_representante', e.target.checked)}
                  style={{ width: 18, height: 18 }}
                />
                <span style={{ fontSize: 14, color: '#374151' }}>
                  Actúo como representante de otra persona
                </span>
              </label>
              {form.con_representante && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, paddingTop: 8 }}>
                  <Field label="Nombre del representante *" error={errors.representante_nombre} style={{ gridColumn: '1 / -1' }}>
                    <input
                      value={form.representante_nombre}
                      onChange={e => set('representante_nombre', e.target.value)}
                      placeholder="Nombre completo del representante"
                      style={inputStyle(!!errors.representante_nombre)}
                    />
                  </Field>
                  <Field label="RUN del representante" error={errors.representante_rut}>
                    <input
                      value={form.representante_rut}
                      onChange={e => set('representante_rut', e.target.value)}
                      placeholder="12345678-9"
                      style={inputStyle(false)}
                    />
                  </Field>
                  <Field
                    label="Poder notarial (descripción) *"
                    error={errors.representante_poder_notarial_notas}
                    style={{ gridColumn: '1 / -1' }}
                    hint="Indique número de escritura, notaría y fecha, o descripción del documento que acredita la representación (Art. 14 quater Ley 21.719)"
                  >
                    <textarea
                      value={form.representante_poder_notarial_notas}
                      onChange={e => set('representante_poder_notarial_notas', e.target.value)}
                      rows={3}
                      placeholder="Ej: Escritura N° 1234 de fecha 01/01/2026 ante Notario Juan Pérez..."
                      style={{ ...inputStyle(!!errors.representante_poder_notarial_notas), resize: 'vertical' }}
                    />
                  </Field>
                </div>
              )}
            </Section>

            {/* Error global */}
            {globalError && (
              <div style={{ padding: '12px 16px', borderRadius: 8, background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626', fontSize: 14 }}>
                {globalError}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '14px 32px', borderRadius: 10, fontWeight: 700, fontSize: 15,
                background: submitting ? '#93C5FD' : '#1E40AF', color: 'white',
                border: 'none', cursor: submitting ? 'not-allowed' : 'pointer',
                width: '100%', transition: 'background 0.15s',
              }}
            >
              {submitting ? 'Enviando solicitud…' : 'Enviar solicitud ARCO'}
            </button>

            <p style={{ textAlign: 'center', fontSize: 12, color: '#9CA3AF' }}>
              Tu solicitud será procesada en un plazo máximo de 10 días hábiles (Art. 12 Ley 21.719).
              Recibirás un código de seguimiento al completar el envío.
            </p>
          </div>
        </form>

        <div style={{ marginTop: 40, textAlign: 'center', fontSize: 12, color: '#D1D5DB' }}>
          Custodio RAT Manager · Ley 21.719 de Chile
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: 'white', borderRadius: 12, padding: '24px', border: '1px solid #E5E7EB', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
      <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1E40AF', marginBottom: 16 }}>{title}</h2>
      {children}
    </div>
  );
}

function Field({
  label, error, hint, children, style,
}: {
  label: string; error?: string; hint?: string; children: React.ReactNode; style?: React.CSSProperties;
}) {
  return (
    <div style={style}>
      <label style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 6 }}>{label}</label>
      {children}
      {hint && !error && <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{hint}</p>}
      {error && <p style={errorStyle}>{error}</p>}
    </div>
  );
}

const errorStyle: React.CSSProperties = { fontSize: 12, color: '#DC2626', marginTop: 4 };

function inputStyle(hasError: boolean): React.CSSProperties {
  return {
    width: '100%', padding: '10px 12px', borderRadius: 8, fontSize: 14,
    border: `1px solid ${hasError ? '#FCA5A5' : '#D1D5DB'}`,
    outline: 'none', background: 'white', color: '#111827',
    boxSizing: 'border-box',
  };
}

function selectStyle(hasError: boolean): React.CSSProperties {
  return {
    ...inputStyle(hasError), cursor: 'pointer', appearance: 'auto',
  };
}
