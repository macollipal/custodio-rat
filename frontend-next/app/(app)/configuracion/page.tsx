'use client';

import { useState, useEffect, useCallback } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { getDbHealth, getAuditoriaGlobal, type DbHealth } from '@/lib/api';

interface AuditEntry {
  id: number;
  rat_id: number;
  accion: string;
  usuario: string;
  timestamp: string;
  detalle?: string;
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

const TABS = [
  { key: 'sistema', label: 'Sistema' },
  { key: 'registros', label: 'Último log' },
  { key: 'solicitudes', label: 'Solicitudes ARCO' },
  { key: 'exportacion', label: 'Exportación' },
];

const EXPORT_KEY = 'custodio_export_config';

interface ExportConfig {
  formatoPredeterminado: 'csv' | 'pdf';
  incluirAuditoria: boolean;
  nombreConRut: boolean;
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

const PAGE_SIZE = 15;

function fmtDate(val: string | undefined | null, opts?: Intl.DateTimeFormatOptions): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CL', opts ?? { dateStyle: 'short' });
}

function fmtDateTime(val: string | undefined | null): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
}

interface HistorialEntry {
  id: number;
  estado_anterior: string | null;
  estado_nuevo: string;
  descripcion: string | null;
  fecha: string | null;
  usuario_nombre: string | null;
}

