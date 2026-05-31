'use client';

import { useState, useEffect } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';

interface DbHealth {
  engine: string;
  database: string;
  url: string;
  status: string;
  latency_ms?: number;
  error?: string;
}

export default function ConexionPage() {
  const { user } = useApp();
  const [dbHealth, setDbHealth] = useState<DbHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);

  async function fetchDbHealth() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/health/db`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('custodio_token')}` },
      });
      const data = await res.json();
      setDbHealth(data);
    } catch {
      setDbHealth({ engine: 'unknown', url: '-', status: 'error' });
    } finally {
      setLoading(false);
    }
  }

  async function testLatency() {
    setTesting(true);
    const start = Date.now();
    try {
      await fetch(`${API_BASE}/health/db`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('custodio_token')}` },
      });
      const latency = Date.now() - start;
      setDbHealth(prev => prev ? { ...prev, latency_ms: latency } : null);
      toast.success(`Latencia: ${latency}ms`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error');
    } finally {
      setTesting(false);
    }
  }

  useEffect(() => {
    fetchDbHealth();
  }, []);

  if (user?.rol_global !== 'superadmin') {
    return (
      <div className="p-8 text-center">
        <p className="text-sm" style={{ color: '#6B7280' }}>Acceso solo para superadmin.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6" style={{ color: '#111827' }}>
        Conexión a base de datos
      </h1>

      <div className="space-y-4">
        {/* Estado de conexión */}
        <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
          <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>
            Estado actual
          </h2>

          {loading ? (
            <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : dbHealth ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm" style={{ color: '#6B7280' }}>Motor</span>
                <span className="text-sm font-medium" style={{ color: '#059669' }}>
                  {dbHealth.engine === 'postgresql' ? '● PostgreSQL (Neon)' : '● Otro'}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm" style={{ color: '#6B7280' }}>Base de datos</span>
                <span className="text-sm font-medium" style={{ color: '#059669' }}>
                  {dbHealth.database}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm" style={{ color: '#6B7280' }}>Estado BD</span>
                <span
                  className="text-sm font-medium"
                  style={{ color: dbHealth.status === 'ok' ? '#059669' : '#DC2626' }}
                >
                  {dbHealth.status === 'ok' ? '● Conectada' : '● Error'}
                </span>
              </div>

              {dbHealth.latency_ms !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: '#6B7280' }}>Latencia</span>
                  <span className="text-sm font-medium" style={{ color: '#059669' }}>
                    {dbHealth.latency_ms}ms
                  </span>
                </div>
              )}

              {dbHealth.error && (
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: '#DC2626' }}>Error</span>
                  <span className="text-sm" style={{ color: '#DC2626' }}>{dbHealth.error}</span>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Probar conexión */}
        <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
          <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>
            Probar conexión
          </h2>

          <div className="flex gap-3">
            <button
              onClick={fetchDbHealth}
              className="px-4 py-2 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
              style={{ borderColor: '#E5E7EB', color: '#374151' }}
            >
              🔄 Refrescar
            </button>
            <button
              onClick={testLatency}
              disabled={testing}
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60"
              style={{ background: '#2563EB' }}
            >
              {testing ? 'Midiendo...' : '📡 Medir latencia'}
            </button>
          </div>
        </div>

        {/* Info del sistema */}
        <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
          <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>
            Configuración del sistema
          </h2>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm" style={{ color: '#6B7280' }}>Frontend</span>
              <span className="text-sm font-mono" style={{ color: '#374151' }}>Next.js 16 (Puerto 3000)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm" style={{ color: '#6B7280' }}>Backend API</span>
              <span className="text-sm font-mono" style={{ color: '#374151' }}>{API_BASE}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}