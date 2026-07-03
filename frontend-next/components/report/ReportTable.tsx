import React from 'react';
import Badge from '@/components/ui/Badge';
import CompletitudBar from '@/components/ui/CompletitudBar';
import type { RAT } from '@/types';

interface ReportTableProps {
  rats: RAT[];
  columns: string[];
  groupBy: string;
  onRowClick: (rat: RAT) => void;
}

function renderCell(rat: RAT, col: string): React.ReactNode {
  switch (col) {
    case 'nombre_proceso': return <><span className="font-semibold" style={{ color: '#111827' }}>{rat.nombre_proceso}</span><br /><span className="text-xs" style={{ color: '#9CA3AF' }}>ID #{rat.id} · {rat.categoria_titulares || '—'}</span></>;
    case 'categoria_datos': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.categoria_datos ?? '—').slice(0, 35)}</span>;
    case 'base_legal': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.base_legal ?? '—').slice(0, 30)}</span>;
    case 'estado': return <Badge estado={rat.estado} />;
    case 'created_by': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.created_by ?? '—'}</span>;
    case 'completitud': return <div className="w-24"><CompletitudBar pct={rat.completitud ?? 0} /></div>;
    case 'flags': return <div className="flex gap-1 flex-wrap">{rat.datos_sensibles && <span title="Datos sensibles" className="text-sm">⚠️</span>}{rat.evaluacion_impacto && <span title="EIPD" className="text-sm">📋</span>}{rat.transferencia_internacional && <span title="Transf. internacional" className="text-sm">🌐</span>}{rat.decisiones_automatizadas && <span title="Dec. automatizadas" className="text-sm">🤖</span>}</div>;
    case 'categoria_titulares': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.categoria_titulares || '—'}</span>;
    case 'fuente_datos': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.fuente_datos ?? '—').slice(0, 25)}</span>;
    case 'finalidad': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.finalidad ?? '—').slice(0, 40)}</span>;
    case 'plazo_retencion': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.plazo_retencion || '—'}</span>;
    case 'medidas_seguridad': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.medidas_seguridad ?? '—').slice(0, 30)}</span>;
    case 'destinatarios': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.destinatarios ?? '—').slice(0, 25)}</span>;
    case 'transferencia_datos': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.transferencia_datos ?? '—').slice(0, 25)}</span>;
    case 'pais_destino': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.pais_destino || '—'}</span>;
    case 'nivel_riesgo': {
      const isCritico = rat.nivel_riesgo === 'Crítico';
      return (
        <div className="flex items-center gap-1">
          {isCritico && (
            <span className="relative flex h-2 w-2" title="Riesgo crítico — acción requerida">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: '#DC2626' }} />
              <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: '#DC2626' }} />
            </span>
          )}
          <span className="text-xs font-medium" style={{ color: isCritico || rat.nivel_riesgo === 'Alto' ? '#DC2626' : '#374151' }}>{rat.nivel_riesgo || '—'}</span>
        </div>
      );
    }
    case 'datos_nna': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.datos_nna || '—'}</span>;
    case 'transferencia_nacional': return rat.transferencia_nacional ? <span className="text-xs" style={{ color: '#059669' }}>Sí</span> : <span className="text-xs" style={{ color: '#9CA3AF' }}>No</span>;
    case 'datos_anonimizados': return rat.datos_anonimizados ? <span className="text-xs" style={{ color: '#059669' }}>Sí</span> : <span className="text-xs" style={{ color: '#9CA3AF' }}>No</span>;
    case 'datos_seudonimizados': return rat.datos_seudonimizados ? <span className="text-xs" style={{ color: '#059669' }}>Sí</span> : <span className="text-xs" style={{ color: '#9CA3AF' }}>No</span>;
    case 'nivel_confidencialidad': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.nivel_confidencialidad || '—'}</span>;
    case 'estructura_dato': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.estructura_dato || '—'}</span>;
    case 'ciclo_procesamiento': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.ciclo_procesamiento || '—'}</span>;
    case 'automatizacion': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.automatizacion || '—'}</span>;
    case 'frecuencia': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.frecuencia || '—'}</span>;
    case 'sistema_almacenamiento': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.sistema_almacenamiento ?? '—').slice(0, 25)}</span>;
    case 'volumen_titulares_estimado': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.volumen_titulares_estimado ?? '—'}</span>;
    case 'responsable_tratamiento_email': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.responsable_tratamiento_email || '—'}</span>;
    case 'logica_automatizada': return <span className="text-xs" style={{ color: '#6B7280' }}>{(rat.logica_automatizada ?? '—').slice(0, 30)}</span>;
    case 'tiene_archivo_base_legal': return rat.tiene_archivo_base_legal ? <span className="text-xs" style={{ color: '#059669' }}>Sí</span> : <span className="text-xs" style={{ color: '#DC2626' }}>No</span>;
    case 'aprobado_por': return <span className="text-xs" style={{ color: '#6B7280' }}>{rat.aprobado_por || '—'}</span>;
    default: return null;
  }
}

function GroupedRows({ rats: ratList, columns, groupBy, onRowClick }: ReportTableProps) {
  if (groupBy === 'none') {
    return (
      <tbody>
        {ratList.map((rat) => (
          <tr key={rat.id} className="cursor-pointer transition-colors hover:bg-blue-50/40" onClick={() => onRowClick(rat)}>
            {columns.map(col => <td key={col} className="px-4 py-3 text-sm border-b" style={{ borderColor: '#F3F4F6' }}>{renderCell(rat, col)}</td>)}
          </tr>
        ))}
      </tbody>
    );
  }
  const groups: Record<string, RAT[]> = {};
  ratList.forEach(r => {
    const key = groupBy === 'estado' ? r.estado : groupBy === 'base_legal' ? (r.base_legal ?? 'Sin base legal') : (r.nivel_riesgo ?? 'Sin riesgo');
    if (!groups[key]) groups[key] = [];
    groups[key].push(r);
  });
  return (
    <tbody>
      {Object.entries(groups).map(([groupKey, groupRats]) => (
        <React.Fragment key={groupKey}>
          <tr style={{ background: '#F9FAFB' }}>
            <td colSpan={columns.length} className="px-4 py-2 text-xs font-bold uppercase tracking-wide" style={{ color: '#374151', borderBottom: '1px solid #E5E7EB', textAlign: 'left' }}>
              {groupBy === 'estado' ? groupKey.replace('_', ' ') : groupKey} ({groupRats.length})
            </td>
          </tr>
          {groupRats.map((rat) => (
            <tr key={rat.id} className="cursor-pointer transition-colors hover:bg-blue-50/40" onClick={() => onRowClick(rat)}>
              {columns.map(col => <td key={col} className="px-4 py-3 text-sm border-b" style={{ borderColor: '#F3F4F6' }}>{renderCell(rat, col)}</td>)}
            </tr>
          ))}
        </React.Fragment>
      ))}
    </tbody>
  );
}

export function ReportTable({ rats, columns, groupBy, onRowClick }: ReportTableProps) {
  return (
    <GroupedRows rats={rats} columns={columns} groupBy={groupBy} onRowClick={onRowClick} />
  );
}