function SolicitudRow({ sol, onResponder }: { sol: SolicitudDerecho; onResponder: (id: number, estado: string, respuesta: string, descripcion: string) => Promise<void> }) {
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
            {fmtDate(sol.created_at)}
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
                {/* Header */}
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

                {/* Historial — prominente */}
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

                {/* Form */}
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

export default function ConfiguracionPage() {
  const { user, company } = useApp();
  const [tab, setTab] = useState('sistema');
  const [dbHealth, setDbHealth] = useState<DbHealth | null>(null);
  const [loadingDb, setLoadingDb] = useState(true);
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [solicitudes, setSolicitudes] = useState<SolicitudDerecho[]>([]);
  const [loadingSolicitudes, setLoadingSolicitudes] = useState(false);
  const [solicitudFiltro, setSolicitudFiltro] = useState<string>('');
  const [page, setPage] = useState(1);
  const [exportConfig, setExportConfig] = useState<ExportConfig>(() => {
    if (typeof window === 'undefined') return { formatoPredeterminado: 'pdf', incluirAuditoria: true, nombreConRut: true };
    const saved = localStorage.getItem(EXPORT_KEY);
    return saved ? JSON.parse(saved) : { formatoPredeterminado: 'pdf', incluirAuditoria: true, nombreConRut: true };
  });

  const fetchDbHealth = useCallback(async () => {
    setLoadingDb(true);
    try {
      setDbHealth(await getDbHealth());
    } catch {
      setDbHealth({ engine: 'unknown', url: '-', status: 'error' });
    } finally {
      setLoadingDb(false);
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    if (!company?.id) return;
    setLoadingLogs(true);
    try {
      const data = await getAuditoriaGlobal(company.id);
      setAuditLogs(Array.isArray(data) ? data.slice(-20).reverse() : []);
    } catch {
      toast.error('No se pudieron cargar los registros.');
    } finally {
      setLoadingLogs(false);
    }
  }, [company?.id]);

  const fetchSolicitudes = useCallback(async () => {
    if (!company?.id) return;
    setLoadingSolicitudes(true);
    try {
      const params = new URLSearchParams({ company_id: String(company.id) });
      if (solicitudFiltro) params.set('estado', solicitudFiltro);
      const res = await fetch(`${API_BASE}/solicitudes-derecho/?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('custodio_token')}` },
      });
      const data = await res.json();
      setSolicitudes(Array.isArray(data) ? data : (data.solicitudes || []));
    } catch {
      toast.error('No se pudieron cargar las solicitudes.');
    } finally {
      setLoadingSolicitudes(false);
    }
  }, [company?.id, solicitudFiltro]);

  function formatoAccion(accion: string) {
    const map: Record<string, { label: string; color: string }> = {
      crear: { label: 'Crear', color: '#059669' },
      editar: { label: 'Editar', color: '#2563EB' },
      eliminar: { label: 'Eliminar', color: '#DC2626' },
      duplicar: { label: 'Duplicar', color: '#7C3AED' },
      revision: { label: 'Revisión', color: '#D97706' },
    };
    return map[accion] ?? { label: accion, color: '#6B7280' };
  }

  function formatearFecha(ts: string) {
    if (!ts) return '—';
    return new Date(ts).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
  }

  useEffect(() => {
    if (tab === 'sistema') fetchDbHealth();
    if (tab === 'registros') fetchAuditLogs();
    if (tab === 'solicitudes' && company?.id) fetchSolicitudes();
  }, [tab, company?.id, fetchAuditLogs, fetchSolicitudes, fetchDbHealth]);

  useEffect(() => {
    localStorage.setItem(EXPORT_KEY, JSON.stringify(exportConfig));
  }, [exportConfig]);

  async function responderSolicitud(id: number, estado: string, respuesta: string, descripcionAccion: string): Promise<void> {
    const res = await fetch(`${API_BASE}/solicitudes-derecho/${id}/responder`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('custodio_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        estado,
        respuesta,
        descripcion_accion: descripcionAccion,
        usuario_nombre: user?.full_name ?? 'Admin',
      }),
    });
    if (!res.ok) throw new Error('Error');
    toast.success('Solicitud actualizada.');
    fetchSolicitudes();
  }

  const totalPages = Math.ceil(solicitudes.length / PAGE_SIZE);
  const paginatedSolicitudes = solicitudes.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const cardCls = 'bg-white rounded-xl p-6 shadow-sm';
  const labelCls = 'text-sm font-medium';
  const valueCls = 'text-sm font-mono';

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Configuración</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b" style={{ borderColor: '#E5E7EB' }}>
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors"
            style={{
              borderColor: tab === t.key ? '#2563EB' : 'transparent',
              color: tab === t.key ? '#2563EB' : '#6B7280',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB 1: Sistema */}
      {tab === 'sistema' && (
        <div className="space-y-6">
          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Estado del sistema</h2>
            {loadingDb ? (
              <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
            ) : dbHealth ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Motor</span>
                  <span className={valueCls} style={{ color: '#059669' }}>
                    {dbHealth.engine === 'postgresql' ? 'PostgreSQL (Neon)' : 'Otro'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>URL</span>
                  <span className={valueCls} style={{ color: '#374151' }} title={dbHealth.url}>
                    {(() => {
                      const u = (dbHealth.url || '').split('?')[0];
                      const parts = u.split('/');
                      const host = parts[0] || '';
                      const db = parts.slice(1).join('/');
                      return `${host.split('.')[0]} / ${db}`;
                    })()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Estado BD</span>
                  <span className={labelCls} style={{ color: dbHealth.status === 'ok' ? '#059669' : '#DC2626' }}>
                    {dbHealth.status === 'ok' ? 'Conectada' : 'Error'}
                  </span>
                </div>
                {dbHealth.latency_ms !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className={labelCls} style={{ color: '#6B7280' }}>Latencia</span>
                    <span className={labelCls} style={{ color: '#059669' }}>{dbHealth.latency_ms}ms</span>
                  </div>
                )}
                {dbHealth.error && (
                  <div className="p-3 rounded-lg" style={{ background: '#FEF2F2' }}>
                    <span className="text-sm" style={{ color: '#DC2626' }}>{dbHealth.error}</span>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Configuración del sistema</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Frontend</span>
                <span className={valueCls} style={{ color: '#374151' }}>Next.js 16</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Backend API</span>
                <span className={valueCls} style={{ color: '#374151' }}>{API_BASE}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Entorno</span>
                <span className={valueCls} style={{ color: '#374151' }}>
                  {typeof window !== 'undefined' && window.location.hostname.includes('vercel') ? 'Producción (Vercel)' : 'Desarrollo local'}
                </span>
              </div>
            </div>
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Usuario actual</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Nombre</span>
                <span className={labelCls} style={{ color: '#374151' }}>{user?.full_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Username</span>
                <span className={valueCls} style={{ color: '#374151' }}>{user?.username}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Rol</span>
                <span className={labelCls} style={{ color: '#374151' }}>
                  {user?.rol_global === 'superadmin' ? 'Superadmin' : user?.rol_global === 'admin_empresa' ? 'Admin empresa' : 'Usuario'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Empresa activa</span>
                <span className={labelCls} style={{ color: '#374151' }}>{company?.nombre ?? 'Ninguna'}</span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={fetchDbHealth}
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition"
              style={{ background: '#2563EB' }}
            >
              🔄 Refrescar estado
            </button>
          </div>
        </div>
      )}

      {/* TAB 2: Último log */}
      {tab === 'registros' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold" style={{ color: '#111827' }}>Últimos registros de auditoría</h2>
            <button
              onClick={fetchAuditLogs}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
              style={{ borderColor: '#E5E7EB', color: '#374151' }}
            >
              🔄
            </button>
          </div>

          {loadingLogs ? (
            <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : auditLogs.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>No hay registros de auditoría.</p>
          ) : (
            <div className="space-y-2">
              {auditLogs.map(log => {
                const { label, color } = formatoAccion(log.accion);
                return (
                  <div
                    key={log.id}
                    className="flex items-start gap-3 p-3 rounded-lg"
                    style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <span
                        className="inline-block px-2 py-0.5 rounded text-xs font-semibold"
                        style={{ background: `${color}20`, color }}
                      >
                        {label}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-semibold" style={{ color: '#111827' }}>
                          RAT #{log.rat_id ?? '—'}
                        </span>
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>·</span>
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>{log.usuario ?? '—'}</span>
                      </div>
                      {log.detalle && (
                        <p className="text-xs truncate" style={{ color: '#6B7280' }} title={log.detalle}>
                          {log.detalle.length > 100 ? log.detalle.slice(0, 100) + '...' : log.detalle}
                        </p>
                      )}
                    </div>
                    <div className="flex-shrink-0 text-xs" style={{ color: '#9CA3AF' }}>
                      {formatearFecha(log.timestamp)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: Solicitudes ARCO */}
      {tab === 'solicitudes' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-base font-semibold" style={{ color: '#111827' }}>Solicitudes ARCO</h2>
              <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>
                {solicitudes.length > 0 ? `${solicitudes.length} total` : 'Acceso, Rectificación, Cancelación, Oposición'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={solicitudFiltro}
                onChange={e => { setSolicitudFiltro(e.target.value); setPage(1); }}
                className="px-3 py-1.5 rounded-lg text-xs border"
                style={{ borderColor: '#E5E7EB', backgroundColor: '#FFFFFF' }}
              >
                <option value="">Todas</option>
                <option value="pendiente">Pendientes</option>
                <option value="en_proceso">En proceso</option>
                <option value="resuelto">Resueltas</option>
                <option value="rechazada">Rechazadas</option>
              </select>
              <button
                onClick={fetchSolicitudes}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
                style={{ borderColor: '#E5E7EB', color: '#374151' }}
              >
                🔄
              </button>
            </div>
          </div>

          {loadingSolicitudes ? (
            <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : solicitudes.length === 0 ? (
            <div className="text-center py-12 rounded-xl" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
              <p className="text-4xl mb-2">📭</p>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>No hay solicitudes</p>
              <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                Las solicitudes que envíen los titulares aparecerán aquí.
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
                <table className="w-full">
                  <thead>
                    <tr style={{ background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                      <th className="py-2.5 pl-3 pr-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Tipo</th>
                      <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Titular</th>
                      <th className="py-2.5 px-2 text-left text-xs font-semibold hidden md:table-cell" style={{ color: '#6B7280' }}>Email</th>
                      <th className="py-2.5 px-2 text-left text-xs font-semibold hidden lg:table-cell" style={{ color: '#6B7280' }}>Respuesta</th>
                      <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Estado</th>
                      <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Fecha</th>
                      <th className="py-2.5 pr-3 pl-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedSolicitudes.map(sol => (
                      <SolicitudRow key={sol.id} sol={sol} onResponder={responderSolicitud} />
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-1 flex-wrap">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border disabled:opacity-40"
                    style={{ borderColor: '#E5E7EB', color: '#374151' }}
                  >
                    ← Anterior
                  </button>
                  {(() => {
                    const pages: (number | '...')[] = [];
                    const maxVisible = 7;
                    let start = Math.max(1, page - 3);
                    let end = Math.min(totalPages, page + 3);
                    if (end - start < maxVisible - 1) {
                      if (start === 1) end = Math.min(totalPages, start + maxVisible - 1);
                      else start = Math.max(1, end - maxVisible + 1);
                    }
                    if (start > 1) { pages.push(1); if (start > 2) pages.push('...'); }
                    for (let i = start; i <= end; i++) pages.push(i);
                    if (end < totalPages) { if (end < totalPages - 1) pages.push('...'); pages.push(totalPages); }
                    return pages.map((p, idx) =>
                      p === '...' ? (
                        <span key={`ellipsis-${idx}`} className="px-1 py-1.5 text-xs" style={{ color: '#9CA3AF' }}>…</span>
                      ) : (
                        <button
                          key={p}
                          onClick={() => setPage(p as number)}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border"
                          style={{
                            borderColor: page === p ? '#2563EB' : '#E5E7EB',
                            background: page === p ? '#2563EB' : 'transparent',
                            color: page === p ? 'white' : '#374151',
                          }}
                        >
                          {p}
                        </button>
                      )
                    );
                  })()}
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium border disabled:opacity-40"
                    style={{ borderColor: '#E5E7EB', color: '#374151' }}
                  >
                    Siguiente →
                  </button>
                </div>
              )}
            </>
          )}

          <div className="rounded-xl p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-medium mb-1" style={{ color: '#374151' }}>¿Qué deben hacer los titulares?</p>
            <p className="text-xs" style={{ color: '#6B7280' }}>
              Pueden ejercer sus derechos ARCO visitando{' '}
              <a href="/solicitud_derecho" className="underline" style={{ color: '#2563EB' }}>/solicitud_derecho</a>
              {' '}o contactando directamente al DPO de la empresa.
            </p>
          </div>
        </div>
      )}

      {/* TAB 4: Exportación */}
      {tab === 'exportacion' && (
        <div className="space-y-6">
          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-1" style={{ color: '#111827' }}>Configuración de exportación</h2>
            <p className="text-xs mb-6" style={{ color: '#9CA3AF' }}>
              Estos ajustes se guardan en tu navegador y se aplican a todas las exportaciones.
            </p>

            <div className="space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Formato predeterminado</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Se usará al exportar desde el listado de RATs</p>
                </div>
                <select
                  value={exportConfig.formatoPredeterminado}
                  onChange={e => setExportConfig(c => ({ ...c, formatoPredeterminado: e.target.value as 'csv' | 'pdf' }))}
                  className="px-3 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', minWidth: 140 }}
                >
                  <option value="pdf">PDF</option>
                  <option value="csv">CSV</option>
                </select>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Nombre de empresa en archivo</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Incluye RUT en el nombre del archivo exportado</p>
                </div>
                <button
                  role="switch"
                  aria-checked={exportConfig.nombreConRut}
                  onClick={() => setExportConfig(c => ({ ...c, nombreConRut: !c.nombreConRut }))}
                  className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                  style={{ background: exportConfig.nombreConRut ? '#2563EB' : '#D1D5DB' }}
                >
                  <span
                    className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                    style={{ transform: exportConfig.nombreConRut ? 'translateX(22px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Incluir historial de auditoría</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Agrega el registro de cambios al exportar PDF individual</p>
                </div>
                <button
                  role="switch"
                  aria-checked={exportConfig.incluirAuditoria}
                  onClick={() => setExportConfig(c => ({ ...c, incluirAuditoria: !c.incluirAuditoria }))}
                  className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                  style={{ background: exportConfig.incluirAuditoria ? '#2563EB' : '#D1D5DB' }}
                >
                  <span
                    className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                    style={{ transform: exportConfig.incluirAuditoria ? 'translateX(22px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Acerca de los formatos</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📄</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>PDF</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Formato oficial para presentar ante la APDC. Incluye todos los campos y es apta para impresión.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📊</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>CSV</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Hoja de cálculo para análisis de datos. Compatible con Excel y Google Sheets.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📋</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>CNI (APDC)</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Formato oficial de la Agencia de Protección de Datos Pessoales para presentar el libro de actividades.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
