'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';

interface TrackingResponse {
  tracking_token: string;
  estado: string;
  tipo: string;
  titular_nombre: string;
  fecha_recepcion: string | null;
  fecha_vencimiento: string | null;
  dias_restantes: number | null;
  vencido: boolean;
  respuesta_texto: string | null;
  evidencia_respuesta_hash: string | null;
  ultima_accion: string | null;
}

const ESTADO_MAP: Record<string, { label: string; color: string; bg: string }> = {
  abierto: { label: 'Abierto', color: '#1E40AF', bg: '#DBEAFE' },
  en_proceso: { label: 'En proceso', color: '#6D28D9', bg: '#EDE9FE' },
  pendiente: { label: 'Pendiente', color: '#92400E', bg: '#FEF3C7' },
  bloqueado: { label: 'Bloqueado', color: '#991B1B', bg: '#FEE2E2' },
  resuelto: { label: 'Resuelto', color: '#065F46', bg: '#D1FAE5' },
  rechazado: { label: 'Rechazado', color: '#7F1D1D', bg: '#FEE2E2' },
  subsanacion: { label: 'Subsanación', color: '#92400E', bg: '#FEF3C7' },
  prorroga: { label: 'Prórroga', color: '#6D28D9', bg: '#EDE9FE' },
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
  const [data, setData] = useState<TrackingResponse | null>(null);
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
      const res = await fetch(`${API_BASE}/solicitudes-derecho/tracking/${t}`);
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
    return (
      <div className="bg-white rounded-2xl shadow-sm p-8 space-y-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold" style={{ color: '#111827' }}>
              Estado de tu solicitud
            </h2>
            <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
              {data.titular_nombre} · Solicitud de tipo <strong>{data.tipo}</strong>
            </p>
          </div>
          <span
            className="px-3 py-1.5 rounded-lg text-sm font-semibold"
            style={{ background: estado.bg, color: estado.color }}
          >
            {estado.label}
          </span>
        </div>

        {data.vencido && (
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
            <p className="text-xs" style={{ color: '#6B7280' }}>Última acción</p>
            <p className="text-sm font-semibold mt-0.5" style={{ color: '#111827' }}>
              {fmtDate(data.ultima_accion)}
            </p>
          </div>
        </div>

        {data.estado === 'resuelto' && data.respuesta_texto && (
          <div className="rounded-lg p-4" style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
            <p className="text-xs font-semibold mb-1" style={{ color: '#065F46' }}>Respuesta</p>
            <p className="text-sm whitespace-pre-wrap" style={{ color: '#111827' }}>
              {data.respuesta_texto}
            </p>
            {data.evidencia_respuesta_hash && (
              <div className="mt-3 pt-3 border-t" style={{ borderColor: '#BBF7D0' }}>
                <p className="text-xs" style={{ color: '#6B7280' }}>
                  Hash de integridad (SHA-256):
                </p>
                <code className="block mt-1 text-xs font-mono break-all" style={{ color: '#111827' }}>
                  {data.evidencia_respuesta_hash}
                </code>
              </div>
            )}
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
