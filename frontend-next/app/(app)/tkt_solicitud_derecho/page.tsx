'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import {
  listarTktTickets,
  getTktDashboard,
  getTktTicket,
  actualizarTktTicket,
  agregarTktNota,
  listarTktNotas,
  listarTktHistorial,
  crearTktTicket,
  listarRats,
  bloquearSolicitud,
  desbloquearSolicitud,
  exportarPortabilidad,
  type TktTicket,
  type TktDashboard,
  type RAT,
} from '@/lib/api';
import Drawer from '@/components/ui/Drawer';

const TKT_TIPO_MAP: Record<string, { label: string; color: string; abbr: string }> = {
  acceso: { label: 'Acceso', color: '#2563EB', abbr: 'AC' },
  rectificacion: { label: 'Rectificación', color: '#7C3AED', abbr: 'RC' },
  cancelacion: { label: 'Cancelación', color: '#DC2626', abbr: 'CA' },
  oposicion: { label: 'Oposición', color: '#D97706', abbr: 'OP' },
  bloqueo: { label: 'Bloqueo temporal', color: '#DC2626', abbr: 'BL' },
  portabilidad: { label: 'Portabilidad', color: '#059669', abbr: 'PT' },
};

const TKT_PRIORIDAD_MAP: Record<string, { label: string; color: string; bg: string }> = {
  alta: { label: 'Alta', color: '#DC2626', bg: '#FEE2E2' },
  normal: { label: 'Normal', color: '#D97706', bg: '#FEF3C7' },
  baja: { label: 'Baja', color: '#6B7280', bg: '#F3F4F6' },
};

const TKT_ESTADO_MAP: Record<string, { label: string; color: string; bg: string }> = {
  abierto: { label: 'Abierto', color: '#2563EB', bg: '#DBEAFE' },
  en_proceso: { label: 'En Proceso', color: '#7C3AED', bg: '#EDE9FE' },
  pendiente: { label: 'Pendiente', color: '#D97706', bg: '#FEF3C7' },
  resuelto: { label: 'Resuelto', color: '#059669', bg: '#DCFCE7' },
};

const TABS = ['abierto', 'en_proceso', 'pendiente', 'resuelto', 'vencido', 'todos'] as const;
type TabType = typeof TABS[number];

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
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

interface KpiCardProps {
  label: string;
  value: number;
  color: string;
  icon: string;
}

function KpiCard({ label, value, color, icon }: KpiCardProps) {
  return (
    <div
      className="rounded-xl p-4 flex items-center gap-3"
      style={{ background: 'white', border: '1px solid #E5E7EB' }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
        style={{ background: `${color}15` }}
      >
        <span style={{ color }}>{icon}</span>
      </div>
      <div>
        <p className="text-xs font-medium" style={{ color: '#6B7280' }}>{label}</p>
        <p className="text-xl font-bold" style={{ color: '#111827' }}>{value}</p>
      </div>
    </div>
  );
}

interface SlaBarProps {
  cumplimiento: number;
}

function SlaBar({ cumplimiento }: SlaBarProps) {
  const color = cumplimiento >= 80 ? '#059669' : cumplimiento >= 50 ? '#D97706' : '#DC2626';
  return (
    <div className="rounded-xl p-4" style={{ background: 'white', border: '1px solid #E5E7EB' }}>
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-medium" style={{ color: '#6B7280' }}>Cumplimiento SLA</p>
        <p className="text-sm font-bold" style={{ color }}>{cumplimiento}%</p>
      </div>
      <div className="w-full h-2 rounded-full" style={{ background: '#E5E7EB' }}>
        <div
          className="h-2 rounded-full transition-all"
          style={{ width: `${cumplimiento}%`, background: color }}
        />
      </div>
    </div>
  );
}

interface CreateTicketFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  companyId: number;
  isAdmin: boolean;
}

