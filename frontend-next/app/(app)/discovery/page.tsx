'use client';

import { useEffect, useState } from 'react';
import { useApp } from '@/context/AppContext';
import Button from '@/components/ui/Button';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import type { DataSource, DataSourceCreate, DiscoveryRunDetail } from '@/lib/api';

// ── Colores por categoría ─────────────────────────────────────────────────────
const CATEGORIA_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  IDENTIFICADOR:      { label: 'Identificador',       color: '#1d4ed8', bg: '#dbeafe' },
  CONTACTO:           { label: 'Contacto',             color: '#065f46', bg: '#d1fae5' },
  UBICACION_PRECISA:  { label: 'Ubicación precisa',    color: '#92400e', bg: '#fef3c7' },
  FINANCIERO:         { label: 'Financiero',           color: '#7c2d12', bg: '#fef2f2' },
  SENSIBLE_SALUD:     { label: 'Salud (sensible)',     color: '#6b21a8', bg: '#f3e8ff' },
  SENSIBLE_BIOMETRICO:{ label: 'Biométrico (sensible)',color: '#5b21b6', bg: '#ede9fe' },
  SENSIBLE_RELIGIOSO: { label: 'Religioso (sensible)', color: '#9a3412', bg: '#fff7ed' },
  SENSIBLE_POLITICO:  { label: 'Político (sensible)',  color: '#701a75', bg: '#fdf4ff' },
  DEMOGRAFICO:        { label: 'Demográfico',          color: '#1e3a5f', bg: '#e0f0ff' },
  TECNICO:            { label: 'Técnico',              color: '#374151', bg: '#f3f4f6' },
};

function CategoriaBadge({ categoria }: { categoria: string }) {
  const cfg = CATEGORIA_CONFIG[categoria] ?? { label: categoria, color: '#374151', bg: '#f3f4f6' };
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px', borderRadius: 4,
      fontSize: 11, fontWeight: 600,
      color: cfg.color, background: cfg.bg,
    }}>
      {cfg.label}
    </span>
  );
}

// ── Formulario de fuente de datos ─────────────────────────────────────────────
function DataSourceForm({
  onSave,
  onCancel,
  initial,
  isEdit,
}: {
  onSave: (data: DataSourceCreate) => Promise<void>;
  onCancel: () => void;
  initial?: Partial<DataSourceCreate>;
  isEdit?: boolean;
}) {
  const [form, setForm] = useState<DataSourceCreate>({
    nombre: initial?.nombre ?? '',
    tipo: initial?.tipo ?? 'postgresql',
    host: initial?.host ?? '',
    port: initial?.port ?? 5432,
    database_name: initial?.database_name ?? '',
    username: initial?.username ?? '',
    password: '',
    schema_name: initial?.schema_name ?? '',
  });
  const [loading, setLoading] = useState(false);

  const inputClass = 'w-full px-3 py-2 border rounded-md text-sm bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100';
  const labelClass = 'block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.nombre || !form.host || !form.database_name || !form.username || (!isEdit && !form.password)) {
      toast.error('Completa todos los campos obligatorios');
      return;
    }
    setLoading(true);
    try {
      await onSave(form);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Nombre *</label>
          <input className={inputClass} value={form.nombre}
            onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
        </div>
        <div>
          <label className={labelClass}>Tipo *</label>
          <select className={inputClass} value={form.tipo}
            onChange={e => setForm(f => ({ ...f, tipo: e.target.value as 'postgresql' | 'sqlserver', port: e.target.value === 'postgresql' ? 5432 : 1433 }))}>
            <option value="postgresql">PostgreSQL</option>
            <option value="sqlserver">SQL Server</option>
          </select>
        </div>
        <div>
          <label className={labelClass}>Host *</label>
          <input className={inputClass} value={form.host} placeholder="db.ejemplo.com"
            onChange={e => setForm(f => ({ ...f, host: e.target.value }))} />
        </div>
        <div>
          <label className={labelClass}>Puerto *</label>
          <input className={inputClass} type="number" value={form.port}
            onChange={e => setForm(f => ({ ...f, port: Number(e.target.value) }))} />
        </div>
        <div>
          <label className={labelClass}>Base de datos *</label>
          <input className={inputClass} value={form.database_name}
            onChange={e => setForm(f => ({ ...f, database_name: e.target.value }))} />
        </div>
        <div>
          <label className={labelClass}>Schema (opcional)</label>
          <input className={inputClass} value={form.schema_name ?? ''} placeholder={form.tipo === 'postgresql' ? 'public' : 'dbo'}
            onChange={e => setForm(f => ({ ...f, schema_name: e.target.value }))} />
        </div>
        <div>
          <label className={labelClass}>Usuario *</label>
          <input className={inputClass} value={form.username}
            onChange={e => setForm(f => ({ ...f, username: e.target.value }))} />
        </div>
        <div>
          <label className={labelClass}>Contraseña {isEdit ? <span className="font-normal text-gray-400">(vacío = sin cambios)</span> : '*'} <span className="text-xs text-gray-400">(cifrada con Fernet)</span></label>
          <input className={inputClass} type="password" value={form.password}
            onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
        </div>
      </div>
      <p className="text-xs text-amber-600 dark:text-amber-400">
        ⚠ Custodio se conecta en modo READ-ONLY. Solo lee metadatos del esquema (information_schema).
        No accede a datos reales de tus tablas.
      </p>
      <div className="flex gap-2 justify-end">
        <Button variant="ghost" type="button" onClick={onCancel}>Cancelar</Button>
        <Button type="submit" disabled={loading}>{loading ? 'Guardando…' : 'Guardar fuente'}</Button>
      </div>
    </form>
  );
}

