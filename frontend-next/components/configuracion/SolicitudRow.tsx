'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';

interface HistorialEntry {
  id: number;
  estado_anterior: string | null;
  estado_nuevo: string;
  descripcion: string | null;
  fecha: string | null;
  usuario_nombre: string | null;
}

interface SolicitudDerecho {
  id: number;
  company_id: number;
  tipo: string;
  nombre_titular: string;
  email_titular: string;
  rut_titular?: string;
  descripcion?: string;
  estado: string;
  solicitud_fecha?: string;
  respuesta?: string;
  respuesta_fecha?: string;
  created_at: string;
  updated_at: string;
}

const TIPO_MAP: Record<string, { label: string; color: string; abbr: string }> = {
  acceso: { label: 'Acceso', color: '#2563EB', abbr: 'AC' },
  rectificacion: { label: 'Rectificación', color: '#7C3AED', abbr: 'RC' },
  cancelacion: { label: 'Cancelación', color: '#DC2626', abbr: 'CA' },
  oposicion: { label: 'Oposición', color: '#D97706', abbr: 'OP' },
};

const ESTADO_MAP: Record<string, { label: string; color: string; bg: string }> = {
  pendiente: { label: 'Pendiente', color: '#D97706', bg: '#FEF3C7' },
  en_proceso: { label: 'En proceso', color: '#2563EB', bg: '#DBEAFE' },
  resuelto: { label: 'Resuelto', color: '#059669', bg: '#DCFCE7' },
  rechazada: { label: 'Rechazada', color: '#DC2626', bg: '#FEE2E2' },
};

function fmtDateTime(val: string | undefined | null): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
}

interface SolicitudRowProps {
  sol: SolicitudDerecho;
  onResponder: (id: number, estado: string, respuesta: string, descripcion: string) => Promise<void>;
}

