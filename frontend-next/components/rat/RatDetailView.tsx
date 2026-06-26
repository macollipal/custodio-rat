'use client';

import { useReducer, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import PdfPreview from './PdfPreview';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import Spinner from '@/components/ui/Spinner';
import Tooltip from '@/components/ui/Tooltip';
import { DIAS_REVISION } from '@/lib/constants';
import type { RAT } from '@/types';

interface AuditLog { accion: string; usuario: string; timestamp: string; }

interface RatDetailViewProps {
  rat: RAT;
  puedeEditar: boolean;
  onEdit: () => void;
  onDuplicate: (rat: RAT) => void;
  onDelete: (id: number) => void;
  onRefresh: () => void;
  auditLogs?: AuditLog[];
}

function necesitaRevision(rat: RAT) {
  return (Date.now() - new Date(rat.updated_at).getTime()) / 86_400_000 > DIAS_REVISION;
}

type LocalState = { confirmDel: boolean; approving: boolean };
type LocalAction =
  | { type: 'RESET' }
  | { type: 'SET_CONFIRM_DEL'; value: boolean }
  | { type: 'SET_APPROVING'; value: boolean };

function localReducer(_: LocalState, action: LocalAction): LocalState {
  switch (action.type) {
    case 'RESET': return { confirmDel: false, approving: false };
    case 'SET_CONFIRM_DEL': return { ..._, confirmDel: action.value };
    case 'SET_APPROVING': return { ..._, approving: action.value };
  }
}

interface FieldRowProps {
  label: string;
  value: string | null | undefined;
  warning?: boolean;
  /** Marca el campo como crítico pendiente si está vacío */
  criticalIfEmpty?: boolean;
}
function FieldRow({ label, value, warning, criticalIfEmpty }: FieldRowProps) {
  const isEmpty = !value || value === '—' || value === '';
  const isWarning = warning || (typeof value === 'string' && value.startsWith('⚠️'));
  const isCriticalEmpty = isEmpty && criticalIfEmpty;
  let display = value;
  let bgColor = 'transparent';
  let valueColor = isWarning ? '#DC2626' : '#111827';

  if (isCriticalEmpty) {
    display = '⚠️ Pendiente';
    valueColor = '#DC2626';
    bgColor = '#FEF2F2';
  } else if (isEmpty) {
    display = '—';
    valueColor = '#9CA3AF';
  }

  return (
    <div
      className="flex items-start gap-3 px-4 py-2.5"
      style={{ borderBottom: '1px solid #F3F4F6', backgroundColor: bgColor }}
    >
      <span className="text-xs font-medium w-40 flex-shrink-0 pt-0.5" style={{ color: '#6B7280' }}>{label}</span>
      <span
        className="text-sm flex-1 break-words font-medium"
        style={{ color: valueColor }}
      >
        {display}
      </span>
    </div>
  );
}

/** Section que solo se muestra si tiene al menos un FieldRow visible */
interface SectionProps { title: string; children: React.ReactNode; isEmpty?: boolean }
function Section({ title, children, isEmpty }: SectionProps) {
  if (isEmpty) return null;
  return (
    <div className="mb-5">
      <p className="text-xs font-bold mb-2 px-1" style={{ color: '#2563EB', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {title}
      </p>
      <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
        {children}
      </div>
    </div>
  );
}

const BADGE_STYLES = {
  warning: { bg: '#FEF3C7', color: '#92400E' },
  info: { bg: '#DBEAFE', color: '#1E40AF' },
  purple: { bg: '#F3E8FF', color: '#5B21B6' },
  gray: { bg: '#F3F4F6', color: '#374151' },
  danger: { bg: '#FEE2E2', color: '#DC2626' },
};

interface BadgeProps { variant: keyof typeof BADGE_STYLES; children: React.ReactNode }
function Badge({ variant, children }: BadgeProps) {
  const s = BADGE_STYLES[variant];
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold" style={{ background: s.bg, color: s.color }}>
      {children}
    </span>
  );
}

const ESTADO_BADGE: Record<string, { bg: string; color: string; icon: string; label: string }> = {
  borrador:    { bg: '#F3F4F6', color: '#374151', icon: '📝', label: 'Borrador' },
  completo:    { bg: '#DBEAFE', color: '#1E40AF', icon: '✓',  label: 'Completo' },
  en_revision: { bg: '#FEF3C7', color: '#92400E', icon: '⏳', label: 'En revisión' },
  aprobado:     { bg: '#DCFCE7', color: '#166534', icon: '✓',  label: 'Aprobado' },
};

const RIESGO_BADGE: Record<string, { bg: string; color: string; icon: string }> = {
  Bajo:    { bg: '#DCFCE7', color: '#166534', icon: '🟢' },
  Medio:   { bg: '#FEF3C7', color: '#92400E', icon: '🟡' },
  Alto:    { bg: '#FEE2E2', color: '#991B1B', icon: '🟠' },
  'Crítico': { bg: '#FEE2E2', color: '#7F1D1D', icon: '🔴' },
};

function EstadoBadge({ estado }: { estado: RAT['estado'] }) {
  const s = ESTADO_BADGE[estado] ?? ESTADO_BADGE.borrador;
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: s.bg, color: s.color }}>
      <span aria-hidden="true">{s.icon}</span>
      {s.label}
    </span>
  );
}

