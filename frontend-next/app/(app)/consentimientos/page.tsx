'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import { API_BASE } from '@/lib/constants';
import * as api from '@/lib/api';
import type { RAT } from '@/types';

import { inputCls, inputStyle, labelCls, labelStyle, panelStyles, panelWrapperCls, panelTitleStyles, btnPrimaryCls, btnPrimaryStyle, btnSecondaryCls, btnSecondaryStyle, gridResponsive1to2, modalHeaderStyle, modalHeaderCls, modalContentCls, formFooterCls } from '@/lib/styles';
import { Button } from '@/components/ui/Button';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

interface Consentimiento {
  id: number;
  company_id: number;
  rat_id: number | null;
  nombre_titular: string;
  email_titular: string | null;
  canal: string;
  texto_consentimiento: string;
  fecha_obtencion: string;
  fecha_revocacion: string | null;
  activo: boolean;
  ip_origen: string | null;
  created_at: string;
  version_politica?: string;
}

const CANAL_LABELS: Record<string, string> = {
  web: 'Web',
  papel: 'Papel',
  firma_digital: 'Firma digital',
  verbal: 'Verbal',
  otro: 'Otro',
};

const CANAL_COLORS: Record<string, string> = {
  web: '#2563EB',
  papel: '#D97706',
  firma_digital: '#7C3AED',
  verbal: '#059669',
  otro: '#6B7280',
};

