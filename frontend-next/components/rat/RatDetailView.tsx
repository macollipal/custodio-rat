'use client';

import { useReducer, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import PdfPreview from './PdfPreview';
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

interface SectionProps { title: string; children: React.ReactNode }
function Section({ title, children }: SectionProps) {
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

interface FieldRowProps { label: string; value: string | null | undefined; warning?: boolean }
function FieldRow({ label, value, warning }: FieldRowProps) {
  const display = value || '—';
  const isWarning = warning || (typeof display === 'string' && display.startsWith('⚠️'));
  return (
    <div className="flex items-start gap-3 px-4 py-2.5" style={{ borderBottom: '1px solid #F3F4F6' }}>
      <span className="text-xs font-medium w-40 flex-shrink-0 pt-0.5" style={{ color: '#6B7280' }}>{label}</span>
      <span
        className="text-sm flex-1 break-words"
        style={{ color: isWarning ? '#DC2626' : '#111827' }}
      >
        {display}
      </span>
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

function fmtDate(d: string | null | undefined): string {
  if (!d) return '—';
  const date = new Date(d);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleDateString('es-CL', { dateStyle: 'short' });
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
      toast.success(`RAT "${rat.nombre_proceso}" aprobado correctamente.`);
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

      <Section title="Identificación">
        <FieldRow label="Categoría titulares" value={rat.categoria_titulares} />
        <FieldRow label="Fuente de datos" value={rat.fuente_datos} />
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
        <FieldRow label="Categoría datos" value={rat.categoria_datos} />
        {rat.datos_sensibles && (
          <FieldRow
            label="Tipo dato sensible"
            value={rat.tipo_dato_sensible || '⚠️ No especificado'}
            warning={!rat.tipo_dato_sensible}
          />
        )}
        {rat.evaluacion_impacto && (
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
        <FieldRow label="Base legal" value={rat.base_legal} />
        <FieldRow label="Finalidad" value={rat.finalidad} />
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
        <FieldRow label="Plazo retención" value={rat.plazo_retencion} />
        <FieldRow label="Medidas de seguridad" value={rat.medidas_seguridad} />
        <FieldRow label="Transferencia datos" value={rat.transferencia_datos} />
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

      {/* Campos nuevos gaps Ley 21.719 (Iter 10) */}
      {(rat.sistema_almacenamiento || rat.volumen_titulares_estimado || (rat.operaciones_tratamiento && rat.operaciones_tratamiento.length > 0) || rat.responsable_tratamiento_email || rat.datos_nna || rat.nivel_confidencialidad || rat.estructura_dato || rat.datos_anonimizados || rat.datos_seudonimizados || rat.ciclo_procesamiento || rat.automatizacion || rat.frecuencia || rat.transferencia_nacional || rat.doc_clausulas || rat.medidas_organizativas || rat.mecanismos_eliminacion || rat.tecnica_anonimizacion || rat.origen_dato_portabilidad || rat.fecha_levantamiento) && (
        <Section title="Compliance · Ley 21.719 (Tier 1 + Tier 2)">
          {rat.sistema_almacenamiento && (
            <FieldRow label="Sistema almacenamiento" value={rat.sistema_almacenamiento} />
          )}
          {rat.volumen_titulares_estimado !== undefined && rat.volumen_titulares_estimado !== null && (
            <FieldRow label="Volumen titulares" value={rat.volumen_titulares_estimado.toLocaleString('es-CL')} />
          )}
          {rat.operaciones_tratamiento && rat.operaciones_tratamiento.length > 0 && (
            <FieldRow label="Operaciones tratamiento" value={rat.operaciones_tratamiento.join(', ')} />
          )}
          {rat.responsable_tratamiento_email && (
            <FieldRow label="Responsable tratamiento" value={rat.responsable_tratamiento_email} />
          )}
          {/* Tier 1 */}
          {rat.datos_nna && (
            <FieldRow label="Tratamiento NNA" value={rat.datos_nna === 'ninguno' ? 'Sin datos de NNA' : rat.datos_nna === 'ninos' ? 'Ninos (< 14 anos)' : rat.datos_nna === 'adolescentes' ? 'Adolescentes (14-17 anos)' : 'Ambos'} />
          )}
          {rat.nivel_confidencialidad && (
            <FieldRow label="Nivel confidencialidad" value={rat.nivel_confidencialidad} />
          )}
          {rat.estructura_dato && (
            <FieldRow label="Estructura del dato" value={rat.estructura_dato} />
          )}
          {(rat.datos_anonimizados || rat.datos_seudonimizados) && (
            <FieldRow label="Anonimizacion" value={[rat.datos_anonimizados ? 'Anonimizados' : '', rat.datos_seudonimizados ? 'Seudonimizados' : ''].filter(Boolean).join(', ') || 'No'} />
          )}
          {/* Tier 2 */}
          {rat.ciclo_procesamiento && (
            <FieldRow label="Ciclo procesamiento" value={rat.ciclo_procesamiento} />
          )}
          {rat.automatizacion && (
            <FieldRow label="Grado automatizacion" value={rat.automatizacion} />
          )}
          {rat.frecuencia && (
            <FieldRow label="Frecuencia" value={rat.frecuencia} />
          )}
          {rat.transferencia_nacional && (
            <FieldRow label="Transferencia nacional" value="Si — dentro del territorio chileno" />
          )}
          {rat.doc_clausulas && (
            <FieldRow label="Doc. clausulas" value={rat.doc_clausulas} />
          )}
          {rat.medidas_organizativas && (
            <FieldRow label="Medidas organizativas" value={rat.medidas_organizativas} />
          )}
          {rat.mecanismos_eliminacion && (
            <FieldRow label="Mecanismos eliminacion" value={rat.mecanismos_eliminacion} />
          )}
          {rat.tecnica_anonimizacion && (
            <FieldRow label="Tecnica anonimizacion" value={rat.tecnica_anonimizacion} />
          )}
          {rat.origen_dato_portabilidad && (
            <FieldRow label="Origen dato (portabilidad)" value={rat.origen_dato_portabilidad} />
          )}
          {rat.fecha_levantamiento && (
            <FieldRow label="Fecha levantamiento" value={fmtDate(rat.fecha_levantamiento)} />
          )}
        </Section>
      )}

      {rat.base_legal && rat.base_legal !== 'Otra' && rat.tiene_archivo_base_legal && (
        <div className="mb-5">
          <p className="text-xs font-bold mb-2 px-1" style={{ color: '#2563EB', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Documento base legal
          </p>
          <PdfPreview ratId={rat.id} filename={rat.archivo_base_legal_nombre} />
        </div>
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
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-white transition disabled:opacity-50"
                  style={{ background: '#059669' }}
                >
                  {approving ? 'Aprobando...' : '✓ Aprobar RAT'}
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

      {confirmDel && (
        <div className="mt-3 rounded-xl p-4" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
          <p className="text-sm font-semibold mb-3" style={{ color: '#7F1D1D' }}>
            ¿Eliminar <strong>{rat.nombre_proceso}</strong>? Esta acción es irreversible.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => { onDelete(rat.id); dispatch({ type: 'SET_CONFIRM_DEL', value: false }); }}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white"
              style={{ background: '#DC2626' }}
            >
              Confirmar eliminación
            </button>
            <button
              onClick={() => dispatch({ type: 'SET_CONFIRM_DEL', value: false })}
              className="px-4 py-2 rounded-xl text-xs font-semibold border"
              style={{ borderColor: '#E5E7EB', color: '#374151' }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

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