function RiesgoBadge({ nivel }: { nivel?: string }) {
  if (!nivel) return null;
  const s = RIESGO_BADGE[nivel];
  if (!s) return null;
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: s.bg, color: s.color }}>
      <span aria-hidden="true">{s.icon}</span>
      Riesgo {nivel}
    </span>
  );
}

function fmtDate(d: string | null | undefined): string {
  if (!d) return '—';
  const date = new Date(d);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('es-CL', { dateStyle: 'short' });
}

function SectionWithTooltip({ title, tooltipText, children }: { title: string; tooltipText: string; children: React.ReactNode }) {
  return (
    <div className="mb-5">
      <div className="flex items-center gap-2 mb-2 px-1">
        <p className="text-xs font-bold" style={{ color: '#2563EB', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {title}
        </p>
        <Tooltip text={tooltipText} />
      </div>
      <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
        {children}
      </div>
    </div>
  );
}

function CompletitudBar({ completitud }: { completitud: number }) {
  const pct = Math.round(completitud || 0);
  const color = pct >= 75 ? '#059669' : pct >= 50 ? '#D97706' : '#DC2626';
  const bgSoft = pct >= 75 ? '#DCFCE7' : pct >= 50 ? '#FEF3C7' : '#FEE2E2';
  const label = pct >= 75 ? '✓ Completo' : pct >= 50 ? '⚠️ Avanzado' : '🚧 En progreso';
  return (
    <div className="rounded-xl p-3 mb-4 flex items-center gap-3" style={{ background: bgSoft, border: `1px solid ${color}33` }}>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-semibold" style={{ color }}>{label}</span>
          <span className="text-xs font-bold" style={{ color }}>{pct}%</span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: '#FFFFFF' }}>
          <div className="h-1.5 rounded-full transition-all" style={{ width: `${Math.min(pct, 100)}%`, background: color }} />
        </div>
      </div>
    </div>
  );
}

function fmtDateTime(d: string | null | undefined): string {
  if (!d) return '—';
  const date = new Date(d);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
}

