'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import { API_BASE } from '@/lib/constants';
import * as api from '@/lib/api';
import type { RAT } from '@/types';
import { Button } from '@/components/ui/Button';

interface EIPD {
  id: number;
  rat_id: number;
  metodologia: string | null;
  objetivos: string | null;
  necesidad_proporcionalidad: string | null;
  riesgos_identificados: string | null;
  medidas_propuestas: string | null;
  parecer_dpo: string | null;
  parecer_dpo_autor: string | null;
  parecer_dpo_fecha: string | null;
  justificacion_no_aplica: string | null;
  fecha_elaboracion: string | null;
  fecha_aprobacion: string | null;
  resultado: 'completada' | 'no_requerida' | 'no_requerida_justificada' | 'en_proceso';
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

const RESULTADO_LABELS: Record<string, string> = {
  en_proceso: 'En proceso',
  completada: 'Completada',
  no_requerida: 'No requerida',
  no_requerida_justificada: 'No requerida (justificada)',
};

const RESULTADO_COLORS: Record<string, { bg: string; fg: string }> = {
  en_proceso: { bg: '#FEF3C7', fg: '#92400E' },
  completada: { bg: '#D1FAE5', fg: '#065F46' },
  no_requerida: { bg: '#E5E7EB', fg: '#374151' },
  no_requerida_justificada: { bg: '#EFF6FF', fg: '#1E40AF' },
};

export default function EIPDPage() {
  const { company, user } = useApp();
  const router = useRouter();
  const searchParams = useSearchParams();
  const ratIdParam = searchParams.get('rat_id');
  const [items, setItems] = useState<EIPD[]>([]);
  const [rats, setRats] = useState<RAT[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<EIPD | null>(null);
  const [creating, setCreating] = useState(!!ratIdParam);

  async function load() {
    if (!company) return;
    setLoading(true);
    try {
      const res = await api.apiFetch(`${API_BASE}/eipd/?company_id=${company.id}`);
      if (!res.ok) throw new Error('Error al listar EIPDs');
      const data = await res.json();
      setItems(data.eipds || []);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    if (company) {
      api.listarRats(company.id).then(setRats).catch(() => {});
    }
  }, [company]);

  const canEdit = user?.rol_global !== 'usuario';

  const ratsWithEipd = new Set(items.map((e) => e.rat_id));
  const ratsRequiringEipd = rats.filter((r) => r.evaluacion_impacto && !ratsWithEipd.has(r.id));

  const stats = {
    total: items.length,
    en_proceso: items.filter((e) => e.resultado === 'en_proceso').length,
    completadas: items.filter((e) => e.resultado === 'completada').length,
    pendientes: ratsRequiringEipd.length,
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold" style={{ color: '#111827' }}>
            📑 Evaluaciones de Impacto (EIPD)
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Art. 15 ter Ley 21.719 — Obligatoria para datos sensibles y tratamientos de alto riesgo
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div className="p-4 rounded-lg" style={{ background: '#EFF6FF' }}>
          <div className="text-xs text-gray-600">Total EIPDs</div>
          <div className="text-2xl font-bold" style={{ color: '#2563EB' }}>{stats.total}</div>
        </div>
        <div className="p-4 rounded-lg" style={{ background: '#FEF3C7' }}>
          <div className="text-xs text-gray-600">En proceso</div>
          <div className="text-2xl font-bold" style={{ color: '#D97706' }}>{stats.en_proceso}</div>
        </div>
        <div className="p-4 rounded-lg" style={{ background: '#ECFDF5' }}>
          <div className="text-xs text-gray-600">Completadas</div>
          <div className="text-2xl font-bold" style={{ color: '#059669' }}>{stats.completadas}</div>
        </div>
        <div className="p-4 rounded-lg" style={{ background: '#FEE2E2' }}>
          <div className="text-xs text-gray-600">Pendientes</div>
          <div className="text-2xl font-bold" style={{ color: '#DC2626' }}>{stats.pendientes}</div>
        </div>
      </div>

      {ratsRequiringEipd.length > 0 && canEdit && (
        <div className="mb-6 p-4 rounded-lg" style={{ background: '#FEF3C7', border: '1px solid #FCD34D' }}>
          <div className="font-semibold text-amber-800 mb-2">
            ⚠️ {ratsRequiringEipd.length} RAT{ratsRequiringEipd.length === 1 ? '' : 's'} requiere{nrPlural(ratsRequiringEipd.length)} EIPD
          </div>
          <div className="text-sm text-amber-700 mb-3">
            Los siguientes RATs declaran datos sensibles o transferencias internacionales pero no tienen EIPD registrada:
          </div>
          <ul className="text-sm space-y-1">
            {ratsRequiringEipd.map((r) => (
              <li key={r.id} className="flex justify-between items-center bg-white/60 rounded p-2">
                <span>• {r.nombre_proceso}</span>
                <Button
                  size="sm"
                  onClick={() => setCreating(true)}
                  style={{ background: '#D97706', color: '#FFFFFF' }}
                >
                  Crear EIPD
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-gray-500">Cargando...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No hay EIPDs registradas. Crea una desde la sección de arriba si tienes RATs que la requieran.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border" style={{ borderColor: '#E5E7EB' }}>
          <table className="w-full text-sm">
            <thead style={{ background: '#F9FAFB' }}>
              <tr>
                <th className="text-left px-4 py-3 font-semibold">RAT</th>
                <th className="text-left px-4 py-3 font-semibold">Resultado</th>
                <th className="text-left px-4 py-3 font-semibold">F. Elaboración</th>
                <th className="text-left px-4 py-3 font-semibold">F. Aprobación</th>
                <th className="text-left px-4 py-3 font-semibold">Actualizado</th>
                <th className="text-left px-4 py-3 font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((e) => {
                const rat = rats.find((r) => r.id === e.rat_id);
                const colors = RESULTADO_COLORS[e.resultado] || RESULTADO_COLORS.en_proceso;
                return (
                  <tr key={e.id} className="border-t" style={{ borderColor: '#E5E7EB' }}>
                    <td className="px-4 py-3 font-medium">
                      {rat?.nombre_proceso || `RAT #${e.rat_id}`}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-0.5 rounded text-xs font-medium"
                        style={{ background: colors.bg, color: colors.fg }}
                      >
                        {RESULTADO_LABELS[e.resultado]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {e.fecha_elaboracion || '—'}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {e.fecha_aprobacion || '—'}
                    </td>
                    <td className="px-4 py-3 text-gray-700 text-xs">
                      {new Date(e.updated_at).toLocaleDateString('es-CL')}
                    </td>
                    <td className="px-4 py-3">
                      {canEdit ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditing(e)}
                          className="!min-h-0"
                          style={{ color: '#1D4ED8' }}
                        >
                          Editar
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditing(e)}
                          className="!min-h-0"
                          style={{ color: '#1D4ED8' }}
                        >
                          Ver
                        </Button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {(editing || creating) && (
        <EIPDForm
          eipd={editing}
          ratsRequiring={ratsRequiringEipd}
          existingRats={rats}
          preselectedRatId={creating ? (ratIdParam || undefined) : undefined}
          onClose={() => {
            setEditing(null);
            setCreating(false);
          }}
          onSaved={() => {
            setEditing(null);
            setCreating(false);
            if (ratIdParam) {
              router.push(`/rat?selected=${ratIdParam}`);
            } else {
              load();
            }
          }}
        />
      )}
    </div>
  );
}

function nrPlural(n: number): string {
  return n === 1 ? '' : 'n';
}

function EIPDForm({
  eipd,
  ratsRequiring,
  existingRats,
  preselectedRatId,
  onClose,
  onSaved,
}: {
  eipd: EIPD | null;
  ratsRequiring: RAT[];
  existingRats: RAT[];
  preselectedRatId?: string;
  onClose: () => void;
  onSaved: () => void;
}) {
  const allRats = Array.from(new Map([...ratsRequiring, ...existingRats].map((r) => [r.id, r])).values());
  const [ratId, setRatId] = useState<string>(
    preselectedRatId ||
    eipd?.rat_id?.toString() ||
    ratsRequiring[0]?.id?.toString() ||
    allRats[0]?.id?.toString() ||
    ''
  );
  const [metodologia, setMetodologia] = useState(eipd?.metodologia || '');
  const [objetivos, setObjetivos] = useState(eipd?.objetivos || '');
  const [necesidad, setNecesidad] = useState(eipd?.necesidad_proporcionalidad || '');
  const [riesgos, setRiesgos] = useState(eipd?.riesgos_identificados || '');
  const [medidas, setMedidas] = useState(eipd?.medidas_propuestas || '');
  const [parecerDpo, setParecerDpo] = useState(eipd?.parecer_dpo || '');
  const [parecerDpoAutor, setParecerDpoAutor] = useState(eipd?.parecer_dpo_autor || '');
  const [parecerDpoFecha, setParecerDpoFecha] = useState(eipd?.parecer_dpo_fecha ? eipd.parecer_dpo_fecha.substring(0, 10) : '');
  const [justificacionNoAplica, setJustificacionNoAplica] = useState(eipd?.justificacion_no_aplica || '');
  const [fechaElaboracion, setFechaElaboracion] = useState(eipd?.fecha_elaboracion || '');
  const [fechaAprobacion, setFechaAprobacion] = useState(eipd?.fecha_aprobacion || '');
  const [resultado, setResultado] = useState(eipd?.resultado || 'en_proceso');
  const [saving, setSaving] = useState(false);

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };
  const labelCls = 'block text-sm font-medium mb-1.5';
  const labelStyle = { color: '#374151' };
  const panelIdent = { background: '#F9FAFB', border: '1px solid #E5E7EB' };
  const panelBlue = { background: '#EFF6FF', border: '1px solid #BFDBFE' };
  const panelRed = { background: '#FEF2F2', border: '1px solid #FECACA' };
  const panelGreen = { background: '#F0FDF4', border: '1px solid #BBF7D0' };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ratId) {
      toast.error('Selecciona un RAT');
      return;
    }
    setSaving(true);
    try {
      if (eipd) {
        const res = await api.apiFetch(`${API_BASE}/eipd/${eipd.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            metodologia: metodologia || null,
            objetivos: objetivos || null,
            necesidad_proporcionalidad: necesidad || null,
            riesgos_identificados: riesgos || null,
            medidas_propuestas: medidas || null,
            parecer_dpo: parecerDpo || null,
            parecer_dpo_autor: parecerDpoAutor || null,
            parecer_dpo_fecha: parecerDpoFecha ? new Date(parecerDpoFecha).toISOString() : null,
            justificacion_no_aplica: justificacionNoAplica || null,
            fecha_elaboracion: fechaElaboracion || null,
            fecha_aprobacion: fechaAprobacion || null,
            resultado,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || 'Error al actualizar');
        }
        toast.success('EIPD actualizada');
      } else {
        const res = await api.apiFetch(`${API_BASE}/eipd/`, {
          method: 'POST',
          body: JSON.stringify({
            rat_id: Number(ratId),
            metodologia: metodologia || null,
            objetivos: objetivos || null,
            necesidad_proporcionalidad: necesidad || null,
            riesgos_identificados: riesgos || null,
            medidas_propuestas: medidas || null,
            parecer_dpo: parecerDpo || null,
            parecer_dpo_autor: parecerDpoAutor || null,
            parecer_dpo_fecha: parecerDpoFecha ? new Date(parecerDpoFecha).toISOString() : null,
            justificacion_no_aplica: justificacionNoAplica || null,
            fecha_elaboracion: fechaElaboracion || null,
            fecha_aprobacion: fechaAprobacion || null,
            resultado,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || 'Error al crear');
        }
        toast.success('EIPD creada');
      }
      onSaved();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error desconocido');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div
        className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header con gradiente */}
        <div className="rounded-t-xl px-6 py-4" style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}>
          <h2 className="text-lg font-bold text-white">
            {eipd ? '📋 Editar EIPD' : '🆕 Nueva EIPD'}
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.7)' }}>
            Art. 15 ter Ley 21.719 — Evaluación de Impacto en Protección de Datos
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Panel 1: Identificación */}
          <div className="rounded-xl p-5 space-y-4" style={panelIdent}>
            <h3 className="text-sm font-semibold" style={{ color: '#1E40AF' }}>1. Identificación del proceso</h3>
            {!eipd && (
              <div>
                <label className={labelCls} style={labelStyle}>RAT *</label>
                <select
                  value={ratId}
                  onChange={(e) => setRatId(e.target.value)}
                  className={inputCls}
                  style={inputStyle}
                  required
                >
                  <option value="">Seleccionar RAT</option>
                  {allRats.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.nombre_proceso}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className={labelCls} style={labelStyle}>Metodología</label>
              <input
                type="text"
                value={metodologia}
                onChange={(e) => setMetodologia(e.target.value)}
                className={inputCls}
                style={inputStyle}
                placeholder="Ej: NIST Privacy Framework, ISO 29134"
              />
            </div>
          </div>

          {/* Panel 2: Evaluación */}
          <div className="rounded-xl p-5 space-y-4" style={panelBlue}>
            <h3 className="text-sm font-semibold" style={{ color: '#1D4ED8' }}>2. Evaluación del tratamiento</h3>
            <div>
              <label className={labelCls} style={labelStyle}>Objetivos</label>
              <textarea
                value={objetivos}
                onChange={(e) => setObjetivos(e.target.value)}
                rows={3}
                className={inputCls}
                style={inputStyle}
                placeholder="¿Qué se busca evaluar con esta EIPD?"
              />
            </div>
            <div>
              <label className={labelCls} style={labelStyle}>Necesidad y proporcionalidad</label>
              <textarea
                value={necesidad}
                onChange={(e) => setNecesidad(e.target.value)}
                rows={3}
                className={inputCls}
                style={inputStyle}
                placeholder="¿Por qué el tratamiento es necesario y proporcionado?"
              />
            </div>
          </div>

          {/* Panel 3: Riesgos y Medidas */}
          <div className="rounded-xl p-5 space-y-4" style={panelRed}>
            <h3 className="text-sm font-semibold" style={{ color: '#B91C1C' }}>3. Riesgos y medidas</h3>
            <div>
              <label className={labelCls} style={labelStyle}>Riesgos identificados</label>
              <textarea
                value={riesgos}
                onChange={(e) => setRiesgos(e.target.value)}
                rows={3}
                className={inputCls}
                style={inputStyle}
                placeholder="Lista de riesgos para los derechos de los titulares"
              />
            </div>
            <div>
              <label className={labelCls} style={labelStyle}>Medidas propuestas</label>
              <textarea
                value={medidas}
                onChange={(e) => setMedidas(e.target.value)}
                rows={3}
                className={inputCls}
                style={inputStyle}
                placeholder="Medidas para mitigar los riesgos identificados"
              />
            </div>
          </div>

          {/* Panel 4: Conclusiones */}
          <div className="rounded-xl p-5 space-y-4" style={panelGreen}>
            <h3 className="text-sm font-semibold" style={{ color: '#065F46' }}>4. Conclusiones y aprobación</h3>
            <div>
              <label className={labelCls} style={labelStyle}>Parecer del DPO</label>
              <textarea
                value={parecerDpo}
                onChange={(e) => setParecerDpo(e.target.value)}
                rows={3}
                className={inputCls}
                style={inputStyle}
                placeholder="Opinión del Delegado de Protección de Datos"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelCls} style={labelStyle}>Autor del parecer (DPO)</label>
                <input
                  type="text"
                  value={parecerDpoAutor}
                  onChange={(e) => setParecerDpoAutor(e.target.value)}
                  className={inputCls}
                  style={inputStyle}
                  placeholder="Nombre del DPO"
                />
              </div>
              <div>
                <label className={labelCls} style={labelStyle}>Fecha del parecer</label>
                <input
                  type="date"
                  value={parecerDpoFecha}
                  onChange={(e) => setParecerDpoFecha(e.target.value)}
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
            </div>
            {resultado === 'no_requerida_justificada' && (
              <div>
                <label className={labelCls} style={labelStyle}>
                  Justificación de no aplicación (mínimo 20 caracteres) *
                </label>
                <textarea
                  value={justificacionNoAplica}
                  onChange={(e) => setJustificacionNoAplica(e.target.value)}
                  rows={3}
                  minLength={20}
                  required
                  className={inputCls}
                  style={inputStyle}
                  placeholder="Explique por qué el tratamiento no requiere EIPD pese a tener datos sensibles (Art. 15 ter Ley 21.719)."
                />
                <div className="text-xs mt-1" style={{ color: justificacionNoAplica.length < 20 ? '#DC2626' : '#059669' }}>
                  {justificacionNoAplica.length} / 20 caracteres
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelCls} style={labelStyle}>Fecha elaboración</label>
                <input
                  type="date"
                  value={fechaElaboracion}
                  onChange={(e) => setFechaElaboracion(e.target.value)}
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
              <div>
                <label className={labelCls} style={labelStyle}>Fecha aprobación</label>
                <input
                  type="date"
                  value={fechaAprobacion}
                  onChange={(e) => setFechaAprobacion(e.target.value)}
                  className={inputCls}
                  style={inputStyle}
                />
              </div>
            </div>
            <div>
              <label className={labelCls} style={labelStyle}>Resultado *</label>
              <select
                value={resultado}
                onChange={(e) => setResultado(e.target.value as EIPD['resultado'])}
                className={inputCls}
                style={inputStyle}
              >
                {Object.entries(RESULTADO_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
              {resultado === 'no_requerida' && (
                <div className="mt-2 p-2 rounded text-xs" style={{ background: '#FEF2F2', color: '#B91C1C' }}>
                  ⚠️ Si el RAT tiene datos sensibles este resultado será rechazado por validación.
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex flex-col sm:flex-row gap-3 justify-between pt-2">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-5 py-2.5 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
                style={{ color: '#6B7280', borderColor: '#E5E7EB' }}
              >
                Cancelar
              </button>
              <a
                href={`/rat?selected=${ratId}`}
                className="px-5 py-2.5 rounded-lg text-sm font-medium border transition hover:bg-gray-50 inline-flex items-center gap-1"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                ← Volver al RAT
              </a>
            </div>
            <Button
              type="submit"
              size="lg"
              disabled={saving}
              loading={saving}
            >
              Guardar EIPD
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
