'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import AlertBanner from '@/components/dashboard/AlertBanner';
import StepIndicator from '@/components/ui/StepIndicator';
import type { Company, RAT, RATWizardData } from '@/types';

import { BASES_LEGALES, TIPOS_DATO_SENSIBLE, DRAFT_KEY_PREFIX } from '@/lib/constants';

const DESCRIPCIONES_BASE: Record<string, string> = {
  'Consentimiento del titular':
    'Art. 12 — Debe ser libre, previo, expreso, informado, específico, revocable y sin condición negocial. ' +
    'Para datos sensibles, el consentimiento debe ser EXPRESO. En relaciones laborales jerárquicas, el consentimiento del empleado no es base válida.',
  'Ejecución de contrato':
    'Art. 13 b) — El tratamiento es necesario para ejecutar un contrato en que el titular es parte, o para aplicar medidas precontractuales a su solicitud.',
  'Obligación legal':
    'Art. 13 a) — El tratamiento es requerido por una norma legal vigente (ley, decreto, etc.). Identifique la norma específica que habilita el tratamiento.',
  'Interés legítimo':
    'Art. 16 — Requiere documentar el test de 3 pasos: (1) ¿existe interés legítimo real? (2) ¿el tratamiento es necesario para ese interés? ' +
    '(3) ¿prevalece sobre los derechos del titular? Sin este test documentado, la base no sirve como defensa ante la APDC.',
  'Interés vital del titular':
    'Art. 13 c) — Proteger intereses vitales del titular u otra persona (situaciones de riesgo para la vida o la integridad física).',
  'Datos biométricos de identificación (Art. 16 BIS)':
    'Art. 16 BIS — Base específica para datos biométricos destinados a identificar inequívocamente a una persona. ' +
    'Requiere EIPD previa. En contextos laborales, el consentimiento NO es base válida — use obligación legal y justifique la necesidad.',
};

const STEPS = ['Identificación', 'Datos tratados', 'Finalidad y ley', 'Transferencias'];

interface RatWizardProps {
  company: Company;
  onDone: () => void;
  onCancel: () => void;
}