export default function RatDetailView({
  rat,
  puedeEditar,
  onEdit,
  onDuplicate,
  onDelete,
  onRefresh,
  auditLogs,
}: RatDetailViewProps) {
  const [{ confirmDel, approving }, dispatch] = useReducer(localReducer, { confirmDel: false, approving: false });
  const router = useRouter();

  useEffect(() => { dispatch({ type: 'RESET' }); }, [rat.id]);

  async function handleApprove() {
    dispatch({ type: 'SET_APPROVING', value: true });
    try {
      await api.aprobarRat(rat.id);
      toast.success(`RAT "${rat.nombre_proceso}" aprobado correctamente · ID #${rat.id}`);
      onRefresh();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Error al aprobar.');
    } finally {
      dispatch({ type: 'SET_APPROVING', value: false });
    }
  }

  const primaryBadges: React.ReactNode[] = [];
  const secondaryBadges: React.ReactNode[] = [];

  if (rat.datos_sensibles) primaryBadges.push(<Badge key="sensible" variant="warning">⚠️ Datos sensibles</Badge>);
  if (rat.evaluacion_impacto) primaryBadges.push(<Badge key="eipd" variant="info">📋 EIPD {rat.estado_eipd && rat.estado_eipd !== 'no_requerida' ? `· ${rat.estado_eipd}` : ''}</Badge>);
  if (rat.transferencia_internacional) primaryBadges.push(<Badge key="trans" variant="purple">🌐 Transfer. internacional</Badge>);
  if (rat.decisiones_automatizadas) secondaryBadges.push(<Badge key="auto" variant="gray">🤖 Dec. automatizadas</Badge>);
  if (necesitaRevision(rat)) secondaryBadges.push(<Badge key="rev" variant="warning">⏰ Sin actualizar +6m</Badge>);
  if (rat.nivel_riesgo === 'Crítico') secondaryBadges.push(<Badge key="crit" variant="danger">⚠️ Crítico</Badge>);

  const allBadges = [...primaryBadges, ...secondaryBadges];

  return (
    <div className="space-y-1">
      {allBadges.length > 0 && (
        <div className="flex gap-2 flex-wrap mb-3">
          {primaryBadges}
          {secondaryBadges.length > 0 && (
            <details className="inline-block">
              <summary className="text-xs cursor-pointer px-2 py-1 rounded-full font-medium" style={{ background: '#F3F4F6', color: '#6B7280' }}>
                +{secondaryBadges.length} más
              </summary>
              <div className="mt-1 flex gap-2 flex-wrap">{secondaryBadges}</div>
            </details>
          )}
        </div>
      )}

      {/* Indicador de completitud — semáforo */}
      <CompletitudBar completitud={rat.completitud} />

      <Section title="Resumen">
        <FieldRow label="Nombre del proceso" value={rat.nombre_proceso} />
        <div className="flex items-center gap-2 px-4 py-2.5" style={{ borderBottom: '1px solid #F3F4F6' }}>
          <span className="text-xs font-medium w-40 flex-shrink-0 pt-0.5" style={{ color: '#6B7280' }}>Estado</span>
          <EstadoBadge estado={rat.estado} />
          {rat.nivel_riesgo && (
            <span className="ml-2"><RiesgoBadge nivel={rat.nivel_riesgo} /></span>
          )}
        </div>
        <FieldRow label="Creado por" value={rat.created_by} />
        <FieldRow label="Fecha de creación" value={fmtDateTime(rat.created_at)} />
        <FieldRow label="Actualizado por" value={rat.updated_by} />
        <FieldRow label="Última actualización" value={fmtDateTime(rat.updated_at)} />
        {rat.estado === 'aprobado' && (
          <>
            <FieldRow label="Aprobado por" value={rat.aprobado_por} />
            <FieldRow label="Fecha de aprobación" value={fmtDateTime(rat.fecha_aprobacion)} />
          </>
        )}
      </Section>

      <Section title="Identificación">
        <FieldRow label="Nombre del proceso" value={rat.nombre_proceso} />
        <FieldRow label="Categoría titulares" value={rat.categoria_titulares} criticalIfEmpty />
        <FieldRow label="Fuente de datos" value={rat.fuente_datos} criticalIfEmpty />
        <FieldRow label="Destinatarios" value={rat.destinatarios} />
        <FieldRow label="Encargado tratamiento" value={rat.nombre_encargado} />
        {rat.tiene_contrato_encargado !== undefined && (
          <FieldRow
            label="Contrato encargado"
            value={rat.tiene_contrato_encargado ? '✓ Contrato firmado' : '⚠️ Sin contrato'}
            warning={!rat.tiene_contrato_encargado}
          />
        )}
      </Section>

      <Section title="Datos tratados">
        <FieldRow label="Categoría datos" value={rat.categoria_datos} criticalIfEmpty />
        {rat.datos_sensibles && (
          <FieldRow
            label="Tipo dato sensible"
            value={rat.tipo_dato_sensible || '⚠️ No especificado'}
            warning={!rat.tipo_dato_sensible}
          />
        )}
        {(rat.evaluacion_impacto || (rat.estado_eipd && rat.estado_eipd !== 'no_requerida')) && (
          <>
            <FieldRow label="EIPD" value={rat.estado_eipd ? `• ${rat.estado_eipd.replace('_', ' ')}` : 'Pendiente'} />
            {rat.fecha_eipd && <FieldRow label="Fecha EIPD" value={fmtDate(rat.fecha_eipd)} />}
            {rat.estado_eipd !== 'completada' && puedeEditar && (
              <div className="px-4 py-2.5">
                <button
                  onClick={() => router.push(`/eipd?rat_id=${rat.id}`)}
                  className="text-xs px-3 py-1.5 rounded-lg font-semibold text-white"
                  style={{ background: '#7C3AED' }}
                >
                  📋 Solicitar EIPD
                </button>
              </div>
            )}
          </>
        )}
        {rat.decisiones_automatizadas && (
          <FieldRow label="Decisiones automatizadas" value="Sí — requiere supervisión" />
        )}
        {rat.logica_automatizada && (
          <FieldRow label="Lógica automatizada" value={rat.logica_automatizada} />
        )}
      </Section>

      <Section title="Base legal y finalidad">
        <FieldRow label="Base legal" value={rat.base_legal} criticalIfEmpty />
        <FieldRow label="Finalidad" value={rat.finalidad} criticalIfEmpty />
        {rat.base_legal === 'Interés legítimo' && (
          <FieldRow
            label="Test interés legítimo"
            value={rat.test_interes_legitimo || '⚠️ Test no documentado'}
            warning={!rat.test_interes_legitimo}
          />
        )}
        {rat.observaciones_auditoria && (
          <FieldRow label="Obs. auditoría" value={rat.observaciones_auditoria} />
        )}
      </Section>

      <Section title="Almacenamiento y transferencias">
        <FieldRow label="Plazo retención" value={rat.plazo_retencion} criticalIfEmpty />
        <FieldRow label="Medidas de seguridad" value={rat.medidas_seguridad} />
        <FieldRow label="Transferencia datos" value={rat.transferencia_datos} />
        {rat.volumen_titulares_estimado !== undefined && rat.volumen_titulares_estimado !== null && (
          <FieldRow label="Volumen titulares" value={rat.volumen_titulares_estimado.toLocaleString('es-CL')} />
        )}
        <FieldRow label="Transferencia nacional" value={rat.transferencia_nacional ? 'Sí — dentro del territorio chileno' : 'No'} />
        {rat.transferencia_internacional && (
          <>
            <FieldRow
              label="País destino"
              value={rat.pais_destino || '⚠️ No especificado'}
              warning={!rat.pais_destino}
            />
            <FieldRow
              label="Garantías"
              value={rat.garantias_transferencia_int || '⚠️ No especificadas'}
              warning={!rat.garantias_transferencia_int}
            />
          </>
        )}
      </Section>

      {/* Compliance (Iter 10) — siempre visible */}
      <Section title="Compliance · Ley 21.719">
        <FieldRow label="Sistema almacenamiento" value={rat.sistema_almacenamiento} />
        <FieldRow label="Volumen titulares" value={rat.volumen_titulares_estimado != null ? rat.volumen_titulares_estimado.toLocaleString('es-CL') : null} />
        <FieldRow label="Operaciones tratamiento" value={rat.operaciones_tratamiento && rat.operaciones_tratamiento.length > 0 ? rat.operaciones_tratamiento.join(', ') : null} />
        <FieldRow label="Responsable tratamiento" value={rat.responsable_tratamiento_email} />
        {rat.decisiones_automatizadas && (
          <FieldRow label="Lógica automatizada" value={rat.logica_automatizada} />
        )}
      </Section>

      {/* Tier 1 — siempre visible con tooltip */}
      <SectionWithTooltip
        title="Datos sensibles y clasificación"
        tooltipText="Datos NNA, clasificación de confidencialidad, estructura del dato, anonimización (AUDIT_LOG Iter 11, Tier 1)"
      >
        <FieldRow label="Tratamiento NNA" value={rat.datos_nna === 'ninguno' ? 'Sin datos de NNA' : rat.datos_nna === 'ninos' ? 'Niños (< 14 años)' : rat.datos_nna === 'adolescentes' ? 'Adolescentes (14-17 años)' : rat.datos_nna === 'ambos' ? 'Ambos' : null} />
        <FieldRow label="Nivel confidencialidad" value={rat.nivel_confidencialidad} />
        <FieldRow label="Estructura del dato" value={rat.estructura_dato} />
        <FieldRow
          label="Anonimización"
          value={
            rat.datos_anonimizados || rat.datos_seudonimizados
              ? [rat.datos_anonimizados ? 'Anonimizados' : '', rat.datos_seudonimizados ? 'Seudonimizados' : ''].filter(Boolean).join(', ')
              : null
          }
        />
      </SectionWithTooltip>

      {/* Tier 2 — siempre visible con tooltip */}
      <SectionWithTooltip
        title="Operativos y técnicos"
        tooltipText="Campos operativos del template ProBest (AUDIT_LOG Iter 11, Tier 2)"
      >
        <FieldRow label="Ciclo procesamiento" value={rat.ciclo_procesamiento} />
        <FieldRow label="Grado automatización" value={rat.automatizacion} />
        <FieldRow label="Frecuencia" value={rat.frecuencia} />
        <FieldRow label="Doc. cláusulas" value={rat.doc_clausulas} />
        <FieldRow label="Medidas organizativas" value={rat.medidas_organizativas} />
        <FieldRow label="Mecanismos eliminación" value={rat.mecanismos_eliminacion} />
        <FieldRow label="Técnica anonimización" value={rat.tecnica_anonimizacion} />
        <FieldRow label="Origen dato (portabilidad)" value={rat.origen_dato_portabilidad} />
        <FieldRow label="Fecha levantamiento" value={fmtDate(rat.fecha_levantamiento)} />
      </SectionWithTooltip>

      {/* Documento base legal — siempre visible */}
      {(rat.tiene_archivo_base_legal || rat.archivo_base_legal_nombre) && (
        <Section title="Documento base legal">
          <FieldRow label="Nombre archivo" value={rat.archivo_base_legal_nombre || 'Sin nombre'} />
          {rat.tiene_archivo_base_legal && (
            <div className="px-4 py-3">
              <PdfPreview ratId={rat.id} filename={rat.archivo_base_legal_nombre} />
            </div>
          )}
        </Section>
      )}

      <div className="border-t pt-4 mt-4" style={{ borderColor: '#E5E7EB' }}>
        <p className="text-xs font-semibold mb-3" style={{ color: '#6B7280' }}>Acciones</p>
        <div className="flex gap-2 flex-wrap items-center">
          {puedeEditar ? (
            <>
              {rat.estado !== 'aprobado' ? (
                <button
                  onClick={handleApprove}
                  disabled={approving}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-white transition disabled:opacity-50 inline-flex items-center justify-center gap-2"
                  style={{ background: '#059669' }}
                >
                  {approving ? (
                    <>
                      <Spinner size="sm" /> Aprobando…
                    </>
                  ) : (
                    '✓ Aprobar RAT'
                  )}
                </button>
              ) : (
                <div
                  className="px-3 py-1.5 rounded-xl text-xs font-medium"
                  style={{ background: '#DCFCE7', color: '#166534' }}
                >
                  ✓ Aprobado
                  {rat.aprobado_por ? ` por ${rat.aprobado_por}` : ''}
                  {rat.fecha_aprobacion ? ` el ${fmtDate(rat.fecha_aprobacion)}` : ''}
                </div>
              )}
              <button
                onClick={onEdit}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-white transition"
                style={{ background: '#2563EB' }}
              >
                ✏ Editar
              </button>
              <button
                onClick={() => onDuplicate(rat)}
                className="px-4 py-2 rounded-xl text-xs font-semibold border transition hover:bg-gray-50"
                style={{ color: '#374151', borderColor: '#E5E7EB' }}
              >
                📋 Duplicar
              </button>
              <button
                onClick={() => dispatch({ type: 'SET_CONFIRM_DEL', value: true })}
                className="px-4 py-2 rounded-xl text-xs font-semibold border transition hover:bg-red-50"
                style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
              >
                🗑 Eliminar
              </button>
            </>
          ) : (
            <span className="text-xs px-3 py-1.5 rounded-xl" style={{ background: '#F3F4F6', color: '#6B7280' }}>
              Solo lectura
            </span>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={confirmDel}
        onClose={() => dispatch({ type: 'SET_CONFIRM_DEL', value: false })}
        onConfirm={() => { onDelete(rat.id); dispatch({ type: 'SET_CONFIRM_DEL', value: false }); }}
        title={`Eliminar "${rat.nombre_proceso}"`}
        message="Esta acción es irreversible. Se eliminará el RAT, sus consentimientos asociados y todo el historial de auditoría."
        confirmText="Eliminar definitivamente"
        cancelText="Cancelar"
        variant="danger"
        requireTyping={rat.nombre_proceso}
      />

      {auditLogs && auditLogs.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2 px-1">
            <p className="text-xs font-bold" style={{ color: '#2563EB', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Historial de cambios
            </p>
            {auditLogs.length > 4 && (
              <span className="text-xs" style={{ color: '#9CA3AF' }}>
                {auditLogs.length} registros
              </span>
            )}
          </div>
          <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
            {auditLogs.slice(0, 6).map((log, li) => (
              <div key={li} className="flex items-start gap-3 px-4 py-2.5" style={{ borderBottom: li < Math.min(auditLogs.length, 6) - 1 ? '1px solid #F3F4F6' : 'none' }}>
                <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{ background: '#2563EB' }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold" style={{ color: '#1E40AF' }}>{log.accion}</span>
                    <span className="text-xs" style={{ color: '#6B7280' }}>por {log.usuario}</span>
                  </div>
                  <span className="text-xs" style={{ color: '#9CA3AF' }}>
                    {fmtDateTime(log.timestamp)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
