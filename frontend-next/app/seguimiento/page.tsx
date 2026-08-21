'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { consultarSeguimiento, type SeguimientoResponse } from '@/lib/api';

const TIPO_COLORS: Record<string, string> = {
  'Acceso': '#2563EB',
  'Rectificación': '#7C3AED',
  'Cancelación': '#DC2626',
  'Oposición': '#D97706',
  'Bloqueo temporal': '#DC2626',
  'Portabilidad': '#059669',
};

const TIPO_ABBR: Record<string, string> = {
  'Acceso': 'AC',
  'Rectificación': 'RC',
  'Cancelación': 'CA',
  'Oposición': 'OP',
  'Bloqueo temporal': 'BL',
  'Portabilidad': 'PT',
};

const ESTADO_STYLES: Record<string, { bg: string; color: string }> = {
  'Abierto': { bg: '#DBEAFE', color: '#2563EB' },
  'En Proceso': { bg: '#EDE9FE', color: '#7C3AED' },
  'Pendiente': { bg: '#FEF3C7', color: '#D97706' },
  'Resuelto': { bg: '#DCFCE7', color: '#059669' },
  'Bloqueado': { bg: '#FEE2E2', color: '#DC2626' },
  'Rechazado': { bg: '#FEE2E2', color: '#991B1B' },
  'Subsanación': { bg: '#FEF3C7', color: '#D97706' },
  'Prórroga': { bg: '#EDE9FE', color: '#7C3AED' },
};

function fmtDate(val: string | null | undefined): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CL', { dateStyle: 'medium' });
}

function fmtDateTime(val: string | null | undefined): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-CL', { dateStyle: 'medium', timeStyle: 'short' });
}

function getDiasRestantesStyle(dias: number | null | undefined): { bg: string; color: string; text: string } {
  if (dias === null || dias === undefined) return { bg: '#F3F4F6', color: '#6B7280', text: '—' };
  if (dias < 0) return { bg: '#FEE2E2', color: '#DC2626', text: `${Math.abs(dias)} días vencido` };
  if (dias === 0) return { bg: '#FEF3C7', color: '#D97706', text: 'Vence hoy' };
  if (dias <= 3) return { bg: '#FEE2E2', color: '#DC2626', text: `${dias} días` };
  if (dias <= 5) return { bg: '#FEF3C7', color: '#D97706', text: `${dias} días` };
  return { bg: '#DCFCE7', color: '#059669', text: `${dias} días` };
}

