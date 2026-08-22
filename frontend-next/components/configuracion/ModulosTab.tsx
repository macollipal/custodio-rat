'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import {
  getCompanyModules,
  toggleCompanyModule,
  type CompanyModules,
} from '@/lib/api';
import { Skeleton } from '@/components/ui/Skeleton';
import type { Company } from '@/types';

const MODULE_INFO: Record<string, { nombre: string; descripcion: string; icon: string }> = {
  RAT: {
    nombre: 'Registro de Actividades de Tratamiento',
    descripcion: 'CRUD de procesos RAT (Art. 16 Ley 21.719). Modulo core del sistema.',
    icon: '📋',
  },
  ARCO: {
    nombre: 'Solicitudes ARCOP+',
    descripcion: 'Tickets de derechos de Acceso, Rectificación, Cancelación, Oposición y Portabilidad (Art. 14).',
    icon: '✉️',
  },
  BRECHAS: {
    nombre: 'Brechas de Seguridad',
    descripcion: 'Gestión de incidentes con notificación APDP en 72h (Art. 14 sexies).',
    icon: '🚨',
  },
  EIPD: {
    nombre: 'Evaluacion de Impacto',
    descripcion: 'EIPD para tratamientos de alto riesgo (Art. 15 ter).',
    icon: '🔍',
  },
  CONSENTIMIENTOS: {
    nombre: 'Consentimientos',
    descripcion: 'Registro de consentimientos expresos y revocacion (Art. 12).',
    icon: '✅',
  },
  ENCARGADOS: {
    nombre: 'Encargados de Tratamiento',
    descripcion: 'Contratos con terceros que tratan datos por cuenta del responsable (Art. 14 quater).',
    icon: '🤝',
  },
  TRANSPARENCIA: {
    nombre: 'Politica de Transparencia',
    descripcion: 'Politica publica generada desde los RATs (Art. 14 ter).',
    icon: '🌐',
  },
  REPORTES: {
    nombre: 'Reportes Avanzados',
    descripcion: 'Reportes filtrables con exportacion CSV/PDF y drawer de detalle.',
    icon: '📊',
  },
  ASESOR: {
    nombre: 'Asesor IA',
    descripcion: 'Chat con RAG sobre Ley 21.719 y documentacion interna.',
    icon: '⚖️',
  },
};

export default function ModulosTab() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [modules, setModules] = useState<Record<string, boolean> | null>(null);
  const [loading, setLoading] = useState(false);
  const [savingKey, setSavingKey] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { listarEmpresas } = await import('@/lib/api');
        const data = await listarEmpresas();
        if (!cancelled) {
          setCompanies(data);
          if (data.length > 0) setSelectedId(data[0].id);
        }
      } catch (e) {
        if (!cancelled) {
          toast.error(e instanceof Error ? e.message : 'Error al cargar empresas.');
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoading(true);
    setModules(null);
    getCompanyModules(selectedId)
      .then((res: CompanyModules) => setModules(res.modules))
      .catch((e) => toast.error(e instanceof Error ? e.message : 'Error al cargar modulos.'))
      .finally(() => setLoading(false));
  }, [selectedId]);

  async function handleToggle(modulo: string, enabled: boolean) {
    if (!selectedId) return;
    setSavingKey(modulo);
    try {
      await toggleCompanyModule(selectedId, modulo, enabled);
      setModules((prev) => (prev ? { ...prev, [modulo]: enabled } : prev));
      toast.success(`${MODULE_INFO[modulo]?.nombre ?? modulo} ${enabled ? 'activado' : 'desactivado'}.`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al cambiar el modulo.');
    } finally {
      setSavingKey(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>
          Feature Gates por Empresa
        </h3>
        <p className="text-sm" style={{ color: '#6B7280' }}>
          Activa o desactiva modulos completos para cada empresa. Si un modulo esta
          deshabilitado, los endpoints retornaran 403 y el menu no lo mostrara.
        </p>
      </div>

      <div className="bg-white rounded-xl p-4" style={{ border: '1px solid #E5E7EB' }}>
        <label className="block text-xs font-semibold mb-2" style={{ color: '#374151' }}>
          Empresa
        </label>
        <select
          value={selectedId ?? ''}
          onChange={(e) => setSelectedId(Number(e.target.value))}
          className="w-full px-3 py-2 rounded-lg text-sm"
          style={{ border: '1px solid #D1D5DB', color: '#111827' }}
        >
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nombre} ({c.rut})
            </option>
          ))}
        </select>
      </div>

      {loading || !modules ? (
        <div className="space-y-2">
          <Skeleton height={64} />
          <Skeleton height={64} />
          <Skeleton height={64} />
        </div>
      ) : (
        <div className="space-y-2">
          {Object.keys(MODULE_INFO).map((modulo) => {
            const info = MODULE_INFO[modulo];
            const enabled = modules[modulo] ?? true;
            const saving = savingKey === modulo;
            return (
              <div
                key={modulo}
                className="bg-white rounded-lg p-4 flex items-start gap-4"
                style={{ border: '1px solid #E5E7EB' }}
              >
                <span className="text-2xl flex-shrink-0" aria-hidden="true">
                  {info.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold" style={{ color: '#111827' }}>
                      {info.nombre}
                    </span>
                    <span
                      className="text-xs px-1.5 py-0.5 rounded font-mono"
                      style={{ background: '#F3F4F6', color: '#6B7280' }}
                    >
                      {modulo}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: '#6B7280' }}>
                    {info.descripcion}
                  </p>
                </div>
                <button
                  onClick={() => handleToggle(modulo, !enabled)}
                  disabled={saving}
                  className="flex-shrink-0 relative inline-flex items-center w-12 h-6 rounded-full transition"
                  style={{
                    background: enabled ? '#059669' : '#D1D5DB',
                    cursor: saving ? 'wait' : 'pointer',
                    opacity: saving ? 0.6 : 1,
                  }}
                  aria-label={`${enabled ? 'Desactivar' : 'Activar'} ${info.nombre}`}
                  role="switch"
                  aria-checked={enabled}
                >
                  <span
                    className="inline-block w-5 h-5 rounded-full bg-white shadow transform transition"
                    style={{ transform: `translateX(${enabled ? 26 : 2}px)` }}
                  />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}