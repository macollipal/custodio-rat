'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';

interface SeguimientoEntry {
  estado_anterior: string | null;
  estado_nuevo: string;
  descripcion: string | null;
  fecha: string;
}

interface SeguimientoResponse {
  id: number;
  tipo: string;
  estado: string;
  fecha_recepcion: string | null;
  fecha_vencimiento: string | null;
  dias_restantes: number | null;
  company_nombre: string | null;
  historial: SeguimientoEntry[];
}

const ESTADO_MAP: Record<string, { label: string; color: string; bg: string }> = {
  abierto: { label: 'Abierto', color: '#1E40AF', bg: '#DBEAFE' },
  // Vienen del backend /seguimiento/{token} con labels formateadas (mayúsculas).
  // Por eso las claves son los labels ya formateados, no los códigos internos.
  Abierto: { label: 'Abierto', color: '#1E40AF', bg: '#DBEAFE' },
  'En Proceso': { label: 'En proceso', color: '#6D28D9', bg: '#EDE9FE' },
  Pendiente: { label: 'Pendiente', color: '#92400E', bg: '#FEF3C7' },
  Bloqueado: { label: 'Bloqueado', color: '#991B1B', bg: '#FEE2E2' },
  Resuelto: { label: 'Resuelto', color: '#065F46', bg: '#D1FAE5' },
  Rechazado: { label: 'Rechazado', color: '#7F1D1D', bg: '#FEE2E2' },
  Subsanación: { label: 'Subsanación', color: '#92400E', bg: '#FEF3C7' },
  Prórroga: { label: 'Prórroga', color: '#6D28D9', bg: '#EDE9FE' },
};

function fmtDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CL', { dateStyle: 'long' });
}