// ── Tabla de hallazgos ────────────────────────────────────────────────────────
function FindingsTable({
  findings,
  filtroGaps,
}: {
  findings: DiscoveryRunDetail['findings'];
  filtroGaps: boolean;
}) {
  const visible = filtroGaps ? findings.filter(f => f.es_gap && !f.descartado) : findings.filter(f => !f.descartado);

  if (visible.length === 0) {
    return <p className="text-sm text-gray-500 py-4 text-center">No hay hallazgos que mostrar.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700 text-xs text-gray-500 uppercase">
            <th className="text-left py-2 px-3">Tabla</th>
            <th className="text-left py-2 px-3">Columna</th>
            <th className="text-left py-2 px-3">Tipo SQL</th>
            <th className="text-left py-2 px-3">Categoría</th>
            <th className="text-left py-2 px-3">Confianza</th>
            <th className="text-left py-2 px-3">Estado</th>
          </tr>
        </thead>
        <tbody>
          {visible.map(f => (
            <tr key={f.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
              <td className="py-2 px-3 font-mono text-xs">{f.table_name}</td>
              <td className="py-2 px-3 font-mono text-xs font-medium">{f.column_name}</td>
              <td className="py-2 px-3 text-gray-500 text-xs">{f.data_type_sql ?? '—'}</td>
              <td className="py-2 px-3"><CategoriaBadge categoria={f.categoria} /></td>
              <td className="py-2 px-3">
                <span className={`text-xs font-semibold ${f.confianza >= 90 ? 'text-green-600' : f.confianza >= 70 ? 'text-yellow-600' : 'text-gray-400'}`}>
                  {f.confianza}%
                </span>
              </td>
              <td className="py-2 px-3">
                {f.es_gap
                  ? <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full">Sin RAT</span>
                  : f.rat_id
                    ? <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">Vinculado</span>
                    : <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">Sin gap</span>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Panel de sugerencias RAT ──────────────────────────────────────────────────
function SugerenciasPanel({
  sugerencias,
  companyId,
  runId,
}: {
  sugerencias: DiscoveryRunDetail['sugerencias_rat'];
  companyId: number;
  runId: number;
}) {
  const [creatingIdx, setCreatingIdx] = useState<number | null>(null);
  const [createdIds, setCreatedIds] = useState<Record<number, number>>(() => {
    try {
      const raw = localStorage.getItem(`disc_rats_${runId}`);
      return raw ? JSON.parse(raw) : {};
    } catch { return {}; }
  });

  function persistCreated(idx: number, ratId: number) {
    const next = { ...createdIds, [idx]: ratId };
    setCreatedIds(next);
    try { localStorage.setItem(`disc_rats_${runId}`, JSON.stringify(next)); } catch {}
  }

  async function handleCrearRat(s: typeof sugerencias[number], idx: number) {
    if (createdIds[idx]) return;
    setCreatingIdx(idx);
    try {
      const payload: Record<string, unknown> = {
        company_id: companyId,
        nombre_proceso: s.template_rat.nombre_proceso,
        categoria_datos: s.template_rat.categoria_datos,
        categoria_titulares: s.template_rat.categoria_titulares,
        finalidad: s.template_rat.finalidad,
        base_legal: s.template_rat.base_legal,
        fuente_datos: s.template_rat.fuente_datos,
        plazo_retencion: s.template_rat.plazo_retencion,
      };
      if (s.template_rat.test_interes_legitimo) {
        payload.test_interes_legitimo = s.template_rat.test_interes_legitimo;
      }
      const rat = await api.crearRat(payload as Parameters<typeof api.crearRat>[0]);
      persistCreated(idx, rat.id);
      toast.success(`RAT "${rat.nombre_proceso}" creado como borrador`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al crear el RAT');
    } finally {
      setCreatingIdx(null);
    }
  }

  if (sugerencias.length === 0) {
    return (
      <div className="py-6 text-center text-sm text-green-600 dark:text-green-400">
        ✅ No se detectaron gaps. Todos los datos personales encontrados están cubiertos por RATs existentes.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <a
          href={api.urlExportarGapsCSV(runId, companyId)}
          download
          className="text-xs px-3 py-1.5 rounded border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          ↓ Exportar gaps CSV
        </a>
      </div>
      {sugerencias.map((s, i) => (
        <div key={i} className={`border rounded-lg p-4 ${createdIds[i] ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20' : 'border-orange-200 dark:border-orange-800 bg-orange-50 dark:bg-orange-900/20'}`}>
          <div className="flex items-center gap-2 mb-2">
            <CategoriaBadge categoria={s.categoria} />
            <span className="text-xs text-gray-500">{s.cantidad_hallazgos} columna(s) detectada(s)</span>
            <div className="ml-auto">
              {createdIds[i] ? (
                <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-300 rounded-full font-medium">
                  ✓ RAT #{createdIds[i]} creado
                </span>
              ) : (
                <Button
                  size="sm"
                  onClick={() => handleCrearRat(s, i)}
                  disabled={creatingIdx === i}
                >
                  {creatingIdx === i ? 'Creando…' : '+ Crear RAT'}
                </Button>
              )}
            </div>
          </div>
          <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
            RAT sugerido: <span className="font-bold">{s.template_rat.nombre_proceso}</span>
          </p>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400 mt-2">
            <span><b>Categoría datos:</b> {s.template_rat.categoria_datos}</span>
            <span><b>Base legal:</b> {s.template_rat.base_legal}</span>
            <span><b>Finalidad:</b> {s.template_rat.finalidad}</span>
            <span><b>Sistema:</b> {s.template_rat.sistema_almacenamiento}</span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Tablas: {s.tablas_involucradas.slice(0, 4).join(', ')}{s.tablas_involucradas.length > 4 ? ` +${s.tablas_involucradas.length - 4} más` : ''}
          </p>
        </div>
      ))}
    </div>
  );
}

// ── Queries SQL para modo manual ──────────────────────────────────────────────
const QUERY_PG = `SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name NOT IN ('alembic_version','django_migrations','spatial_ref_sys')
ORDER BY table_name, ordinal_position;`;

const QUERY_MSSQL = `SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME, ORDINAL_POSITION;`;

// ── Panel de modo manual ──────────────────────────────────────────────────────
function ModoManualPanel({
  source,
  companyId,
  onResult,
  onClose,
}: {
  source: DataSource;
  companyId: number;
  onResult: (detail: DiscoveryRunDetail) => void;
  onClose: () => void;
}) {
  const [rawInput, setRawInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const query = source.tipo === 'postgresql' ? QUERY_PG : QUERY_MSSQL;

  function copiarQuery() {
    navigator.clipboard.writeText(query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function parseInput(raw: string): { table_name: string; column_name: string; data_type: string }[] | null {
    const text = raw.trim();
    if (!text) return null;

    // Intentar JSON array
    if (text.startsWith('[')) {
      try {
        const arr = JSON.parse(text);
        if (Array.isArray(arr) && arr[0]?.column_name) return arr;
      } catch {}
    }

    // CSV/TSV: primera línea = headers, resto = datos
    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length < 2) return null;

    const sep = lines[0].includes('\t') ? '\t' : ',';
    const headers = lines[0].split(sep).map(h => h.trim().toLowerCase().replace(/['"]/g, ''));

    const idxTable = headers.findIndex(h => h.includes('table'));
    const idxCol   = headers.findIndex(h => h.includes('column'));
    const idxType  = headers.findIndex(h => h.includes('type') || h.includes('data'));

    if (idxTable === -1 || idxCol === -1) return null;

    return lines.slice(1).map(line => {
      const cells = line.split(sep).map(c => c.trim().replace(/^['"]|['"]$/g, ''));
      return {
        table_name:  cells[idxTable] ?? '',
        column_name: cells[idxCol]   ?? '',
        data_type:   idxType >= 0 ? (cells[idxType] ?? '') : '',
      };
    }).filter(r => r.table_name && r.column_name);
  }

  async function handleProcesar() {
    const columns = parseInput(rawInput);
    if (!columns || columns.length === 0) {
      toast.error('No se pudo parsear el resultado. Pega el CSV/TSV con encabezados o un JSON array.');
      return;
    }
    setLoading(true);
    try {
      const detail = await api.ejecutarScanManual(source.id, companyId, columns);
      toast.success(`Escaneo manual completado: ${detail.run.total_hallazgos} hallazgos, ${detail.run.total_gaps} gaps`);
      onResult(detail);
      onClose();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al procesar');
    } finally {
      setLoading(false);
    }
  }

  const preClass = 'block w-full text-xs font-mono bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 overflow-x-auto whitespace-pre select-all';

  return (
    <div className="border border-amber-200 dark:border-amber-700 rounded-xl p-5 bg-white dark:bg-gray-900 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">Modo manual — {source.nombre}</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Ejecuta la query en tu BD y pega el resultado aquí. Custodio clasifica las columnas sin necesidad de conexión directa.
          </p>
        </div>
        <Button size="sm" variant="ghost" onClick={onClose}>✕</Button>
      </div>

      {/* Query a copiar */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
            1. Copia y ejecuta esta query en tu {source.tipo === 'postgresql' ? 'PostgreSQL' : 'SQL Server'}:
          </p>
          <Button size="sm" variant="ghost" onClick={copiarQuery}>
            {copied ? '✓ Copiado' : 'Copiar query'}
          </Button>
        </div>
        <pre className={preClass}>{query}</pre>
      </div>

      {/* Textarea para pegar resultado */}
      <div>
        <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
          2. Pega el resultado aquí (CSV, TSV con encabezados, o JSON array):
        </p>
        <textarea
          className="w-full h-40 px-3 py-2 text-xs font-mono border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 resize-y"
          placeholder={'table_name\tcolumn_name\tdata_type\nclientes\tnombre\tvarchar\nclientes\temail\tvarchar\n...'}
          value={rawInput}
          onChange={e => setRawInput(e.target.value)}
        />
        <p className="text-xs text-gray-400 mt-1">
          Formatos aceptados: CSV (comas), TSV (tabs), o JSON <code>[{`{table_name, column_name, data_type}`}]</code>. La primera fila debe ser el encabezado.
        </p>
      </div>

      <div className="flex gap-2 justify-end">
        <Button variant="ghost" onClick={onClose}>Cancelar</Button>
        <Button onClick={handleProcesar} disabled={loading || !rawInput.trim()}>
          {loading ? 'Procesando…' : 'Analizar columnas'}
        </Button>
      </div>
    </div>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────
export default function DiscoveryPage() {
  const { company } = useApp();
  const companyId = company?.id;

  const [sources, setSources] = useState<DataSource[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editSource, setEditSource] = useState<DataSource | null>(null);
  const [manualSource, setManualSource] = useState<DataSource | null>(null);
  const [scanning, setScanningId] = useState<number | null>(null);
  const [runDetail, setRunDetail] = useState<DiscoveryRunDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'hallazgos' | 'gaps' | 'sugerencias'>('hallazgos');
  const [loading, setLoading] = useState(true);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (!companyId) return;
    load();
  }, [companyId]);

  async function load() {
    if (!companyId) return;
    setLoading(true);
    try {
      const data = await api.listarDiscoverySources(companyId);
      setSources(data);
      // Si hay un último run completado, cargarlo automáticamente
      const conRun = data.find(s => s.ultimo_run_id && s.ultimo_run_estado === 'completado');
      if (conRun && conRun.ultimo_run_id) {
        const detail = await api.obtenerDiscoveryRun(conRun.ultimo_run_id, companyId);
        setRunDetail(detail);
      }
    } catch {
      toast.error('Error al cargar fuentes de datos');
    } finally {
      setLoading(false);
    }
  }

  async function handleCrearSource(data: DataSourceCreate) {
    if (!companyId) return;
    try {
      await api.crearDiscoverySource(companyId, data);
      toast.success('Fuente de datos agregada');
      setShowForm(false);
      load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar');
    }
  }

  async function handleActualizarSource(data: DataSourceCreate) {
    if (!companyId || !editSource) return;
    // Si password está vacío, no incluirla en el payload (PATCH parcial)
    const payload: Partial<DataSourceCreate> = { ...data };
    if (!payload.password) delete payload.password;
    try {
      await api.actualizarDiscoverySource(editSource.id, companyId, payload);
      toast.success('Fuente de datos actualizada');
      setEditSource(null);
      load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al actualizar');
    }
  }

  async function handleScan(source: DataSource) {
    if (!companyId) return;
    setScanningId(source.id);
    setRunDetail(null);
    try {
      const detail = await api.ejecutarScan(source.id, companyId);
      setRunDetail(detail);
      setActiveTab('hallazgos');
      toast.success(`Escaneo completado: ${detail.run.total_hallazgos} hallazgos, ${detail.run.total_gaps} gaps`);
      load();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al conectar con la fuente de datos');
    } finally {
      setScanningId(null);
    }
  }

  async function handleEliminar(source: DataSource) {
    if (!companyId) return;
    try {
      await api.eliminarDiscoverySource(source.id, companyId);
      toast.success('Fuente eliminada');
      setConfirmDeleteId(null);
      if (runDetail?.run.source_id === source.id) setRunDetail(null);
      load();
    } catch {
      toast.error('Error al eliminar');
    }
  }

  if (!companyId) {
    return (
      <div className="p-8 text-center text-gray-500">
        Selecciona una empresa para usar el módulo de Descubrimiento.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Encabezado */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">🔍 Descubrimiento de Datos</h1>
          <p className="text-sm text-gray-500 mt-1">
            Escanea tus bases de datos para detectar columnas con datos personales y compáralas con tus RATs (Ley 21.719).
          </p>
        </div>
        <Button onClick={() => setShowForm(true)} disabled={showForm}>+ Agregar fuente</Button>
      </div>

      {/* Formulario de nueva fuente */}
      {showForm && (
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl p-5 bg-white dark:bg-gray-900">
          <h2 className="text-base font-semibold mb-4 text-gray-900 dark:text-gray-100">Nueva fuente de datos</h2>
          <DataSourceForm onSave={handleCrearSource} onCancel={() => setShowForm(false)} />
        </div>
      )}

      {/* Formulario de edición */}
      {editSource && (
        <div className="border border-blue-200 dark:border-blue-700 rounded-xl p-5 bg-white dark:bg-gray-900">
          <h2 className="text-base font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Editar fuente: <span className="text-blue-600">{editSource.nombre}</span>
          </h2>
          <p className="text-xs text-gray-500 mb-3">Deja la contraseña vacía para no modificarla.</p>
          <DataSourceForm
            onSave={handleActualizarSource}
            onCancel={() => setEditSource(null)}
            initial={editSource}
            isEdit
          />
        </div>
      )}

      {/* Panel de modo manual */}
      {manualSource && (
        <ModoManualPanel
          source={manualSource}
          companyId={companyId}
          onResult={(detail) => { setRunDetail(detail); setActiveTab('hallazgos'); load(); }}
          onClose={() => setManualSource(null)}
        />
      )}

      {/* Lista de fuentes */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-3">
          Fuentes configuradas
        </h2>
        {loading ? (
          <p className="text-sm text-gray-400">Cargando…</p>
        ) : sources.length === 0 ? (
          <div className="border border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center text-gray-400 text-sm">
            Sin fuentes configuradas. Agrega tu primera base de datos para comenzar.
          </div>
        ) : (
          <div className="grid gap-3 grid-cols-1 md:grid-cols-2">
            {sources.map(s => (
              <div key={s.id} className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-white dark:bg-gray-900 flex flex-col gap-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-gray-100 text-sm">{s.nombre}</p>
                    <p className="text-xs text-gray-500 font-mono mt-0.5">
                      {s.tipo === 'postgresql' ? '🐘' : '🗄'} {s.host}:{s.port}/{s.database_name}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    s.ultimo_run_estado === 'completado' ? 'bg-green-100 text-green-700' :
                    s.ultimo_run_estado === 'error' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-500'
                  }`}>
                    {s.ultimo_run_estado ?? 'Sin escaneo'}
                  </span>
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Button
                    size="sm"
                    onClick={() => handleScan(s)}
                    disabled={scanning === s.id}
                  >
                    {scanning === s.id ? '⏳ Escaneando…' : '▶ Escanear'}
                  </Button>
                  {s.ultimo_run_id && (
                    <Button size="sm" variant="ghost" onClick={async () => {
                      const detail = await api.obtenerDiscoveryRun(s.ultimo_run_id!, companyId);
                      setRunDetail(detail);
                      setActiveTab('hallazgos');
                    }}>
                      Ver último resultado
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => { setEditSource(s); setShowForm(false); setManualSource(null); }}
                  >
                    ✏ Editar
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => { setManualSource(s); setShowForm(false); setEditSource(null); }}
                    className="text-amber-600 dark:text-amber-400"
                  >
                    Modo manual
                  </Button>
                  {confirmDeleteId === s.id ? (
                    <div className="ml-auto flex items-center gap-2">
                      <span className="text-xs text-gray-600 dark:text-gray-400">¿Eliminar?</span>
                      <Button size="sm" variant="ghost" onClick={() => handleEliminar(s)} className="text-red-600 font-semibold">
                        Sí
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => setConfirmDeleteId(null)}>
                        No
                      </Button>
                    </div>
                  ) : (
                    <Button size="sm" variant="ghost" onClick={() => setConfirmDeleteId(s.id)} className="ml-auto text-red-500">
                      Eliminar
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resultados del escaneo */}
      {runDetail && (
        <div className="border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 overflow-hidden">
          {/* Header del resultado */}
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 flex flex-wrap items-center gap-4">
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Resultado del escaneo #{runDetail.run.id}
              </p>
              <p className="text-xs text-gray-500">
                {runDetail.run.started_at ? new Date(runDetail.run.started_at).toLocaleString('es-CL') : ''}
                {' · '}{runDetail.run.ejecutado_por}
              </p>
            </div>
            <div className="flex gap-4 ml-auto text-center">
              {[
                { label: 'Tablas', value: runDetail.run.total_tablas },
                { label: 'Columnas', value: runDetail.run.total_columnas },
                { label: 'Hallazgos', value: runDetail.run.total_hallazgos },
                { label: 'Gaps (sin RAT)', value: runDetail.run.total_gaps, warn: true },
              ].map(m => (
                <div key={m.label}>
                  <p className={`text-lg font-bold ${m.warn && (m.value ?? 0) > 0 ? 'text-red-600' : 'text-gray-900 dark:text-gray-100'}`}>
                    {m.value ?? 0}
                  </p>
                  <p className="text-xs text-gray-500">{m.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Panel de error */}
          {runDetail.run.estado === 'error' && (
            <div className="px-5 py-6">
              <div className="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4">
                <p className="text-sm font-semibold text-red-700 dark:text-red-400 mb-1">Error en el escaneo</p>
                <p className="text-xs text-red-600 dark:text-red-300 font-mono break-all">
                  {runDetail.run.error_msg ?? 'Error desconocido al conectar con la fuente de datos.'}
                </p>
              </div>
            </div>
          )}

          {/* Tabs y contenido (solo cuando no hay error) */}
          {runDetail.run.estado !== 'error' && (<>
            <div className="flex border-b border-gray-100 dark:border-gray-800 px-5">
              {([
                { key: 'hallazgos', label: `Todos los hallazgos (${runDetail.findings.filter(f => !f.descartado).length})` },
                { key: 'gaps', label: `Gaps sin RAT (${runDetail.run.total_gaps ?? 0})` },
                { key: 'sugerencias', label: `RATs sugeridos (${runDetail.sugerencias_rat.length})` },
              ] as const).map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`py-3 px-4 text-sm border-b-2 transition-colors ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600 font-medium'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="p-5">
              {activeTab === 'hallazgos' && (
                <FindingsTable findings={runDetail.findings} filtroGaps={false} />
              )}
              {activeTab === 'gaps' && (
                <FindingsTable findings={runDetail.findings} filtroGaps={true} />
              )}
              {activeTab === 'sugerencias' && (
                <SugerenciasPanel sugerencias={runDetail.sugerencias_rat} companyId={companyId} runId={runDetail.run.id} />
              )}
            </div>
          </>)}
        </div>
      )}
    </div>
  );
}