function CreateTicketForm({ open, onClose, onSuccess, companyId, isAdmin }: CreateTicketFormProps) {
  const [tipo, setTipo] = useState('acceso');
  const [prioridad, setPrioridad] = useState('normal');
  const [origen, setOrigen] = useState('web');
  const [titularNombre, setTitularNombre] = useState('');
  const [titularEmail, setTitularEmail] = useState('');
  const [titularRut, setTitularRut] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    if (open) {
      setTipo('acceso');
      setPrioridad('normal');
      setOrigen('web');
      setTitularNombre('');
      setTitularEmail('');
      setTitularRut('');
      setDescripcion('');
    }
  }, [open]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!titularNombre.trim() || !titularEmail.trim()) {
      toast.error('Nombre y email del titular son obligatorios');
      return;
    }
    setGuardando(true);
    try {
      await crearTktTicket({
        company_id: companyId,
        tipo,
        prioridad,
        origen,
        titular_nombre: sanitize(titularNombre),
        titular_email: sanitize(titularEmail),
        titular_rut: titularRut ? sanitize(titularRut) : undefined,
        descripcion: descripcion ? sanitize(descripcion) : undefined,
      });
      toast.success('Solicitud creada');
      onSuccess();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al crear solicitud');
    } finally {
      setGuardando(false);
    }
  }

  if (!open) return null;

  return (
    <Drawer open={open} onClose={onClose} title="">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div
          className="rounded-xl p-4 flex items-center gap-3"
          style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}
        >
          <span
            className="inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold text-sm"
            style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
          >
            + NUEVA
          </span>
          <div>
            <p className="font-semibold text-white text-sm">Nueva Solicitud ARCO</p>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>Complete los datos del titular</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Tipo *</label>
            <select
              value={tipo}
              onChange={e => setTipo(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
            >
              <option value="acceso">Acceso</option>
              <option value="rectificacion">Rectificación</option>
              <option value="cancelacion">Cancelación</option>
              <option value="oposicion">Oposición</option>
              <option value="bloqueo">Bloqueo temporal</option>
              <option value="portabilidad">Portabilidad</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Prioridad</label>
            <select
              value={prioridad}
              onChange={e => setPrioridad(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
            >
              <option value="alta">Alta</option>
              <option value="normal">Normal</option>
              <option value="baja">Baja</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Origen</label>
          <select
            value={origen}
            onChange={e => setOrigen(e.target.value)}
            className="w-full px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#E5E7EB' }}
          >
            <option value="web">Web</option>
            <option value="email">Email</option>
            <option value="telefono">Teléfono</option>
            <option value="presencial">Presencial</option>
            <option value="manual">Manual</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Nombre del titular *</label>
          <input
            type="text"
            value={titularNombre}
            onChange={e => setTitularNombre(e.target.value)}
            className="w-full px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#E5E7EB' }}
            placeholder="Nombre completo"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Email del titular *</label>
          <input
            type="email"
            value={titularEmail}
            onChange={e => setTitularEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#E5E7EB' }}
            placeholder="email@ejemplo.cl"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>RUT del titular</label>
          <input
            type="text"
            value={titularRut}
            onChange={e => setTitularRut(e.target.value)}
            className="w-full px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#E5E7EB' }}
            placeholder="12.345.678-9"
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Descripción</label>
          <textarea
            value={descripcion}
            onChange={e => setDescripcion(e.target.value)}
            className="w-full px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#E5E7EB' }}
            rows={3}
            placeholder="Detalle de la solicitud..."
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={guardando}
            className="flex-1 px-4 py-2 rounded-lg text-sm font-medium text-white transition"
            style={{ background: '#2563EB' }}
          >
            {guardando ? 'Guardando...' : 'Crear Solicitud'}
          </button>
        </div>
      </form>
    </Drawer>
  );
}

interface TicketDrawerProps {
  ticket: TktTicket | null;
  open: boolean;
  onClose: () => void;
  isAdmin: boolean;
  companyId: number;
}

function TicketDrawer({ ticket, open, onClose, isAdmin, companyId }: TicketDrawerProps) {
  const [notas, setNotas] = useState<{ id: number; nota: string; user_id: number; created_at: string }[]>([]);
  const [historial, setHistorial] = useState<{ id: number; estado_anterior?: string; estado_nuevo: string; descripcion?: string; user_id: number; created_at: string }[]>([]);
  const [loading, setLoading] = useState(false);
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

  useEffect(() => {
    if (open && ticket) {
      setRespuesta(ticket.respuesta_texto ?? '');
      setNuevoEstado(ticket.estado);
      setNuevaNota('');
      setNotas([]);
      setHistorial([]);
      setSelectedRatId(null);
      setPlazoDias(30);
      if ((ticket.tipo === 'bloqueo' || ticket.tipo === 'portabilidad') && companyId) {
        listarRats(companyId).then(setRats).catch(() => setRats([]));
      }
    }
  }, [open, ticket, companyId]);

  const fetchNotas = useCallback(async () => {
    if (!ticket?.id) return;
    setLoadingNotas(true);
    try {
      const data = await listarTktNotas(ticket.id);
      setNotas(data);
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
      setHistorial(data);
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
  const prioridad = TKT_PRIORIDAD_MAP[ticket.prioridad] ?? { label: ticket.prioridad, color: '#6B7280', bg: '#F3F4F6' };
  const sla = getSlaColor(ticket.dias_restantes);

  return (
    <Drawer open={open} onClose={onClose} title="">
      <div className="space-y-5">
        <div
          className="rounded-xl p-4 flex items-center gap-3"
          style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}
        >
          <button
            onClick={onClose}
            className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg transition hover:bg-white/20"
            style={{ color: 'white' }}
            aria-label="Cerrar"
          >
            ←
          </button>
          <span
            className="inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold text-sm"
            style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
          >
            {tipo.abbr}
          </span>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-white text-sm truncate">{sanitize(ticket.titular_nombre)}</p>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>
              {sanitize(ticket.titular_rut) || 'Sin RUT'} · {sanitize(ticket.titular_email)}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span
              className="px-2 py-1 rounded-lg text-xs font-medium"
              style={{ background: estado.bg, color: estado.color }}
            >
              {estado.label}
            </span>
            <span
              className="px-2 py-1 rounded-lg text-xs font-medium"
              style={{ background: prioridad.bg, color: prioridad.color }}
            >
              {prioridad.label}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg p-3" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-medium mb-1" style={{ color: '#6B7280' }}>Fecha recepción</p>
            <p className="text-sm font-medium" style={{ color: '#111827' }}>{fmtDate(ticket.fecha_recepcion ?? undefined)}</p>
          </div>
          <div
            className="rounded-lg p-3"
            style={{ background: sla.bg, border: `1px solid ${sla.color}` }}
          >
            <p className="text-xs font-medium mb-1" style={{ color: sla.color }}>Vencimiento SLA</p>
            <p className="text-sm font-bold" style={{ color: sla.color }}>
              {ticket.fecha_vencimiento ? fmtDate(ticket.fecha_vencimiento) : '—'}
              <span className="ml-2 text-xs font-medium">({sla.text})</span>
            </p>
          </div>
        </div>

        {ticket.descripcion && (
          <div className="rounded-lg p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>Descripción</p>
            <p className="text-sm" style={{ color: '#6B7280' }}>{sanitize(ticket.descripcion)}</p>
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

        {/* B-01/B-04: Acciones especiales de Solicitud de Derecho */}
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
    </Drawer>
  );
}

export default function TktSolicitudDerechoPage() {
  const { user, company } = useApp();
  const [tab, setTab] = useState<TabType>('abierto');
  const [tickets, setTickets] = useState<TktTicket[]>([]);
  const [dashboard, setDashboard] = useState<TktDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState<TktTicket | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [ticketDetail, setTicketDetail] = useState<TktTicket | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  const isAdmin = user?.rol_global === 'superadmin' || user?.rol_global === 'admin_empresa';

  const ticketCounts = useMemo(() => {
    return tickets.reduce<Record<string, number>>((acc, t) => {
      acc[t.estado] = (acc[t.estado] ?? 0) + 1;
      return acc;
    }, {});
  }, [tickets]);

  const fetchData = useCallback(async () => {
    if (!company?.id) return;
    setLoading(true);
    try {
      const [tktData, dashData] = await Promise.all([
        listarTktTickets(company.id),
        getTktDashboard(company.id),
      ]);
      setTickets(tktData.tickets ?? []);
      setDashboard(dashData);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  }, [company?.id]);

  useEffect(() => {
    if (company?.id) {
      fetchData();
    }
  }, [company?.id, fetchData]);

  async function handleVerTicket(ticket: TktTicket) {
    setSelectedTicket(ticket);
    setDrawerOpen(true);
    setLoadingDetail(true);
    try {
      const detail = await getTktTicket(ticket.id);
      setTicketDetail(detail);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al cargar detalle');
      setTicketDetail(ticket);
    } finally {
      setLoadingDetail(false);
    }
  }

  const filteredTickets = tickets.filter(t => {
    if (tab === 'todos') return true;
    if (tab === 'vencido') {
      return t.estado !== 'resuelto' && (t.dias_restantes ?? 0) < 0;
    }
    return t.estado === tab;
  });

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Solicitudes ARCO</h1>
        <div className="flex items-center gap-2">
          {isAdmin && (
            <button
              onClick={() => setCreateOpen(true)}
              className="px-3 py-2 rounded-lg text-sm font-medium text-white transition"
              style={{ background: '#2563EB' }}
            >
              + Nueva Solicitud
            </button>
          )}
          <button
            onClick={fetchData}
            className="px-3 py-2 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            🔄 Refrescar
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="rounded-xl p-4 animate-pulse" style={{ background: '#E5E7EB', height: 80 }} />
          ))}
        </div>
      ) : dashboard ? (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <KpiCard label="Total" value={dashboard.total} color="#2563EB" icon="📋" />
            <KpiCard label="Abiertos" value={dashboard.abiertos} color="#2563EB" icon="📬" />
            <KpiCard label="En Proceso" value={dashboard.en_proceso} color="#7C3AED" icon="⚙️" />
            <KpiCard label="Pendientes" value={dashboard.pendientes} color="#D97706" icon="⏳" />
            <KpiCard label="Resueltos" value={dashboard.resueltos} color="#059669" icon="✅" />
            <KpiCard label="Vencidos" value={dashboard.vencidos} color="#DC2626" icon="⚠️" />
          </div>
          <SlaBar cumplimiento={dashboard.cumplimiento_sla} />
        </>
      ) : null}

      <div className="flex flex-wrap gap-1 border-b" style={{ borderColor: '#E5E7EB' }}>
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize"
            style={{
              borderColor: tab === t ? '#2563EB' : 'transparent',
              color: tab === t ? '#2563EB' : '#6B7280',
            }}
          >
            {t === 'todos' ? 'Todos' : t === 'en_proceso' ? 'En Proceso' : t.charAt(0).toUpperCase() + t.slice(1)}
            {t !== 'todos' && (ticketCounts[t] ?? 0) > 0 && (
              <span
                className="ml-2 px-1.5 py-0.5 rounded text-xs"
                style={{ background: '#E5E7EB', color: '#6B7280' }}
              >
                {ticketCounts[t]}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
          <div className="p-8 text-center" style={{ background: 'white' }}>
            <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
          </div>
        </div>
      ) : filteredTickets.length === 0 ? (
        <div className="rounded-xl text-center py-12" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
          <p className="text-4xl mb-2">📭</p>
          <p className="text-sm font-medium" style={{ color: '#374151' }}>No hay tickets</p>
          <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
            {tab === 'todos' ? 'No hay solicitudes ARCO registradas' : `No hay tickets en estado "${tab}"`}
          </p>
          {isAdmin && (
            <button
              onClick={() => setCreateOpen(true)}
              className="mt-4 px-4 py-2 rounded-lg text-sm font-medium text-white transition"
              style={{ background: '#2563EB' }}
            >
              + Nueva Solicitud
            </button>
          )}
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr style={{ background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                  <th className="py-2.5 pl-3 pr-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Tipo</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Titular</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold hidden md:table-cell" style={{ color: '#6B7280' }}>Email</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Prioridad</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold hidden lg:table-cell" style={{ color: '#6B7280' }}>Estado</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>SLA</th>
                  <th className="py-2.5 px-2 text-left text-xs font-semibold hidden sm:table-cell" style={{ color: '#6B7280' }}>Fecha</th>
                  <th className="py-2.5 pr-3 pl-2 text-left text-xs font-semibold" style={{ color: '#6B7280' }}>Acción</th>
                </tr>
              </thead>
              <tbody>
                {filteredTickets.map(ticket => {
                  const tipo = TKT_TIPO_MAP[ticket.tipo] ?? { label: ticket.tipo, color: '#6B7280', abbr: '??' };
                  const prioridad = TKT_PRIORIDAD_MAP[ticket.prioridad] ?? { label: ticket.prioridad, color: '#6B7280', bg: '#F3F4F6' };
                  const estado = TKT_ESTADO_MAP[ticket.estado] ?? { label: ticket.estado, color: '#6B7280', bg: '#F3F4F6' };
                  const sla = getSlaColor(ticket.dias_restantes);

                  return (
                    <tr
                      key={ticket.id}
                      className="border-b cursor-pointer hover:bg-gray-50 transition"
                      style={{ borderColor: '#F3F4F6' }}
                      onClick={() => handleVerTicket(ticket)}
                    >
                      <td className="py-2.5 pl-3 pr-2">
                        <span
                          className="inline-flex items-center justify-center w-8 h-8 rounded-lg font-bold text-xs"
                          style={{ background: `${tipo.color}15`, color: tipo.color }}
                        >
                          {tipo.abbr}
                        </span>
                      </td>
                      <td className="py-2.5 px-2">
                        <p className="text-xs font-medium" style={{ color: '#111827' }}>{sanitize(ticket.titular_nombre)}</p>
                        <p className="text-xs" style={{ color: '#9CA3AF' }}>{sanitize(ticket.titular_rut) || '—'}</p>
                      </td>
                      <td className="py-2.5 px-2 hidden md:table-cell">
                        <a
                          href={`mailto:${encodeURIComponent(ticket.titular_email)}`}
                          className="text-xs underline"
                          style={{ color: '#2563EB' }}
                          onClick={e => e.stopPropagation()}
                        >
                          {sanitize(ticket.titular_email)}
                        </a>
                      </td>
                      <td className="py-2.5 px-2">
                        <span
                          className="px-2 py-1 rounded text-xs font-medium"
                          style={{ background: prioridad.bg, color: prioridad.color }}
                        >
                          {prioridad.label}
                        </span>
                      </td>
                      <td className="py-2.5 px-2 hidden lg:table-cell">
                        <span
                          className="px-2 py-1 rounded text-xs font-medium"
                          style={{ background: estado.bg, color: estado.color }}
                        >
                          {estado.label}
                        </span>
                      </td>
                      <td className="py-2.5 px-2">
                        <span
                          className="px-2 py-1 rounded text-xs font-bold"
                          style={{ background: sla.bg, color: sla.color }}
                        >
                          {sla.text}
                        </span>
                      </td>
                      <td className="py-2.5 px-2 hidden sm:table-cell">
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>
                          {fmtDate(ticket.fecha_recepcion ?? undefined)}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3 pl-2">
                        <button
                          onClick={e => { e.stopPropagation(); handleVerTicket(ticket); }}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border transition hover:bg-gray-100"
                          style={{ borderColor: '#E5E7EB', color: '#374151' }}
                        >
                          Ver
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <TicketDrawer
        ticket={ticketDetail}
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); fetchData(); }}
        isAdmin={isAdmin}
        companyId={company?.id ?? 0}
      />

      <CreateTicketForm
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSuccess={() => { setCreateOpen(false); fetchData(); }}
        companyId={company?.id ?? 0}
        isAdmin={isAdmin}
      />
    </div>
  );
}
i m p o r t 
 
 t y p e 
 
 R A T 
 
 f r o m 
 
 @ / t y p e s 
 
 