export default function ConsentimientosPage() {
  const { company } = useApp();
  const [items, setItems] = useState<Consentimiento[]>([]);
  const [rats, setRats] = useState<RAT[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroRat, setFiltroRat] = useState<string>('');
  const [soloActivos, setSoloActivos] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [detail, setDetail] = useState<Consentimiento | null>(null);
  const [confirmRevokeOpen, setConfirmRevokeOpen] = useState(false);
  const [pendingRevoke, setPendingRevoke] = useState<Consentimiento | null>(null);

  async function load() {
    if (!company) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({ company_id: String(company.id) });
      if (filtroRat) params.set('rat_id', filtroRat);
      if (soloActivos) params.set('solo_activos', 'true');
      const res = await api.apiFetch(`${API_BASE}/consentimientos/?${params}`);
      if (!res.ok) throw new Error('Error al listar consentimientos');
      const data = await res.json();
      setItems(data.consentimientos || []);
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
  }, [company, filtroRat, soloActivos]);

  async function handleRevoke(c: Consentimiento) {
    try {
      const res = await api.apiFetch(`${API_BASE}/consentimientos/${c.id}/revocar`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Error al revocar');
      }
      toast.success('Consentimiento revocado');
      load();
      setDetail(null);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error desconocido');
    }
  }

  const stats = {
    total: items.length,
    activos: items.filter((c) => c.activo).length,
    revocados: items.filter((c) => !c.activo).length,
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>
            ✅ Consentimientos
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Gestión de consentimientos expresos (Art. 12 Ley 21.719)
          </p>
        </div>
        <Button
          onClick={() => setShowCreate(true)}
          aria-label="Crear nuevo consentimiento"
        >
          + Nuevo consentimiento
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="p-4 rounded-lg" style={{ background: '#EFF6FF' }}>
          <div className="text-xs text-gray-600">Total</div>
          <div className="text-2xl font-bold" style={{ color: '#2563EB' }}>{stats.total}</div>
        </div>
        <div className="p-4 rounded-lg" style={{ background: '#ECFDF5' }}>
          <div className="text-xs text-gray-600">Activos</div>
          <div className="text-2xl font-bold" style={{ color: '#059669' }}>{stats.activos}</div>
        </div>
        <div className="p-4 rounded-lg" style={{ background: '#FEE2E2' }}>
          <div className="text-xs text-gray-600">Revocados</div>
          <div className="text-2xl font-bold" style={{ color: '#DC2626' }}>{stats.revocados}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <select
          value={filtroRat}
          onChange={(e) => setFiltroRat(e.target.value)}
          aria-label="Filtrar consentimientos por RAT"
          className="px-3 py-2 border rounded-lg text-sm"
        >
          <option value="">Todos los RATs</option>
          {rats.map((r) => (
            <option key={r.id} value={r.id}>
              {r.nombre_proceso}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={soloActivos}
            onChange={(e) => setSoloActivos(e.target.checked)}
            aria-label="Mostrar solo consentimientos activos"
          />
          Solo activos
        </label>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Cargando...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No hay consentimientos registrados.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border" style={{ borderColor: '#E5E7EB' }}>
          <table className="w-full text-sm">
            <thead style={{ background: '#F9FAFB' }}>
              <tr>
                <th className="text-left px-4 py-3 font-semibold">Titular</th>
                <th className="text-left px-4 py-3 font-semibold">RAT</th>
                <th className="text-left px-4 py-3 font-semibold">Canal</th>
                <th className="text-left px-4 py-3 font-semibold">Fecha obtención</th>
                <th className="text-left px-4 py-3 font-semibold">Estado</th>
                <th className="text-left px-4 py-3 font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => {
                const rat = rats.find((r) => r.id === c.rat_id);
                return (
                  <tr key={c.id} className="border-t" style={{ borderColor: '#E5E7EB' }}>
                    <td className="px-4 py-3">
                      <div className="font-medium">{c.nombre_titular}</div>
                      {c.email_titular && (
                        <div className="text-xs text-gray-500">{c.email_titular}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {rat?.nombre_proceso || `RAT #${c.rat_id}`}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className="px-2 py-0.5 rounded text-xs font-medium text-white"
                        style={{ background: CANAL_COLORS[c.canal] || '#6B7280' }}
                      >
                        {CANAL_LABELS[c.canal] || c.canal}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {new Date(c.fecha_obtencion).toLocaleDateString('es-CL')}
                    </td>
                    <td className="px-4 py-3">
                      {c.activo ? (
                        <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#D1FAE5', color: '#065F46' }}>
                          Activo
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEE2E2', color: '#991B1B' }}>
                          Revocado
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="!min-h-0"
                          onClick={() => setDetail(c)}
                          aria-label={`Ver detalle de consentimiento de ${c.nombre_titular}`}
                          style={{ color: '#1D4ED8' }}
                        >
                          Ver
                        </Button>
                        {c.activo && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="!min-h-0"
                            onClick={() => { setPendingRevoke(c); setConfirmRevokeOpen(true); }}
                            aria-label={`Revocar consentimiento de ${c.nombre_titular}`}
                            style={{ color: '#DC2626' }}
                          >
                            Revocar
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && (
        <CreateConsentimientoModal
          rats={rats}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            load();
          }}
        />
      )}

      {detail && (
        <DetailModal
          consentimiento={detail}
          rat={rats.find((r) => r.id === detail.rat_id)}
          onClose={() => setDetail(null)}
          onRevoke={detail.activo ? () => { setPendingRevoke(detail); setConfirmRevokeOpen(true); } : undefined}
        />
      )}

      <ConfirmDialog
        open={confirmRevokeOpen}
        onClose={() => { setConfirmRevokeOpen(false); setPendingRevoke(null); }}
        onConfirm={() => { if (pendingRevoke) handleRevoke(pendingRevoke); setConfirmRevokeOpen(false); setPendingRevoke(null); }}
        title="Revocar consentimiento"
        message={pendingRevoke ? `¿Revocar el consentimiento de "${pendingRevoke.nombre_titular}"? Esta acción no se puede deshacer.` : ''}
        confirmText="Revocar"
        variant="danger"
      />
    </div>
  );
}

function CreateConsentimientoModal({
  rats,
  onClose,
  onCreated,
}: {
  rats: RAT[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [ratId, setRatId] = useState<string>(rats[0]?.id?.toString() || '');
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [canal, setCanal] = useState('web');
  const [texto, setTexto] = useState('');
  const [versionPolitica, setVersionPolitica] = useState('');
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ratId || !nombre || !texto) {
      toast.error('Completa los campos requeridos');
      return;
    }
    setSaving(true);
    try {
      const res = await api.apiFetch(`${API_BASE}/consentimientos/`, {
        method: 'POST',
        body: JSON.stringify({
          rat_id: Number(ratId),
          nombre_titular: nombre,
          email_titular: email || null,
          canal,
          texto_consentimiento: texto,
          fecha_obtencion: new Date().toISOString(),
          ...(versionPolitica ? { version_politica: versionPolitica } : {}),
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Error al crear');
      }
      toast.success('Consentimiento registrado');
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error desconocido');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-xl font-bold mb-4">Nuevo consentimiento</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className={labelCls}>RAT *</label>
            <select
              value={ratId}
              onChange={(e) => setRatId(e.target.value)}
              className={inputCls}
              required
            >
              <option value="">Seleccionar RAT</option>
              {rats.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.nombre_proceso}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls} htmlFor="consent-nombre">Nombre del titular *</label>
            <input
              id="consent-nombre"
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className={inputCls}
              aria-required="true"
              required
            />
          </div>
          <div>
            <label className={labelCls} htmlFor="consent-email">Email del titular</label>
            <input
              id="consent-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls} htmlFor="consent-canal">Canal de obtención *</label>
            <select
              id="consent-canal"
              value={canal}
              onChange={(e) => setCanal(e.target.value)}
              className={inputCls}
              aria-required="true"
            >
              {Object.entries(CANAL_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls} htmlFor="consent-texto">Texto del consentimiento *</label>
            <textarea
              id="consent-texto"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              rows={4}
              className={inputCls}
              placeholder="Por medio del presente autorizo el tratamiento de mis datos personales para..."
              aria-required="true"
              required
            />
          </div>
          <div>
            <label className={labelCls} htmlFor="consent-version">Versión de la política (Art. 12)</label>
            <input
              id="consent-version"
              type="text"
              value={versionPolitica}
              onChange={(e) => setVersionPolitica(e.target.value)}
              className={inputCls}
              placeholder="Ej: v2.1, 2026-01-15, 3"
            />
            <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>Versión de la política de privacidad vigente al momento de obtener el consentimiento.</p>
          </div>
          <div className="flex gap-2 justify-end pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              aria-label="Cancelar creacion de consentimiento"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={saving}
              loading={saving}
              aria-label="Guardar consentimiento"
            >
              Guardar
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

function DetailModal({
  consentimiento,
  rat,
  onClose,
  onRevoke,
}: {
  consentimiento: Consentimiento;
  rat?: RAT;
  onClose: () => void;
  onRevoke?: () => void;
}) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-xl font-bold mb-4">Detalle del consentimiento</h2>
        <div className="space-y-3 text-sm">
          <div><span className="font-medium">ID:</span> #{consentimiento.id}</div>
          <div><span className="font-medium">Titular:</span> {consentimiento.nombre_titular}</div>
          {consentimiento.email_titular && (
            <div><span className="font-medium">Email:</span> {consentimiento.email_titular}</div>
          )}
          <div>
            <span className="font-medium">RAT:</span>{' '}
            {rat?.nombre_proceso || `RAT #${consentimiento.rat_id}`}
          </div>
          <div>
            <span className="font-medium">Canal:</span>{' '}
            <span
              className="px-2 py-0.5 rounded text-xs font-medium text-white"
              style={{ background: CANAL_COLORS[consentimiento.canal] || '#6B7280' }}
            >
              {CANAL_LABELS[consentimiento.canal] || consentimiento.canal}
            </span>
          </div>
          <div>
            <span className="font-medium">Fecha de obtención:</span>{' '}
            {new Date(consentimiento.fecha_obtencion).toLocaleString('es-CL')}
          </div>
          {consentimiento.version_politica && (
            <div>
              <span className="font-medium">Versión política (Art. 12):</span>{' '}
              <span className="font-mono text-sm px-1.5 py-0.5 rounded" style={{ background: '#F3F4F6', color: '#374151' }}>
                {consentimiento.version_politica}
              </span>
            </div>
          )}
          {consentimiento.fecha_revocacion && (
            <div>
              <span className="font-medium">Fecha de revocación:</span>{' '}
              {new Date(consentimiento.fecha_revocacion).toLocaleString('es-CL')}
            </div>
          )}
          {consentimiento.ip_origen && (
            <div><span className="font-medium">IP de origen:</span> {consentimiento.ip_origen}</div>
          )}
          <div>
            <span className="font-medium">Estado:</span>{' '}
            {consentimiento.activo ? (
              <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#D1FAE5', color: '#065F46' }}>
                Activo
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEE2E2', color: '#991B1B' }}>
                Revocado
              </span>
            )}
          </div>
          <div>
            <div className="font-medium mb-1">Texto del consentimiento:</div>
            <div className="p-3 bg-gray-50 rounded-lg text-gray-700 whitespace-pre-wrap">
              {consentimiento.texto_consentimiento}
            </div>
          </div>
        </div>
        <div className="flex gap-2 justify-end mt-4">
          {onRevoke && (
            <Button variant="danger" onClick={onRevoke}>
              Revocar consentimiento
            </Button>
          )}
          <Button variant="secondary" onClick={onClose}>Cerrar</Button>
        </div>
      </div>
    </div>
  );
}

