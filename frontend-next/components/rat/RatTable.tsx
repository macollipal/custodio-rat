'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import Badge from '@/components/ui/Badge';
import CompletitudBar from '@/components/ui/CompletitudBar';
import type { RAT, Company } from '@/types';
import { DIAS_REVISION, ESTADO_OPTIONS, RIESGO_OPTIONS, EIPD_OPTIONS } from '@/lib/constants';

function necesitaRevision(rat: RAT, now: number) {
  const dias = (now - new Date(rat.updated_at).getTime()) / 86_400_000;
  return dias > DIAS_REVISION;
}

interface RatTableProps {
  rats: RAT[];
  company: Company;
  onSelect: (rat: RAT) => void;
  onRefresh: () => void;
  puedeEditar?: boolean;
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const ESTADO_MAP: Record<string, string> = {
  'Borrador': 'borrador', 'Completo': 'completo', 'En revisión': 'en_revision', 'Aprobado': 'aprobado',
};

export default function RatTable({ rats, company, onSelect, onRefresh, puedeEditar = true }: RatTableProps) {
  const router = useRouter();
  const [filtroEstado, setFiltroEstado] = useState('Todos');
  const [filtroSensibles, setFiltroSensibles] = useState('Todos');
  const [filtroRiesgo, setFiltroRiesgo] = useState('Todos');
  const [filtroEIPD, setFiltroEIPD] = useState('Todos');
  const [buscar, setBuscar] = useState('');
  const [filteredRats, setFilteredRats] = useState<RAT[] | null>(null);
  const [filtersActive, setFiltersActive] = useState(false);
  const [exporting, setExporting] = useState<'csv' | 'pdf' | null>(null);
  const [duplicating, setDuplicating] = useState<number | null>(null);
  const now = Date.now();

  async function aplicarFiltros() {
    const estadoMap: Record<string, string> = { Todos: '', Borrador: 'borrador', Completo: 'completo', 'En revisión': 'en_revision', Aprobado: 'aprobado' };
    const riesgoMap: Record<string, string> = { Todos: '', Bajo: 'Bajo', Medio: 'Medio', Alto: 'Alto', 'Crítico': 'Crítico' };
    const eipdMap: Record<string, boolean | undefined> = { Todos: undefined, Requerida: true, 'No requerida': false };

    try {
      const result = await api.getReportes({
        company_id: company.id,
        estado: estadoMap[filtroEstado] || undefined,
        datos_sensibles: filtroSensibles === 'Solo con datos sensibles' ? true : undefined,
        evaluacion_impacto: eipdMap[filtroEIPD],
      });
      let filtered = result.rats;
      if (filtroRiesgo !== 'Todos') {
        filtered = filtered.filter(r => r.nivel_riesgo === riesgoMap[filtroRiesgo]);
      }
      setFilteredRats(filtered);
      setFiltersActive(true);
    } catch {}
  }

  function limpiarFiltros() {
    setFilteredRats(null);
    setFiltersActive(false);
    setFiltroEstado('Todos');
    setFiltroRiesgo('Todos');
    setFiltroEIPD('Todos');
    setFiltroSensibles('Todos');
    setBuscar('');
  }

  const displayRats = [...(filtersActive && filteredRats ? filteredRats : rats)]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const filtrados = displayRats.filter(r => {
    if (filtroEstado !== 'Todos' && r.estado !== ESTADO_MAP[filtroEstado]) return false;
    if (filtroSensibles === 'Solo con datos sensibles' && !r.datos_sensibles) return false;
    if (buscar.trim()) {
      const q = buscar.toLowerCase();
      return r.nombre_proceso.toLowerCase().includes(q) || (r.categoria_datos ?? '').toLowerCase().includes(q);
    }
    return true;
  });

  async function handleDuplicate(rat: RAT) {
    setDuplicating(rat.id);
    try {
      await api.duplicarRat(rat);
      toast.success(`"${rat.nombre_proceso}" duplicado correctamente.`);
      onRefresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al duplicar.');
    } finally {
      setDuplicating(null);
    }
  }

  async function exportCsv() {
    setExporting('csv');
    try {
      const blob = await api.exportarCsv(company.id);
      downloadBlob(blob, `RAT_${company.rut}.csv`);
    } catch { toast.error('Error al exportar CSV.'); }
    finally { setExporting(null); }
  }

  async function exportPdf() {
    setExporting('pdf');
    try {
      const blob = await api.exportarPdf(company.id);
      downloadBlob(blob, `RAT_${company.rut}.pdf`);
    } catch { toast.error('Error al exportar PDF.'); }
    finally { setExporting(null); }
  }

  const selectCls = 'px-3 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition';
  const selectStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', color: '#374151' };

  return (
    <div className="space-y-4">
      <details className="rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
        <summary className="px-4 py-2.5 text-sm font-medium cursor-pointer" style={{ color: '#374151' }}>Filtrar</summary>
        <div className="px-4 pb-4 flex gap-3 flex-wrap items-end">
          <div className="flex flex-col gap-1">
            <label className="text-xs" style={{ color: '#6B7280' }}>Estado</label>
            <select value={filtroEstado} onChange={e => setFiltroEstado(e.target.value)} className={selectCls} style={selectStyle}>
              {['Todos', ...ESTADO_OPTIONS].map(o => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs" style={{ color: '#6B7280' }}>Riesgo</label>
            <select value={filtroRiesgo} onChange={e => setFiltroRiesgo(e.target.value)} className={selectCls} style={selectStyle}>
              {['Todos', ...RIESGO_OPTIONS].map(o => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs" style={{ color: '#6B7280' }}>EIPD</label>
            <select value={filtroEIPD} onChange={e => setFiltroEIPD(e.target.value)} className={selectCls} style={selectStyle}>
              {['Todos', ...EIPD_OPTIONS].map(o => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2 pb-1">
            <input type="checkbox" id="filtroSensibles" checked={filtroSensibles === 'Solo con datos sensibles'} onChange={e => setFiltroSensibles(e.target.checked ? 'Solo con datos sensibles' : 'Todos')} className="w-4 h-4 rounded" />
            <label htmlFor="filtroSensibles" className="text-xs" style={{ color: '#6B7280' }}>Solo con datos sensibles</label>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs" htmlFor="rat-buscar" style={{ color: '#6B7280' }}>Buscar</label>
            <input id="rat-buscar" type="text" value={buscar} onChange={e => setBuscar(e.target.value)} placeholder="Buscar proceso..." aria-label="Buscar procesos RAT" className="px-3.5 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition" style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', minWidth: 180 }} />
          </div>
          <div className="flex gap-2 pb-1">
            <button onClick={aplicarFiltros} aria-label="Aplicar filtros de busqueda" className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition" style={{ background: '#2563EB' }}>Aplicar</button>
            {filtersActive && <button onClick={limpiarFiltros} aria-label="Limpiar filtros aplicados" className="px-4 py-2 rounded-lg text-sm font-semibold border transition" style={{ borderColor: '#E5E7EB', color: '#374151' }}>Limpiar</button>}
          </div>
        </div>
      </details>

      <p className="text-xs" style={{ color: '#9CA3AF' }}>
        {filtrados.length < rats.length ? `Mostrando ${filtrados.length} de ${rats.length} procesos` : `${rats.length} proceso${rats.length !== 1 ? 's' : ''} registrado${rats.length !== 1 ? 's' : ''}`}
      </p>

      {filtrados.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl" style={{ border: '1px solid #E5E7EB' }}>
          <div className="text-5xl mb-4">📋</div>
          <p className="text-base font-semibold mb-1" style={{ color: '#111827' }}>
            {rats.length === 0 ? 'Aún no tienes procesos RAT' : 'Sin resultados para los filtros'}
          </p>
          <p className="text-sm mb-6" style={{ color: '#6B7280' }}>
            {rats.length === 0
              ? 'Crea tu primer proceso de tratamiento de datos personales conforme a la Ley 21.719'
              : 'Intenta ajustar los filtros de búsqueda'}
          </p>
          {rats.length === 0 && puedeEditar && (
            <button
              onClick={() => router.push('/rat')}
              className="px-6 py-3 rounded-xl text-sm font-semibold text-white transition hover:opacity-90"
              style={{ background: '#2563EB' }}
            >
              + Crear mi primer proceso RAT
            </button>
          )}
          {rats.length === 0 && !puedeEditar && (
            <p className="text-xs" style={{ color: '#9CA3AF' }}>Contacta al administrador para crear procesos RAT.</p>
          )}
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden overflow-x-auto" style={{ border: '1px solid #E5E7EB' }}>
          <div className="grid text-xs font-semibold uppercase tracking-wide px-5 py-3 whitespace-nowrap" style={{ gridTemplateColumns: '3fr 2fr 1.5fr 1fr 120px 80px', color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
            <span>Proceso</span><span>Categoría de datos</span><span>Base legal</span><span>Estado</span><span>Completitud</span><span>Riesgo</span>
          </div>
          {filtrados.map((rat, i) => (
            <div key={rat.id}>
              <button
                onClick={() => onSelect(rat)}
                className="hidden sm:grid items-center px-5 py-3.5 cursor-pointer transition-colors text-left w-full"
                style={{ gridTemplateColumns: '3fr 2fr 1.5fr 1fr 120px 100px', background: i % 2 === 0 ? 'white' : '#FAFAFA', borderTop: i > 0 ? '1px solid #F3F4F6' : 'none' }}
              >
                <div>
                  <div className="text-sm font-semibold" style={{ color: '#111827' }}>{rat.nombre_proceso}</div>
                  <div className="text-xs" style={{ color: '#9CA3AF' }}>ID #{rat.id} · {rat.updated_at?.slice(0, 10)}</div>
                </div>
                <div className="text-xs" style={{ color: '#6B7280' }}>{(rat.categoria_datos ?? '').slice(0, 45)}{(rat.categoria_datos ?? '').length > 45 ? '...' : ''}</div>
                <div className="text-xs" style={{ color: '#6B7280' }}>{(rat.base_legal ?? '').slice(0, 30)}</div>
                <div><Badge estado={rat.estado} /></div>
                <div><CompletitudBar pct={rat.completitud ?? 0} /></div>
                <div className="flex gap-1 flex-wrap">
                  {rat.nivel_riesgo === 'Crítico' && (
                    <span className="relative flex h-2 w-2" title="Nivel de riesgo crítico — acción requerida">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: '#DC2626' }} />
                      <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: '#DC2626' }} />
                    </span>
                  )}
                  {necesitaRevision(rat, now) && <span title="Sin actualizar hace +6 meses" className="text-xs font-semibold px-1.5 py-0.5 rounded-full" style={{ background: '#FEF3C7', color: '#92400E' }}>⏰ Revisar</span>}
                  {rat.datos_sensibles && <span title={`Datos sensibles${rat.tipo_dato_sensible ? ': ' + rat.tipo_dato_sensible : ''}`}>⚠️</span>}
                  {rat.evaluacion_impacto && <span title="EIPD requerida">📋</span>}
                  {rat.transferencia_internacional && <span title={`Transfer. internacional${rat.pais_destino ? ' — ' + rat.pais_destino : ''}${rat.garantias_transferencia_int ? ' (' + rat.garantias_transferencia_int + ')' : ''}`}>🌐</span>}
                  {rat.decisiones_automatizadas && <span title="Involucra decisiones automatizadas (Art. 8)">🤖</span>}
                  {rat.base_legal && rat.base_legal !== 'Otra' && !rat.tiene_archivo_base_legal && (
                    <span title="Sin documento de base legal" className="text-xs font-semibold px-1.5 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#DC2626' }}>📄 Sin doc</span>
                  )}
                  {rat.base_legal && rat.base_legal !== 'Otra' && rat.tiene_archivo_base_legal && (
                    <span title="Documento de base legal adjunto">📄</span>
                  )}
                  {puedeEditar && (
                    <button
                      onClick={e => { e.stopPropagation(); handleDuplicate(rat); }}
                      disabled={duplicating === rat.id}
                      className="text-xs font-medium px-1.5 py-0.5 rounded transition hover:bg-gray-200 disabled:opacity-60"
                      title="Duplicar"
                    >
                      📋
                    </button>
                  )}
                </div>
              </button>
              <button
                onClick={() => onSelect(rat)}
                className="sm:hidden px-4 py-3.5 cursor-pointer transition-colors bg-white text-left w-full"
                style={{ background: i % 2 === 0 ? 'white' : '#FAFAFA', borderTop: i > 0 ? '1px solid #F3F4F6' : 'none', borderBottom: '1px solid #E5E7EB' }}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold truncate" style={{ color: '#111827' }}>{rat.nombre_proceso}</div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <Badge estado={rat.estado} />
                      <CompletitudBar pct={rat.completitud ?? 0} />
                      <span className="text-xs" style={{ color: '#9CA3AF' }}>ID #{rat.id}</span>
                    </div>
                  </div>
                  <div className="flex gap-1 flex-wrap flex-shrink-0">
                    {rat.nivel_riesgo === 'Crítico' && (
                      <span className="relative flex h-2 w-2 mt-1.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: '#DC2626' }} />
                        <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: '#DC2626' }} />
                      </span>
                    )}
                    {rat.datos_sensibles && <span>⚠️</span>}
                    {rat.evaluacion_impacto && <span>📋</span>}
                    {rat.transferencia_internacional && <span>🌐</span>}
                    {rat.decisiones_automatizadas && <span>🤖</span>}
                    {rat.base_legal && rat.base_legal !== 'Otra' && !rat.tiene_archivo_base_legal && (
                      <span className="text-xs font-semibold px-1.5 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#DC2626' }}>📄 Sin doc</span>
                    )}
                    {rat.base_legal && rat.base_legal !== 'Otra' && rat.tiene_archivo_base_legal && <span>📄</span>}
                    {puedeEditar && (
                      <button
                        onClick={e => { e.stopPropagation(); handleDuplicate(rat); }}
                        disabled={duplicating === rat.id}
                        className="text-xs font-medium px-1 py-0.5 rounded transition hover:bg-gray-200 disabled:opacity-60"
                        title="Duplicar"
                      >
                        📋
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-xs truncate" style={{ color: '#6B7280' }}>{rat.categoria_datos || '—'}</div>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white rounded-xl p-5 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
        <h3 className="text-sm font-semibold mb-1" style={{ color: '#111827' }}>Exportar Registro RAT</h3>
        <p className="text-xs mb-4" style={{ color: '#6B7280' }}>Descarga el RAT completo para presentar ante la Agencia de Protección de Datos Personales.</p>
        <div className="flex gap-3">
          <button onClick={exportCsv} disabled={exporting === 'csv'} className="px-4 py-2 rounded-lg text-sm font-semibold border transition disabled:opacity-60 hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#374151' }}>{exporting === 'csv' ? 'Exportando...' : '📥 Descargar CSV'}</button>
          <button onClick={exportPdf} disabled={exporting === 'pdf'} className="px-4 py-2 rounded-lg text-sm font-semibold border transition disabled:opacity-60 hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#374151' }}>{exporting === 'pdf' ? 'Exportando...' : '📄 Descargar PDF'}</button>
        </div>
      </div>
    </div>
  );
}
