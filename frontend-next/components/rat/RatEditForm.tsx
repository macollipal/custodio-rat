'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import AlertBanner from '@/components/dashboard/AlertBanner';
import StepIndicator from '@/components/ui/StepIndicator';
import Spinner from '@/components/ui/Spinner';
import CategoryChips from '@/components/ui/CategoryChips';
import { useApp } from '@/context/AppContext';
import { TIPOS_DATO_SENSIBLE, DATOS_NNA_OPCIONES, NIVEL_CONFIDENCIALIDAD_OPCIONES, ESTRUCTURA_DATO_OPCIONES, CICLO_PROCESAMIENTO_OPCIONES, AUTOMATIZACION_OPCIONES, FRECUENCIA_OPCIONES, OPERACIONES_TRATAMIENTO_OPCIONES } from '@/lib/constants';
import type { RAT } from '@/types';

const ESTADOS_EIPD = ['no_requerida', 'pendiente', 'en_proceso', 'completada'];
const ESTADOS: RAT['estado'][] = ['borrador', 'completo', 'en_revision', 'aprobado'];
const STEPS = ['Identificación', 'Datos tratados', 'Finalidad y ley', 'Transferencias', 'Compliance'];

const validatePaso4 = (form: any): string | null => {
  if (!form.plazo_retencion?.toString().trim()) return 'Debes indicar el plazo de retención.';
  if (!form.medidas_seguridad?.toString().trim()) return 'Debes describir las medidas de seguridad.';
  return null;
};
interface RatEditFormProps {
  rat: RAT;
  onDone: () => void;
  onCancel: () => void;
}