export default function SeguimientoPage() {
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SeguimientoResponse | null>(null);
  const [error, setError] = useState('');

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!token.trim()) {
      toast.error('Ingresá tu número de seguimiento');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await consultarSeguimiento(token.trim());
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se encontró ninguna solicitud con ese número.');
    } finally {
      setLoading(false);
    }
  }

  const estadoStyle = result ? (ESTADO_STYLES[result.estado] ?? { bg: '#F3F4F6', color: '#6B7280' }) : null;
  const diasStyle = result ? getDiasRestantesStyle(result.dias_restantes) : null;
  const tipoColor = result ? (TIPO_COLORS[result.tipo] ?? '#6B7280') : '#6B7280';
  const tipoAbbr = result ? (TIPO_ABBR[result.tipo] ?? '??') : '??';

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F9FAFB' }}>
      <div className="max-w-xl mx-auto px-4 py-12 space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#111827' }}>
            Consultá el estado de tu solicitud
          </h1>
          <p className="text-base" style={{ color: '#6B7280' }}>
            Ingresá el número de seguimiento que recibiste por email al momento de hacer tu solicitud ARCOP+.
          </p>
        </div>

        <form onSubmit={handleSearch} className="bg-white rounded-2xl shadow-sm p-6 space-y-4">
          <div>
            <label htmlFor="token-input" className="block text-sm font-semibold mb-1" style={{ color: '#374151' }}>
              Número de seguimiento
            </label>
            <input
              id="token-input"
              type="text"
              value={token}
              onChange={e => setToken(e.target.value)}
              placeholder="Ej: a3f8b2c1-9d4e-4a1b-8f3c-d2e1f0a9b8c7"
              className="w-full px-4 py-3 rounded-xl border text-sm font-mono"
              style={{ borderColor: error ? '#DC2626' : '#E5E7EB', outline: 'none' }}
              aria-describedby={error ? 'token-error' : undefined}
            />
            {error && (
              <p id="token-error" className="text-sm mt-1" style={{ color: '#DC2626' }}>{error}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl text-white font-semibold text-sm disabled:opacity-50"
            style={{ backgroundColor: '#2563EB' }}
          >
            {loading ? 'Buscando...' : 'Consultar estado'}
          </button>
          <p className="text-xs text-center" style={{ color: '#9CA3AF' }}>
            ¿No recibiste el número? Contactá a la empresa por otro canal.
          </p>
        </form>

        {result && estadoStyle && diasStyle && (
          <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
            <div
              className="p-6"
              style={{ background: `${tipoColor}11`, borderBottom: `1px solid ${tipoColor}22` }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center font-bold text-sm"
                  style={{ background: `${tipoColor}22`, color: tipoColor }}
                >
                  {tipoAbbr}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className="px-2.5 py-0.5 rounded-lg text-xs font-bold"
                      style={{ background: estadoStyle.bg, color: estadoStyle.color }}
                    >
                      {result.estado}
                    </span>
                    <span className="text-sm font-semibold" style={{ color: '#111827' }}>
                      {result.tipo}
                    </span>
                  </div>
                  {result.company_nombre && (
                    <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>
                      {result.company_nombre}
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl p-3" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                  <p className="text-xs font-medium mb-1" style={{ color: '#6B7280' }}>Fecha de recepción</p>
                  <p className="text-sm font-semibold" style={{ color: '#111827' }}>
                    {fmtDate(result.fecha_recepcion)}
                  </p>
                </div>
                <div
                  className="rounded-xl p-3"
                  style={{ background: diasStyle.bg, border: `1px solid ${diasStyle.color}33` }}
                >
                  <p className="text-xs font-medium mb-1" style={{ color: diasStyle.color }}>Vencimiento SLA</p>
                  <p className="text-sm font-bold" style={{ color: diasStyle.color }}>
                    {fmtDate(result.fecha_vencimiento)}
                    <span className="ml-1.5 text-xs font-medium">({diasStyle.text})</span>
                  </p>
                </div>
              </div>

              <div
                className="rounded-xl p-4 flex items-center gap-3"
                style={{ background: estadoStyle.bg, border: `1px solid ${estadoStyle.color}22` }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-sm"
                  style={{ background: estadoStyle.color, color: 'white' }}
                >
                  {result.estado === 'Resuelto' ? '✅' :
                   result.estado === 'En Proceso' ? '⚙️' :
                   result.estado === 'Rechazado' ? '🚫' :
                   result.estado === 'Bloqueado' ? '🔒' :
                   result.estado === 'Subsanación' ? '📝' :
                   result.estado === 'Prórroga' ? '⏰' : '📋'}
                </div>
                <div>
                  <p className="text-sm font-semibold" style={{ color: '#111827' }}>
                    Estado actual: {result.estado}
                  </p>
                  <p className="text-xs" style={{ color: '#6B7280' }}>
                    {result.estado === 'Resuelto' ? 'La empresa respondió tu solicitud.' :
                     result.estado === 'En Proceso' ? 'La empresa está procesando tu solicitud.' :
                     result.estado === 'Subsanación' ? 'La empresa solicitó información adicional.' :
                     result.estado === 'Prórroga' ? 'La empresa extendió el plazo de respuesta.' :
                     result.estado === 'Rechazado' ? 'La solicitud fue rechazada por la empresa.' :
                     result.estado === 'Bloqueado' ? 'El RAT asociado está bloqueado.' :
                     'La empresa está evaluando tu solicitud.'}
                  </p>
                </div>
              </div>

              {result.historial.length > 0 && (
                <div>
                  <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Historial de cambios</p>
                  <div className="space-y-2">
                    {result.historial.map((h, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <div
                          className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                          style={{ background: i === result.historial.length - 1 ? tipoColor : '#D1D5DB' }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-medium" style={{ color: '#374151' }}>
                              {h.estado_anterior ? `${h.estado_anterior} → ${h.estado_nuevo}` : h.estado_nuevo}
                            </span>
                            <span className="text-xs" style={{ color: '#9CA3AF' }}>{fmtDateTime(h.fecha)}</span>
                          </div>
                          {h.descripcion && (
                            <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{h.descripcion}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="rounded-xl p-4" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                <p className="text-xs" style={{ color: '#1E40AF' }}>
                  📧 La empresa te notificará por email cuando haya una respuesta.
                  Si tenés dudas, contactá directamente a la empresa.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="text-center text-xs" style={{ color: '#9CA3AF' }}>
          <p>Este portal es parte de <strong>Custodio RAT</strong>, gestión de derechos ARCOP+ conforme a la Ley 21.719.</p>
        </div>
      </div>
    </div>
  );
}
