'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import {
  listarTktTickets,
  getTktDashboard,
  getTktTicket,
  descargarTktCsv,
  descargarTktExcel,
  descargarTktPdf,
  type TktTicket,
  type TktDashboard,
} from '@/lib/api';
import { CreateTicketForm } from '@/components/tkt/CreateTicketForm';
import { TicketDrawer } from '@/components/tkt/TicketDrawer';
import { Button } from '@/components/ui/Button';

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
  bloqueado: { label: 'Bloqueado', color: '#DC2626', bg: '#FEE2E2' },
  rechazado: { label: 'Rechazado', color: '#991B1B', bg: '#FEE2E2' },
  subsanacion: { label: 'Subsanación', color: '#D97706', bg: '#FEF3C7' },
  prorroga: { label: 'Prórroga', color: '#7C3AED', bg: '#EDE9FE' },
};

const TABS = ['abierto', 'en_proceso', 'pendiente', 'bloqueado', 'subsanacion', 'prorroga', 'resuelto', 'rechazado', 'vencido', 'todos'] as const;
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

function sanitize(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#039;');
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
  const [exportOpen, setExportOpen] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);

  const isAdmin = user?.rol_global === 'superadmin' || user?.rol_global === 'admin_empresa';

  const slaAlertTickets = useMemo(() =>
    tickets.filter(t => {
      if (t.estado === 'resuelto' || t.estado === 'rechazado') return false;
      const dias = t.dias_restantes ?? 999;
      return dias <= 2;
    }),
    [tickets]
  );

  async function handleExport(format: 'csv' | 'excel' | 'pdf') {
    if (!company?.id) return;
    setExporting(format);
    try {
      if (format === 'csv') await descargarTktCsv(company.id, { estado: tab === 'todos' ? undefined : tab === 'vencido' ? undefined : tab });
      else if (format === 'excel') await descargarTktExcel(company.id, { estado: tab === 'todos' ? undefined : tab === 'vencido' ? undefined : tab });
      else await descargarTktPdf(company.id, { estado: tab === 'todos' ? undefined : tab === 'vencido' ? undefined : tab });
      toast.success(`Exportación ${format.toUpperCase()} iniciada`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : `Error al exportar ${format.toUpperCase()}`);
    } finally {
      setExporting(null);
      setExportOpen(false);
    }
  }

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

  const filteredTickets = [...tickets]
    .sort((a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime())
    .filter(t => {
      if (tab === 'todos') return true;
      if (tab === 'vencido') {
        return t.estado !== 'resuelto' && (t.dias_restantes ?? 0) < 0;
      }
      return t.estado === tab;
    });

  return (
    <div className="p-4 sm:p-6 space-y-6">
      {slaAlertTickets.length > 0 && (
        <div
          className="rounded-xl p-4 flex items-center gap-3"
          style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}
          role="alert"
          aria-label={`Alerta: ${slaAlertTickets.length} solicitudes próximo a vencer`}
        >
          <span className="text-xl">⚠️</span>
          <div className="flex-1">
            <p className="text-sm font-semibold" style={{ color: '#991B1B' }}>
              {slaAlertTickets.length} solicitud(es) ARCOP+ con SLA próximo a vencer
            </p>
            <p className="text-xs" style={{ color: '#B91C1C' }}>
              {slaAlertTickets.filter(t => (t.dias_restantes ?? 999) <= 0).length} vencido(s) ·
              {slaAlertTickets.filter(t => (t.dias_restantes ?? 999) > 0 && (t.dias_restantes ?? 999) <= 2).length} vence(n) en 2 días o menos
            </p>
          </div>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setTab('abierto')}
          >
            Ver tickets
          </Button>
        </div>
      )}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Solicitudes ARCOP+</h1>
        <div className="flex items-center gap-2">
          {isAdmin && (
            <Button
              size="md"
              onClick={() => setCreateOpen(true)}
            >
              + Nueva Solicitud
            </Button>
          )}
          <div className="relative">
            <Button
              variant="secondary"
              size="md"
              onClick={() => setExportOpen(o => !o)}
              disabled={exporting !== null}
            >
              {exporting ? `⏳ Exportando ${exporting.toUpperCase()}...` : '⬇ Exportar'}
            </Button>
            {exportOpen && (
              <div
                className="absolute right-0 top-full mt-1 w-40 rounded-lg shadow-lg z-50 border"
                style={{ background: 'white', borderColor: '#E5E7EB' }}
              >
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport('csv')}
                  disabled={!!exporting}
                  className="!min-h-0 w-full justify-start"
                >
                  📄 CSV
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport('excel')}
                  disabled={!!exporting}
                  className="!min-h-0 w-full justify-start"
                >
                  📊 Excel (.xlsx)
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport('pdf')}
                  disabled={!!exporting}
                  className="!min-h-0 w-full justify-start"
                >
                  📑 PDF
                </Button>
              </div>
            )}
          </div>
          <Button
            variant="secondary"
            size="md"
            onClick={fetchData}
          >
            🔄 Refrescar
          </Button>
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
          {/* Panel de estadísticas unificado */}
          <div className="bg-white rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
            {/* Fila superior: total + SLA + alerta vencidos */}
            <div className="px-5 py-4 flex flex-wrap items-center gap-4 border-b" style={{ borderColor: '#F3F4F6' }}>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold" style={{ color: '#111827' }}>{dashboard.total}</span>
                <span className="text-sm font-medium" style={{ color: '#6B7280' }}>solicitudes totales</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 rounded-full" style={{ background: '#E5E7EB' }}>
                  <div
                    className="h-1.5 rounded-full transition-all"
                    style={{
                      width: `${Math.min(100, dashboard.cumplimiento_sla ?? 0)}%`,
                      background: (dashboard.cumplimiento_sla ?? 0) >= 80 ? '#059669' : (dashboard.cumplimiento_sla ?? 0) >= 50 ? '#D97706' : '#DC2626',
                    }}
                  />
                </div>
                <span className="text-xs font-semibold" style={{
                  color: (dashboard.cumplimiento_sla ?? 0) >= 80 ? '#059669' : (dashboard.cumplimiento_sla ?? 0) >= 50 ? '#D97706' : '#DC2626',
                }}>
                  SLA {dashboard.cumplimiento_sla ?? 0}%
                </span>
              </div>
              {dashboard.vencidos > 0 && (
                <button
                  onClick={() => setTab('vencido')}
                  className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:opacity-80 transition"
                  style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}
                >
                  <span>⚠️</span>
                  <span className="text-sm font-semibold" style={{ color: '#DC2626' }}>
                    {dashboard.vencidos} vencida{dashboard.vencidos !== 1 ? 's' : ''}
                  </span>
                </button>
              )}
            </div>
            {/* Tira de estados — clickeable para filtrar */}
            <div className="overflow-x-auto">
              <div className="flex divide-x divide-gray-100 min-w-max">
                {([
                  { key: 'abierto'     as TabType, label: 'Abiertos',    value: dashboard.abiertos,         color: '#2563EB' },
                  { key: 'en_proceso'  as TabType, label: 'En proceso',  value: dashboard.en_proceso,        color: '#7C3AED' },
                  { key: 'pendiente'   as TabType, label: 'Pendientes',  value: dashboard.pendientes,        color: '#D97706' },
                  { key: 'bloqueado'   as TabType, label: 'Bloqueados',  value: dashboard.bloqueados ?? 0,   color: '#DC2626' },
                  { key: 'subsanacion' as TabType, label: 'Subsanación', value: dashboard.subsanacion ?? 0,  color: '#D97706' },
                  { key: 'prorroga'    as TabType, label: 'Prórroga',    value: dashboard.prorrogas ?? 0,    color: '#7C3AED' },
                  { key: 'resuelto'    as TabType, label: 'Resueltos',   value: dashboard.resueltos,         color: '#059669' },
                  { key: 'rechazado'   as TabType, label: 'Rechazados',  value: dashboard.rechazados ?? 0,   color: '#991B1B' },
                  { key: 'vencido'     as TabType, label: 'Vencidos',    value: dashboard.vencidos,          color: '#DC2626' },
                ] as const).map(({ key, label, value, color }) => (
                  <button
                    key={key}
                    onClick={() => setTab(key)}
                    className="flex-1 px-5 py-4 text-center hover:bg-gray-50 transition min-w-[90px]"
                    style={{ borderBottom: tab === key ? `2px solid ${color}` : '2px solid transparent' }}
                  >
                    <p className="text-2xl font-bold" style={{ color: value > 0 ? color : '#E5E7EB' }}>
                      {value}
                    </p>
                    <p className="text-xs mt-0.5 whitespace-nowrap" style={{ color: value > 0 ? '#6B7280' : '#D1D5DB' }}>
                      {label}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </div>
          {dashboard.por_tipo && Object.keys(dashboard.por_tipo).length > 0 && (
            <div className="bg-white rounded-xl p-5" style={{ border: '1px solid #E5E7EB' }}>
              <p className="text-xs font-semibold uppercase tracking-wide mb-3" style={{ color: '#6B7280' }}>
                Derechos más ejercidos (Art. 12 Ley 21.719)
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {Object.entries(dashboard.por_tipo)
                  .sort(([, a], [, b]) => b - a)
                  .map(([tipo, count]) => (
                    <div
                      key={tipo}
                      className="rounded-lg p-3"
                      style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}
                    >
                      <p className="text-xs font-medium capitalize" style={{ color: '#1E3A8A' }}>
                        {tipo.replace(/_/g, ' ')}
                      </p>
                      <p className="text-2xl font-bold mt-1" style={{ color: '#1E3A8A' }}>
                        {count}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          )}
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
            {tab === 'todos' ? 'No hay solicitudes ARCOP+ registradas' : `No hay tickets en estado "${tab}"`}
          </p>
          {isAdmin && (
            <Button
              className="mt-4"
              onClick={() => setCreateOpen(true)}
            >
              + Nueva Solicitud
            </Button>
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
                  <th className="py-2.5 px-2 text-left text-xs font-semibold hidden md:table-cell" style={{ color: '#6B7280' }}>Descripción</th>
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
                        <p className="text-xs truncate" style={{ color: '#6B7280' }}>{sanitize(ticket.titular_email)}</p>
                        {ticket.tracking_token && (
                          <p className="text-xs font-mono mt-0.5 truncate" style={{ color: '#9CA3AF' }} title={ticket.tracking_token}>
                            #{ticket.tracking_token.slice(0, 8)}...
                          </p>
                        )}
                      </td>
                      <td className="py-2.5 px-2 hidden md:table-cell">
                        <p className="text-xs line-clamp-2" style={{ color: '#374151' }} title={ticket.descripcion || ''}>
                          {sanitize(ticket.descripcion) || '—'}
                        </p>
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
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={e => { e.stopPropagation(); handleVerTicket(ticket); }}
                        >
                          Ver
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {drawerOpen && ticketDetail && (
        <TicketDrawer
          ticket={ticketDetail}
          open={drawerOpen}
          onClose={() => { setDrawerOpen(false); fetchData(); }}
          isAdmin={isAdmin}
          companyId={company?.id ?? 0}
        />
      )}

      {createOpen && (
        <CreateTicketForm
          open={createOpen}
          onClose={() => setCreateOpen(false)}
          onSuccess={() => { setCreateOpen(false); fetchData(); }}
          companyId={company?.id ?? 0}
          isAdmin={isAdmin}
        />
      )}
    </div>
  );
}