export default function RatEditForm({ rat, onDone, onCancel }: RatEditFormProps) {
  const { baseLegalOptions, baseLegalDescripciones } = useApp();
  const [step, setStep] = useState(1);

  // Parsear el test_interes_legitimo existente: JSON {paso1,paso2,paso3} o legacy "Paso 1:...\nPaso 2:...\nPaso 3:..."
  const initialTestIL = (() => {
    const raw = rat.test_interes_legitimo ?? '';
    if (!raw) return { paso1: '', paso2: '', paso3: '' };
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && 'paso1' in parsed) {
        return {
          paso1: parsed.paso1 ?? '',
          paso2: parsed.paso2 ?? '',
          paso3: parsed.paso3 ?? '',
        };
      }
    } catch {}
    const m1 = raw.match(/Paso 1:\s*([\s\S]*?)(?=\nPaso 2:|$)/);
    const m2 = raw.match(/Paso 2:\s*([\s\S]*?)(?=\nPaso 3:|$)/);
    const m3 = raw.match(/Paso 3:\s*([\s\S]*?)$/);
    return {
      paso1: m1 ? m1[1].trim() : '',
      paso2: m2 ? m2[1].trim() : '',
      paso3: m3 ? m3[1].trim() : '',
    };
  })();
  const [testIL, setTestIL] = useState(initialTestIL);

  const [form, setForm] = useState({
    nombre_proceso:               rat.nombre_proceso ?? '',
    categoria_titulares:          rat.categoria_titulares ?? '',
    fuente_datos:                 rat.fuente_datos ?? '',
    destinatarios:                rat.destinatarios ?? '',
    categoria_datos:              rat.categoria_datos ?? '',
    datos_sensibles:              rat.datos_sensibles ?? false,
    tipo_dato_sensible:           rat.tipo_dato_sensible ?? '',
    evaluacion_impacto:            rat.evaluacion_impacto ?? false,
    estado_eipd:                  rat.estado_eipd ?? 'no_requerida',
    fecha_eipd:                  rat.fecha_eipd ?? '',
    decisiones_automatizadas:     rat.decisiones_automatizadas ?? false,
    finalidad:                    rat.finalidad ?? '',
    base_legal:                   rat.base_legal ?? baseLegalOptions[0],
    test_interes_legitimo:        rat.test_interes_legitimo ?? '',
    plazo_retencion:              rat.plazo_retencion ?? '',
    medidas_seguridad:            rat.medidas_seguridad ?? '',
    transferencia_datos:           rat.transferencia_datos ?? '',
    transferencia_internacional:   rat.transferencia_internacional ?? false,
    pais_destino:                rat.pais_destino ?? '',
    garantias_transferencia_int:  rat.garantias_transferencia_int ?? '',
    nombre_encargado:             rat.nombre_encargado ?? '',
    tiene_contrato_encargado:      rat.tiene_contrato_encargado ?? false,
    estado:                       rat.estado ?? 'borrador',
    observaciones_auditoria:     rat.observaciones_auditoria ?? '',
    archivo_base_legal_base64:  '',
    archivo_base_legal_nombre:  '',
    archivo_base_legal_tipo:   '',
    consentimiento_nombre:  '',
    consentimiento_email:  '',
    consentimiento_texto:  '',
    // Campos nuevos gaps Ley 21.719 (Iter 10)
    sistema_almacenamiento: rat.sistema_almacenamiento ?? '',
    volumen_titulares_estimado: rat.volumen_titulares_estimado ?? '',
    operaciones_tratamiento: rat.operaciones_tratamiento ?? [],
    logica_automatizada: rat.logica_automatizada ?? '',
    responsable_tratamiento_email: rat.responsable_tratamiento_email ?? '',
    // Campos Tier 1 - Gaps criticos (Iter 11)
    datos_nna: rat.datos_nna ?? 'ninguno',
    nivel_confidencialidad: rat.nivel_confidencialidad ?? '',
    estructura_dato: rat.estructura_dato ?? '',
    datos_anonimizados: rat.datos_anonimizados ?? false,
    datos_seudonimizados: rat.datos_seudonimizados ?? false,
    // Campos Tier 2 - Operativos (Iter 11)
    ciclo_procesamiento: rat.ciclo_procesamiento ?? '',
    automatizacion: rat.automatizacion ?? '',
    frecuencia: rat.frecuencia ?? '',
    transferencia_nacional: rat.transferencia_nacional ?? false,
    doc_clausulas: rat.doc_clausulas ?? '',
    medidas_organizativas: rat.medidas_organizativas ?? '',
    mecanismos_eliminacion: rat.mecanismos_eliminacion ?? '',
    tecnica_anonimizacion: rat.tecnica_anonimizacion ?? '',
    origen_dato_portabilidad: rat.origen_dato_portabilidad ?? '',
    fecha_levantamiento: rat.fecha_levantamiento ?? '',
  });
  const [saving, setSaving] = useState(false);

  function set(field: string, value: unknown) {
    setForm(f => ({ ...f, [field]: value }));
  }

  async function handleSave() {
    if (!form.nombre_proceso.trim()) { toast.error('El nombre del proceso es obligatorio.'); return; }
    if (!form.categoria_datos.trim()) { toast.error('La categoría de datos es obligatoria.'); return; }
    if (!form.finalidad.trim()) { toast.error('La finalidad es obligatoria.'); return; }
    if (!form.base_legal.trim()) { toast.error('La base legal es obligatoria.'); return; }
    if (!form.fuente_datos.trim()) { toast.error('La fuente de datos es obligatoria.'); return; }
    if (!form.plazo_retencion.trim()) { toast.error('El plazo de retención es obligatorio.'); return; }
    if (form.base_legal === 'Interés legítimo') {
      const totalTestIL = [testIL.paso1, testIL.paso2, testIL.paso3].join(' ').trim();
      if (!totalTestIL) {
        toast.error('Complete los 3 pasos del test de interés legítimo.');
        return;
      }
      if (totalTestIL.length < 50) {
        toast.error(`El test de interés legítimo debe tener al menos 50 caracteres (actual: ${totalTestIL.length}).`);
        return;
      }
    }
    // Consentimiento expreso obligatorio para datos sensibles (Art. 16 Ley 21.719)
    if (form.datos_sensibles) {
      const consentimientos = await api.listarConsentimientos(rat.company_id, rat.id, true);
      if (consentimientos.length === 0) {
        toast.error('Un RAT con datos sensibles requiere al menos un consentimiento expreso registrado. Use la alerta de Consentimiento en el detalle del RAT.');
        setSaving(false);
        return;
      }
    }
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (typeof v === 'string') payload[k] = v?.trim() || null;
        else payload[k] = v ?? null;
      }
      // Reemplazar test_interes_legitimo con JSON estructurado
      if (form.base_legal === 'Interés legítimo') {
        payload.test_interes_legitimo = JSON.stringify({ paso1: testIL.paso1.trim(), paso2: testIL.paso2.trim(), paso3: testIL.paso3.trim() });
      } else {
        payload.test_interes_legitimo = null;
      }
      await api.actualizarRat(rat.id, payload as Partial<RAT>);
      if (form.datos_sensibles && form.consentimiento_nombre && form.consentimiento_email) {
        await api.registrarConsentimiento({
          rat_id: rat.id,
          nombre_titular: form.consentimiento_nombre,
          email_titular: form.consentimiento_email,
          canal: 'sistema',
          texto_consentimiento: form.consentimiento_texto || 'Consentimiento expreso para tratamiento de datos sensibles.',
          datos_sensibles: true,
        });
 }
      toast.success(`RAT "${form.nombre_proceso}" actualizado correctamente`);
      onDone();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al actualizar.');
    } finally {
      setSaving(false);
    }
  }

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onCancel}
          className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50"
          style={{ color: '#6B7280', borderColor: '#E5E7EB' }}
        >
          ← Volver
        </button>
        <h2 className="text-lg font-bold" style={{ color: '#111827' }}>
          Editar proceso · {rat.nombre_proceso}
        </h2>
      </div>

      <StepIndicator steps={STEPS} current={step} />

      <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>

        {/* PASO 1 */}
        {step === 1 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 1 · Identificación del proceso</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Información básica del proceso de tratamiento.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Nombre del proceso *
              </label>
              <input type="text" value={form.nombre_proceso} onChange={e => set('nombre_proceso', e.target.value)} aria-required="true" className={inputCls} style={inputStyle} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Categorías de titulares * <span className="text-xs font-normal" style={{ color: '#6B7280' }}>(Art. 16 Ley 21.719)</span>
              </label>
              <CategoryChips
                value={form.categoria_titulares}
                onChange={v => set('categoria_titulares', v)}
                suggestions={['Clientes', 'Empleados', 'Proveedores', 'Pacientes', 'Postulantes', 'Estudiantes', 'Usuarios web', 'Menores de edad', 'Acreedores']}
                placeholder="Ej: Clientes, empleados, proveedores..."
                ariaLabel="Categorías de titulares"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fuente de los datos *</label>
                <input type="text" value={form.fuente_datos} onChange={e => set('fuente_datos', e.target.value)} aria-required="true" className={inputCls} style={inputStyle} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Destinatarios / Encargados</label>
                <input type="text" value={form.destinatarios} onChange={e => set('destinatarios', e.target.value)} className={inputCls} style={inputStyle} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nombre del encargado del tratamiento</label>
              <input type="text" value={form.nombre_encargado} onChange={e => set('nombre_encargado', e.target.value)} placeholder="Ej: Proveedor CRM, asesora laboral..." className={inputCls} style={inputStyle} />
              <div className="mt-2">
                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input type="checkbox" checked={form.tiene_contrato_encargado} onChange={e => set('tiene_contrato_encargado', e.target.checked)} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>
                    ✓ Tiene contrato de encargo (Art. 14 quáter Ley 21.719)
                  </span>
                </label>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => {
                  if (!form.nombre_proceso?.trim()) { toast.error('El nombre del proceso es obligatorio.'); return; }
                  if (!form.categoria_titulares?.trim()) { toast.error('Las categorías de titulares son obligatorias.'); return; }
                  if (!form.fuente_datos?.trim()) { toast.error('La fuente de datos es obligatoria.'); return; }
                  setStep(2);
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}

        {/* PASO 2 */}
        {step === 2 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 2 · Datos personales tratados</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Qué datos personales se tratan, su clasificación y si existen categorías especiales.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Categoría de datos tratados *</label>
              <textarea value={form.categoria_datos} onChange={e => set('categoria_datos', e.target.value)} rows={4} className={inputCls} style={inputStyle} />
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={form.datos_sensibles} onChange={e => set('datos_sensibles', e.target.checked)} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>⚠️ El proceso trata datos sensibles (Art. 2 letra g)</span>
                </label>
                {form.datos_sensibles && (
                  <div className="space-y-2 pl-6">
                    <select value={form.tipo_dato_sensible} onChange={e => set('tipo_dato_sensible', e.target.value)} className={inputCls} style={inputStyle}>
                      <option value="">— Seleccione el tipo de dato sensible —</option>
                      {TIPOS_DATO_SENSIBLE.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <AlertBanner message="Dato sensible: requiere base legal expresa y medidas de seguridad reforzadas." type="warning" />
                    <div className="rounded-lg p-3" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                      <p className="text-xs font-semibold mb-2" style={{ color: '#1E40AF' }}>B-06: Consentimiento Expreso (Art. 12)</p>
                      <p className="text-xs mb-2" style={{ color: '#374151' }}>Para datos sensibles, el consentimiento debe ser expreso. Registre el consentimiento del titular.</p>
                      <div className="grid grid-cols-2 gap-2">
                        <input type="text" value={form.consentimiento_nombre ?? ''} onChange={e => set('consentimiento_nombre', e.target.value)} placeholder="Nombre del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                        <input type="email" value={form.consentimiento_email ?? ''} onChange={e => set('consentimiento_email', e.target.value)} placeholder="Email del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                      </div>
                      <textarea value={form.consentimiento_texto ?? ''} onChange={e => set('consentimiento_texto', e.target.value)} rows={2} placeholder="Texto del consentimiento expreso..." className="w-full mt-2 px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                    </div>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={form.evaluacion_impacto} onChange={e => set('evaluacion_impacto', e.target.checked)} className="mt-0.5 rounded" />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>📋 Requiere Evaluación de Impacto (EIPD)</span>
                  </label>
                  {form.evaluacion_impacto && (
                    <div className="pl-6 space-y-2">
                      <select value={form.estado_eipd} onChange={e => set('estado_eipd', e.target.value)} className={inputCls} style={inputStyle}>
                        {ESTADOS_EIPD.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                      </select>
                      <input type="date" value={form.fecha_eipd ?? ''} onChange={e => set('fecha_eipd', e.target.value)} className={inputCls} style={inputStyle} />
                      <AlertBanner message="La EIPD debe completarse antes de iniciar el tratamiento (Art. 15 bis)." type="info" />
                      <a
                        href={`/eipd?rat_id=${rat.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-sm font-medium underline underline-offset-2"
                        style={{ color: '#2563EB' }}
                      >
                        Ir a Evaluación de Impacto →
                      </a>
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={form.decisiones_automatizadas} onChange={e => set('decisiones_automatizadas', e.target.checked)} className="mt-0.5 rounded" />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>🤖 Involucra decisiones automatizadas</span>
                  </label>
                  {form.decisiones_automatizadas && (
                    <div className="pl-6 space-y-2">
                      <AlertBanner message="Los titulares tienen derecho a solicitar revisión humana e impugnar la decisión (Art. 8)." type="info" />
                      <textarea
                        value={form.logica_automatizada}
                        onChange={e => set('logica_automatizada', e.target.value)}
                        rows={3}
                        placeholder="Describa la lógica aplicada, consecuencias para el titular y posibilidad de revisión humana..."
                        className={inputCls}
                        style={inputStyle}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Clasificación y NNA — canonical Step 2 */}
            <div className="rounded-lg p-4 space-y-4" style={{ border: '1px solid #E5E7EB' }}>
              <h4 className="text-sm font-bold" style={{ color: '#374151' }}>Clasificación y NNA</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                    Tratamiento de NNA
                  </label>
                  <select value={form.datos_nna ?? 'ninguno'} onChange={e => set('datos_nna', e.target.value)} className={inputCls} style={inputStyle}>
                    {DATOS_NNA_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                    Nivel de confidencialidad
                  </label>
                  <select value={form.nivel_confidencialidad ?? ''} onChange={e => set('nivel_confidencialidad', e.target.value)} aria-describedby="nivel-conf-tooltip-edit-form" className={inputCls} style={inputStyle}>
                    <option value="">— Seleccionar —</option>
                    {NIVEL_CONFIDENCIALIDAD_OPCIONES.map(o => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                  {form.nivel_confidencialidad && (() => {
                    const opt = NIVEL_CONFIDENCIALIDAD_OPCIONES.find(o => o.value === form.nivel_confidencialidad);
                    return opt?.tooltip ? (
                      <div role="tooltip" id="nivel-conf-tooltip-edit-form" className="text-xs mt-1" style={{ color: '#6B7280' }}>{opt.tooltip}</div>
                    ) : null;
                  })()}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Estructura del dato</label>
                  <select value={form.estructura_dato ?? ''} onChange={e => set('estructura_dato', e.target.value)} className={inputCls} style={inputStyle}>
                    <option value="">— Seleccionar —</option>
                    {ESTRUCTURA_DATO_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.datos_anonimizados} onChange={e => set('datos_anonimizados', e.target.checked)} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos anonimizados</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.datos_seudonimizados} onChange={e => set('datos_seudonimizados', e.target.checked)} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos seudonimizados</span>
                </label>
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(1)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  if (!form.categoria_datos?.trim()) { toast.error('La categoría de datos es obligatoria.'); return; }
                  setStep(3);
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}

        {/* PASO 3 */}
        {step === 3 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 3 · Finalidad y base legal</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Por qué y con qué fundamento jurídico se tratan los datos.</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Finalidad del tratamiento *</label>
              <textarea value={form.finalidad} onChange={e => set('finalidad', e.target.value)} rows={3} aria-required="true" className={inputCls} style={inputStyle} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Base legal del tratamiento * <span className="text-xs font-normal" style={{ color: '#6B7280' }}>(Art. 13 Ley 21.719)</span>
              </label>
              <select value={form.base_legal} onChange={e => set('base_legal', e.target.value)} className={inputCls} style={inputStyle}>
                {baseLegalOptions.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
              {form.base_legal && baseLegalDescripciones[form.base_legal] && (
                <div className="mt-2">
                  <AlertBanner
                    message={baseLegalDescripciones[form.base_legal]}
                    type={form.base_legal === 'Interés legítimo' || form.base_legal === 'Datos biométricos de identificación (Art. 16 BIS)' ? 'warning' : 'info'}
                  />
                </div>
              )}
              {form.base_legal === 'Consentimiento del titular' && form.datos_sensibles && (
                <div className="mt-2">
                  <AlertBanner message="⚠️ Consentimiento + datos sensibles: el consentimiento debe ser EXPRESO." type="warning" />
                </div>
              )}

              {form.base_legal && form.base_legal !== 'Otra' && (
                <div className="mt-4 p-4 rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#374151' }}>
                    📄 Documento que respalda la base legal *
                  </label>
                  <p className="text-xs mb-3" style={{ color: '#6B7280' }}>
                    {rat.tiene_archivo_base_legal && !form.archivo_base_legal_base64
                      ? 'Ya existe un documento adjunto. Seleccione uno nuevo para reemplazarlo.'
                      : 'Adjunte el documento: consentimiento firmado, contrato, norma legal, EIPD, etc. (PDF, imagen o Word, máx. 10MB).'}
                  </p>
                  {!form.archivo_base_legal_base64 ? (
                    <input
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                      onChange={e => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        if (file.size > 10 * 1024 * 1024) {
                          toast.error('El archivo excede el límite de 10MB.');
                          return;
                        }
                        const reader = new FileReader();
                        reader.onload = ev => {
                          const b64 = (ev.target?.result as string)?.split(',')[1] || '';
                          setForm(f => ({ ...f, archivo_base_legal_base64: b64, archivo_base_legal_nombre: file.name, archivo_base_legal_tipo: file.type }));
                        };
                        reader.readAsDataURL(file);
                      }}
                      className="block w-full text-sm border rounded-lg p-2"
                      style={{ borderColor: '#D1D5DB' }}
                    />
                  ) : (
                    <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: 'white', border: '1px solid #D1D5DB' }}>
                      <span className="text-lg">📎</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>{form.archivo_base_legal_nombre}</p>
                        <p className="text-xs" style={{ color: '#6B7280' }}>{form.archivo_base_legal_tipo}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => setForm(f => ({ ...f, archivo_base_legal_base64: '', archivo_base_legal_nombre: '', archivo_base_legal_tipo: '' }))}
                        className="text-xs font-semibold px-2 py-1 rounded"
                        style={{ color: '#DC2626', background: '#FEE2E2' }}
                      >
                        Eliminar
                      </button>
                    </div>
                  )}
                  {rat.tiene_archivo_base_legal && !form.archivo_base_legal_base64 && (
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const blob = await api.descargarArchivoRAT(rat.id);
                          const url = URL.createObjectURL(blob);
                          window.open(url, '_blank', 'noopener,noreferrer');
                          setTimeout(() => URL.revokeObjectURL(url), 60000);
                        } catch (err) {
                          toast.error(err instanceof Error ? err.message : 'Error al abrir el documento');
                        }
                      }}
                      className="mt-2 text-xs font-medium underline"
                      style={{ color: '#2563EB' }}
                    >
                      Ver documento actual
                    </button>
                  )}
                </div>
              )}

              {/* alerta de documento ahora es opcional */}
            </div>

            {(form.base_legal === 'Interés legítimo') && (
              <div className="rounded-lg p-4 space-y-3" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold" style={{ color: '#374151' }}>
                    Test de interés legítimo (3 pasos)
                  </p>
                  <span className="text-xs font-medium" style={{ color: '#6B7280' }}>
                    {[testIL.paso1, testIL.paso2, testIL.paso3].join(' ').trim().length} / 50+ caracteres
                  </span>
                </div>
                <AlertBanner message="El test de interés legítimo es obligatorio (Art. 16 Ley 21.719). Mínimo 50 caracteres necesarios para ser válido como documentación ante la APDC." type="warning" />
                <div>
                  <label htmlFor="ef-testil-paso1" className="block text-xs font-semibold mb-1" style={{ color: '#374151' }}>
                    Paso 1 — ¿Existe un interés legítimo real?
                  </label>
                  <textarea
                    id="ef-testil-paso1"
                    rows={2}
                    value={testIL.paso1}
                    onChange={e => setTestIL(t => ({ ...t, paso1: e.target.value }))}
                    placeholder="Describa el interés legítimo: marketing directo, seguridad, prevención de fraude..."
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label htmlFor="ef-testil-paso2" className="block text-xs font-semibold mb-1" style={{ color: '#374151' }}>
                    Paso 2 — ¿El tratamiento es necesario para ese interés?
                  </label>
                  <textarea
                    id="ef-testil-paso2"
                    rows={2}
                    value={testIL.paso2}
                    onChange={e => setTestIL(t => ({ ...t, paso2: e.target.value }))}
                    placeholder="Justifique por qué el tratamiento es necesario y no hay alternativa menos invasiva."
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label htmlFor="ef-testil-paso3" className="block text-xs font-semibold mb-1" style={{ color: '#374151' }}>
                    Paso 3 — ¿Prevalece sobre los derechos del titular?
                  </label>
                  <textarea
                    id="ef-testil-paso3"
                    rows={3}
                    value={testIL.paso3}
                    onChange={e => setTestIL(t => ({ ...t, paso3: e.target.value }))}
                    placeholder="Considere expectativas razonables del titular, impacto en su privacidad, medidas mitigadoras..."
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
              </div>
            )}

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(2)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  if (!form.finalidad?.trim()) { toast.error('La finalidad es obligatoria.'); return; }
                  if (form.base_legal === 'Interés legítimo') {
                    const totalIL = [testIL.paso1, testIL.paso2, testIL.paso3].join(' ').trim();
                    if (!totalIL || totalIL.length < 50) {
                      toast.error('El test de interés legítimo debe tener al menos 50 caracteres (Art. 16 Ley 21.719).'); return;
                    }
                  }
                  setStep(4);
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}

        {/* PASO 4 */}
        {step === 4 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 4 · Almacenamiento y transferencias</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Por cuánto tiempo se conservan los datos y cómo se comparten.</p>
            </div>

            {/* Iter 10 fields — storage system and volume */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Sistema de almacenamiento</label>
                <input
                  type="text"
                  value={form.sistema_almacenamiento}
                  onChange={e => set('sistema_almacenamiento', e.target.value)}
                  placeholder="Ej: CRM Salesforce, Excel, Google Drive, Sistema clínico..."
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Volumen estimado de titulares</label>
                <input
                  type="number"
                  value={form.volumen_titulares_estimado}
                  onChange={e => set('volumen_titulares_estimado', e.target.value ? parseInt(e.target.value) : '')}
                  placeholder="Ej: 50000"
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Plazo de retención *</label>
                  <input type="text" value={form.plazo_retencion} onChange={e => set('plazo_retencion', e.target.value)} placeholder="Ej: 5 años desde el último contacto" aria-required="true" className={inputCls} style={inputStyle} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Medidas de seguridad</label>
                  <textarea value={form.medidas_seguridad} onChange={e => set('medidas_seguridad', e.target.value)} rows={3} placeholder="Ej: Cifrado AES-256, MFA, acceso por roles..." className={inputCls} style={inputStyle} />
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Transferencias o comunicaciones de datos</label>
                  <textarea value={form.transferencia_datos} onChange={e => set('transferencia_datos', e.target.value)} rows={3} className={inputCls} style={inputStyle} />
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={form.transferencia_internacional} onChange={e => set('transferencia_internacional', e.target.checked)} className="mt-0.5 rounded" />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>🌐 Transferencia internacional de datos</span>
                  </label>
                  {form.transferencia_internacional && (
                    <div className="space-y-2 pl-6">
                      <input type="text" value={form.pais_destino} onChange={e => set('pais_destino', e.target.value)} placeholder="Ej: Estados Unidos, España" className={inputCls} style={inputStyle} />
                      <select value={form.garantias_transferencia_int} onChange={e => set('garantias_transferencia_int', e.target.value)} className={inputCls} style={inputStyle}>
                        <option value="">— Garantías aplicables —</option>
                        <option value="Nivel adecuado de protección (decisión APDC o UE)">Nivel adecuado de protección</option>
                        <option value="Cláusulas Contractuales Tipo (SCC)">Cláusulas Contractuales Tipo (SCC)</option>
                        <option value="Normas Corporativas Vinculantes (BCR)">BCR</option>
                        <option value="Consentimiento explícito del titular">Consentimiento explícito</option>
                        <option value="Contrato con cláusulas de protección equivalentes">Contrato equivalente</option>
                        <option value="Otra garantía adecuada">Otra garantía</option>
                      </select>
                      <AlertBanner message="Chile NO está en la lista de adecuación de la UE. Si el destinatario es europeo, se requieren SCC." type="warning" />
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Estado del proceso</label>
              <select value={form.estado} onChange={e => set('estado', e.target.value)} className={inputCls} style={inputStyle}>
                {ESTADOS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Observaciones de auditoría</label>
              <textarea value={form.observaciones_auditoria} onChange={e => set('observaciones_auditoria', e.target.value)} rows={2} className={inputCls} style={inputStyle} />
            </div>

            {/* Campos nuevos gaps Ley 21.719 (Iter 10) */}
            <div className="rounded-lg p-4 space-y-4" style={{ border: '1px solid #E5E7EB' }}>
              <h4 className="text-sm font-bold" style={{ color: '#374151' }}>📋 Operaciones y responsable</h4>

              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Operaciones de tratamiento</label>
                <div className="flex flex-wrap gap-2">
                  {OPERACIONES_TRATAMIENTO_OPCIONES.map(op => (
                    <label key={op} className="flex items-center gap-1.5 cursor-pointer px-3 py-1.5 rounded-full text-xs font-medium border transition" style={{
                      backgroundColor: (form.operaciones_tratamiento as string[])?.includes(op) ? '#DBEAFE' : 'white',
                      borderColor: (form.operaciones_tratamiento as string[])?.includes(op) ? '#2563EB' : '#D1D5DB',
                      color: (form.operaciones_tratamiento as string[])?.includes(op) ? '#1D4ED8' : '#6B7280',
                    }}>
                      <input
                        type="checkbox"
                        checked={(form.operaciones_tratamiento as string[])?.includes(op) || false}
                        onChange={e => {
                          const current = (form.operaciones_tratamiento as string[]) || [];
                          if (e.target.checked) {
                            set('operaciones_tratamiento', [...current, op]);
                          } else {
                            set('operaciones_tratamiento', current.filter((x: string) => x !== op));
                          }
                        }}
                        className="sr-only"
                      />
                      {op}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Responsable del tratamiento (email)</label>
                <input
                  type="email"
                  value={form.responsable_tratamiento_email}
                  onChange={e => set('responsable_tratamiento_email', e.target.value)}
                  placeholder="Ej: responsable@empresa.cl"
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(3)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  const err = validatePaso4(form);
                  if (err) {
                    toast.error(err);
                    return;
                  }
                  setStep(5);
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#7C3AED' }}
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}

        {/* PASO 5 */}
        {step === 5 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 5 · Compliance avanzado (Tier 1 + Tier 2)</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Campos de cierre de gaps críticos y operativos - ProBest template.</p>
            </div>

            {/* Tier 2 — Operativos (ProBest template) */}
            <div className="rounded-lg p-4 space-y-4" style={{ border: '1px solid #E5E7EB' }}>
              <h4 className="text-sm font-bold" style={{ color: '#374151' }}>Tier 2 — Operativos (ProBest template)</h4>

              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.transferencia_nacional} onChange={e => set('transferencia_nacional', e.target.checked)} className="mt-0.5 rounded" />
                <span className="text-sm font-medium" style={{ color: '#374151' }}>Existe transferencia de datos a nivel nacional (dentro de Chile)</span>
              </label>

              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Documentación de cláusulas informativas</label>
                <textarea value={form.doc_clausulas ?? ''} onChange={e => set('doc_clausulas', e.target.value)} rows={2} placeholder="Ej: Politica de privacidad en sitio web, aviso de privacidad en formularios..." className={inputCls} style={inputStyle} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Medidas organizativas</label>
                <textarea value={form.medidas_organizativas ?? ''} onChange={e => set('medidas_organizativas', e.target.value)} rows={2} placeholder="Ej: Designacion RAI, procedimientos de acceso, politicas internas..." className={inputCls} style={inputStyle} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Mecanismos de eliminación</label>
                  <textarea value={form.mecanismos_eliminacion ?? ''} onChange={e => set('mecanismos_eliminacion', e.target.value)} rows={2} placeholder="Ej: Borrado seguro NIST 800-88, destrucción física, retención hasta fin de plazo..." className={inputCls} style={inputStyle} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Técnica de anonimización</label>
                  <input value={form.tecnica_anonimizacion ?? ''} onChange={e => set('tecnica_anonimizacion', e.target.value)} placeholder="Ej: Pseudonimización, k-anonimidad, agregación..." className={inputCls} style={inputStyle} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Origen del dato (portabilidad)</label>
                  <input value={form.origen_dato_portabilidad ?? ''} onChange={e => set('origen_dato_portabilidad', e.target.value)} placeholder="Ej: Directamente del titular, de otro responsable..." className={inputCls} style={inputStyle} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fecha de levantamiento</label>
                  <input type="date" value={form.fecha_levantamiento ?? ''} onChange={e => set('fecha_levantamiento', e.target.value)} className={inputCls} style={inputStyle} />
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(4)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  if (!form.plazo_retencion?.trim()) { toast.error('El plazo de retención es obligatorio.'); return; }
                  handleSave();
                }}
                disabled={saving}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60 inline-flex items-center justify-center gap-2"
                style={{ background: '#059669' }}
              >
                {saving ? (
                  <>
                    <Spinner size="sm" /> Guardando…
                  </>
                ) : (
                  '✓ Guardar cambios'
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

