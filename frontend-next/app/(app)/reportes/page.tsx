'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { RAT, ReportesParams } from '@/types';
import Badge from '@/components/ui/Badge';
import CompletitudBar from '@/components/ui/CompletitudBar';
import Drawer from '@/components/ui/Drawer';
import { ReportTable } from '@/components/report';
import { Field } from '@/components/ui/Field';
import { Button } from '@/components/ui/Button';

const ESTADOS = ['borrador', 'completo', 'en_revision', 'aprobado'];

const COLUMN_OPTIONS = [
  { key: 'nombre_proceso', label: 'Proceso' },
  { key: 'categoria_datos', label: 'Categoría datos' },
  { key: 'base_legal', label: 'Base legal' },
  { key: 'estado', label: 'Estado' },
  { key: 'created_by', label: 'Creado por' },
  { key: 'completitud', label: 'Completitud' },
  { key: 'flags', label: 'Flags' },
  { key: 'nivel_riesgo', label: 'Nivel riesgo' },
  { key: 'categoria_titulares', label: 'Categoría titulares' },
  { key: 'fuente_datos', label: 'Fuente de datos' },
  { key: 'finalidad', label: 'Finalidad' },
  { key: 'plazo_retencion', label: 'Plazo retención' },
  { key: 'medidas_seguridad', label: 'Medidas seguridad' },
  { key: 'destinatarios', label: 'Destinatarios' },
  { key: 'transferencia_datos', label: 'Transferencia datos' },
  { key: 'pais_destino', label: 'País destino' },
  { key: 'datos_nna', label: 'Datos NNA' },
  { key: 'nivel_confidencialidad', label: 'Nivel confidencialidad' },
  { key: 'estructura_dato', label: 'Estructura dato' },
  { key: 'ciclo_procesamiento', label: 'Ciclo procesamiento' },
  { key: 'automatizacion', label: 'Automatización' },
  { key: 'frecuencia', label: 'Frecuencia' },
  { key: 'sistema_almacenamiento', label: 'Sistema almacenamiento' },
  { key: 'volumen_titulares_estimado', label: 'Volumen titulares' },
  { key: 'logica_automatizada', label: 'Lógica automatizada' },
  { key: 'responsable_tratamiento_email', label: 'Responsable email' },
  { key: 'transferencia_nacional', label: 'Transferencia nacional' },
  { key: 'datos_anonimizados', label: 'Anonimizados' },
  { key: 'datos_seudonimizados', label: 'Seudonimizados' },
  { key: 'tiene_archivo_base_legal', label: 'Archivo base legal' },
  { key: 'aprobado_por', label: 'Aprobado por' },
];

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Fecha creación' },
  { value: 'updated_at', label: 'Fecha actualización' },
  { value: 'nombre_proceso', label: 'Nombre proceso' },
  { value: 'estado', label: 'Estado' },
  { value: 'completitud', label: 'Completitud' },
  { value: 'nivel_riesgo', label: 'Nivel riesgo' },
  { value: 'base_legal', label: 'Base legal' },
];

const SAVED_FILTERS_KEY = 'custodio_saved_filters';

const ESTADO_COLOR: Record<string, string> = {
  borrador:    '#94A3B8',
  completo:    '#3B82F6',
  en_revision: '#F59E0B',
  aprobado:    '#10B981',
};

const RIESGO_COLOR: Record<string, string> = {
  'Crítico': '#DC2626',
  'Alto':    '#F59E0B',
  'Medio':   '#3B82F6',
  'Bajo':    '#10B981',
};