function TrackingForm() {
  const searchParams = useSearchParams();
  const tokenInicial = searchParams.get('token') || '';
  const [token, setToken] = useState(tokenInicial);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SeguimientoResponse | null>(null);
  const [notFound, setNotFound] = useState(false);

  async function consultar(e: React.FormEvent) {
    e.preventDefault();
    const t = token.trim();
    if (!t) {
      toast.error('Ingresá tu número de seguimiento.');
      return;
    }
    setLoading(true);
    setNotFound(false);
    try {
      const res = await fetch(`${API_BASE}/seguimiento/${t}`);
      if (res.status === 404) {
        setNotFound(true);
        setData(null);
        return;
      }
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Error al consultar');
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  }

  if (data) {
    const estado = ESTADO_MAP[data.estado] || { label: data.estado, color: '#374151', bg: '#F3F4F6' };
    const vencido = data.dias_restantes !== null && data.dias_restantes < 0 && data.estado !== 'resuelto' && data.estado !== 'Rechazado';
    return (
      <div className="bg-white rounded-2xl shadow-sm p-8 space-y-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold" style={{ color: '#111827' }}>
              Estado de tu solicitud
            </h2>
            <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
              Solicitud de tipo <strong>{data.tipo}</strong>
              {data.company_nombre && ` para ${data.company_nombre}`}
            </p>
          </div>
          <span
            className="px-3 py-1.5 rounded-lg text-sm font-semibold"
            style={{ background: estado.bg, color: estado.color }}
          >
            {estado.label}
          </span>
        </div>

        {vencido && (
          <div className="p-3 rounded-lg" style={{ background: '#FEE2E2', border: '1px solid #FECACA' }}>
            <p className="text-sm font-semibold" style={{ color: '#991B1B' }}>
              ⚠️ Solicitud vencida ({Math.abs(data.dias_restantes ?? 0)} días)
            </p>
            <p className="text-xs mt-1" style={{ color: '#7F1D1D' }}>
              El plazo legal de 10 días hábiles (Art. 14 Ley 21.719) ha sido superado.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded-lg" style={{ background: '#F9FAFB' }}>
            <p className="text-xs" style={{ color: '#6B7280' }}>Recepción</p>
            <p className="text-sm font-semibold mt-0.5" style={{ color: '#111827' }}>
              {fmtDate(data.fecha_recepcion)}
            </p>
          </div>
          <div className="p-3 rounded-lg" style={{ background: '#F9FAFB' }}>
            <p className="text-xs" style={{ color: '#6B7280' }}>Vencimiento</p>
            <p className="text-sm font-semibold mt-0.5" style={{ color: '#111827' }}>
              {fmtDate(data.fecha_vencimiento)}
            </p>
          </div>
          <div className="p-3 rounded-lg" style={{ background: '#F9FAFB' }}>
            <p className="text-xs" style={{ color: '#6B7280' }}>Días restantes</p>
            <p className="text-sm font-semibold mt-0.5" style={{ color: '#111827' }}>
              {data.dias_restantes === null ? '—' : data.dias_restantes < 0 ? `${Math.abs(data.dias_restantes)}d vencido` : `${data.dias_restantes}d`}
            </p>
          </div>
        </div>

        {data.historial.length > 0 && (
          <div>
            <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Historial</p>
            <ol className="space-y-2 border-l-2 pl-4" style={{ borderColor: '#E5E7EB' }}>
              {data.historial.map((h, idx) => {
                const e = ESTADO_MAP[h.estado_nuevo] || { label: h.estado_nuevo, color: '#374151', bg: '#F3F4F6' };
                return (
                  <li key={idx} className="text-sm relative">
                    <span
                      className="absolute -left-[26px] top-0.5 inline-block w-3 h-3 rounded-full"
                      style={{ background: e.color }}
                      aria-hidden
                    />
                    <span className="font-medium" style={{ color: e.color }}>{e.label}</span>
                    {h.descripcion && <span style={{ color: '#6B7280' }}> — {h.descripcion}</span>}
                    <div className="text-xs" style={{ color: '#9CA3AF' }}>{fmtDate(h.fecha)}</div>
                  </li>
                );
              })}
            </ol>
          </div>
        )}

        <button
          onClick={() => setData(null)}
          className="text-sm font-medium underline underline-offset-2"
          style={{ color: '#2563EB' }}
        >
          Consultar otro seguimiento
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={consultar} className="bg-white rounded-2xl shadow-sm p-8 space-y-4">
      <h2 className="text-lg font-bold" style={{ color: '#111827' }}>
        Ingresá tu número de seguimiento
      </h2>
      <p className="text-sm" style={{ color: '#6B7280' }}>
        Es el código que recibiste al enviar tu solicitud ARCO.
      </p>

      {notFound && (
        <div className="p-3 rounded-lg" style={{ background: '#FEE2E2', border: '1px solid #FECACA' }} role="alert">
          <p className="text-sm" style={{ color: '#991B1B' }}>
            No encontramos una solicitud con ese número. Verificá que esté bien escrito.
          </p>
        </div>
      )}

      <input
        type="text"
        value={token}
        onChange={e => setToken(e.target.value)}
        placeholder="Ej: 7b9f2c80-12ab-4e8f-9b3a-2d4f5e6a1b2c"
        className="w-full p-3 rounded-lg border font-mono text-sm"
        style={{ borderColor: '#E5E7EB', outline: 'none' }}
        aria-label="Tracking token"
      />
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 rounded-lg text-white font-semibold disabled:opacity-50"
        style={{ backgroundColor: '#2563EB' }}
      >
        {loading ? 'Consultando...' : 'Consultar estado'}
      </button>
    </form>
  );
}

export default function ConsultarSolicitudPage() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F9FAFB' }}>
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#111827' }}>
            🔍 Consultar solicitud ARCO
          </h1>
          <p className="text-base" style={{ color: '#6B7280' }}>
            Ley 21.719 — Protección de Datos Personales de Chile
          </p>
        </div>
        <Suspense fallback={<div className="text-center py-12" style={{ color: '#6B7280' }}>Cargando...</div>}>
          <TrackingForm />
        </Suspense>
      </div>
    </div>
  );
}
