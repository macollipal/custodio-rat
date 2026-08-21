'use client';

import { useState, useEffect, useCallback } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import { getDbHealth, getAuditoriaGlobal, type DbHealth } from '@/lib/api';
import StorageTab from '@/components/configuracion/StorageTab';
import AsesorCorpusTab from '@/components/configuracion/AsesorCorpusTab';
import { EmpresasManagementTab } from '@/components/configuracion/EmpresasManagementTab';
import { FeriadosTab } from '@/components/configuracion/FeriadosTab';
import ModulosTab from '@/components/configuracion/ModulosTab';
import { Button } from '@/components/ui/Button';

interface AuditEntry {
  id: number;
  rat_id: number;
  accion: string;
  usuario: string;
  timestamp: string;
  detalle?: string;
}

const BASE_TABS = [
  { key: 'sistema', label: 'Sistema' },
  { key: 'registros', label: 'Último log' },
  { key: 'exportacion', label: 'Exportación' },
  { key: 'almacenamiento', label: 'Almacenamiento' },
  { key: 'feriados', label: 'Feriados' },
];

function getTabs(isSuperadmin: boolean) {
  if (!isSuperadmin) return BASE_TABS;
  return [
    ...BASE_TABS.slice(0, 2),
    { key: 'asesor_corpus', label: 'Asesor · Corpus' },
    { key: 'empresas', label: 'Gestión Empresas' },
    { key: 'modulos', label: 'Módulos' },
    ...BASE_TABS.slice(2),
  ];
}

const EXPORT_KEY = 'custodio_export_config';

interface ExportConfig {
  formatoPredeterminado: 'csv' | 'pdf';
  incluirAuditoria: boolean;
  nombreConRut: boolean;
}

const PAGE_SIZE = 15;

