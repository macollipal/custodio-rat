'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { API_BASE } from '@/lib/constants';
import * as api from '@/lib/api';
import type { Company } from '@/types';

function fmtDateTime(val: string | undefined | null): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' });
}

export function EmpresasManagementTab() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<Company | null>(null);
  const [password, setPassword] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    try {
      const res = await api.apiFetch(`${API_BASE}/companies/?incluir_inactivas=true`);
      const data = await res.json();
      setCompanies(data.empresas || []);
    } catch {
      toast.error('Error al cargar empresas.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleReactivar(id: number) {
    try {
      await api.reactivarEmpresa(id);
      toast.success('Empresa reactivada.');
      await load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al reactivar.');
    }
  }

  async function handleHardDelete() {
    if (!deleteTarget) return;
    if (!password.trim()) { setError('Ingresa tu contraseña.'); return; }
    setDeleting(true);
    setError('');
    try {
      await api.hardDeleteEmpresa(deleteTarget.id, password);
      toast.success(`Empresa "${deleteTarget.nombre}" eliminada permanentemente.`);
      setDeleteTarget(null);
      setPassword('');
      await load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Contraseña incorrecta.');
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border" style={{ borderColor: '#E5E7EB' }}>
        <div className="px-5 py-4 border-b" style={{ borderColor: '#E5E7EB' }}>
          <h2 className="text-base font-semibold" style={{ color: '#111827' }}>Gestión de Empresas</h2>
          <p className="text-sm mt-0.5" style={{ color: '#6B7280' }}>
            Ver todas las empresas e eliminar permanentemente (superadmin).
          </p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm" style={{ color: '#6B7280' }}>Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ background: '#F9FAFB' }}>
                  <th className="px-4 py-3 text-left font-medium" style={{ color: '#374151' }}>Empresa</th>
                  <th className="px-4 py-3 text-left font-medium" style={{ color: '#374151' }}>RUT</th>
                  <th className="px-4 py-3 text-left font-medium" style={{ color: '#374151' }}>DPO</th>
                  <th className="px-4 py-3 text-left font-medium" style={{ color: '#374151' }}>Estado</th>
                  <th className="px-4 py-3 text-left font-medium" style={{ color: '#374151' }}>Desactivada</th>
                  <th className="px-4 py-3 text-right font-medium" style={{ color: '#374151' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {companies.map(emp => (
                  <tr key={emp.id} className="border-t" style={{ borderColor: '#E5E7EB' }}>
                    <td className="px-4 py-3 font-medium" style={{ color: '#111827' }}>{emp.nombre}</td>
                    <td className="px-4 py-3" style={{ color: '#374151' }}>{emp.rut}</td>
                    <td className="px-4 py-3" style={{ color: '#374151' }}>{emp.email_dpo || '—'}</td>
                    <td className="px-4 py-3">
                      {emp.activa !== false ? (
                        <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#DCFCE7', color: '#065F46' }}>Activa</span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEE2E2', color: '#991B1B' }}>Desactivada</span>
                      )}
                    </td>
                    <td className="px-4 py-3" style={{ color: '#6B7280' }}>
                      {emp.desactivada_at ? fmtDateTime(emp.desactivada_at) : '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex gap-2 justify-end">
                        {emp.activa === false && (
                          <button
                            onClick={() => handleReactivar(emp.id)}
                            className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-blue-50"
                            style={{ borderColor: '#BFDBFE', color: '#1D4ED8' }}
                          >
                            Reactivar
                          </button>
                        )}
                        <button
                          onClick={() => { setDeleteTarget(emp); setPassword(''); setError(''); }}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-red-50"
                          style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
                        >
                          Eliminar permanentemente
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {companies.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center" style={{ color: '#9CA3AF' }}>Sin empresas registradas.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div className="px-6 py-5 border-b" style={{ borderColor: '#E5E7EB' }}>
              <h3 className="text-lg font-bold" style={{ color: '#111827' }}>Eliminar empresa</h3>
              <p className="text-sm mt-1" style={{ color: '#DC2626' }}>
                Esta acción es <strong>irreversible</strong>. Se eliminarán todos los datos de "{deleteTarget.nombre}".
              </p>
            </div>
            <div className="px-6 py-5 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>
                  Contraseña de administrador
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Tu contraseña"
                  className="w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-red-500"
                  style={{ borderColor: error ? '#FCA5A5' : '#D1D5DB' }}
                  onKeyDown={e => e.key === 'Enter' && handleHardDelete()}
                />
                {error && <p className="mt-1.5 text-xs" style={{ color: '#DC2626' }}>{error}</p>}
              </div>
            </div>
            <div className="px-6 py-4 flex gap-3 justify-end" style={{ background: '#F9FAFB', borderColor: '#E5E7EB' }}>
              <button
                onClick={() => { setDeleteTarget(null); setPassword(''); setError(''); }}
                className="px-4 py-2 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
                style={{ borderColor: '#E5E7EB', color: '#374151' }}
                disabled={deleting}
              >
                Cancelar
              </button>
              <button
                onClick={handleHardDelete}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition hover:opacity-90"
                style={{ background: '#DC2626' }}
                disabled={deleting || !password.trim()}
              >
                {deleting ? 'Eliminando...' : 'Eliminar permanentemente'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