function HBarChart({
  data, title, getColor,
}: {
  data: Record<string, number>;
  title: string;
  getColor?: (key: string) => string;
}) {
  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total  = sorted.reduce((s, [, v]) => s + v, 0) || 1;
  return (
    <div className="bg-white rounded-xl p-5" style={{ border: '1px solid #E5E7EB' }}>
      <p className="text-xs font-semibold uppercase tracking-wide mb-4" style={{ color: '#6B7280' }}>{title}</p>
      {sorted.length === 0 ? (
        <p className="text-xs" style={{ color: '#D1D5DB' }}>Sin datos</p>
      ) : (
        <div className="space-y-3">
          {sorted.map(([key, count]) => {
            const pct   = Math.round((count / total) * 100);
            const color = getColor ? getColor(key) : '#2563EB';
            const label = key.replace(/_/g, ' ');
            return (
              <div key={key}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium truncate max-w-[60%]" style={{ color: '#374151' }} title={label}>{label}</span>
                  <span className="text-xs font-bold tabular-nums ml-2 flex-shrink-0" style={{ color }}>
                    {count} <span className="font-normal" style={{ color: '#9CA3AF' }}>({pct}%)</span>
                  </span>
                </div>
                <div className="w-full h-2 rounded-full" style={{ background: '#F3F4F6' }}>
                  <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: color }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function ReportesPage() {
  const { company, puedeEditar, baseLegalOptions } = useApp();
  const [rats, setRats] = useState<RAT[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedRat, setSelectedRat] = useState<RAT | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [auditLogs, setAuditLogs] = useState<Record<number, { accion: string; usuario: string; timestamp: string }[]>>({});
  const auditLogsRef = useRef(auditLogs);
  auditLogsRef.current = auditLogs;
  const [columns, setColumns] = useState<string[]>(['nombre_proceso', 'base_legal', 'estado', 'created_by', 'completitud', 'flags']);
  const [showColPicker, setShowColPicker] = useState(false);
  const [groupBy, setGroupBy] = useState<string>('none');
  const [savedFilters, setSavedFilters] = useState<{ id: string; name: string; filters: Partial<ReportesParams> }[]>([]);
  const [saveFilterName, setSaveFilterName] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const limit = 20;
  const colPickerRef = useRef<HTMLDivElement>(null);

  // AI chat state
  const MAX_CHAT_MESSAGES = 50;
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
    { role: 'assistant', content: 'Hola! Soy tu asistente RAT. Puedo responder dudas sobre la Ley 21.719 de Chile, qué es un RAT, cuándo se requiere EIPD, transferencias internacionales, y más. ¿En qué puedo ayudarte?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [filters, setFilters] = useState<ReportesParams>(() => {
    return {
      search: searchParams.get('search') ?? '',
      estado: searchParams.get('estado') ?? '',
      base_legal: searchParams.get('base_legal') ?? '',
      categoria_titulares: searchParams.get('categoria_titulares') ?? '',
      datos_sensibles: searchParams.get('datos_sensibles') === 'true',
      evaluacion_impacto: searchParams.get('evaluacion_impacto') === 'true',
      transferencia_internacional: searchParams.get('transferencia_internacional') === 'true',
    };
  });

  const [filtrosActivos, setFiltrosActivos] = useState<Record<string, boolean>>(() => ({
    estado: !!searchParams.get('estado'),
    base_legal: !!searchParams.get('base_legal'),
    categoria_titulares: !!searchParams.get('categoria_titulares'),
    datos_sensibles: searchParams.get('datos_sensibles') === 'true',
    evaluacion_impacto: searchParams.get('evaluacion_impacto') === 'true',
    transferencia_internacional: searchParams.get('transferencia_internacional') === 'true',
  }));

  async function sendChat() {
    const q = chatInput.trim();
    if (!q || chatLoading) return;
    setChatMessages(m => {
      const next = [...m, { role: 'user' as const, content: q }];
      return next.length > MAX_CHAT_MESSAGES ? next.slice(-MAX_CHAT_MESSAGES) : next;
    });
    setChatInput('');
    setChatLoading(true);
    try {
      const context = rats.length > 0
        ? `Empresa: ${company?.nombre}. RATs activos: ${rats.map(r => `${r.nombre_proceso} (${r.estado})`).join(', ')}`
        : undefined;
      const res = await api.askAI(q, context);
      setChatMessages(m => {
        const next = [...m, { role: 'assistant' as const, content: res.answer }];
        return next.length > MAX_CHAT_MESSAGES ? next.slice(-MAX_CHAT_MESSAGES) : next;
      });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Error';
      setChatMessages(m => {
        const next = [...m, { role: 'assistant' as const, content: `Error: ${msg}`}];
        return next.length > MAX_CHAT_MESSAGES ? next.slice(-MAX_CHAT_MESSAGES) : next;
      });
    } finally {
      setChatLoading(false);
    }
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, chatLoading]);

  useEffect(() => {
    const stored = localStorage.getItem(SAVED_FILTERS_KEY);
    if (stored) setSavedFilters(JSON.parse(stored));
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (colPickerRef.current && !colPickerRef.current.contains(e.target as Node)) {
        setShowColPicker(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const load = useCallback(async () => {
    if (!company) return;
    setLoading(true);
    try {
      const params: ReportesParams = {
        company_id: company.id,
        search: filters.search || undefined,
        estado: filters.estado || undefined,
        base_legal: filters.base_legal || undefined,
        categoria_titulares: filters.categoria_titulares || undefined,
        datos_sensibles: filtrosActivos.datos_sensibles ? true : undefined,
        evaluacion_impacto: filtrosActivos.evaluacion_impacto ? true : undefined,
        transferencia_internacional: filtrosActivos.transferencia_internacional ? true : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        skip: page * limit,
        limit,
      };
      const result = await api.getReportes(params);
      setRats(result.rats);
      setTotal(result.total);
    } catch {
      toast.error('No se pudo cargar el reporte.');
    } finally {
      setLoading(false);
    }
  }, [company, filters, filtrosActivos, sortBy, sortOrder, page, limit]);

  useEffect(() => { load(); }, [load]);

  function applyFilters() {
    setPage(0);
    const params = new URLSearchParams();
    if (filters.search) params.set('search', filters.search);
    if (filters.estado) params.set('estado', filters.estado);
    if (filters.base_legal) params.set('base_legal', filters.base_legal);
    if (filters.categoria_titulares) params.set('categoria_titulares', filters.categoria_titulares);
    if (filtrosActivos.datos_sensibles) params.set('datos_sensibles', 'true');
    if (filtrosActivos.evaluacion_impacto) params.set('evaluacion_impacto', 'true');
    if (filtrosActivos.transferencia_internacional) params.set('transferencia_internacional', 'true');
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    load();
  }

  function limpiarFiltros() {
    setFilters({ search: '', estado: '', base_legal: '', categoria_titulares: '', datos_sensibles: false, evaluacion_impacto: false, transferencia_internacional: false });
    setFiltrosActivos({ estado: false, base_legal: false, categoria_titulares: false, datos_sensibles: false, evaluacion_impacto: false, transferencia_internacional: false });
    setPage(0);
    router.replace(pathname, { scroll: false });
  }

  function loadSavedFilter(f: { id: string; name: string; filters: Partial<ReportesParams> }) {
    setFilters({
      search: f.filters.search ?? '',
      estado: f.filters.estado ?? '',
      base_legal: f.filters.base_legal ?? '',
      categoria_titulares: f.filters.categoria_titulares ?? '',
      datos_sensibles: f.filters.datos_sensibles ?? false,
      evaluacion_impacto: f.filters.evaluacion_impacto ?? false,
      transferencia_internacional: f.filters.transferencia_internacional ?? false,
    });
    setFiltrosActivos({
      estado: !!f.filters.estado,
      base_legal: !!f.filters.base_legal,
      categoria_titulares: !!f.filters.categoria_titulares,
      datos_sensibles: !!f.filters.datos_sensibles,
      evaluacion_impacto: !!f.filters.evaluacion_impacto,
      transferencia_internacional: !!f.filters.transferencia_internacional,
    });
    setPage(0);
    const params = new URLSearchParams();
    if (f.filters.search) params.set('search', f.filters.search);
    if (f.filters.estado) params.set('estado', f.filters.estado);
    if (f.filters.base_legal) params.set('base_legal', f.filters.base_legal);
    if (f.filters.categoria_titulares) params.set('categoria_titulares', f.filters.categoria_titulares);
    if (f.filters.datos_sensibles) params.set('datos_sensibles', 'true');
    if (f.filters.evaluacion_impacto) params.set('evaluacion_impacto', 'true');
    if (f.filters.transferencia_internacional) params.set('transferencia_internacional', 'true');
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    load();
  }

  const openDrawer = useCallback(async (rat: RAT) => {
    setSelectedRat(rat);
    setDrawerOpen(true);
    if (!auditLogsRef.current[rat.id]) {
      try {
        const logs = await api.getAuditoria(rat.id);
        if (Array.isArray(logs)) { setAuditLogs(l => ({ ...l, [rat.id]: logs })); }
      } catch {}
    }
  }, []);

  function toggleFiltro(key: keyof typeof filtrosActivos) {
    setFiltrosActivos(f => ({ ...f, [key]: !f[key] }));
  }

  function toggleColumn(key: string) {
    setColumns(c => c.includes(key) ? c.filter(x => x !== key) : [...c, key]);
  }

  function saveFilter() {
    if (!saveFilterName.trim()) return;
    const newFilter = { id: Date.now().toString(), name: saveFilterName.trim(), filters: { ...filters, ...filtrosActivos } };
    const updated = [...savedFilters, newFilter];
    setSavedFilters(updated);
    localStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(updated));
    setSaveFilterName('');
    setShowSaveModal(false);
    toast.success('Filtro guardado');
  }

  function deleteSavedFilter(id: string) {
    const updated = savedFilters.filter(f => f.id !== id);
    setSavedFilters(updated);
    localStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(updated));
  }

  function exportCSV() {
    const rows = [['ID', 'Proceso', 'Base Legal', 'Estado', 'Completitud', 'Nivel Riesgo', 'Datos Sensibles', 'EIPD', 'Transfer Int.', 'Creado por']];
    rats.forEach(r => {
      rows.push([
        String(r.id),
        r.nombre_proceso ?? '',
        r.base_legal ?? '',
        r.estado ?? '',
        String(r.completitud ?? 0),
        r.nivel_riesgo ?? '',
        r.datos_sensibles ? 'Sí' : 'No',
        r.evaluacion_impacto ? 'Sí' : 'No',
        r.transferencia_internacional ? 'Sí' : 'No',
        r.created_by ?? '',
      ]);
    });
    const csv = rows.map(r => r.map(v => {
      const str = String(v ?? '');
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`;
      }
      return `"${str}"`;
    }).join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reportes_rat_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('CSV exportado');
  }

  async function exportPDF() {
    const { default: jsPDF } = await import('jspdf');
    const { default: autoTable } = await import('jspdf-autotable');
    const doc = new jsPDF();
    doc.setFontSize(14);
    doc.text('Reporte RAT', 14, 16);
    doc.setFontSize(9);
    doc.text(`${company?.nombre ?? ''} — ${new Date().toLocaleDateString('es-CL')}`, 14, 22);
    autoTable(doc, {
      startY: 28,
      head: [['ID', 'Proceso', 'Base Legal', 'Estado', 'Compl.', 'Riesgo', 'Sens.', 'EIPD', 'Transf. Int.']],
      body: rats.map(r => [
        String(r.id),
        (r.nombre_proceso ?? '').slice(0, 30),
        (r.base_legal ?? '').slice(0, 20),
        r.estado ?? '',
        `${r.completitud ?? 0}%`,
        r.nivel_riesgo ?? '',
        r.datos_sensibles ? 'Sí' : 'No',
        r.evaluacion_impacto ? 'Sí' : 'No',
        r.transferencia_internacional ? 'Sí' : 'No',
      ]),
      styles: { fontSize: 8 },
      headStyles: { fillColor: [37, 99, 235] },
    });
    doc.save(`reportes_rat_${new Date().toISOString().slice(0, 10)}.pdf`);
    toast.success('PDF exportado');
  }

  function calcStats() {
    const porEstado: Record<string, number> = {};
    const porBaseLegal: Record<string, number> = {};
    const porRiesgo: Record<string, number> = {};
    let sumaComp = 0;
    rats.forEach(r => {
      porEstado[r.estado] = (porEstado[r.estado] ?? 0) + 1;
      if (r.base_legal) porBaseLegal[r.base_legal] = (porBaseLegal[r.base_legal] ?? 0) + 1;
      if (r.nivel_riesgo) porRiesgo[r.nivel_riesgo] = (porRiesgo[r.nivel_riesgo] ?? 0) + 1;
      sumaComp += r.completitud ?? 0;
    });
    return { porEstado, porBaseLegal, porRiesgo, completitudAvg: rats.length ? Math.round(sumaComp / rats.length) : 0 };
  }

  const tieneFiltrosActivos = Object.values(filtrosActivos).some(Boolean) || filters.search || filters.estado || filters.base_legal || filters.categoria_titulares;
  const stats = calcStats();
  const totalPages = Math.ceil(total / limit);

  const inputCls = 'px-3 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition';

  return (
    <div className="p-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Reportes & Analíticas</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
            {total} proceso(s) · página {page + 1} de {totalPages || 1}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Button variant="secondary" size="md" onClick={() => exportCSV()}>
            📥 CSV
          </Button>
          <Button variant="secondary" size="md" onClick={() => exportPDF()}>
            📥 PDF
          </Button>
          <Button
            variant="secondary"
            size="md"
            onClick={async () => {
              if (!company) return;
              try {
                const blob = await api.exportarPdfApdp(company.id);
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `APDP_${company.nombre}_${new Date().toISOString().slice(0, 10)}.pdf`;
                a.click();
                URL.revokeObjectURL(url);
                toast.success('Reporte APDP exportado');
              } catch { toast.error('Error al exportar Reporte APDP'); }
            }}
          >
            📋 Reporte APDP
          </Button>
          <Button variant="secondary" size="md" onClick={() => load()}>
            🔄 Actualizar
          </Button>
          {puedeEditar && (
            <Button onClick={() => window.location.href = '/rat'}>
              + Nuevo proceso
            </Button>
          )}
        </div>
      </div>

      {/* Panel de analytics */}
      <div className="bg-white rounded-xl overflow-hidden mb-6" style={{ border: '1px solid #E5E7EB' }}>
        {/* KPI strip */}
        <div className="flex flex-wrap divide-x divide-gray-100 border-b" style={{ borderColor: '#F3F4F6' }}>
          {(() => {
            const nSensibles = rats.filter(r => r.datos_sensibles).length;
            const nAprobados = stats.porEstado['aprobado'] ?? 0;
            const compColor  = stats.completitudAvg >= 75 ? '#059669' : stats.completitudAvg >= 50 ? '#D97706' : '#DC2626';
            const items = [
              { label: 'Procesos totales', value: total,                                  color: '#2563EB' },
              { label: 'Aprobados',         value: `${nAprobados} (${total ? Math.round(nAprobados/total*100) : 0}%)`, color: '#059669' },
              { label: 'Completitud prom.', value: `${stats.completitudAvg}%`,            color: compColor },
              { label: 'Datos sensibles',   value: `${nSensibles} (${total ? Math.round(nSensibles/total*100) : 0}%)`, color: '#D97706' },
              { label: 'Requieren EIPD',    value: rats.filter(r => r.evaluacion_impacto).length, color: '#2563EB' },
              { label: 'Transfer. int.',    value: rats.filter(r => r.transferencia_internacional).length, color: '#7C3AED' },
            ];
            return items.map(({ label, value, color }) => (
              <div key={label} className="flex-1 px-5 py-4 min-w-[120px]">
                <p className="text-xs mb-1" style={{ color: '#9CA3AF' }}>{label}</p>
                <p className="text-xl font-bold" style={{ color }}>{value}</p>
              </div>
            ));
          })()}
        </div>
        {/* Bar charts */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-0 divide-x divide-gray-100">
          <HBarChart title="Por estado"     data={stats.porEstado}    getColor={k => ESTADO_COLOR[k] ?? '#94A3B8'} />
          <HBarChart title="Por riesgo"     data={stats.porRiesgo}    getColor={k => RIESGO_COLOR[k] ?? '#6B7280'} />
        </div>
      </div>

      {/* Gráfico base legal (ancho completo) */}
      <div className="mb-6">
        <HBarChart title="Distribución por base legal" data={stats.porBaseLegal} getColor={() => '#4F46E5'} />
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl p-5 mb-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold" style={{ color: '#111827' }}>Filtros</span>
            {tieneFiltrosActivos && (
              <button onClick={limpiarFiltros} className="text-xs px-3 py-2 rounded-lg transition hover:bg-gray-100 min-h-[44px]" style={{ color: '#6B7280' }}>
                Limpiar todos
              </button>
            )}
          </div>
          <div className="flex gap-2 items-center">
            {savedFilters.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {savedFilters.map(f => (
                  <div key={f.id} className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs" style={{ background: '#EEF2FF', color: '#3730A3' }}>
                    <button onClick={() => loadSavedFilter(f)} className="hover:underline">{f.name}</button>
                    <button aria-label={`Eliminar filtro "${f.name}"`} onClick={() => deleteSavedFilter(f.id)} className="font-bold hover:text-red-500">✕</button>
                  </div>
                ))}
              </div>
            )}
            <button onClick={() => setShowSaveModal(true)} className="text-xs px-3 py-2.5 rounded-lg border transition hover:bg-gray-50 min-h-[44px]" style={{ borderColor: '#E5E7EB', color: '#6B7280' }}>
              💾 Guardar filtro
            </button>
          </div>
        </div>

        <div className="flex gap-3 flex-wrap mb-4">
          <input type="text" aria-label="Buscar por nombre" value={filters.search ?? ''} onChange={e => setFilters(f => ({ ...f, search: e.target.value }))} placeholder="Buscar por nombre..." className={`${inputCls} flex-1`} style={{ minWidth: 180 }} />
          <select value={filters.estado ?? ''} onChange={e => setFilters(f => ({ ...f, estado: e.target.value }))} className={inputCls}>
            <option value="">Estado (todos)</option>
            {ESTADOS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </select>
          <select value={filters.base_legal ?? ''} onChange={e => setFilters(f => ({ ...f, base_legal: e.target.value }))} className={inputCls}>
            <option value="">Base legal (todas)</option>
            {baseLegalOptions.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
          <input type="text" value={filters.categoria_titulares ?? ''} onChange={e => setFilters(f => ({ ...f, categoria_titulares: e.target.value }))} placeholder="Categoría titulares..." className={inputCls} style={{ minWidth: 160 }} />
          <button onClick={limpiarFiltros} className="px-4 py-2 rounded-lg text-xs font-semibold border transition" style={{ background: '#CCFBF1', borderColor: '#06B6D4', color: '#0F766E' }}>
            🗑 Limpiar filtros
          </button>
        </div>

        <div className="flex gap-2 flex-wrap">
          <button onClick={() => setFiltrosActivos(f => ({ ...f, datos_sensibles: !f.datos_sensibles }))} className={`px-3 py-2.5 rounded-lg text-xs font-medium border transition min-h-[44px] ${filtrosActivos.datos_sensibles ? '' : 'opacity-60'}`} style={{ background: filtrosActivos.datos_sensibles ? '#FEF3C7' : '#F9FAFB', borderColor: filtrosActivos.datos_sensibles ? '#D97706' : '#E5E7EB', color: filtrosActivos.datos_sensibles ? '#92400E' : '#6B7280' }}>⚠️ Datos sensibles</button>
          <button onClick={() => setFiltrosActivos(f => ({ ...f, evaluacion_impacto: !f.evaluacion_impacto }))} className={`px-3 py-2.5 rounded-lg text-xs font-medium border transition min-h-[44px] ${filtrosActivos.evaluacion_impacto ? '' : 'opacity-60'}`} style={{ background: filtrosActivos.evaluacion_impacto ? '#DBEAFE' : '#F9FAFB', borderColor: filtrosActivos.evaluacion_impacto ? '#2563EB' : '#E5E7EB', color: filtrosActivos.evaluacion_impacto ? '#1E3A8A' : '#6B7280' }}>📋 Requieren EIPD</button>
          <button onClick={() => setFiltrosActivos(f => ({ ...f, transferencia_internacional: !f.transferencia_internacional }))} className={`px-3 py-2.5 rounded-lg text-xs font-medium border transition min-h-[44px] ${filtrosActivos.transferencia_internacional ? '' : 'opacity-60'}`} style={{ background: filtrosActivos.transferencia_internacional ? '#F3E8FF' : '#F9FAFB', borderColor: filtrosActivos.transferencia_internacional ? '#7C3AED' : '#E5E7EB', color: filtrosActivos.transferencia_internacional ? '#5B21B6' : '#6B7280' }}>🌐 Transfer. internacional</button>
          <button onClick={applyFilters} className="px-3 py-2.5 rounded-lg text-xs font-semibold text-white transition min-h-[44px]" style={{ background: '#2563EB' }}>Aplicar filtros</button>
        </div>

        {/* Ordenar y agrupar */}
        <div className="flex gap-3 mt-4 flex-wrap items-center">
          <div className="flex items-center gap-2">
            <span className="text-xs" style={{ color: '#6B7280' }}>Ordenar por:</span>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)} className={`${inputCls} py-2.5 min-h-[44px]`} style={{ minWidth: 130 }}>
              {SORT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')} className="px-3 py-2.5 rounded-lg text-xs font-medium border transition hover:bg-gray-50 min-h-[44px]" style={{ borderColor: '#E5E7EB' }}>
              {sortOrder === 'desc' ? '↓ Desc' : '↑ Asc'}
            </button>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs" style={{ color: '#6B7280' }}>Agrupar por:</span>
            <select value={groupBy} onChange={e => setGroupBy(e.target.value)} className={`${inputCls} py-2.5 min-h-[44px]`} style={{ minWidth: 120 }}>
              <option value="none">Sin agrupar</option>
              <option value="estado">Estado</option>
              <option value="base_legal">Base legal</option>
              <option value="nivel_riesgo">Nivel riesgo</option>
            </select>
          </div>
          <div className="relative" ref={colPickerRef}>
            <button onClick={() => setShowColPicker(v => !v)} className="px-3 py-2.5 rounded-lg text-xs font-medium border transition hover:bg-gray-50 min-h-[44px]" style={{ borderColor: '#E5E7EB', color: '#6B7280' }}>
              ☰ Columnas ({columns.length})
            </button>
            {showColPicker && (
              <div className="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-lg p-3 z-10" style={{ border: '1px solid #E5E7EB', minWidth: 180 }}>
                {COLUMN_OPTIONS.map(col => (
                  <label key={col.key} className="flex items-center gap-2 py-1 cursor-pointer hover:bg-gray-50 px-2 rounded-lg">
                    <input type="checkbox" checked={columns.includes(col.key)} onChange={() => toggleColumn(col.key)} />
                    <span className="text-xs" style={{ color: '#374151' }}>{col.label}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Paginación */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mb-4">
          <button onClick={() => setPage(0)} disabled={page === 0} className="px-3 py-1 rounded-lg text-xs border transition hover:bg-gray-50 disabled:opacity-40" style={{ borderColor: '#E5E7EB' }}>«</button>
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="px-3 py-1 rounded-lg text-xs border transition hover:bg-gray-50 disabled:opacity-40" style={{ borderColor: '#E5E7EB' }}>‹</button>
          <span className="text-xs px-3" style={{ color: '#6B7280' }}>Página {page + 1} de {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-3 py-1 rounded-lg text-xs border transition hover:bg-gray-50 disabled:opacity-40" style={{ borderColor: '#E5E7EB' }}>›</button>
          <button onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1} className="px-3 py-1 rounded-lg text-xs border transition hover:bg-gray-50 disabled:opacity-40" style={{ borderColor: '#E5E7EB' }}>»</button>
        </div>
      )}

      {/* Tabla */}
      {loading ? (
        <div className="text-center py-16 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
      ) : rats.length === 0 ? (
        <div className="text-center py-14 bg-white rounded-xl" style={{ border: '1px solid #E5E7EB' }}>
          <div className="text-3xl mb-2">🔍</div>
          <p className="text-sm font-medium" style={{ color: '#374151' }}>Sin resultados</p>
          <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>Ajusta los filtros o limpialos para ver todos los procesos.</p>
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden bg-white" style={{ border: '1px solid #E5E7EB' }}>
          <div className="overflow-x-auto">
            <table className="w-full" style={{ minWidth: Math.max(600, columns.length * 100) }}>
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                  {columns.map(col => <th key={col} role="columnheader" scope="col" className="px-4 py-3 text-left whitespace-nowrap">{COLUMN_OPTIONS.find(c => c.key === col)?.label ?? col}</th>)}
                </tr>
              </thead>
              <ReportTable rats={rats} columns={columns} groupBy={groupBy} onRowClick={openDrawer} />
            </table>
          </div>
        </div>
      )}

      {/* Drawer detalle */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title="Detalle RAT"
        size="xl"
        extraAction={
          <button
            onClick={async () => {
              if (!selectedRat) return;
              try {
                const blob = await api.exportarRatPdf(selectedRat.id);
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const fecha = new Date().toISOString().slice(0, 10);
                const nombre = (selectedRat.nombre_proceso || 'RAT').replace(/\s+/g, '_');
                a.download = `reporte_rat_${selectedRat.id}_${nombre}_${fecha}.pdf`;
                a.click();
                URL.revokeObjectURL(url);
              } catch { toast.error('Error al exportar PDF'); }
            }}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-100"
            style={{ borderColor: '#DC2626', color: '#DC2626' }}
          >
            📄 Exportar PDF
          </button>
        }
      >
        {selectedRat && (
          <div className="space-y-6">
            {/* Encabezado con nombre del RAT */}
            <div className="rounded-xl p-5 flex flex-row items-start justify-between" style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)' }}>
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>Registro de Actividades de Tratamiento</p>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-mono font-bold" style={{ color: 'rgba(255,255,255,0.6)' }}>#{selectedRat.id}</span>
                  <h3 className="text-lg font-bold text-white">{selectedRat.nombre_proceso}</h3>
                </div>
                <p className="text-xs" style={{ color: 'rgba(255,255,255,0.6)' }}>Documento que identifica y describe el tratamiento de datos personales conforme a la Ley 21.719</p>
              </div>
            </div>

            {/* Estado y badges principales */}
            <div className="flex flex-wrap items-center gap-3 pb-4" style={{ borderBottom: '1px solid #E5E7EB' }}>
              <Badge estado={selectedRat.estado} />
              <CompletitudBar pct={selectedRat.completitud ?? 0} />
              {selectedRat.nivel_riesgo === 'Crítico' && (
                <span className="px-3 py-1 rounded-full text-xs font-bold" style={{ background: '#FEE2E2', color: '#DC2626' }}>⚠️ Crítico</span>
              )}
              {selectedRat.nivel_riesgo && selectedRat.nivel_riesgo !== 'Crítico' && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold" style={{
                  background: selectedRat.nivel_riesgo === 'Alto' ? '#FEF3C7' : selectedRat.nivel_riesgo === 'Medio' ? '#DBEAFE' : '#F3F4F6',
                  color: selectedRat.nivel_riesgo === 'Alto' ? '#92400E' : selectedRat.nivel_riesgo === 'Medio' ? '#1E3A8A' : '#6B7280'
                }}>{selectedRat.nivel_riesgo}</span>
              )}
            </div>

            {/* Flags */}
            <div className="flex gap-2 flex-wrap">
              {selectedRat.datos_sensibles && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#FEF3C7', color: '#92400E' }}>⚠️ Datos sensibles</span>}
              {selectedRat.evaluacion_impacto && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#DBEAFE', color: '#1E3A8A' }}>📋 EIPD requerida</span>}
              {selectedRat.transferencia_internacional && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#F3E8FF', color: '#5B21B6' }}>🌐 Transfer. internacional</span>}
              {selectedRat.transferencia_nacional && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#ECFDF5', color: '#065F46' }}>🏠 Transfer. nacional</span>}
              {selectedRat.decisiones_automatizadas && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#F3F4F6', color: '#374151' }}>🤖 Decisiones automatizadas</span>}
              {selectedRat.datos_nna && <span className="px-3 py-1.5 rounded-full text-xs font-semibold" style={{ background: '#FEF3C7', color: '#92400E' }}>👶 Datos NNA</span>}
            </div>

            {/* Sección: Identificación */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Identificación</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Categoría titulares" value={selectedRat.categoria_titulares} />
                <Field label="Fuente de datos" value={selectedRat.fuente_datos} />
                <Field label="Destinatarios" value={selectedRat.destinatarios} />
                <Field label="Encargado tratamiento" value={selectedRat.nombre_encargado} />
              </div>
            </div>

            {/* Sección: Base legal y finalidad */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Base legal y finalidad</p>
              <div className="space-y-3">
                <Field label="Base legal" value={selectedRat.base_legal} />
                <Field label="Finalidad" value={selectedRat.finalidad} />
                {selectedRat.test_interes_legitimo && (
                  <div className="p-4 rounded-xl" style={{ background: '#FFFBEB', border: '1px solid #FCD34D' }}>
                    <p className="text-xs font-bold mb-1" style={{ color: '#92400E' }}>Test de interés legítimo</p>
                    <p className="text-sm whitespace-pre-wrap" style={{ color: '#374151' }}>{selectedRat.test_interes_legitimo}</p>
                  </div>
                )}
                {selectedRat.logica_automatizada && (
                  <div className="p-4 rounded-xl" style={{ background: '#F3F4F6', border: '1px solid #E5E7EB' }}>
                    <p className="text-xs font-bold mb-1" style={{ color: '#374151' }}>Lógica automatizada (Art. 8)</p>
                    <p className="text-sm whitespace-pre-wrap" style={{ color: '#374151' }}>{selectedRat.logica_automatizada}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Sección: Datos tratados */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Datos tratados</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Categoría datos" value={selectedRat.categoria_datos} />
                <Field label="Tipo dato sensible" value={selectedRat.tipo_dato_sensible} />
                <Field label="Datos NNA" value={selectedRat.datos_nna} />
                <Field label="Nivel confidencialidad" value={selectedRat.nivel_confidencialidad} />
                <Field label="Estructura dato" value={selectedRat.estructura_dato} />
                <Field label="Anonimizados" value={selectedRat.datos_anonimizados ? 'Sí' : 'No'} />
                <Field label="Seudonimizados" value={selectedRat.datos_seudonimizados ? 'Sí' : 'No'} />
              </div>
            </div>

            {/* Sección: Almacenamiento */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Almacenamiento y transferencias</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Plazo retención" value={selectedRat.plazo_retencion} />
                <Field label="Medidas de seguridad" value={selectedRat.medidas_seguridad} />
                <Field label="Sistema almacenamiento" value={selectedRat.sistema_almacenamiento} />
                <Field label="Frecuencia" value={selectedRat.frecuencia} />
                <Field label="Transferencia datos" value={selectedRat.transferencia_datos} />
                <Field label="País destino" value={selectedRat.pais_destino} />
                <Field label="Garantías transferencia" value={selectedRat.garantias_transferencia_int} />
                <Field label="Responsable email" value={selectedRat.responsable_tratamiento_email} />
                <Field label="Ciclo procesamiento" value={selectedRat.ciclo_procesamiento} />
                <Field label="Automatización" value={selectedRat.automatizacion} />
              </div>
            </div>

            {/* Sección: Metadatos */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Información del registro</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Creado por" value={selectedRat.created_by} />
                <Field label="Fecha creación" value={selectedRat.created_at?.slice(0, 10) ?? '—'} />
                <Field label="Última actualización" value={selectedRat.updated_at?.slice(0, 10) ?? '—'} />
                <Field label="Observaciones auditoría" value={selectedRat.observaciones_auditoria} />
                <Field label="Aprobado por" value={selectedRat.aprobado_por} />
                <Field label="Fecha aprobación" value={selectedRat.fecha_aprobacion?.slice(0, 10) ?? '—'} />
                <Field label="Archivo base legal" value={selectedRat.tiene_archivo_base_legal ? 'Sí' : 'No'} />
                <Field label="Técnica anonimización" value={selectedRat.tecnica_anonimizacion} />
                <Field label="Mecanismos eliminación" value={selectedRat.mecanismos_eliminacion} />
                <Field label="Origen portabilidad" value={selectedRat.origen_dato_portabilidad} />
                <Field label="Fecha levantamiento" value={selectedRat.fecha_levantamiento?.slice(0, 10) ?? '—'} />
              </div>
            </div>

            {/* Sección: Métricas avanzadas (Tier 1 / Tier 2) */}
            <div>
              <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Métricas avanzadas — Tier 1 y Tier 2</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field label="Volumen titulares" value={selectedRat.volumen_titulares_estimado?.toLocaleString('es-CL')} />
                <Field label="Doc cláusulas" value={selectedRat.doc_clausulas} />
                <Field label="Medidas organizativas" value={selectedRat.medidas_organizativas} />
              </div>
            </div>

            {/* Historial */}
            {auditLogs[selectedRat.id] && auditLogs[selectedRat.id].length > 0 && (
              <div>
                <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Historial de cambios</p>
                <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
                  {auditLogs[selectedRat.id].slice(0, 10).map((log, li) => (
                    <div key={li} className="flex items-center gap-3 px-4 py-2.5 text-sm" style={{ borderTop: li > 0 ? '1px solid #F3F4F6' : 'none', background: li % 2 === 0 ? '#FFFFFF' : '#F9FAFB' }}>
                      <span className="font-bold px-2 py-0.5 rounded text-white flex-shrink-0 text-xs" style={{ background: '#2563EB', minWidth: 48, textAlign: 'center' }}>{log.accion?.slice(0, 3).toUpperCase()}</span>
                      <div className="flex-1">
                        <span className="font-medium" style={{ color: '#374151' }}>{log.usuario}</span>
                        <span className="ml-2 text-xs" style={{ color: '#9CA3AF' }}>{log.timestamp?.slice(0, 16).replace('T', ' ')}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {/* Chat IA */}
      <button
        onClick={() => setChatOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center text-2xl transition hover:scale-105 z-40"
        style={{ background: '#2563EB', color: 'white' }}
        title="Asistente IA — Ley 21.719"
      >
        🤖
      </button>

      {chatOpen && (
        <div className="fixed inset-0 z-50 flex justify-end" onClick={() => setChatOpen(false)}>
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
          <div
            className="relative flex flex-col h-full shadow-2xl overflow-hidden"
            style={{ width: '95vw', maxWidth: 420, background: 'white', animation: 'slideInRight 0.25s ease' }}
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 flex-shrink-0" style={{ borderBottom: '1px solid #E5E7EB', background: '#F9FAFB' }}>
              <div className="flex items-center gap-2">
                <span className="text-xl">🤖</span>
                <div>
                  <h2 className="text-sm font-semibold" style={{ color: '#111827' }}>Asistente RAT</h2>
                  <p className="text-xs" style={{ color: '#6B7280' }}>Ley 21.719 Chile</p>
                </div>
              </div>
              <button onClick={() => setChatOpen(false)} className="w-8 h-8 rounded-lg flex items-center justify-center transition hover:bg-gray-200 text-sm font-bold" style={{ color: '#6B7280' }}>✕</button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ background: '#F9FAFB' }}>
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className="max-w-[85%] px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap"
                    style={{
                      background: msg.role === 'user' ? '#2563EB' : 'white',
                      color: msg.role === 'user' ? 'white' : '#111827',
                      border: msg.role === 'assistant' ? '1px solid #E5E7EB' : 'none',
                      borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                      borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px',
                    }}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 rounded-2xl text-sm" style={{ background: 'white', border: '1px solid #E5E7EB', color: '#9CA3AF' }}>
                    Escribiendo...
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <div className="p-4 flex gap-2 flex-shrink-0" style={{ borderTop: '1px solid #E5E7EB', background: 'white' }}>
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') sendChat(); }}
                placeholder="Pregunta sobre la Ley 21.719..."
                className="flex-1 px-3 py-2 rounded-xl text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ borderColor: '#E5E7EB' }}
                disabled={chatLoading}
              />
              <button
                onClick={sendChat}
                disabled={chatLoading || !chatInput.trim()}
                className="px-4 py-2 rounded-xl text-sm font-semibold text-white transition disabled:opacity-50"
                style={{ background: '#2563EB' }}
              >
                →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Guardar filtro modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={() => setShowSaveModal(false)}>
          <div className="bg-white rounded-2xl p-6 w-96 shadow-2xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Guardar filtro</h3>
            <input type="text" value={saveFilterName} onChange={e => setSaveFilterName(e.target.value)} onKeyDown={e => e.key === 'Enter' && saveFilter()} placeholder="Nombre del filtro..." className="w-full px-3 py-2 rounded-lg text-sm border mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500" style={{ borderColor: '#E5E7EB' }} />
            <div className="flex gap-2 justify-end">
              <Button variant="secondary" onClick={() => setShowSaveModal(false)}>Cancelar</Button>
              <Button onClick={saveFilter}>Guardar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
