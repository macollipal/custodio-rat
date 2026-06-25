'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import Drawer from '@/components/ui/Drawer';
import { FlujoModal } from '@/components/arco/FlujoModal';
import {
  listarTktNotas,
  listarTktHistorial,
  actualizarTktTicket,
  agregarTktNota,
  listarRats,
  bloquearSolicitud,
  desbloquearSolicitud,
  exportarPortabilidad,
  solicitarSubsanacion,
  completarSubsanacion,
  prorrogarTicket,
  type TktTicket,
} from '@/lib/api';
import type { RAT } from '@/types';

const TKT_TIPO_MAP: Record<string, { label: string; color: string; abbr: string }> = {
  acceso: { label: 'Acceso', color: '#2563EB', abbr: 'AC' },
  rectificacion: { label: 'Rectificación', color: '#7C3AED', abbr: 'RC' },
  cancelacion: { label: 'Cancelación', color: '#DC2626', abbr: 'CA' },
  oposicion: { label: 'Oposición', color: '#D97706', abbr: 'OP' },
  bloqueo: { label: 'Bloqueo temporal', color: '#DC2626', abbr: 'BL' },
  portabilidad: { label: 'Portabilidad', color: '#059669', abbr: 'PT' },
};

const TKT_ESTADO_MAP: Record<string, { label: string; color: string; bg: string }> = {
  abierto: { label: 'Abierto', color: '#2563EB', bg: '#DBEAFE' },
  en_proceso: { label: 'En Proceso', color: '#7C3AED', bg: '#EDE9FE' },
  pendiente: { label: 'Pendiente', color: '#D97706', bg: '#FEF3C7' },
  resuelto: { label: 'Resuelto', color: '#059669', bg: '#DCFCE7' },
  bloqueado: { label: 'Bloqueado', color: '#DC2626', bg: '#FEE2E2' },
  rechazado: { label: 'Rechazado', color: '#991B1B', bg: '#FEE2E2' },
  subsanacion: { label: 'Subsanación', color: '#D97706', bg: '#FEF3C7' },
  prorroga: { label: 'Prórroga', color: '#7C3AED', bg: '#EDE9FE' },
};

function getSlaColor(dias: number | null | undefined): { color: string; bg: string; text: string } {
  if (dias === null || dias === undefined) return { color: '#6B7280', bg: '#F3F4F6', text: '—' };
  if (dias <= 0) return { color: '#DC2626', bg: '#FEE2E2', text: `${Math.abs(dias)}d vencido` };
  if (dias <= 3) return { color: '#DC2626', bg: '#FEE2E2', text: `${dias}d` };
  if (dias <= 5) return { color: '#D97706', bg: '#FEF3C7', text: `${dias}d` };
  return { color: '#059669', bg: '#DCFCE7', text: `${dias}d` };
}

function fmtDate(val: string | null | undefined): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CL', { dateStyle: 'short' });
}

function fmtDateTime(val: string | null | undefined): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
}

function sanitize(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#039;');
}

interface TicketDrawerProps {
  ticket: TktTicket | null;
  open: boolean;
  onClose: () => void;
  isAdmin: boolean;
  companyId: number;
}