export default function RatWizard({ company, onDone, onCancel }: RatWizardProps) {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<RATWizardData>({});
  const [tipos, setTipos] = useState<string[]>([]);
  const [tipoSel, setTipoSel] = useState('');
  const [saving, setSaving] = useState(false);
  const [draftToastShown, setDraftToastShown] = useState(false);
  const [sugerencias, setSugerencias] = useState<import('@/types').RATSugerido[]>([]);
  const [mostrarPaso0, setMostrarPaso0] = useState(false);
  const [rubroNombre, setRubroNombre] = useState('');

  const DRAFT_KEY = `${DRAFT_KEY_PREFIX}${company.id}`;

  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setData(parsed.data ?? {});
        setStep(parsed.step ?? 1);
        if (parsed.data && Object.keys(parsed.data).length > 0 && !draftToastShown) {
          toast.success('Borrador restaurado automáticamente', { id: 'draft-restored' });
          setDraftToastShown(true);
        }
      } catch {}
    }
  }, [DRAFT_KEY]);

  useEffect(() => {
    api.listarTiposProceso().then(setTipos).catch(() => {});
  }, []);

  useEffect(() => {
    if (company.rubro_id) {
      api.sugerenciasPorRubro(company.rubro_id).then(sugs => {
        setSugerencias(sugs);
        setMostrarPaso0(sugs.length > 0);
      }).catch(() => {});
      api.listarRubros().then(rubros => {
        const r = rubros.find(rub => rub.id === company.rubro_id);
        if (r) setRubroNombre(r.nombre);
      }).catch(() => {});
    }
  }, [company.rubro_id]);

  function usarSugerencia(sug: import('@/types').RATSugerido) {
    setData(d => ({
      ...d,
      nombre_proceso: sug.nombre_proceso,
      categoria_datos: sug.categoria_datos,
      categoria_titulares: sug.categoria_titulares || '',
      finalidad: sug.finalidad || '',
      base_legal: sug.base_legal || 'Consentimiento del titular',
      plazo_retencion: sug.plazo_retencion || '',
      datos_sensibles: sug.datos_sensibles,
      evaluacion_impacto: sug.evaluacion_impacto,
      decisiones_automatizadas: sug.decisiones_automatizadas,
    }));
    setMostrarPaso0(false);
    setStep(1);
  }

  function crearPersonalizado() {
    setMostrarPaso0(false);
    setStep(1);
  }

  function guardarDraft() {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ data, step }));
    if (!draftToastShown) {
      toast.success('Borrador guardado automáticamente', { id: 'draft-saved', duration: 2000 });
      setDraftToastShown(true);
    }
  }

  function limpiarDraft() {
    localStorage.removeItem(DRAFT_KEY);
  }

  function cambiarStep(n: number) {
    setStep(n);
    guardarDraft();
  }

  async function aplicarSugerencias() {
    if (!tipoSel || tipoSel.startsWith('—')) return;
    try {
      const sug = await api.sugerirRat(tipoSel);
      setData(d => ({
        ...d,
        categoria_datos:        sug.categoria_datos as string ?? '',
        categoria_titulares:    sug.categoria_titulares as string ?? '',
        finalidad:              sug.finalidad as string ?? '',
        base_legal:             sug.base_legal as string ?? '',
        plazo_retencion:        sug.plazo_retencion_sugerido as string ?? '',
        datos_sensibles:        sug.datos_sensibles as boolean ?? false,
        tipo_dato_sensible:     sug.tipo_dato_sensible as string ?? '',
        evaluacion_impacto:     sug.evaluacion_impacto as boolean ?? false,
        decisiones_automatizadas: sug.decisiones_automatizadas as boolean ?? false,
        _sug_observacion:       sug.observacion as string ?? '',
      }));
      toast.success(`Sugerencias aplicadas para: ${tipoSel}`);
    } catch {
      toast.error('No se pudieron obtener sugerencias.');
    }
  }

  async function guardar() {
    setSaving(true);
    try {
      const testIL = data.base_legal === 'Interés legítimo' && data._testIL
        ? `Paso 1: ${data._testIL.paso1}\nPaso 2: ${data._testIL.paso2}\nPaso 3: ${data._testIL.paso3}`
        : undefined;
      const payload = {
        company_id:                  company.id,
        nombre_proceso:              data.nombre_proceso!,
        categoria_datos:             data.categoria_datos,
        categoria_titulares:         data.categoria_titulares || undefined,
        finalidad:                   data.finalidad,
        base_legal:                  data.base_legal,
        fuente_datos:                data.fuente_datos,
        plazo_retencion:             data.plazo_retencion,
        transferencia_datos:         data.transferencia_datos || undefined,
        medidas_seguridad:           data.medidas_seguridad || undefined,
        destinatarios:               data.destinatarios || undefined,
        transferencia_internacional: data.transferencia_internacional ?? false,
        pais_destino:                data.pais_destino || undefined,
        garantias_transferencia_int: data.garantias_transferencia_int || undefined,
        datos_sensibles:             data.datos_sensibles ?? false,
        tipo_dato_sensible:          data.tipo_dato_sensible || undefined,
        evaluacion_impacto:          data.evaluacion_impacto ?? false,
        decisiones_automatizadas:    data.decisiones_automatizadas ?? false,
        test_interes_legitimo:        testIL,
      };
      const result = await api.crearRat(payload);
      toast.success(`Proceso "${result.nombre_proceso}" registrado exitosamente en el RAT.`);
      limpiarDraft();
      onDone();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  }

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  return (
    <div className="overflow-y-auto pb-4 -mx-4 px-4 min-h-0">
      {/* PASO 0: Sugerencias por rubro */}
      {mostrarPaso0 && step === 0 && (
        <div className="space-y-6">
          <div className="rounded-xl p-5" style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}>
            <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>Rat sugeridos para tu rubro</p>
            <h3 className="text-lg font-bold text-white">{rubroNombre || '...'}</h3>
            <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.6)' }}>Selecciona un proceso predefinido o crea uno personalizado</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sugerencias.map(sug => (
              <div
                key={sug.id}
                className="rounded-xl p-4 cursor-pointer transition hover:shadow-md"
                style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}
                onClick={() => usarSugerencia(sug)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-semibold text-sm" style={{ color: '#111827' }}>{sug.nombre_proceso}</p>
                    <p className="text-xs mt-1" style={{ color: '#6B7280' }}>{sug.categoria_datos}</p>
                    {sug.categoria_titulares && (
                      <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Titulares: {sug.categoria_titulares}</p>
                    )}
                    <div className="flex gap-1 flex-wrap mt-2">
                      {sug.datos_sensibles && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEF3C7', color: '#92400E' }}>⚠️ Datos sensibles</span>}
                      {sug.evaluacion_impacto && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#DBEAFE', color: '#1E3A8A' }}>📋 EIPD</span>}
                      {sug.decisiones_automatizadas && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#F3F4F6', color: '#374151' }}>🤖 Dec. auto</span>}
                    </div>
                  </div>
                  <button
                    className="ml-3 px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition flex-shrink-0"
                    style={{ background: '#2563EB' }}
                    onClick={e => { e.stopPropagation(); usarSugerencia(sug); }}
                  >
                    Usar
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-center">
            <button
              onClick={crearPersonalizado}
              className="px-6 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
              style={{ color: '#374151', borderColor: '#E5E7EB' }}
            >
              + Crear proceso personalizado
            </button>
          </div>
        </div>
      )}

      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => {
            if (confirm('¿Estás seguro de que quieres salir?\n\nLos datos no guardados se perderán.')) {
              limpiarDraft();
              onCancel();
            }
          }}
          className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50"
          style={{ color: '#6B7280', borderColor: '#E5E7EB' }}
        >
          ← Volver al listado
        </button>
        <h2 className="text-lg font-bold" style={{ color: '#111827' }}>Nuevo proceso RAT</h2>
      </div>

      <StepIndicator steps={STEPS} current={step} />

      <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
        {/* PASO 1 */}
        {step === 1 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 1 · Identificación del proceso</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Nombre y tipo de actividad de tratamiento que deseas registrar.</p>
            </div>

            {/* Sugerencias */}
            <div className="rounded-xl p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
              <p className="text-sm font-semibold mb-1" style={{ color: '#111827' }}>🤖 Sugerencias inteligentes</p>
              <p className="text-xs mb-3" style={{ color: '#6B7280' }}>
                Selecciona el tipo de proceso y Custodio completará automáticamente los campos más relevantes.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <select
                  value={tipoSel}
                  onChange={e => setTipoSel(e.target.value)}
                  className={inputCls + ' flex-1'}
                  style={inputStyle}
                >
                  <option value="">— Selecciona para obtener sugerencias —</option>
                  {tipos.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
                <button
                  onClick={aplicarSugerencias}
                  disabled={!tipoSel || tipoSel.startsWith('—')}
                  className="px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50 transition flex-shrink-0"
                  style={{ background: '#2563EB' }}
                >
                  Aplicar
                </button>
              </div>
              {data._sug_observacion && (
                <div className="mt-3">
                  <AlertBanner message={data._sug_observacion} type="info" />
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Nombre del proceso *
              </label>
              <input
                type="text"
                value={data.nombre_proceso ?? ''}
                onChange={e => setData(d => ({ ...d, nombre_proceso: e.target.value }))}
                placeholder="Ej: Gestión de datos de clientes, Nómina de empleados"
                className={inputCls}
                style={inputStyle}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Categorías de titulares * <span className="text-xs font-normal" style={{ color: '#9CA3AF' }}>(Art. 16 Ley 21.719 — campo mínimo)</span>
              </label>
              <input
                type="text"
                value={data.categoria_titulares ?? ''}
                onChange={e => setData(d => ({ ...d, categoria_titulares: e.target.value }))}
                placeholder="Ej: Clientes, empleados, proveedores, pacientes, postulantes..."
                className={inputCls}
                style={inputStyle}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                  Fuente de los datos *
                </label>
                <input
                  type="text"
                  value={data.fuente_datos ?? ''}
                  onChange={e => { setData(d => { const n = { ...d, fuente_datos: e.target.value }; guardarDraft(); return n; }); }}
                  placeholder="Ej: Directamente del titular, base interna, terceros"
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                  Destinatarios / Encargados del tratamiento
                </label>
                <input
                  type="text"
                  value={data.destinatarios ?? ''}
                  onChange={e => setData(d => ({ ...d, destinatarios: e.target.value }))}
                  placeholder="Ej: Proveedor CRM (encargado), área de RRHH, SII"
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={() => {
                  if (confirm('¿Estás seguro de que quieres cancelar?\n\nSe perderán los datos ingresados en este paso.')) {
                    limpiarDraft();
                    onCancel();
                  }
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  if (!data.nombre_proceso?.trim()) { toast.error('El nombre del proceso es obligatorio.'); return; }
                  if (!data.categoria_titulares?.trim()) { toast.error('Las categorías de titulares son obligatorias (Art. 16 Ley 21.719).'); return; }
                  if (!data.fuente_datos?.trim()) { toast.error('La fuente de datos es obligatoria.'); return; }
                  cambiarStep(2);
                }}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
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
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Categoría de datos tratados *
              </label>
              <textarea
                value={data.categoria_datos ?? ''}
                onChange={e => setData(d => ({ ...d, categoria_datos: e.target.value }))}
                rows={3}
                placeholder="Ej: Datos identificativos (nombre, RUT, email), datos laborales, datos de salud..."
                className={inputCls}
                style={inputStyle}
              />
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="flex items-start gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={data.datos_sensibles ?? false}
                    onChange={e => setData(d => ({ ...d, datos_sensibles: e.target.checked, tipo_dato_sensible: e.target.checked ? d.tipo_dato_sensible : '' }))}
                    className="mt-0.5 rounded"
                  />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>
                    ⚠️ El proceso trata datos sensibles (Art. 2 letra g)
                  </span>
                </label>
                {data.datos_sensibles && (
                  <div className="space-y-2 pl-6">
                    <select
                      value={data.tipo_dato_sensible ?? ''}
                      onChange={e => setData(d => ({ ...d, tipo_dato_sensible: e.target.value }))}
                      className={inputCls}
                      style={inputStyle}
                    >
                      <option value="">— Seleccione el tipo de dato sensible (Art. 2 g) —</option>
                      {TIPOS_DATO_SENSIBLE.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                    <AlertBanner
                      message="Dato sensible: requiere base legal expresa y medidas de seguridad reforzadas. Si es biometría, aplica Art. 16 BIS y la EIPD es obligatoria."
                      type="warning"
                    />
                  </div>
                )}
              </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={data.evaluacion_impacto ?? false}
                      onChange={e => setData(d => ({ ...d, evaluacion_impacto: e.target.checked }))}
                      className="mt-0.5 rounded"
                    />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>
                      📋 Requiere Evaluación de Impacto (EIPD)
                    </span>
                  </label>
                  {data.evaluacion_impacto && (
                    <AlertBanner
                      message="La EIPD debe realizarse y documentarse antes de iniciar el tratamiento (Art. 15 bis)."
                      type="info"
                    />
                  )}
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={data.decisiones_automatizadas ?? false}
                      onChange={e => setData(d => ({ ...d, decisiones_automatizadas: e.target.checked }))}
                      className="mt-0.5 rounded"
                    />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>
                      🤖 Involucra decisiones automatizadas
                    </span>
                  </label>
                  {data.decisiones_automatizadas && (
                    <AlertBanner
                      message="Los titulares tienen derecho a solicitar revisión humana e impugnar la decisión (Art. 8). Documente la lógica del sistema."
                      type="info"
                    />
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={() => cambiarStep(1)}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                ← Anterior
              </button>
              <button
                onClick={() => {
                  if (!data.categoria_datos?.trim()) { toast.error('La categoría de datos es obligatoria.'); return; }
                  cambiarStep(3);
                }}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                Siguiente →
              </button>
              <button
                onClick={() => {
                  if (confirm('¿Estás seguro de que quieres cancelar?\n\nSe perderán los datos ingresados en este paso.')) {
                    limpiarDraft();
                    onCancel();
                  }
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
              >
                Cancelar
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
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Finalidad del tratamiento *
              </label>
              <textarea
                value={data.finalidad ?? ''}
                onChange={e => setData(d => ({ ...d, finalidad: e.target.value }))}
                rows={3}
                placeholder="Ej: Gestión de la relación comercial, liquidación de remuneraciones..."
                className={inputCls}
                style={inputStyle}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Base legal del tratamiento * <span className="text-xs font-normal" style={{ color: '#9CA3AF' }}>(Art. 13 Ley 21.719)</span>
              </label>
              <select
                value={data.base_legal ?? BASES_LEGALES[0]}
                onChange={e => setData(d => ({ ...d, base_legal: e.target.value }))}
                className={inputCls}
                style={inputStyle}
              >
                {BASES_LEGALES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
              {data.base_legal && DESCRIPCIONES_BASE[data.base_legal] && (
                <div className="mt-2">
                  <AlertBanner
                    message={DESCRIPCIONES_BASE[data.base_legal]}
                    type={data.base_legal === 'Interés legítimo' || data.base_legal === 'Datos biométricos de identificación (Art. 16 BIS)' ? 'warning' : 'info'}
                  />
                </div>
              )}
              {data.base_legal === 'Consentimiento del titular' && data.datos_sensibles && (
                <div className="mt-2">
                  <AlertBanner
                    message="⚠️ Consentimiento + datos sensibles: el consentimiento debe ser EXPRESO (no basta implícito o tácito). Documente el mecanismo de obtención y revocación."
                    type="warning"
                  />
                </div>
              )}
            </div>

            {data.base_legal === 'Interés legítimo' && (
              <details className="rounded-lg" style={{ border: '1px solid #E5E7EB' }}>
                <summary className="px-4 py-3 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>
                  📋 Test de interés legítimo (3 pasos)
                </summary>
                <div className="px-4 pb-4 space-y-3">
                  <div>
                    <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                      Paso 1 — ¿Existe un interés legítimo real?
                    </label>
                    <textarea
                      rows={2}
                      value={data._testIL?.paso1 ?? ''}
                      onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL!, paso1: e.target.value } }))}
                      placeholder="Describa el interés legítimo: marketing directo, seguridad, prevención de fraude..."
                      className={inputCls}
                      style={inputStyle}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                      Paso 2 — ¿El tratamiento es necesario para ese interés?
                    </label>
                    <textarea
                      rows={2}
                      value={data._testIL?.paso2 ?? ''}
                      onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL, paso2: e.target.value } }))}
                      placeholder="Justifique por qué el tratamiento es necesario y no hay alternativa menos invasiva."
                      className={inputCls}
                      style={inputStyle}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>
                      Paso 3 — ¿Prevalece sobre los derechos del titular?
                    </label>
                    <textarea
                      rows={3}
                      value={data._testIL?.paso3 ?? ''}
                      onChange={e => setData(d => ({ ...d, _testIL: { ...d._testIL, paso3: e.target.value } }))}
                      placeholder="Considere expectativas razonables del titular, impacto en su privacidad, medidas mitigadoras..."
                      className={inputCls}
                      style={inputStyle}
                    />
                  </div>
                </div>
              </details>
            )}

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={() => cambiarStep(2)}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                ← Anterior
              </button>
              <button
                onClick={() => {
                  if (!data.finalidad?.trim()) { toast.error('La finalidad es obligatoria.'); return; }
                  if (!data.base_legal) setData(d => ({ ...d, base_legal: BASES_LEGALES[0] }));
                  if (data.base_legal === 'Interés legítimo' && (!data._testIL?.paso1 || !data._testIL?.paso2 || !data._testIL?.paso3)) {
                    toast.error('Complete los 3 pasos del test de interés legítimo.'); return;
                  }
                  cambiarStep(4);
                }}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                Siguiente →
              </button>
              <button
                onClick={() => {
                  if (confirm('¿Estás seguro de que quieres cancelar?\n\nSe perderán los datos ingresados en este paso.')) {
                    limpiarDraft();
                    onCancel();
                  }
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
              >
                Cancelar
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
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                    Plazo de retención *
                  </label>
                  <input
                    type="text"
                    value={data.plazo_retencion ?? ''}
                    onChange={e => setData(d => ({ ...d, plazo_retencion: e.target.value }))}
                    placeholder="Ej: 5 años desde el último contacto comercial"
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                    Medidas de seguridad implementadas
                  </label>
                  <textarea
                    value={data.medidas_seguridad ?? ''}
                    onChange={e => setData(d => ({ ...d, medidas_seguridad: e.target.value }))}
                    rows={2}
                    placeholder="Ej: Cifrado AES-256, acceso por roles, MFA..."
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                    Transferencias o comunicaciones de datos
                  </label>
                  <textarea
                    value={data.transferencia_datos ?? ''}
                    onChange={e => setData(d => ({ ...d, transferencia_datos: e.target.value }))}
                    rows={2}
                    placeholder="Ej: Compartidos con proveedor de nómina bajo contrato de encargo"
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
                <div className="space-y-2">
                  <label className="flex items-start gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={data.transferencia_internacional ?? false}
                      onChange={e => setData(d => ({ ...d, transferencia_internacional: e.target.checked, pais_destino: e.target.checked ? d.pais_destino : undefined }))}
                      className="mt-0.5 rounded"
                    />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>
                      🌐 Transferencia internacional de datos
                    </span>
                  </label>
                  {data.transferencia_internacional && (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={data.pais_destino ?? ''}
                        onChange={e => setData(d => ({ ...d, pais_destino: e.target.value }))}
                        placeholder="Ej: Estados Unidos, España, Brasil"
                        className={inputCls}
                        style={inputStyle}
                      />
                      <select
                        value={data.garantias_transferencia_int ?? ''}
                        onChange={e => setData(d => ({ ...d, garantias_transferencia_int: e.target.value }))}
                        className={inputCls}
                        style={inputStyle}
                      >
                        <option value="">— Garantías aplicables (obligatorio) —</option>
                        <option value="Nivel adecuado de protección (decisión APDC o UE)">Nivel adecuado de protección (decisión APDC o UE)</option>
                        <option value="Cláusulas Contractuales Tipo (SCC)">Cláusulas Contractuales Tipo (SCC)</option>
                        <option value="Normas Corporativas Vinculantes (BCR)">Normas Corporativas Vinculantes (BCR)</option>
                        <option value="Consentimiento explícito del titular para la transferencia">Consentimiento explícito del titular para la transferencia</option>
                        <option value="Contrato con cláusulas de protección equivalentes">Contrato con cláusulas de protección equivalentes</option>
                        <option value="Otra garantía adecuada">Otra garantía adecuada (especificar en transferencia de datos)</option>
                      </select>
                      <AlertBanner
                        message="Chile NO está en la lista de adecuación de la UE. Si el destinatario es europeo, se requieren SCC u otras garantías. Documente siempre las garantías aplicadas (Art. 28 Ley 21.719)."
                        type="warning"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Resumen */}
            <details className="rounded-lg" style={{ border: '1px solid #E5E7EB' }}>
              <summary className="px-4 py-3 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>
                📋 Revisar resumen antes de guardar
              </summary>
              <div className="px-4 pb-4 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                {[
                  ['Proceso', data.nombre_proceso],
                  ['Titulares', data.categoria_titulares],
                  ['Fuente', data.fuente_datos],
                  ['Finalidad', data.finalidad],
                  ['Base legal', data.base_legal],
                  ['Datos sensibles', data.datos_sensibles ? `Sí ⚠️ (${data.tipo_dato_sensible || 'tipo no especificado'})` : 'No'],
                  ['Decisiones automatizadas', data.decisiones_automatizadas ? 'Sí 🤖' : 'No'],
                  ['EIPD requerida', data.evaluacion_impacto ? 'Sí 📋' : 'No'],
                  ['Transfer. internacional', data.transferencia_internacional ? `Sí 🌐 — ${data.garantias_transferencia_int || 'garantías pendientes'}` : 'No'],
                ].map(([k, v]) => (
                  <div key={k} className="text-sm py-0.5">
                    <span className="font-medium" style={{ color: '#374151' }}>{k}: </span>
                    <span style={{ color: '#6B7280' }}>{v ?? '—'}</span>
                  </div>
                ))}
              </div>
            </details>

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={() => cambiarStep(3)}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                ← Anterior
              </button>
              <button
                onClick={() => {
                  if (!data.plazo_retencion?.trim()) { toast.error('El plazo de retención es obligatorio.'); return; }
                  guardar();
                }}
                disabled={saving}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {saving ? 'Guardando...' : '✓ Guardar en el RAT'}
              </button>
              <button
                onClick={() => {
                  if (confirm('¿Estás seguro de que quieres cancelar?\n\nSe perderán los datos ingresados en este paso.')) {
                    limpiarDraft();
                    onCancel();
                  }
                }}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