export default function ConfiguracionPage() {
  const { user, company } = useApp();
  const [tab, setTab] = useState('sistema');
  const isSuperadmin = user?.rol_global === 'superadmin';
  const TABS = getTabs(isSuperadmin);
  const [dbHealth, setDbHealth] = useState<DbHealth | null>(null);
  const [loadingDb, setLoadingDb] = useState(true);
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [exportConfig, setExportConfig] = useState<ExportConfig>(() => {
    if (typeof window === 'undefined') return { formatoPredeterminado: 'pdf', incluirAuditoria: true, nombreConRut: true };
    const saved = localStorage.getItem(EXPORT_KEY);
    return saved ? JSON.parse(saved) : { formatoPredeterminado: 'pdf', incluirAuditoria: true, nombreConRut: true };
  });

  const fetchDbHealth = useCallback(async () => {
    setLoadingDb(true);
    try {
      setDbHealth(await getDbHealth());
    } catch {
      setDbHealth({ engine: 'unknown', url: '-', status: 'error' });
    } finally {
      setLoadingDb(false);
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    if (!company?.id) return;
    setLoadingLogs(true);
    try {
      const data = await getAuditoriaGlobal(company.id);
      setAuditLogs(Array.isArray(data) ? data.slice(-20).reverse() : []);
    } catch {
      toast.error('No se pudieron cargar los registros.');
    } finally {
      setLoadingLogs(false);
    }
  }, [company?.id]);

  function formatoAccion(accion: string) {
    const map: Record<string, { label: string; color: string }> = {
      crear: { label: 'Crear', color: '#059669' },
      editar: { label: 'Editar', color: '#2563EB' },
      eliminar: { label: 'Eliminar', color: '#DC2626' },
      duplicar: { label: 'Duplicar', color: '#7C3AED' },
      revision: { label: 'Revisión', color: '#D97706' },
    };
    return map[accion] ?? { label: accion, color: '#6B7280' };
  }

  function formatearFecha(ts: string) {
    if (!ts) return '—';
    return new Date(ts).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
  }

  useEffect(() => {
    if (tab === 'sistema') fetchDbHealth();
    if (tab === 'registros') fetchAuditLogs();
  }, [tab, company?.id, fetchAuditLogs, fetchDbHealth]);

  useEffect(() => {
    localStorage.setItem(EXPORT_KEY, JSON.stringify(exportConfig));
  }, [exportConfig]);

  const cardCls = 'bg-white rounded-xl p-6 shadow-sm';
  const labelCls = 'text-sm font-medium';
  const valueCls = 'text-sm font-mono';

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Configuración</h1>
      </div>

      <div className="flex gap-1 border-b" style={{ borderColor: '#E5E7EB' }}>
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5"
            style={{
              borderColor: tab === t.key ? '#2563EB' : 'transparent',
              color: tab === t.key ? '#2563EB' : '#6B7280',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'sistema' && (
        <div className="space-y-6">
          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Estado del sistema</h2>
            {loadingDb ? (
              <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
            ) : dbHealth ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Motor</span>
                  <span className={valueCls} style={{ color: '#059669' }}>
                    {dbHealth.engine === 'postgresql' ? 'PostgreSQL (Neon)' : 'Otro'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>URL</span>
                  <span className={valueCls} style={{ color: '#374151' }} title={dbHealth.url}>
                    {(() => {
                      const u = (dbHealth.url || '').split('?')[0];
                      const parts = u.split('/');
                      const host = parts[0] || '';
                      const db = parts.slice(1).join('/');
                      return `${host.split('.')[0]} / ${db}`;
                    })()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Estado BD</span>
                  <span className={labelCls} style={{ color: dbHealth.status === 'ok' ? '#059669' : '#DC2626' }}>
                    {dbHealth.status === 'ok' ? 'Conectada' : 'Error'}
                  </span>
                </div>
                {dbHealth.latency_ms !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className={labelCls} style={{ color: '#6B7280' }}>Latencia</span>
                    <span className={labelCls} style={{ color: '#059669' }}>{dbHealth.latency_ms}ms</span>
                  </div>
                )}
                {dbHealth.error && (
                  <div className="p-3 rounded-lg" style={{ background: '#FEF2F2' }}>
                    <span className="text-sm" style={{ color: '#DC2626' }}>{dbHealth.error}</span>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Configuración del sistema</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Frontend</span>
                <span className={valueCls} style={{ color: '#374151' }}>Next.js 16</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Backend API</span>
                <span className={valueCls} style={{ color: '#374151' }}>{API_BASE}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Entorno</span>
                <span className={valueCls} style={{ color: '#374151' }}>
                  {typeof window !== 'undefined' && window.location.hostname.includes('vercel') ? 'Producción (Vercel)' : 'Desarrollo local'}
                </span>
              </div>
            </div>
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Usuario actual</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Nombre</span>
                <span className={labelCls} style={{ color: '#374151' }}>{user?.full_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Username</span>
                <span className={valueCls} style={{ color: '#374151' }}>{user?.username}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Rol</span>
                <span className={labelCls} style={{ color: '#374151' }}>
                  {user?.rol_global === 'superadmin' ? 'Superadmin' : user?.rol_global === 'admin_empresa' ? 'Admin empresa' : 'Usuario'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className={labelCls} style={{ color: '#6B7280' }}>Empresa activa</span>
                <span className={labelCls} style={{ color: '#374151' }}>{company?.nombre ?? 'Ninguna'}</span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={fetchDbHealth}>
              🔄 Refrescar estado
            </Button>
          </div>
        </div>
      )}

      {tab === 'registros' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold" style={{ color: '#111827' }}>Últimos registros de auditoría</h2>
            <Button
              variant="secondary"
              size="sm"
              onClick={fetchAuditLogs}
              aria-label="Refrescar registros"
            >
              🔄
            </Button>
          </div>

          {loadingLogs ? (
            <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : auditLogs.length === 0 ? (
            <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>No hay registros de auditoría.</p>
          ) : (
            <div className="space-y-2">
              {auditLogs.map(log => {
                const { label, color } = formatoAccion(log.accion);
                return (
                  <div
                    key={log.id}
                    className="flex items-start gap-3 p-3 rounded-lg"
                    style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <span
                        className="inline-block px-2 py-0.5 rounded text-xs font-semibold"
                        style={{ background: `${color}20`, color }}
                      >
                        {label}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-semibold" style={{ color: '#111827' }}>
                          RAT #{log.rat_id ?? '—'}
                        </span>
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>·</span>
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>{log.usuario ?? '—'}</span>
                      </div>
                      {log.detalle && (
                        <p className="text-xs truncate" style={{ color: '#6B7280' }} title={log.detalle}>
                          {log.detalle.length > 100 ? log.detalle.slice(0, 100) + '...' : log.detalle}
                        </p>
                      )}
                    </div>
                    <div className="flex-shrink-0 text-xs" style={{ color: '#9CA3AF' }}>
                      {formatearFecha(log.timestamp)}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {tab === 'exportacion' && (
        <div className="space-y-6">
          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-1" style={{ color: '#111827' }}>Configuración de exportación</h2>
            <p className="text-xs mb-6" style={{ color: '#9CA3AF' }}>
              Estos ajustes se guardan en tu navegador y se aplican a todas las exportaciones.
            </p>

            <div className="space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Formato predeterminado</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Se usará al exportar desde el listado de RATs</p>
                </div>
                <select
                  value={exportConfig.formatoPredeterminado}
                  onChange={e => setExportConfig(c => ({ ...c, formatoPredeterminado: e.target.value as 'csv' | 'pdf' }))}
                  className="px-3 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
                  style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', minWidth: 140 }}
                >
                  <option value="pdf">PDF</option>
                  <option value="csv">CSV</option>
                </select>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Nombre de empresa en archivo</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Incluye RUT en el nombre del archivo exportado</p>
                </div>
                <button
                  role="switch"
                  aria-checked={exportConfig.nombreConRut}
                  onClick={() => setExportConfig(c => ({ ...c, nombreConRut: !c.nombreConRut }))}
                  className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                  style={{ background: exportConfig.nombreConRut ? '#2563EB' : '#D1D5DB' }}
                >
                  <span
                    className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                    style={{ transform: exportConfig.nombreConRut ? 'translateX(22px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:justify-between">
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>Incluir historial de auditoría</p>
                  <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Agrega el registro de cambios al exportar PDF individual</p>
                </div>
                <button
                  role="switch"
                  aria-checked={exportConfig.incluirAuditoria}
                  onClick={() => setExportConfig(c => ({ ...c, incluirAuditoria: !c.incluirAuditoria }))}
                  className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                  style={{ background: exportConfig.incluirAuditoria ? '#2563EB' : '#D1D5DB' }}
                >
                  <span
                    className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                    style={{ transform: exportConfig.incluirAuditoria ? 'translateX(22px)' : 'translateX(2px)' }}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
            <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Acerca de los formatos</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📄</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>PDF</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Formato oficial para presentar ante la APDP. Incluye todos los campos y es apta para impresión.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📊</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>CSV</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Hoja de cálculo para análisis de datos. Compatible con Excel y Google Sheets.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-sm flex-shrink-0" aria-hidden="true">📋</span>
                <div>
                  <p className={labelCls} style={{ color: '#374151' }}>CNI (APDC)</p>
                  <p className="text-xs" style={{ color: '#9CA3AF' }}>Formato oficial de la Agencia de Protección de Datos Pessoales para presentar el libro de actividades.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === 'almacenamiento' && <StorageTab />}

      {tab === 'asesor_corpus' && isSuperadmin && <AsesorCorpusTab />}

      {tab === 'empresas' && isSuperadmin && <EmpresasManagementTab />}

      {tab === 'modulos' && isSuperadmin && <ModulosTab />}

      {tab === 'feriados' && <FeriadosTab currentTab={tab} />}
    </div>
  );
}