export function SolicitudRow({ sol, onResponder }: SolicitudRowProps) {
  const [showPanel, setShowPanel] = useState(false);
  const [respuesta, setRespuesta] = useState(sol.respuesta ?? '');
  const [nuevoEstado, setNuevoEstado] = useState(sol.estado);
  const [descripcionAccion, setDescripcionAccion] = useState('');
  const [historial, setHistorial] = useState<HistorialEntry[]>([]);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  const [saving, setSaving] = useState(false);

  const tipo = TIPO_MAP[sol.tipo] ?? { label: sol.tipo, color: '#6B7280', abbr: '??' };
  const estado = ESTADO_MAP[sol.estado] ?? { label: sol.estado, color: '#6B7280', bg: '#F3F4F6' };

  function fetchHistorial() {
    if (!sol.id) return;
    setLoadingHistorial(true);
    fetch(`${API_BASE}/solicitudes-derecho/${sol.id}/historial`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('custodio_token')}` },
    })
      .then(r => r.json())
      .then(data => { setHistorial(Array.isArray(data) ? data : []); })
      .catch(() => setHistorial([]))
      .finally(() => setLoadingHistorial(false));
  }

  useEffect(() => {
    if (showPanel && sol.id) {
      fetchHistorial();
    }
  }, [showPanel, sol.id]);

  function handleGuardar() {
    setSaving(true);
    onResponder(sol.id, nuevoEstado, respuesta, descripcionAccion)
      .then(() => {
        fetchHistorial();
        setShowPanel(false);
        setDescripcionAccion('');
      })
      .catch(() => {
        toast.error('Error al guardar. Intentá de nuevo.');
      })
      .finally(() => {
        setSaving(false);
      });
  }

  return (
    <>
      <tr
        className="border-b cursor-pointer hover:bg-gray-50 transition"
        style={{ borderColor: '#F3F4F6' }}
        onClick={() => setShowPanel(p => !p)}
      >
        <td className="py-2.5 pl-3 pr-2">
          <span
            className="inline-flex items-center justify-center w-7 h-7 rounded font-bold text-xs"
            style={{ background: `${tipo.color}15`, color: tipo.color }}
            title={tipo.label}
          >
            {tipo.abbr}
          </span>
        </td>
        <td className="py-2.5 px-2">
          <div className="text-xs font-medium" style={{ color: '#111827' }}>{sol.nombre_titular}</div>
          <div className="text-xs" style={{ color: '#9CA3AF' }}>{sol.rut_titular || '—'}</div>
        </td>
        <td className="py-2.5 px-2 hidden md:table-cell">
          <a href={`mailto:${sol.email_titular}`} className="text-xs underline" style={{ color: '#2563EB' }} onClick={e => e.stopPropagation()}>
            {sol.email_titular}
          </a>
        </td>
        <td className="py-2.5 px-2 hidden lg:table-cell">
          <span className="text-xs" style={{ color: '#6B7280' }}>
            {sol.respuesta
              ? sol.respuesta.length > 40 ? sol.respuesta.slice(0, 40) + '…' : sol.respuesta
              : <span style={{ color: '#D1D5DB' }}>Sin respuesta</span>
            }
          </span>
        </td>
        <td className="py-2.5 px-2">
          <span
            className="px-2 py-0.5 rounded text-xs font-medium"
            style={{ background: estado.bg, color: estado.color }}
          >
            {estado.label}
          </span>
        </td>
        <td className="py-2.5 px-2">
          <span className="text-xs" style={{ color: '#9CA3AF' }}>
            {sol.created_at ? new Date(sol.created_at).toLocaleDateString('es-CL', { dateStyle: 'short' }) : '—'}
          </span>
        </td>
        <td className="py-2.5 pr-3 pl-2">
          <button
            onClick={e => { e.stopPropagation(); setShowPanel(p => !p); }}
            className="px-2.5 py-1 rounded text-xs font-medium border transition hover:bg-gray-100"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            {sol.respuesta ? 'Editar' : 'Responder'}
          </button>
        </td>
      </tr>
      {showPanel && (
        <tr>
          <td colSpan={7} className="p-0">
            <div className="p-4 mx-4 my-2 rounded-xl" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
              <div className="space-y-4">
                <div className="flex items-start gap-6 flex-wrap">
                  <div className="flex-1 min-w-48">
                    <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Datos del titular</p>
                    <div className="space-y-1">
                      <p className="text-xs" style={{ color: '#6B7280' }}>
                        <span className="font-medium" style={{ color: '#374151' }}>Nombre:</span> {sol.nombre_titular}
                      </p>
                      <p className="text-xs" style={{ color: '#6B7280' }}>
                        <span className="font-medium" style={{ color: '#374151' }}>RUT:</span> {sol.rut_titular || '—'}
                      </p>
                      <p className="text-xs" style={{ color: '#6B7280' }}>
                        <span className="font-medium" style={{ color: '#374151' }}>Email:</span>{' '}
                        <a href={`mailto:${sol.email_titular}`} className="underline" style={{ color: '#2563EB' }}>{sol.email_titular}</a>
                      </p>
                      <p className="text-xs" style={{ color: '#6B7280' }}>
                        <span className="font-medium" style={{ color: '#374151' }}>Fecha:</span>{' '}
                        {fmtDateTime(sol.solicitud_fecha ?? sol.created_at)}
                      </p>
                      {sol.descripcion && (
                        <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
                          <span className="font-medium" style={{ color: '#374151' }}>Detalle:</span>{' '}
                          {sol.descripcion}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-xs font-semibold" style={{ color: '#374151' }}>Historial</p>
                    {historial.length > 0 && (
                      <span className="px-1.5 py-0.5 rounded text-xs" style={{ background: '#E5E7EB', color: '#6B7280' }}>
                        {historial.length} {historial.length === 1 ? 'entrada' : 'entradas'}
                      </span>
                    )}
                  </div>
                  {loadingHistorial ? (
                    <p className="text-xs" style={{ color: '#9CA3AF' }}>Cargando...</p>
                  ) : historial.length === 0 ? (
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ background: '#D1D5DB' }} />
                      <p className="text-xs" style={{ color: '#D1D5DB' }}>
                        Sin cambios registrados — usá el formulario para registrar la primera acción.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-1.5">
                      {historial.map(h => (
                        <div key={h.id} className="flex items-start gap-2">
                          <div className="flex-shrink-0 mt-1">
                            <div className="w-2 h-2 rounded-full" style={{ background: ESTADO_MAP[h.estado_nuevo]?.color ?? '#6B7280' }} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-xs font-medium" style={{ color: '#374151' }}>
                                {h.estado_anterior
                                  ? `${ESTADO_MAP[h.estado_anterior]?.label ?? h.estado_anterior} → ${ESTADO_MAP[h.estado_nuevo]?.label ?? h.estado_nuevo}`
                                  : ESTADO_MAP[h.estado_nuevo]?.label ?? h.estado_nuevo}
                              </span>
                              <span className="text-xs" style={{ color: '#9CA3AF' }}>
                                {fmtDateTime(h.fecha)}
                              </span>
                              {h.usuario_nombre && (
                                <span className="text-xs" style={{ color: '#9CA3AF' }}>· {h.usuario_nombre}</span>
                              )}
                            </div>
                            {h.descripcion && (
                              <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{h.descripcion}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Registrar acción</p>
                  <div className="flex flex-col gap-2">
                    <div className="flex gap-3 flex-wrap">
                      <select
                        value={nuevoEstado}
                        onChange={e => setNuevoEstado(e.target.value)}
                        className="px-3 py-1.5 rounded-lg text-xs border"
                        style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', minWidth: 140 }}
                      >
                        <option value="pendiente">Pendiente</option>
                        <option value="en_proceso">En proceso</option>
                        <option value="resuelto">Resuelto</option>
                        <option value="rechazada">Rechazada</option>
                      </select>
                      <input
                        type="text"
                        value={descripcionAccion}
                        onChange={e => setDescripcionAccion(e.target.value)}
                        placeholder="Ej: Se envió correo de respuesta al titular..."
                        className="flex-1 px-3 py-1.5 rounded-lg text-xs border min-w-48"
                        style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
                      />
                    </div>
                    <textarea
                      value={respuesta}
                      onChange={e => setRespuesta(e.target.value)}
                      rows={2}
                      placeholder="Respuesta formal para el titular (opcional)..."
                      className="w-full px-3 py-2 rounded-lg text-xs border"
                      style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={handleGuardar}
                        disabled={saving}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white disabled:opacity-60"
                        style={{ background: '#059669' }}
                      >
                        {saving ? 'Guardando...' : 'Registrar'}
                      </button>
                      <button
                        onClick={() => { setRespuesta(sol.respuesta ?? ''); setNuevoEstado(sol.estado); setDescripcionAccion(''); setShowPanel(false); }}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium border"
                        style={{ borderColor: '#E5E7EB', color: '#374151' }}
                      >
                        Cerrar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
