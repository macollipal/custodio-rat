'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import { API_BASE } from '@/lib/constants';
import * as api from '@/lib/api';
import type { RAT } from '@/types';

interface EIPD {
  id: number;
  rat_id: number;
  metodologia: string | null;
  objetivos: string | null;
  necesidad_proporcionalidad: string | null;
  riesgos_identificados: string | null;
  medidas_propuestas: string | null;
  parecer_dpo: string | null;
  fecha_elaboracion: string | null;
  fecha_aprobacion: string | null;
  resultado: 'completada' | 'no_requerida' | 'en_proceso';
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

const RESULTADO_LABELS: Record<string, string> = {
  en_proceso: 'En proceso',
  completada: 'Completada',
  no_requerida: 'No requerida',
};

const RESULTADO_COLORS: Record<string, { bg: string; fg: string }> = {
  en_proceso: { bg: '#FEF3C7', fg: '#92400E' },
  completada: { bg: '#D1FAE5', fg: '#065F46' },
  no_requerida: { bg: '#E5E7EB', fg: '#374151' },
};

export default function EIPDPage() {
  const { company, user } = useApp();
  const [items, setItems] = useState<EIPD[]>([]);
  const [rats, setRats] = useState<RAT[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<EIPD | null>(null);
  const [creating, setCreating] = useState(false);

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
            Art. 15 bis Ley 21.719 — Obligatoria para datos sensibles y transferencias de alto riesgo
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
                <button
                  onClick={() => setCreating(true)}
                  className="text-xs px-2 py-1 rounded text-white"
                  style={{ background: '#D97706' }}
                >
                  Crear EIPD
                </button>
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
                        <button
                          onClick={() => setEditing(e)}
                          className="text-xs px-2 py-1 rounded text-blue-700 hover:bg-blue-50"
                        >
                          Editar
                        </button>
                      ) : (
                        <button
                          onClick={() => setEditing(e)}
                          className="text-xs px-2 py-1 rounded text-blue-700 hover:bg-blue-50"
                        >
                          Ver
                        </button>
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
          onClose={() => {
            setEditing(null);
            setCreating(false);
          }}
          onSaved={() => {
            setEditing(null);
            setCreating(false);
            load();
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
  onClose,
  onSaved,
}: {
  eipd: EIPD | null;
  ratsRequiring: RAT[];
  existingRats: RAT[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const allRats = Array.from(new Map([...ratsRequiring, ...existingRats].map((r) => [r.id, r])).values());
  const [ratId, setRatId] = useState<string>(eipd?.rat_id?.toString() || ratsRequiring[0]?.id?.toString() || allRats[0]?.id?.toString() || '');
  const [metodologia, setMetodologia] = useState(eipd?.metodologia || '');
  const [objetivos, setObjetivos] = useState(eipd?.objetivos || '');
  const [necesidad, setNecesidad] = useState(eipd?.necesidad_proporcionalidad || '');
  const [riesgos, setRiesgos] = useState(eipd?.riesgos_identificados || '');
  const [medidas, setMedidas] = useState(eipd?.medidas_propuestas || '');
  const [parecerDpo, setParecerDpo] = useState(eipd?.parecer_dpo || '');
  const [fechaElaboracion, setFechaElaboracion] = useState(eipd?.fecha_elaboracion || '');
  const [fechaAprobacion, setFechaAprobacion] = useState(eipd?.fecha_aprobacion || '');
  const [resultado, setResultado] = useState(eipd?.resultado || 'en_proceso');
  const [saving, setSaving] = useState(false);

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
        className="bg-white rounded-xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-xl font-bold mb-4">
          {eipd ? 'Editar EIPD' : 'Nueva EIPD'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          {!eipd && (
            <div>
              <label className="block text-sm font-medium mb-1">RAT *</label>
              <select
                value={ratId}
                onChange={(e) => setRatId(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
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
            <label className="block text-sm font-medium mb-1">Metodología</label>
            <input
              type="text"
              value={metodologia}
              onChange={(e) => setMetodologia(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ej: NIST Privacy Framework, ISO 29134"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Objetivos</label>
            <textarea
              value={objetivos}
              onChange={(e) => setObjetivos(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="¿Qué se busca evaluar con esta EIPD?"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Necesidad y proporcionalidad</label>
            <textarea
              value={necesidad}
              onChange={(e) => setNecesidad(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="¿Por qué el tratamiento es necesario y proporcionado?"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Riesgos identificados</label>
            <textarea
              value={riesgos}
              onChange={(e) => setRiesgos(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Lista de riesgos para los derechos de los titulares"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Medidas propuestas</label>
            <textarea
              value={medidas}
              onChange={(e) => setMedidas(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Medidas para mitigar los riesgos identificados"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Parecer del DPO</label>
            <textarea
              value={parecerDpo}
              onChange={(e) => setParecerDpo(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Opinión del Delegado de Protección de Datos"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Fecha elaboración</label>
              <input
                type="date"
                value={fechaElaboracion}
                onChange={(e) => setFechaElaboracion(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Fecha aprobación</label>
              <input
                type="date"
                value={fechaAprobacion}
                onChange={(e) => setFechaAprobacion(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Resultado *</label>
            <select
              value={resultado}
              onChange={(e) => setResultado(e.target.value as EIPD['resultado'])}
              className="w-full px-3 py-2 border rounded-lg"
            >
              {Object.entries(RESULTADO_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-2 justify-end pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-lg border">
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 rounded-lg text-white font-medium"
              style={{ background: saving ? '#9CA3AF' : '#2563EB' }}
            >
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
