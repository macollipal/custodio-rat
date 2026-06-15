'use client';

import { useReducer, useEffect } from 'react';
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
type LocalAction = { type: 'RESET' } | { type: 'SET_CONFIRM_DEL'; value: boolean } | { type: 'SET_APPROVING'; value: boolean };

function localReducer(_: LocalState, action: LocalAction): LocalState {
  switch (action.type) {
    case 'RESET': return { confirmDel: false, approving: false };
    case 'SET_CONFIRM_DEL': return { ..._, confirmDel: action.value };
    case 'SET_APPROVING': return { ..._, approving: action.value };
  }
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

  const fieldRows: [string, string | null | undefined][] = [
    ['Categoría titulares', rat.categoria_titulares],
    ['Fuente de datos', rat.fuente_datos],
    ['Finalidad', rat.finalidad],
    ['Plazo retención', rat.plazo_retencion],
    ['Medidas de seguridad', rat.medidas_seguridad],
    ['Destinatarios', rat.destinatarios],
    rat.datos_sensibles ? ['Tipo dato sensible', rat.tipo_dato_sensible || 'No especificado'] : null,
    rat.transferencia_internacional ? ['País destino', rat.pais_destino || '—'] : null,
    rat.transferencia_internacional ? ['Garantías transferencia', rat.garantias_transferencia_int || '⚠️ No especificadas'] : null,
    rat.observaciones_auditoria ? ['Obs. auditoría', rat.observaciones_auditoria] : null,
    rat.base_legal && rat.base_legal !== 'Otra' ? [
      'Doc. base legal',
      rat.tiene_archivo_base_legal ? '📄 Documento adjunto' : '⚠️ Sin documento',
    ] : null,
  ].filter(Boolean) as [string, string | null | undefined][];

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        {rat.datos_sensibles && (
          <span className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: '#FEF3C7', color: '#92400E' }}>
            ⚠️ Datos sensibles
          </span>
        )}
        {rat.evaluacion_impacto && (
          <span className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: '#DBEAFE', color: '#1E3A8A' }}>
            📋 EIPD requerida
          </span>
        )}
        {rat.transferencia_internacional && (
          <span className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: '#F3E8FF', color: '#5B21B6' }}>
            🌐 Transfer. internacional
          </span>
        )}
        {rat.decisiones_automatizadas && (
          <span className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: '#F3F4F6', color: '#374151' }}>
            🤖 Dec. automatizadas
          </span>
        )}
        {necesitaRevision(rat) && (
          <span className="px-2 py-1 rounded-full text-xs font-semibold" style={{ background: '#FEF3C7', color: '#92400E' }}>
            ⏰ Sin actualizar +6m
          </span>
        )}
        {rat.nivel_riesgo === 'Crítico' && (
          <span className="px-2 py-1 rounded-full text-xs font-bold" style={{ background: '#FEE2E2', color: '#DC2626' }}>
            ⚠️ Crítico
          </span>
        )}
      </div>

      <div className="space-y-2">
        {fieldRows.map(([k, v]) => (
          <div key={k} className="bg-white rounded-lg p-3" style={{ border: '1px solid #E5E7EB' }}>
            <span className="text-xs font-semibold block mb-0.5" style={{ color: '#9CA3AF' }}>{k}</span>
            <span
              className="text-sm break-words"
              style={{ color: v && (v as string).startsWith('⚠️') ? '#DC2626' : '#111827' }}
            >
              {(v as string) || '—'}
            </span>
          </div>
        ))}
      </div>

      {rat.base_legal && rat.base_legal !== 'Otra' && rat.tiene_archivo_base_legal && (
        <PdfPreview ratId={rat.id} filename={rat.archivo_base_legal_nombre} />
      )}

      <div className="flex gap-2 flex-wrap items-center pt-2">
        {puedeEditar ? (
          <>
            {rat.estado !== 'aprobado' ? (
              <button
                onClick={handleApprove}
                disabled={approving}
                className="px-4 py-2 rounded-lg text-xs font-semibold text-white transition disabled:opacity-60"
                style={{ background: '#059669' }}
              >
                {approving ? 'Aprobando...' : '✓ Aprobar RAT'}
              </button>
            ) : (
              <div
                className="px-3 py-1.5 rounded-lg text-xs font-medium"
                style={{ background: '#DCFCE7', color: '#166534' }}
              >
                ✓ Aprobado
                {rat.aprobado_por ? ` por ${rat.aprobado_por}` : ''}
                {rat.fecha_aprobacion ? ` el ${new Date(rat.fecha_aprobacion).toLocaleDateString('es-CL')}` : ''}
              </div>
            )}
            <button
              onClick={onEdit}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-white transition"
              style={{ background: '#2563EB' }}
            >
              ✏ Editar
            </button>
            <button
              onClick={() => onDuplicate(rat)}
              className="px-4 py-2 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
              style={{ color: '#374151', borderColor: '#E5E7EB' }}
            >
              📋 Duplicar
            </button>
            <button
              onClick={() => dispatch({ type: 'SET_CONFIRM_DEL', value: true })}
              className="px-4 py-2 rounded-lg text-xs font-semibold border transition hover:bg-red-50"
              style={{ color: '#DC2626', borderColor: '#FCA5A5' }}
            >
              🗑 Eliminar
            </button>
          </>
        ) : (
          <span className="text-xs px-3 py-1.5 rounded-lg" style={{ background: '#F3F4F6', color: '#6B7280' }}>
            Solo lectura
          </span>
        )}
      </div>

      {confirmDel && (
        <div className="rounded-lg p-3" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
          <p className="text-sm font-medium mb-2" style={{ color: '#7F1D1D' }}>
            ¿Eliminar <strong>{rat.nombre_proceso}</strong>? Irreversible.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => { onDelete(rat.id); dispatch({ type: 'SET_CONFIRM_DEL', value: false }); }}
              className="px-3 py-1 rounded text-xs font-semibold text-white"
              style={{ background: '#DC2626' }}
            >
              Confirmar
            </button>
            <button
              onClick={() => dispatch({ type: 'SET_CONFIRM_DEL', value: false })}
              className="px-3 py-1 rounded text-xs font-semibold border"
              style={{ borderColor: '#E5E7EB', color: '#374151' }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {auditLogs && auditLogs.length > 0 && (
        <div className="pt-1">
          <p className="text-xs font-semibold mb-2" style={{ color: '#374151' }}>
            Historial ({auditLogs.length})
          </p>
          <div className="space-y-1">
            {auditLogs.slice(0, 4).map((log, li) => (
              <div key={li} className="text-xs" style={{ color: '#9CA3AF' }}>
                <span className="font-bold" style={{ color: '#2563EB' }}>
                  {log.accion?.toUpperCase()}
                </span>
                {' · '}{log.usuario}{' · '}{log.timestamp?.slice(0, 16).replace('T', ' ')}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
