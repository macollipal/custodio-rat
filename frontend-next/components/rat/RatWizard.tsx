'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import AlertBanner from '@/components/dashboard/AlertBanner';
import StepIndicator from '@/components/ui/StepIndicator';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import FormField from '@/components/ui/FormField';
import { useStepValidation } from './ratWizardValidation';
import type { Company, RAT, RATWizardData } from '@/types';

import { BASES_LEGALES, TIPOS_DATO_SENSIBLE, DRAFT_KEY_PREFIX, DATOS_NNA_OPCIONES, NIVEL_CONFIDENCIALIDAD_OPCIONES, ESTRUCTURA_DATO_OPCIONES, CICLO_PROCESAMIENTO_OPCIONES, AUTOMATIZACION_OPCIONES, FRECUENCIA_OPCIONES } from '@/lib/constants';

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

const STEPS = ['Identificación', 'Datos tratados', 'Finalidad y ley', 'Transferencias', 'Compliance'];
const OPERACIONES_TRATAMIENTO_OPCIONES = ['recoleccion','almacenamiento','consulta','uso','comunicacion','cesion','eliminacion'];

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
  const [confirmCancel, setConfirmCancel] = useState(false);

  const validation = useStepValidation(step, data);
  const fieldErrors = validation.errors;
  const stepIsValid = validation.isValid;

  const DRAFT_KEY = `${DRAFT_KEY_PREFIX}${company.id}`;

  useEffect(() => {
    if (typeof window === 'undefined') return;
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
        nombre_encargado:           data.nombre_encargado || undefined,
        tiene_contrato_encargado:   data.tiene_contrato_encargado ?? false,
        transferencia_internacional: data.transferencia_internacional ?? false,
        pais_destino:                data.pais_destino || undefined,
        garantias_transferencia_int: data.garantias_transferencia_int || undefined,
        datos_sensibles:             data.datos_sensibles ?? false,
        tipo_dato_sensible:          data.tipo_dato_sensible || undefined,
        evaluacion_impacto:          data.evaluacion_impacto ?? false,
        decisiones_automatizadas:    data.decisiones_automatizadas ?? false,
        test_interes_legitimo:        testIL,
        // Campos nuevos gaps Ley 21.719 (Iter 10)
        sistema_almacenamiento:       data.sistema_almacenamiento || undefined,
        volumen_titulares_estimado:   data.volumen_titulares_estimado || undefined,
        operaciones_tratamiento:      (data.operaciones_tratamiento?.length ?? 0) > 0 ? data.operaciones_tratamiento : undefined,
        logica_automatizada:          data.logica_automatizada || undefined,
        responsable_tratamiento_email: data.responsable_tratamiento_email || undefined,
        // Campos Tier 1 - Gaps criticos (Iter 11)
        datos_nna:                    data.datos_nna || undefined,
        nivel_confidencialidad:       data.nivel_confidencialidad || undefined,
        estructura_dato:               data.estructura_dato || undefined,
        datos_anonimizados:           data.datos_anonimizados ?? false,
        datos_seudonimizados:          data.datos_seudonimizados ?? false,
        // Campos Tier 2 - Operativos (Iter 11)
        ciclo_procesamiento:          data.ciclo_procesamiento || undefined,
        automatizacion:               data.automatizacion || undefined,
        frecuencia:                   data.frecuencia || undefined,
        transferencia_nacional:       data.transferencia_nacional ?? false,
        doc_clausulas:                data.doc_clausulas || undefined,
        medidas_organizativas:        data.medidas_organizativas || undefined,
        mecanismos_eliminacion:        data.mecanismos_eliminacion || undefined,
        tecnica_anonimizacion:        data.tecnica_anonimizacion || undefined,
        origen_dato_portabilidad:     data.origen_dato_portabilidad || undefined,
        fecha_levantamiento:          data.fecha_levantamiento || undefined,
      };
      const result = await api.crearRat(payload);
      if (data.datos_sensibles && data.consentimiento_nombre && data.consentimiento_email) {
        await api.registrarConsentimiento({
          rat_id: result.id,
          nombre_titular: data.consentimiento_nombre,
          email_titular: data.consentimiento_email,
          canal: 'sistema',
          texto_consentimiento: data.consentimiento_texto || 'Consentimiento expreso para tratamiento de datos sensibles.',
          datos_sensibles: true,
        });
      }
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

      <div className="flex items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setConfirmCancel(true)}
            className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50"
            style={{ color: '#6B7280', borderColor: '#E5E7EB' }}
          >
            ← Volver al listado
          </button>
          <h2 className="text-lg font-bold" style={{ color: '#111827' }}>Nuevo proceso RAT</h2>
        </div>
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

            <FormField label="Nombre del proceso" required htmlFor="rw-nombre_proceso" error={fieldErrors.nombre_proceso}>
              <input
                id="rw-nombre_proceso"
                type="text"
                value={data.nombre_proceso ?? ''}
                onChange={e => setData(d => ({ ...d, nombre_proceso: e.target.value }))}
                placeholder="Ej: Gestión de datos de clientes, Nómina de empleados"
                aria-required="true"
                aria-invalid={!!fieldErrors.nombre_proceso}
                className={inputCls}
                style={{
                  ...inputStyle,
                  borderColor: fieldErrors.nombre_proceso ? '#DC2626' : '#D1D5DB',
                }}
              />
            </FormField>

            <FormField
              label="Categorías de titulares"
              required
              htmlFor="rw-categoria_titulares"
              hint="Art. 16 Ley 21.719 — campo mínimo"
              error={fieldErrors.categoria_titulares}
            >
              <input
                id="rw-categoria_titulares"
                type="text"
                value={data.categoria_titulares ?? ''}
                onChange={e => setData(d => ({ ...d, categoria_titulares: e.target.value }))}
                placeholder="Ej: Clientes, empleados, proveedores, pacientes, postulantes..."
                aria-required="true"
                aria-invalid={!!fieldErrors.categoria_titulares}
                className={inputCls}
                style={{
                  ...inputStyle,
                  borderColor: fieldErrors.categoria_titulares ? '#DC2626' : '#D1D5DB',
                }}
              />
            </FormField>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FormField label="Fuente de los datos" required htmlFor="rw-fuente_datos" error={fieldErrors.fuente_datos}>
                <input
                  id="rw-fuente_datos"
                  type="text"
                  value={data.fuente_datos ?? ''}
                  onChange={e => { setData(d => { const n = { ...d, fuente_datos: e.target.value }; guardarDraft(); return n; }); }}
                  placeholder="Ej: Directamente del titular, base interna, terceros"
                  aria-required="true"
                  aria-invalid={!!fieldErrors.fuente_datos}
                  className={inputCls}
                  style={{
                    ...inputStyle,
                    borderColor: fieldErrors.fuente_datos ? '#DC2626' : '#D1D5DB',
                  }}
                />
              </FormField>
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

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                Nombre del encargado del tratamiento
              </label>
              <input
                type="text"
                value={data.nombre_encargado ?? ''}
                onChange={e => setData(d => ({ ...d, nombre_encargado: e.target.value }))}
                placeholder="Ej: Proveedor CRM, asesora laboral..."
                className={inputCls}
                style={inputStyle}
              />
              <div className="mt-2">
                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={data.tiene_contrato_encargado ?? false}
                    onChange={e => setData(d => ({ ...d, tiene_contrato_encargado: e.target.checked }))}
                    className="mt-0.5 rounded"
                  />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>
                    ✓ Tiene contrato de encargo (Art. 14 quáter Ley 21.719)
                  </span>
                </label>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={() => {
                  if (!stepIsValid) {
                    toast.error('Completa los campos obligatorios antes de continuar.');
                    return;
                  }
                  cambiarStep(2);
                }}
                disabled={!stepIsValid}
                aria-disabled={!stepIsValid}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50"
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

            <FormField label="Categoría de datos tratados" required htmlFor="rw-categoria_datos" error={fieldErrors.categoria_datos}>
              <textarea
                id="rw-categoria_datos"
                value={data.categoria_datos ?? ''}
                onChange={e => setData(d => ({ ...d, categoria_datos: e.target.value }))}
                rows={3}
                placeholder="Ej: Datos identificativos (nombre, RUT, email), datos laborales, datos de salud..."
                aria-required="true"
                aria-invalid={!!fieldErrors.categoria_datos}
                className={inputCls}
                style={{
                  ...inputStyle,
                  borderColor: fieldErrors.categoria_datos ? '#DC2626' : '#D1D5DB',
                }}
              />
            </FormField>

            <div className="space-y-4">
              <div className="space-y-2">
                <label className="flex items-start gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={data.datos_sensibles ?? false}
                    onChange={e => setData(d => ({
                      ...d,
                      datos_sensibles: e.target.checked,
                      tipo_dato_sensible: e.target.checked ? d.tipo_dato_sensible : '',
                      evaluacion_impacto: e.target.checked ? true : d.evaluacion_impacto,
                    }))}
                    className="mt-0.5 rounded"
                  />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>
                    ⚠️ El proceso trata datos sensibles (Art. 2 letra g)
                  </span>
                </label>
                {data.datos_sensibles && (
                  <div className="space-y-2 pl-6">
                    <FormField label="Tipo de dato sensible (Art. 2 g)" required htmlFor="rw-tipo_dato_sensible" error={fieldErrors.tipo_dato_sensible}>
                      <select
                        id="rw-tipo_dato_sensible"
                        value={data.tipo_dato_sensible ?? ''}
                        onChange={e => setData(d => ({ ...d, tipo_dato_sensible: e.target.value }))}
                        aria-required="true"
                        aria-invalid={!!fieldErrors.tipo_dato_sensible}
                        className={inputCls}
                        style={{
                          ...inputStyle,
                          borderColor: fieldErrors.tipo_dato_sensible ? '#DC2626' : '#D1D5DB',
                        }}
                      >
                        <option value="">— Seleccione el tipo de dato sensible (Art. 2 g) —</option>
                        {TIPOS_DATO_SENSIBLE.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </FormField>
                    <AlertBanner
                      message="Dato sensible: requiere base legal expresa y medidas de seguridad reforzadas. Si es biometría, aplica Art. 16 BIS y la EIPD es obligatoria."
                      type="warning"
                    />
                    <div className="rounded-lg p-3" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                      <p className="text-xs font-semibold mb-2" style={{ color: '#1E40AF' }}>B-06: Consentimiento Expreso (Art. 12)</p>
                      <p className="text-xs mb-2" style={{ color: '#374151' }}>Para datos sensibles, el consentimiento debe ser expreso. Registre el consentimiento del titular.</p>
                      <div className="grid grid-cols-2 gap-2">
                        <input type="text" value={data.consentimiento_nombre ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_nombre: e.target.value }))} placeholder="Nombre del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                        <input type="email" value={data.consentimiento_email ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_email: e.target.value }))} placeholder="Email del titular" className="px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                      </div>
                      <textarea value={data.consentimiento_texto ?? ''} onChange={e => setData(d => ({ ...d, consentimiento_texto: e.target.value }))} rows={2} placeholder="Texto del consentimiento expreso..." className="w-full mt-2 px-2 py-1.5 rounded text-xs border" style={{ borderColor: '#BFDBFE' }} />
                    </div>
                  </div>
                )}
              </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className={`flex items-start gap-2.5 ${data.datos_sensibles ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}>
                    <input
                      type="checkbox"
                      checked={data.evaluacion_impacto ?? false}
                      disabled={data.datos_sensibles}
                      onChange={e => setData(d => ({ ...d, evaluacion_impacto: e.target.checked }))}
                      className="mt-0.5 rounded"
                    />
                    <span className="text-sm font-medium" style={{ color: '#374151' }}>
                      📋 Requiere Evaluación de Impacto (EIPD) {data.datos_sensibles ? '(obligatoria por datos sensibles — Art. 15 bis)' : ''}
                    </span>
                  </label>
                  {data.datos_sensibles && (
                    <AlertBanner
                      message="EIPD obligatoria: el tratamiento de datos sensibles requiere evaluación de impacto documentada antes de iniciar (Art. 15 bis Ley 21.719)."
                      type="warning"
                    />
                  )}
                  {data.evaluacion_impacto && !data.datos_sensibles && (
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
                    <>
                      <AlertBanner
                        message="Los titulares tienen derecho a solicitar revisión humana e impugnar la decisión (Art. 8). Documente la lógica del sistema."
                        type="info"
                      />
                      <textarea
                        value={data.logica_automatizada ?? ''}
                        onChange={e => setData(d => ({ ...d, logica_automatizada: e.target.value }))}
                        rows={3}
                        placeholder="Describa la lógica aplicada, consecuencias para el titular y posibilidad de revisión humana..."
                        className={inputCls}
                        style={inputStyle}
                      />
                    </>
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
                  if (!stepIsValid) {
                    toast.error('Completa los campos obligatorios antes de continuar.');
                    return;
                  }
                  cambiarStep(3);
                }}
                disabled={!stepIsValid}
                aria-disabled={!stepIsValid}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50"
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

            <FormField label="Finalidad del tratamiento" required htmlFor="rw-finalidad" error={fieldErrors.finalidad}>
              <textarea
                id="rw-finalidad"
                value={data.finalidad ?? ''}
                onChange={e => setData(d => ({ ...d, finalidad: e.target.value }))}
                rows={3}
                placeholder="Ej: Gestión de la relación comercial, liquidación de remuneraciones..."
                aria-required="true"
                aria-invalid={!!fieldErrors.finalidad}
                className={inputCls}
                style={{
                  ...inputStyle,
                  borderColor: fieldErrors.finalidad ? '#DC2626' : '#D1D5DB',
                }}
              />
            </FormField>

            <FormField
              label="Base legal del tratamiento"
              required
              htmlFor="rw-base_legal"
              hint="Art. 13 Ley 21.719"
              error={fieldErrors.base_legal}
            >
              <select
                id="rw-base_legal"
                value={data.base_legal ?? BASES_LEGALES[0]}
                onChange={e => setData(d => ({ ...d, base_legal: e.target.value }))}
                aria-required="true"
                aria-invalid={!!fieldErrors.base_legal}
                className={inputCls}
                style={{
                  ...inputStyle,
                  borderColor: fieldErrors.base_legal ? '#DC2626' : '#D1D5DB',
                }}
              >
                {BASES_LEGALES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </FormField>

            <div className="space-y-3">
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

              {data.base_legal && data.base_legal !== 'Otra' && (
                <div className="mt-4 p-4 rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                  <label className="block text-sm font-semibold mb-2" style={{ color: '#374151' }}>
                    📄 Documento que respalda la base legal *
                  </label>
                  <p className="text-xs mb-3" style={{ color: '#6B7280' }}>
                    Adjunte el documento correspondiente: consentimiento firmado, contrato, norma legal, EIPD, etc. (PDF, imagen o Word, máx. 10MB).
                  </p>
                  {!data.archivo_base_legal_base64 ? (
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
                          setData(d => ({
                            ...d,
                            archivo_base_legal_base64: b64,
                            archivo_base_legal_nombre: file.name,
                            archivo_base_legal_tipo: file.type,
                          }));
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
                        <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>{data.archivo_base_legal_nombre}</p>
                        <p className="text-xs" style={{ color: '#9CA3AF' }}>{data.archivo_base_legal_tipo}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => setData(d => ({ ...d, archivo_base_legal_base64: undefined, archivo_base_legal_nombre: undefined, archivo_base_legal_tipo: undefined }))}
                        className="text-xs font-semibold px-2 py-1 rounded"
                        style={{ color: '#DC2626', background: '#FEE2E2' }}
                      >
                        Eliminar
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* documento de base legal ahora es opcional */}
            </div>

            {data.base_legal === 'Interés legítimo' && (
              <details className="rounded-lg" style={{ border: '1px solid #E5E7EB' }}>
                <summary className="px-4 py-3 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>
                  📋 Test de interés legítimo (3 pasos)
                </summary>
                <div className="px-4 pt-2 pb-4 space-y-3">
                  <AlertBanner message="El test de interés legítimo es obligatorio (Art. 16 Ley 21.719). Sin este análisis documentado en los 3 pasos, la base legal no será válida como defensa ante la APDC." type="warning" />
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
                {fieldErrors._testIL && (
                  <p role="alert" className="text-xs flex items-center gap-1 mt-2" style={{ color: '#DC2626' }}>
                    <span aria-hidden="true">⚠</span>
                    {fieldErrors._testIL}
                  </p>
                )}
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
                  if (!stepIsValid) {
                    toast.error('Completa los campos obligatorios antes de continuar.');
                    return;
                  }
                  if (!data.base_legal) setData(d => ({ ...d, base_legal: BASES_LEGALES[0] }));
                  cambiarStep(4);
                }}
                disabled={!stepIsValid}
                aria-disabled={!stepIsValid}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-50"
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
                <FormField label="Plazo de retención" required htmlFor="rw-plazo_retencion" error={fieldErrors.plazo_retencion}>
                  <input
                    id="rw-plazo_retencion"
                    type="text"
                    value={data.plazo_retencion ?? ''}
                    onChange={e => setData(d => ({ ...d, plazo_retencion: e.target.value }))}
                    placeholder="Ej: 5 años desde el último contacto comercial"
                    aria-required="true"
                    aria-invalid={!!fieldErrors.plazo_retencion}
                    className={inputCls}
                    style={{
                      ...inputStyle,
                      borderColor: fieldErrors.plazo_retencion ? '#DC2626' : '#D1D5DB',
                    }}
                  />
                </FormField>
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
                      <FormField label="País destino" required htmlFor="rw-pais_destino" error={fieldErrors.pais_destino}>
                        <input
                          id="rw-pais_destino"
                          type="text"
                          value={data.pais_destino ?? ''}
                          onChange={e => setData(d => ({ ...d, pais_destino: e.target.value }))}
                          placeholder="Ej: Estados Unidos, España, Brasil"
                          aria-required="true"
                          aria-invalid={!!fieldErrors.pais_destino}
                          className={inputCls}
                          style={{
                            ...inputStyle,
                            borderColor: fieldErrors.pais_destino ? '#DC2626' : '#D1D5DB',
                          }}
                        />
                      </FormField>
                      <FormField label="Garantías aplicables" required htmlFor="rw-garantias_transferencia_int" error={fieldErrors.garantias_transferencia_int}>
                        <select
                          id="rw-garantias_transferencia_int"
                          value={data.garantias_transferencia_int ?? ''}
                          onChange={e => setData(d => ({ ...d, garantias_transferencia_int: e.target.value }))}
                          aria-required="true"
                          aria-invalid={!!fieldErrors.garantias_transferencia_int}
                          className={inputCls}
                          style={{
                            ...inputStyle,
                            borderColor: fieldErrors.garantias_transferencia_int ? '#DC2626' : '#D1D5DB',
                          }}
                        >
                          <option value="">— Garantías aplicables (obligatorio) —</option>
                          <option value="Nivel adecuado de protección (decisión APDC o UE)">Nivel adecuado de protección (decisión APDC o UE)</option>
                          <option value="Cláusulas Contractuales Tipo (SCC)">Cláusulas Contractuales Tipo (SCC)</option>
                          <option value="Normas Corporativas Vinculantes (BCR)">Normas Corporativas Vinculantes (BCR)</option>
                          <option value="Consentimiento explícito del titular para la transferencia">Consentimiento explícito del titular para la transferencia</option>
                          <option value="Contrato con cláusulas de protección equivalentes">Contrato con cláusulas de protección equivalentes</option>
                          <option value="Otra garantía adecuada">Otra garantía adecuada (especificar en transferencia de datos)</option>
                        </select>
                      </FormField>
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
                  if (!stepIsValid) {
                    toast.error('Completa los campos obligatorios antes de guardar.');
                    return;
                  }
                  guardar();
                }}
                disabled={!stepIsValid || saving}
                aria-disabled={!stepIsValid || saving}
                className="flex-1 px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {saving ? 'Guardando...' : '✓ Guardar en el RAT'}
              </button>
            </div>
          </div>
        )}

        {/* PASO 5 */}
        {step === 5 && (
          <div className="space-y-5">
            <div>
              <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Paso 5 · Compliance avanzado (Tier 1 + Tier 2)</h3>
              <p className="text-sm" style={{ color: '#6B7280' }}>Campos criticos y operativos del template ProBest para compliance total Ley 21.719.</p>
            </div>

            {/* Iter 10 fields + new Tier 1 + Tier 2 */}
            <div className="rounded-lg p-4 space-y-4" style={{ background: '#F0F9FF', border: '1px solid #BAE6FD' }}>
              <h4 className="text-sm font-bold" style={{ color: '#0369A1' }}>Campos de Compliance (Iter 10)</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Sistema de almacenamiento</label>
                  <input type="text" value={data.sistema_almacenamiento ?? ''} onChange={e => setData(d => ({ ...d, sistema_almacenamiento: e.target.value }))} placeholder="Ej: CRM Salesforce, Excel, Google Drive..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Volumen estimado de titulares</label>
                  <input type="number" value={data.volumen_titulares_estimado ?? ''} onChange={e => setData(d => ({ ...d, volumen_titulares_estimado: e.target.value ? parseInt(e.target.value) : undefined }))} placeholder="Ej: 50000" className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Operaciones de tratamiento</label>
                <div className="flex flex-wrap gap-2">
                  {OPERACIONES_TRATAMIENTO_OPCIONES.map(op => (
                    <label key={op} className="flex items-center gap-1.5 cursor-pointer px-3 py-1.5 rounded-full text-xs font-medium border transition" style={{ backgroundColor: (data.operaciones_tratamiento as string[])?.includes(op) ? '#DBEAFE' : 'white', borderColor: (data.operaciones_tratamiento as string[])?.includes(op) ? '#2563EB' : '#D1D5DB', color: (data.operaciones_tratamiento as string[])?.includes(op) ? '#1D4ED8' : '#6B7280' }}>
                      <input type="checkbox" checked={(data.operaciones_tratamiento as string[])?.includes(op) || false} onChange={e => { const current = (data.operaciones_tratamiento as string[]) || []; if (e.target.checked) { setData(d => ({ ...d, operaciones_tratamiento: [...current, op] })); } else { setData(d => ({ ...d, operaciones_tratamiento: current.filter((x: string) => x !== op) })); } }} className="sr-only" />
                      {op}
                    </label>
                  ))}
                </div>
              </div>
              {data.decisiones_automatizadas && (
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Logica de decisiones automatizadas</label>
                  <textarea value={data.logica_automatizada ?? ''} onChange={e => setData(d => ({ ...d, logica_automatizada: e.target.value }))} rows={3} placeholder="Describa la logica aplicada, consecuencias para el titular e intervencion humana disponible" className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Responsable del tratamiento (email)</label>
                <input type="email" value={data.responsable_tratamiento_email ?? ''} onChange={e => setData(d => ({ ...d, responsable_tratamiento_email: e.target.value }))} placeholder="Ej: responsable@empresa.cl" className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
              </div>
            </div>

            {/* Tier 1 */}
            <div className="rounded-lg p-4 space-y-4" style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}>
              <h4 className="text-sm font-bold" style={{ color: '#991B1B' }}>Tier 1 — Datos NNA y Clasificacion de confidencialidad</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Tratamiento de NNA</label>
                  <select value={(data.datos_nna as string) ?? 'ninguno'} onChange={e => setData(d => ({ ...d, datos_nna: e.target.value as 'ninguno' | 'ninos' | 'adolescentes' | 'ambos' }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    {DATOS_NNA_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nivel de confidencialidad</label>
                  <select value={(data.nivel_confidencialidad as string) ?? ''} onChange={e => setData(d => ({ ...d, nivel_confidencialidad: e.target.value as 'DC0' | 'DC1' | 'DC2' | 'DC3' }))} aria-describedby="nivel-conf-tooltip" className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    <option value="">— Seleccionar —</option>
                    {NIVEL_CONFIDENCIALIDAD_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                  {(data.nivel_confidencialidad as string) && (() => {
                    const opt = NIVEL_CONFIDENCIALIDAD_OPCIONES.find(o => o.value === data.nivel_confidencialidad);
                    return opt?.tooltip ? <div role="tooltip" id="nivel-conf-tooltip" className="text-xs mt-1" style={{ color: '#6B7280' }}>{opt.tooltip}</div> : null;
                  })()}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Estructura del dato</label>
                  <select value={(data.estructura_dato as string) ?? ''} onChange={e => setData(d => ({ ...d, estructura_dato: e.target.value as 'estructurado' | 'semiestructurado' | 'no_estructurado' | 'fisico' }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    <option value="">— Seleccionar —</option>
                    {ESTRUCTURA_DATO_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={data.datos_anonimizados ?? false} onChange={e => setData(d => ({ ...d, datos_anonimizados: e.target.checked }))} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos anonimizados</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={data.datos_seudonimizados ?? false} onChange={e => setData(d => ({ ...d, datos_seudonimizados: e.target.checked }))} className="mt-0.5 rounded" />
                  <span className="text-sm font-medium" style={{ color: '#374151' }}>Datos seudonimizados</span>
                </label>
              </div>
            </div>

            {/* Tier 2 */}
            <div className="rounded-lg p-4 space-y-4" style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
              <h4 className="text-sm font-bold" style={{ color: '#166534' }}>Tier 2 — Operativos (ProBest template)</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Ciclo de procesamiento</label>
                  <select value={data.ciclo_procesamiento ?? ''} onChange={e => setData(d => ({ ...d, ciclo_procesamiento: e.target.value }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    <option value="">— Seleccionar —</option>
                    {CICLO_PROCESAMIENTO_OPCIONES.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Grado de automatizacion</label>
                  <select value={data.automatizacion ?? ''} onChange={e => setData(d => ({ ...d, automatizacion: e.target.value }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    <option value="">— Seleccionar —</option>
                    {AUTOMATIZACION_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Frecuencia del tratamiento</label>
                  <select value={data.frecuencia ?? ''} onChange={e => setData(d => ({ ...d, frecuencia: e.target.value }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}>
                    <option value="">— Seleccionar —</option>
                    {FRECUENCIA_OPCIONES.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={data.transferencia_nacional ?? false} onChange={e => setData(d => ({ ...d, transferencia_nacional: e.target.checked }))} className="mt-0.5 rounded" />
                <span className="text-sm font-medium" style={{ color: '#374151' }}>Existe transferencia de datos a nivel nacional (dentro de Chile)</span>
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Documentacion de clausulas</label>
                  <textarea value={data.doc_clausulas ?? ''} onChange={e => setData(d => ({ ...d, doc_clausulas: e.target.value }))} rows={2} placeholder="Politica de privacidad, aviso de privacidad..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Medidas organizativas</label>
                  <textarea value={data.medidas_organizativas ?? ''} onChange={e => setData(d => ({ ...d, medidas_organizativas: e.target.value }))} rows={2} placeholder="Designacion RAI, procedimientos de acceso..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Mecanismos de eliminacion</label>
                  <textarea value={data.mecanismos_eliminacion ?? ''} onChange={e => setData(d => ({ ...d, mecanismos_eliminacion: e.target.value }))} rows={2} placeholder="Borrado seguro NIST 800-88, destruccion fisica..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Tecnica de anonimizacion</label>
                  <input value={data.tecnica_anonimizacion ?? ''} onChange={e => setData(d => ({ ...d, tecnica_anonimizacion: e.target.value }))} placeholder="Pseudonimizacion, k-anonimidad..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Origen del dato (portabilidad)</label>
                  <input value={data.origen_dato_portabilidad ?? ''} onChange={e => setData(d => ({ ...d, origen_dato_portabilidad: e.target.value }))} placeholder="Directamente del titular, de otro responsable..." className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fecha de levantamiento</label>
                  <input type="date" value={data.fecha_levantamiento ?? ''} onChange={e => setData(d => ({ ...d, fecha_levantamiento: e.target.value }))} className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }} />
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button onClick={() => cambiarStep(4)} className="px-5 py-2.5 rounded-lg text-sm font-semibold border transition hover:bg-gray-50" style={{ color: '#374151', borderColor: '#E5E7EB' }}>Anterior</button>
              <button
                onClick={() => {
                  if (!data.plazo_retencion?.trim()) {
                    toast.error('Vuelve al paso 4 y completa el plazo de retención.');
                    setStep(4);
                    return;
                  }
                  guardar();
                }}
                disabled={saving}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {saving ? 'Guardando...' : 'Guardar en el RAT'}
              </button>
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={confirmCancel}
        onClose={() => setConfirmCancel(false)}
        onConfirm={() => {
          limpiarDraft();
          setConfirmCancel(false);
          onCancel();
        }}
        title="¿Salir del wizard?"
        message="Los datos no guardados se perderán.\nSi tienes un borrador, no se restaurará al volver a entrar."
        confirmText="Sí, salir"
        cancelText="Continuar aquí"
        variant="danger"
      />
    </div>
  );
}