export function TicketDrawer({ ticket, open, onClose, isAdmin, companyId }: TicketDrawerProps) {
  const [notas, setNotas] = useState<{ id: number; nota: string; user_id: number; created_at: string }[]>([]);
  const [historial, setHistorial] = useState<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]>([]);
  const [loadingNotas, setLoadingNotas] = useState(false);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  const [nuevaNota, setNuevaNota] = useState('');
  const [guardandoNota, setGuardandoNota] = useState(false);
  const [respuesta, setRespuesta] = useState('');
  const [nuevoEstado, setNuevoEstado] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [rats, setRats] = useState<RAT[]>([]);
  const [selectedRatId, setSelectedRatId] = useState<number | null>(null);
  const [plazoDias, setPlazoDias] = useState(30);
  const [accionLoading, setAccionLoading] = useState(false);
  const [subsanacionDetalle, setSubsanacionDetalle] = useState('');
  const [mostrarSubsanacion, setMostrarSubsanacion] = useState(false);
  const [mostrarProrroga, setMostrarProrroga] = useState(false);
  const [prorrogaDias, setProrrogaDias] = useState(10);
  const [prorrogaMotivo, setProrrogaMotivo] = useState('');
  const [flujoModalOpen, setFlujoModalOpen] = useState(false);

  useEffect(() => {
    if (open && ticket) {
      setRespuesta(ticket.respuesta_texto ?? '');
      setNuevoEstado(ticket.estado);
      setNuevaNota('');
      setNotas([]);
      setHistorial([]);
      setSelectedRatId(null);
      setPlazoDias(30);
      setSubsanacionDetalle('');
      setMostrarSubsanacion(false);
      setMostrarProrroga(false);
      setProrrogaDias(10);
      setProrrogaMotivo('');
      if ((ticket.tipo === 'bloqueo' || ticket.tipo === 'portabilidad') && companyId) {
        listarRats(companyId).then(r => setRats(Array.isArray(r) ? r : [])).catch(() => setRats([]));
      }
    }
  }, [open, ticket, companyId]);

  const fetchNotas = useCallback(async () => {
    if (!ticket?.id) return;
    setLoadingNotas(true);
    try {
      const data = await listarTktNotas(ticket.id);
      setNotas(Array.isArray(data) ? data : []);
    } catch {
      toast.error('Error al cargar notas');
    } finally {
      setLoadingNotas(false);
    }
  }, [ticket?.id]);

  const fetchHistorial = useCallback(async () => {
    if (!ticket?.id) return;
    setLoadingHistorial(true);
    try {
      const data = await listarTktHistorial(ticket.id);
      setHistorial(Array.isArray(data) ? data : []);
    } catch {
      toast.error('Error al cargar historial');
    } finally {
      setLoadingHistorial(false);
    }
  }, [ticket?.id]);

  useEffect(() => {
    if (open && ticket) {
      fetchNotas();
      fetchHistorial();
    }
  }, [open, ticket, fetchNotas, fetchHistorial]);

  async function handleGuardarRespuesta() {
    if (!ticket?.id) return;
    setGuardando(true);
    try {
      await actualizarTktTicket(ticket.id, {
        estado: nuevoEstado,
        respuesta_texto: respuesta,
      });
      toast.success('Respuesta guardada');
      onClose();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setGuardando(false);
    }
  }

  async function handleBloquear() {
    if (!ticket?.id || !selectedRatId) return;
    setAccionLoading(true);
    try {
      await bloquearSolicitud(ticket.id, selectedRatId, plazoDias);
      toast.success('RAT bloqueado exitosamente');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al bloquear');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleDesbloquear() {
    if (!ticket?.id) return;
    setAccionLoading(true);
    try {
      await desbloquearSolicitud(ticket.id);
      toast.success('RAT desbloqueado');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al desbloquear');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleExportarPortabilidad() {
    if (!ticket?.id) return;
    setAccionLoading(true);
    try {
      const blob = await exportarPortabilidad(ticket.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `portabilidad_solicitud_${ticket.id}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Portabilidad exportada');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al exportar');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleSolicitarSubsanacion() {
    if (!ticket?.id || !subsanacionDetalle.trim()) return;
    setAccionLoading(true);
    try {
      await solicitarSubsanacion(ticket.id, subsanacionDetalle);
      toast.success('Subsanación solicitada al titular');
      setMostrarSubsanacion(false);
      onClose();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al solicitar subsanación');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleCompletarSubsanacion() {
    if (!ticket?.id) return;
    setAccionLoading(true);
    try {
      await completarSubsanacion(ticket.id);
      toast.success('Subsanación completada');
      onClose();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al completar subsanación');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleProrrogar() {
    if (!ticket?.id) return;
    setAccionLoading(true);
    try {
      await prorrogarTicket(ticket.id, prorrogaDias, prorrogaMotivo || undefined);
      toast.success(`Prórroga de ${prorrogaDias} días aplicada`);
      setMostrarProrroga(false);
      onClose();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al aplicar prorroga');
    } finally {
      setAccionLoading(false);
    }
  }

  async function handleAgregarNota() {
    if (!ticket?.id || !nuevaNota.trim()) return;
    setGuardandoNota(true);
    try {
      await agregarTktNota(ticket.id, nuevaNota);
      setNuevaNota('');
      fetchNotas();
      toast.success('Nota agregada');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al agregar nota');
    } finally {
      setGuardandoNota(false);
    }
  }

  if (!ticket) return null;

  const tipo = TKT_TIPO_MAP[ticket.tipo] ?? { label: ticket.tipo, color: '#6B7280', abbr: '??' };
  const estado = TKT_ESTADO_MAP[ticket.estado] ?? { label: ticket.estado, color: '#6B7280', bg: '#F3F4F6' };
  const prioridadMap: Record<string, { label: string; color: string; bg: string }> = {
    alta: { label: 'Alta', color: '#DC2626', bg: '#FEE2E2' },
    normal: { label: 'Normal', color: '#D97706', bg: '#FEF3C7' },
    baja: { label: 'Baja', color: '#6B7280', bg: '#F3F4F6' },
  };
  const prioridad = prioridadMap[ticket.prioridad] ?? { label: ticket.prioridad, color: '#6B7280', bg: '#F3F4F6' };
  const sla = getSlaColor(ticket.dias_restantes);

  return (
    <Drawer open={open} onClose={onClose} title="Solicitud de Derecho" size="lg">
      <div className="space-y-4">
        <div
          className="rounded-2xl p-5"
          style={{ background: `linear-gradient(135deg, ${tipo.color}22, ${tipo.color}11)`, border: `1px solid ${tipo.color}33` }}
        >
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={onClose}
              className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg transition hover:bg-black/10"
              style={{ color: tipo.color }}
              aria-label="Cerrar"
            >
              ←
            </button>
            <span
              className="inline-flex items-center justify-center w-10 h-10 rounded-xl font-bold text-sm"
              style={{ background: `${tipo.color}22`, color: tipo.color, border: `1px solid ${tipo.color}44` }}
            >
              {tipo.abbr}
            </span>
            <div className="flex items-center gap-2">
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-bold"
                style={{ background: `${tipo.color}22`, color: tipo.color }}
              >
                #{ticket.id}
              </span>
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-semibold"
                style={{ background: `${tipo.color}15`, color: tipo.color }}
              >
                {tipo.label}
              </span>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-semibold"
                style={{ background: estado.bg, color: estado.color }}
              >
                {estado.label}
              </span>
              <span
                className="px-2.5 py-1 rounded-lg text-xs font-semibold"
                style={{ background: prioridad.bg, color: prioridad.color }}
              >
                {prioridad.label}
              </span>
              <button
                onClick={() => setFlujoModalOpen(true)}
                className="px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors"
                style={{ background: '#EFF6FF', color: '#2563EB', border: '1px solid #BFDBFE' }}
                title="Ver flujo del proceso"
              >
                Ver Flujo
              </button>
            </div>
          </div>

          <div className="pl-11">
            <p className="font-bold text-sm mb-0.5" style={{ color: '#111827' }}>{sanitize(ticket.titular_nombre)}</p>
            <p className="text-xs" style={{ color: '#6B7280' }}>
              {sanitize(ticket.titular_rut) || 'Sin RUT'}
              {ticket.titular_email && ` · ${sanitize(ticket.titular_email)}`}
            </p>
            {ticket.representante_nombre && (
              <p className="text-xs mt-0.5" style={{ color: '#7C3AED' }}>
                Representado por: {sanitize(ticket.representante_nombre)}
                {ticket.representante_rut && ` (${sanitize(ticket.representante_rut)})`}
              </p>
            )}
            {ticket.tracking_token && (
              <p className="text-xs mt-0.5 font-mono" style={{ color: '#9CA3AF' }}>
                Tracking: {ticket.tracking_token}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl p-3" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-medium mb-1" style={{ color: '#6B7280' }}>Fecha recepción</p>
            <p className="text-sm font-semibold" style={{ color: '#111827' }}>{fmtDate(ticket.fecha_recepcion ?? undefined)}</p>
          </div>
          <div
            className="rounded-xl p-3"
            style={{ background: sla.bg, border: `1px solid ${sla.color}55` }}
          >
            <p className="text-xs font-medium mb-1" style={{ color: sla.color }}>Vencimiento SLA</p>
            <p className="text-sm font-bold" style={{ color: sla.color }}>
              {ticket.fecha_vencimiento ? fmtDate(ticket.fecha_vencimiento) : '—'}
              <span className="ml-1.5 text-xs font-medium">({sla.text})</span>
            </p>
          </div>
        </div>

        {ticket.descripcion && (
          <div className="rounded-lg p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Descripción</p>
            <p className="text-sm" style={{ color: '#6B7280' }}>{sanitize(ticket.descripcion)}</p>
          </div>
        )}

        {ticket.subsanacion_detalle && (
          <div className="rounded-lg p-4" style={{ background: '#FFFBEB', border: '1px solid #FDE68A' }}>
            <p className="text-xs font-semibold mb-1" style={{ color: '#92400E' }}>Subsanación solicitada</p>
            <p className="text-sm" style={{ color: '#78350F' }}>{sanitize(ticket.subsanacion_detalle)}</p>
            {ticket.subsanacion_fecha_pedido && (
              <p className="text-xs mt-1" style={{ color: '#B45309' }}>
                Pedida el: {fmtDate(ticket.subsanacion_fecha_pedido)}
              </p>
            )}
          </div>
        )}

        {ticket.prorroga_fecha && (
          <div className="rounded-lg p-4" style={{ background: '#F5F3FF', border: '1px solid #C4B5FD' }}>
            <p className="text-xs font-semibold mb-1" style={{ color: '#5B21B6' }}>Prórroga aplicada (Art. 12 bis)</p>
            <p className="text-sm" style={{ color: '#6D28D9' }}>
              +{ticket.prorroga_dias ?? 10} días hábiles desde el {fmtDate(ticket.prorroga_fecha)}
            </p>
          </div>
        )}

        {/* Campos nuevos gaps Ley 21.719 (Iter 10) */}
        {(ticket.metodo_verificacion_identidad || ticket.evidencia_identidad || ticket.evidencia_respuesta_hash || ticket.causal_rechazo || ticket.medio_respuesta) && (
          <div className="rounded-lg p-4" style={{ background: '#F0F9FF', border: '1px solid #BAE6FD' }}>
            <p className="text-xs font-semibold mb-2" style={{ color: '#0369A1' }}>📋 Compliance · Ley 21.719</p>
            <div className="space-y-2">
              {ticket.metodo_verificacion_identidad && (
                <div className="flex items-start gap-2">
                  <span className="text-xs font-medium w-36 flex-shrink-0" style={{ color: '#6B7280' }}>Método verificación:</span>
                  <span className="text-xs" style={{ color: '#111827' }}>{ticket.metodo_verificacion_identidad}</span>
                </div>
              )}
              {ticket.evidencia_identidad && (
                <div className="flex items-start gap-2">
                  <span className="text-xs font-medium w-36 flex-shrink-0" style={{ color: '#6B7280' }}>Evidencia identidad:</span>
                  <span className="text-xs" style={{ color: '#111827' }}>{ticket.evidencia_identidad}</span>
                </div>
              )}
              {ticket.evidencia_respuesta_hash && (
                <div className="flex items-start gap-2">
                  <span className="text-xs font-medium w-36 flex-shrink-0" style={{ color: '#6B7280' }}>Hash respuesta:</span>
                  <span className="text-xs font-mono" style={{ color: '#111827' }}>{ticket.evidencia_respuesta_hash}</span>
                </div>
              )}
              {ticket.causal_rechazo && (
                <div className="flex items-start gap-2">
                  <span className="text-xs font-medium w-36 flex-shrink-0" style={{ color: '#6B7280' }}>Causal rechazo:</span>
                  <span className="text-xs" style={{ color: '#DC2626' }}>{ticket.causal_rechazo}</span>
                </div>
              )}
              {ticket.medio_respuesta && (
                <div className="flex items-start gap-2">
                  <span className="text-xs font-medium w-36 flex-shrink-0" style={{ color: '#6B7280' }}>Medio respuesta:</span>
                  <span className="text-xs" style={{ color: '#111827' }}>{ticket.medio_respuesta}</span>
                </div>
              )}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Respuesta formal</p>
          {isAdmin ? (
            <div className="space-y-2">
              <select
                value={nuevoEstado}
                onChange={e => setNuevoEstado(e.target.value)}
                className="w-full px-3 py-2 rounded-lg text-sm border"
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
              >
                <option value="abierto">Abierto</option>
                <option value="en_proceso">En Proceso</option>
                <option value="pendiente">Pendiente</option>
                <option value="resuelto">Resuelto</option>
                <option value="bloqueado">Bloqueado</option>
                <option value="rechazado">Rechazado</option>
                <option value="subsanacion">Subsanación</option>
                <option value="prorroga">Prórroga</option>
              </select>
              <textarea
                value={respuesta}
                onChange={e => setRespuesta(e.target.value)}
                rows={3}
                placeholder="Escribe la respuesta formal para el titular..."
                className="w-full px-3 py-2 rounded-lg text-sm border"
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
              />
              <button
                onClick={handleGuardarRespuesta}
                disabled={guardando}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {guardando ? 'Guardando...' : 'Guardar respuesta'}
              </button>
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#6B7280' }}>
              {respuesta || 'Sin respuesta aún'}
            </p>
          )}
        </div>

        {(ticket.tipo === 'bloqueo' || ticket.tipo === 'portabilidad') && isAdmin && (
          <div className="rounded-xl p-4 space-y-3" style={{ background: '#F0FDF4', border: '1px solid #86EFAC' }}>
            <p className="text-xs font-semibold" style={{ color: '#166534' }}>
              {ticket.tipo === 'bloqueo' ? 'Acciones de Bloqueo Temporal (Art. 8 ter)' : 'Acciones de Portabilidad (Art. 9)'}
            </p>

            {ticket.tipo === 'bloqueo' && (
              <div className="space-y-2">
                <p className="text-xs" style={{ color: '#166534' }}>
                  Seleccioná el RAT asociado y el plazo de bloqueo en días.
                </p>
                <div className="flex gap-2">
                  <select
                    value={selectedRatId ?? ''}
                    onChange={e => setSelectedRatId(e.target.value ? Number(e.target.value) : null)}
                    className="flex-1 px-3 py-2 rounded-lg text-sm border"
                    style={{ borderColor: '#86EFAC' }}
                  >
                    <option value="">Seleccioná un RAT</option>
                    {rats.map(r => (
                      <option key={r.id} value={r.id}>{r.nombre_proceso}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min={1}
                    max={365}
                    value={plazoDias}
                    onChange={e => setPlazoDias(Number(e.target.value))}
                    className="w-20 px-3 py-2 rounded-lg text-sm border"
                    style={{ borderColor: '#86EFAC' }}
                    placeholder="Días"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleBloquear}
                    disabled={!selectedRatId || accionLoading}
                    className="flex-1 px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                    style={{ background: '#DC2626' }}
                  >
                    {accionLoading ? 'Bloqueando...' : 'Bloquear RAT'}
                  </button>
                  <button
                    onClick={handleDesbloquear}
                    disabled={accionLoading}
                    className="flex-1 px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                    style={{ background: '#059669' }}
                  >
                    {accionLoading ? 'Desbloqueando...' : 'Desbloquear'}
                  </button>
                </div>
              </div>
            )}

            {ticket.tipo === 'portabilidad' && (
              <div className="space-y-2">
                <p className="text-xs" style={{ color: '#166534' }}>
                  Exportá los datos del titular en formato JSON estructurado.
                </p>
                <button
                  onClick={handleExportarPortabilidad}
                  disabled={accionLoading}
                  className="w-full px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                  style={{ background: '#059669' }}
                >
                  {accionLoading ? 'Exportando...' : 'Exportar Portabilidad (JSON)'}
                </button>
              </div>
            )}
          </div>
        )}

        {isAdmin && ticket.estado !== 'resuelto' && ticket.estado !== 'rechazado' && (
          <div className="rounded-xl p-4 space-y-3" style={{ background: '#FFFBEB', border: '1px solid #FDE68A' }}>
            <p className="text-xs font-semibold" style={{ color: '#92400E' }}>Subsanación (Art. 12)</p>
            {ticket.estado === 'subsanacion' ? (
              <div className="space-y-2">
                <p className="text-xs" style={{ color: '#92400E' }}>
                  El titular fue notificado para completar información faltante.
                  Una vez que subsane, hacé clic en completar.
                </p>
                <button
                  onClick={handleCompletarSubsanacion}
                  disabled={accionLoading}
                  className="w-full px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                  style={{ background: '#059669' }}
                >
                  {accionLoading ? 'Procesando...' : 'Completar Subsanación'}
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {mostrarSubsanacion ? (
                  <>
                    <textarea
                      value={subsanacionDetalle}
                      onChange={e => setSubsanacionDetalle(e.target.value)}
                      rows={3}
                      placeholder="Detallá qué información falta para procesar la solicitud..."
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: '#FDE68A' }}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => setMostrarSubsanacion(false)}
                        className="flex-1 px-4 py-2 rounded-lg text-sm font-medium border"
                        style={{ borderColor: '#FDE68A', color: '#92400E' }}
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleSolicitarSubsanacion}
                        disabled={accionLoading || !subsanacionDetalle.trim()}
                        className="flex-1 px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                        style={{ background: '#D97706' }}
                      >
                        {accionLoading ? 'Enviando...' : 'Enviar Solicitud'}
                      </button>
                    </div>
                  </>
                ) : (
                  <button
                    onClick={() => setMostrarSubsanacion(true)}
                    disabled={accionLoading}
                    className="w-full px-4 py-2 rounded-lg text-sm font-semibold border disabled:opacity-60"
                    style={{ borderColor: '#FDE68A', color: '#92400E' }}
                  >
                    Solicitar Subsanación
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {isAdmin && ticket.estado !== 'resuelto' && ticket.estado !== 'rechazado' && !ticket.prorroga_fecha && (
          <div className="rounded-xl p-4 space-y-3" style={{ background: '#F5F3FF', border: '1px solid #C4B5FD' }}>
            <p className="text-xs font-semibold" style={{ color: '#5B21B6' }}>Prórroga (Art. 12 bis — máximo 10 días)</p>
            {mostrarProrroga ? (
              <>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="text-xs block mb-1" style={{ color: '#5B21B6' }}>Días adicionales</label>
                    <input
                      type="number"
                      min={1}
                      max={10}
                      value={prorrogaDias}
                      onChange={e => setProrrogaDias(Number(e.target.value))}
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: '#C4B5FD' }}
                    />
                  </div>
                  <div className="flex-[3]">
                    <label className="text-xs block mb-1" style={{ color: '#5B21B6' }}>Motivo (opcional)</label>
                    <input
                      type="text"
                      value={prorrogaMotivo}
                      onChange={e => setProrrogaMotivo(e.target.value)}
                      placeholder="Complejidad del caso..."
                      className="w-full px-3 py-2 rounded-lg text-sm border"
                      style={{ borderColor: '#C4B5FD' }}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setMostrarProrroga(false)}
                    className="flex-1 px-4 py-2 rounded-lg text-sm font-medium border"
                    style={{ borderColor: '#C4B5FD', color: '#5B21B6' }}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleProrrogar}
                    disabled={accionLoading}
                    className="flex-1 px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
                    style={{ background: '#7C3AED' }}
                  >
                    {accionLoading ? 'Aplicando...' : `Aplicar +${prorrogaDias} días`}
                  </button>
                </div>
              </>
            ) : (
              <button
                onClick={() => setMostrarProrroga(true)}
                disabled={accionLoading}
                className="w-full px-4 py-2 rounded-lg text-sm font-semibold border disabled:opacity-60"
                style={{ borderColor: '#C4B5FD', color: '#5B21B6' }}
              >
                Aplicar Prórroga (+10 días hábiles)
              </button>
            )}
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold" style={{ color: '#374151' }}>Notas internas</p>
            {notas.length > 0 && (
              <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#6B7280' }}>
                {notas.length}
              </span>
            )}
          </div>
          {loadingNotas ? (
            <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : notas.length === 0 ? (
            <p className="text-xs" style={{ color: '#D1D5DB' }}>Sin notas internas</p>
          ) : (
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {notas.map(n => (
                <div key={n.id} className="rounded-lg p-3 text-sm" style={{ background: '#FEF3C7', border: '1px solid #FDE68A' }}>
                  <p style={{ color: '#374151' }}>{sanitize(n.nota)}</p>
                  <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>{fmtDateTime(n.created_at)}</p>
                </div>
              ))}
            </div>
          )}
          {isAdmin && (
            <div className="mt-2 flex gap-2">
              <input
                type="text"
                value={nuevaNota}
                onChange={e => setNuevaNota(e.target.value)}
                placeholder="Agregar nota interna..."
                className="flex-1 px-3 py-2 rounded-lg text-sm border"
                style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
                onKeyDown={e => { if (e.key === 'Enter') handleAgregarNota(); }}
              />
              <button
                onClick={handleAgregarNota}
                disabled={guardandoNota || !nuevaNota.trim()}
                className="px-3 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-60"
                style={{ background: '#D97706' }}
              >
                +
              </button>
            </div>
          )}
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold" style={{ color: '#374151' }}>Historial</p>
            {historial.length > 0 && (
              <span className="text-xs px-2 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#6B7280' }}>
                {historial.length}
              </span>
            )}
          </div>
          {loadingHistorial ? (
            <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : historial.length === 0 ? (
            <p className="text-xs" style={{ color: '#D1D5DB' }}>Sin cambios registrados</p>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {historial.map(h => (
                <div key={h.id} className="flex items-start gap-2">
                  <div
                    className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                    style={{ background: TKT_ESTADO_MAP[h.estado_nuevo]?.color ?? '#6B7280' }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-medium" style={{ color: '#374151' }}>
                        {h.estado_anterior ? `${TKT_ESTADO_MAP[h.estado_anterior]?.label ?? h.estado_anterior} → ${TKT_ESTADO_MAP[h.estado_nuevo]?.label ?? h.estado_nuevo}` : h.estado_nuevo}
                      </span>
                      <span className="text-xs" style={{ color: '#9CA3AF' }}>{fmtDateTime(h.created_at)}</span>
                    </div>
                    {h.descripcion && (
                      <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{sanitize(h.descripcion)}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <FlujoModal
        open={flujoModalOpen}
        onClose={() => setFlujoModalOpen(false)}
        tipo={ticket.tipo as any}
        estadoActual={ticket.estado as any}
        trackingToken={ticket.tracking_token}
      />
    </Drawer>
  );
}
