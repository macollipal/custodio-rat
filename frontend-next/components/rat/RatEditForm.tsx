'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import AlertBanner from '@/components/dashboard/AlertBanner';
import StepIndicator from '@/components/ui/StepIndicator';
import { BASES_LEGALES, DESCRIPCIONES_BASE, TIPOS_DATO_SENSIBLE } from '@/lib/constants';
import type { RAT } from '@/types';

const ESTADOS_EIPD = ['no_requerida', 'pendiente', 'en_proceso', 'completada'];
const ESTADOS: RAT['estado'][] = ['borrador', 'completo', 'en_revision', 'aprobado'];
const STEPS = ['Identificación', 'Datos tratados', 'Finalidad y ley', 'Transferencias'];

interface RatEditFormProps {
  rat: RAT;
  onDone: () => void;
  onCancel: () => void;
}

export default function RatEditForm({ rat, onDone, onCancel }: RatEditFormProps) {
  const [step, setStep] = useState(1);
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
    base_legal:                   rat.base_legal ?? BASES_LEGALES[0],
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
  });
  const [saving, setSaving] = useState(false);

  function set(field: string, value: unknown) {
    setForm(f => ({ ...f, [field]: value }));
  }

  async function handleSave() {
    if (!form.nombre_proceso.trim()) { toast.error('El nombre del proceso es obligatorio.'); return; }
    if (!form.categoria_datos.trim()) { toast.error('La categoria de datos es obligatoria.'); return; }
    if (!form.finalidad.trim()) { toast.error('La finalidad es obligatoria.'); return; }
    if (!form.base_legal.trim()) { toast.error('La base legal es obligatoria.'); return; }
    if (!form.fuente_datos.trim()) { toast.error('La fuente de datos es obligatoria.'); return; }
    if (!form.plazo_retencion.trim()) { toast.error('El plazo de retencion es obligatorio.'); return; }
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (typeof v === 'string') payload[k] = v?.trim() || null;
        else payload[k] = v ?? null;
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
      toast.success(`"${form.nombre_proceso}" actualizado correctamente.`);
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
              <input type="text" value={form.nombre_proceso} onChange={e => set('nombre_proceso', e.target.value)} className={inputCls} style={inputStyle} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Categorías de titulares * <span className="text-xs font-normal" style={{ color: '#9CA3AF' }}>(Art. 16 Ley 21.719)</span>
              </label>
              <input type="text" value={form.categoria_titulares} onChange={e => set('categoria_titulares', e.target.value)} placeholder="Ej: Clientes, empleados, proveedores..." className={inputCls} style={inputStyle} />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fuente de los datos *</label>
                <input type="text" value={form.fuente_datos} onChange={e => set('fuente_datos', e.target.value)} className={inputCls} style={inputStyle} />
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
              <p className="text-sm" style={{ color: '#6B7280' }}>Qué datos personales se tratan y si existen categorías especiales.</p>
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
                      <p className="text-xs mb-2" style={{ color: '#374151' }}>Para datos sensibles, el consentimiento debe ser expreso. Registrá el consentimiento del titular.</p>
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
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input type="checkbox" checked={form.decisiones_automatizadas} onChange={e => set('decisiones_automatizadas', e.target.checked)} className="mt-0.5 rounded" />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>🤖 Involucra decisiones automatizadas</span>
                  </label>
                  {form.decisiones_automatizadas && (
                    <AlertBanner message="Los titulares tienen derecho a solicitar revisión humana e impugnar la decisión (Art. 8)." type="info" />
                  )}
                </div>
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
              <textarea value={form.finalidad} onChange={e => set('finalidad', e.target.value)} rows={3} className={inputCls} style={inputStyle} />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Base legal del tratamiento * <span className="text-xs font-normal" style={{ color: '#9CA3AF' }}>(Art. 13 Ley 21.719)</span>
              </label>
              <select value={form.base_legal} onChange={e => set('base_legal', e.target.value)} className={inputCls} style={inputStyle}>
                {BASES_LEGALES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
              {form.base_legal && DESCRIPCIONES_BASE[form.base_legal] && (
                <div className="mt-2">
                  <AlertBanner
                    message={DESCRIPCIONES_BASE[form.base_legal]}
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
                        <p className="text-xs" style={{ color: '#9CA3AF' }}>{form.archivo_base_legal_tipo}</p>
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
                      onClick={() => window.open(`/api/rats/${rat.id}/archivo`, '_blank')}
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
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                  Test de interés legítimo (3 pasos) <span className="text-xs font-normal" style={{ color: '#9CA3AF' }}>(obligatorio para esta base legal)</span>
                </label>
                <textarea
                  value={form.test_interes_legitimo}
                  onChange={e => set('test_interes_legitimo', e.target.value)}
                  rows={4}
                  placeholder="Documente los 3 pasos: (1) ¿existe interés legítimo real? (2) ¿el tratamiento es necesario? (3) ¿prevalece sobre los derechos del titular?"
                  className={inputCls}
                  style={inputStyle}
                />
                <AlertBanner message="Sin este test documentado, la base 'Interés legítimo' no sirve como defensa ante la APDC." type="warning" />
              </div>
            )}

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(2)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  if (!form.finalidad?.trim()) { toast.error('La finalidad es obligatoria.'); return; }
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

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Plazo de retención *</label>
                  <input type="text" value={form.plazo_retencion} onChange={e => set('plazo_retencion', e.target.value)} placeholder="Ej: 5 años desde el último contacto" className={inputCls} style={inputStyle} />
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

            <div className="flex justify-between pt-2">
              <button onClick={() => setStep(3)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>← Anterior</button>
              <button
                onClick={() => {
                  if (!form.plazo_retencion?.trim()) { toast.error('El plazo de retención es obligatorio.'); return; }
                  handleSave();
                }}
                disabled={saving}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {saving ? 'Guardando...' : '✓ Guardar cambios'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}