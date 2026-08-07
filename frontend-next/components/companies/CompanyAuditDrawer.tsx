'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import Drawer from '@/components/ui/Drawer';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Company } from '@/types';

interface AuditEntry {
  id: number;
  rat_id: number;
  accion: string;
  usuario: string;
  timestamp: string;
  detalle?: string;
}

const ACCION_COLORS: Record<string, { bg: string; color: string; dot: string }> = {
  crear:         { bg: '#DBEAFE', color: '#1E40AF', dot: '#2563EB' },
  create:        { bg: '#DBEAFE', color: '#1E40AF', dot: '#2563EB' },
  editar:        { bg: '#FEF3C7', color: '#92400E', dot: '#D97706' },
  update:        { bg: '#FEF3C7', color: '#92400E', dot: '#D97706' },
  eliminar:      { bg: '#FEE2E2', color: '#7F1D1D', dot: '#DC2626' },
  delete:        { bg: '#FEE2E2', color: '#7F1D1D', dot: '#DC2626' },
  revisar:       { bg: '#D1FAE5', color: '#065F46', dot: '#059669' },
  exportar:      { bg: '#EDE9FE', color: '#5B21B6', dot: '#7C3AED' },
  export:        { bg: '#EDE9FE', color: '#5B21B6', dot: '#7C3AED' },
  duplicar:      { bg: '#FCE7F3', color: '#9F1239', dot: '#DB2777' },
  duplicate:     { bg: '#FCE7F3', color: '#9F1239', dot: '#DB2777' },
};

const DEFAULT_COLOR = { bg: '#F3F4F6', color: '#374151', dot: '#6B7280' };

function getAccionColor(accion: string) {
  return ACCION_COLORS[accion.toLowerCase()] ?? DEFAULT_COLOR;
}

function formatDetalle(detalle: unknown): string {
  if (!detalle) return '';
  if (typeof detalle === 'string') {
    try {
      return JSON.stringify(JSON.parse(detalle), null, 2);
    } catch {
      return detalle;
    }
  }
  return JSON.stringify(detalle, null, 2);
}

function formatTimestamp(ts: string): string {
  try {
    const d = new Date(ts);
    return d.toLocaleString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return ts;
  }
}

export const __test__ = { formatDetalle, formatTimestamp, getAccionColor };

export default function CompanyAuditDrawer({
  company,
  open,
  onClose,
}: {
  company: Company | null;
  open: boolean;
  onClose: () => void;
}) {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterAccion, setFilterAccion] = useState<string>('todas');

  useEffect(() => {
    if (!open || !company) return;
    setLoading(true);
    setFilterAccion('todas');
    api
      .getAuditoriaGlobal(company.id)
      .then(setEntries)
      .catch(() => toast.error('No se pudo cargar la auditoría.'))
      .finally(() => setLoading(false));
  }, [open, company]);

  const accionesUnicas = Array.from(new Set(entries.map((e) => e.accion))).sort();
  const entriesFiltradas = filterAccion === 'todas'
    ? entries
    : entries.filter((e) => e.accion === filterAccion);

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title=""
      size="xl"
    >
      <div className="p-6">
        <div
          className="rounded-xl p-5 mb-5"
          style={{ background: 'linear-gradient(135deg, #1F2937 0%, #111827 100%)' }}
        >
          <div className="flex items-center gap-3 mb-1">
            <span className="text-2xl" aria-hidden="true">📋</span>
            <h2 className="text-lg font-bold text-white">
              Auditoría · {company?.nombre ?? '—'}
            </h2>
          </div>
          <p className="text-xs" style={{ color: '#9CA3AF' }}>
            Historial de eventos de los RATs de esta empresa.
            Cada acción queda registrada con hash chain verificable (Art. 28 Ley 21.719).
          </p>
        </div>

        {loading ? (
          <div className="space-y-2">
            <Skeleton height={48} />
            <Skeleton height={48} />
            <Skeleton height={48} />
            <Skeleton height={48} />
            <Skeleton height={48} />
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-3xl mb-2">📭</div>
            <p className="text-sm font-medium" style={{ color: '#374151' }}>
              Sin eventos de auditoría
            </p>
            <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
              Esta empresa aún no tiene acciones registradas.
            </p>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              <span className="text-xs font-medium" style={{ color: '#374151' }}>
                Filtrar por acción:
              </span>
              <button
                type="button"
                onClick={() => setFilterAccion('todas')}
                aria-pressed={filterAccion === 'todas'}
                className="px-2.5 py-1 rounded-full text-xs font-medium transition min-h-[36px]"
                style={{
                  background: filterAccion === 'todas' ? '#111827' : '#F3F4F6',
                  color: filterAccion === 'todas' ? 'white' : '#374151',
                }}
              >
                Todas ({entries.length})
              </button>
              {accionesUnicas.map((a) => {
                const count = entries.filter((e) => e.accion === a).length;
                const isActive = filterAccion === a;
                const c = getAccionColor(a);
                return (
                  <button
                    key={a}
                    type="button"
                    onClick={() => setFilterAccion(a)}
                    aria-pressed={isActive}
                    className="px-2.5 py-1 rounded-full text-xs font-medium transition min-h-[36px]"
                    style={{
                      background: isActive ? c.color : c.bg,
                      color: isActive ? 'white' : c.color,
                    }}
                  >
                    {a} ({count})
                  </button>
                );
              })}
            </div>

            <ol className="space-y-2">
              {entriesFiltradas.map((e) => {
                const c = getAccionColor(e.accion);
                return (
                  <li
                    key={e.id}
                    className="rounded-lg p-3 border"
                    style={{ borderColor: '#E5E7EB', background: 'white' }}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0 mt-1.5"
                        style={{ background: c.dot }}
                        aria-hidden="true"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className="px-2 py-0.5 rounded-full text-xs font-bold uppercase"
                            style={{ background: c.bg, color: c.color }}
                          >
                            {e.accion}
                          </span>
                          <span className="text-xs" style={{ color: '#6B7280' }}>
                            RAT #{e.rat_id}
                          </span>
                          <span className="text-xs" style={{ color: '#6B7280' }}>
                            por <strong style={{ color: '#111827' }}>{e.usuario}</strong>
                          </span>
                          <span className="text-xs ml-auto" style={{ color: '#6B7280' }}>
                            {formatTimestamp(e.timestamp)}
                          </span>
                        </div>
                        {e.detalle && (
                          <pre
                            className="text-xs mt-2 p-2 rounded overflow-x-auto"
                            style={{ background: '#F9FAFB', color: '#374151' }}
                          >
                            {formatDetalle(e.detalle)}
                          </pre>
                        )}
                      </div>
                    </div>
                  </li>
                );
              })}
            </ol>
          </>
        )}
      </div>
    </Drawer>
  );
}