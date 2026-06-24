'use client';

import { useEffect, useState, useCallback } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';
import type { RolEmpresa, UserCompany } from '@/types';

const ROL_LABELS: Record<RolEmpresa, string> = {
  admin: 'Administrador',
  editor: 'Editor',
  viewer: 'Solo lectura',
};

interface UserAccessPanelProps {
  companyId: number;
}

export function UserAccessPanel({ companyId }: UserAccessPanelProps) {
  const [accesos, setAccesos] = useState<UserCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [rol, setRol] = useState<RolEmpresa>('viewer');
  const [adding, setAdding] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const accesses = await api.listarAccesos(companyId);
      setAccesos(Array.isArray(accesses) ? accesses : []);
    } catch {
      toast.error('No se pudieron cargar los accesos.');
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => { load(); }, [load]);

  async function handleAdd() {
    if (!username.trim()) { toast.error('Ingresa un nombre de usuario.'); return; }
    setAdding(true);
    try {
      const uc = await api.agregarAcceso(companyId, username.trim(), rol);
      setAccesos(prev => [...prev, uc]);
      setUsername('');
      toast.success(`Acceso otorgado a "${uc.username}".`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al agregar acceso.');
    } finally {
      setAdding(false);
    }
  }

  async function handleChangeRol(userId: number, newRol: RolEmpresa) {
    try {
      const updated = await api.actualizarRolAcceso(companyId, userId, newRol);
      setAccesos(prev => prev.map(a => a.user_id === userId ? updated : a));
      toast.success('Rol actualizado.');
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al cambiar rol.');
    }
  }

  async function handleRemove(userId: number, uname: string) {
    try {
      await api.removerAcceso(companyId, userId);
      setAccesos(prev => prev.filter(a => a.user_id !== userId));
      toast.success(`Acceso de "${uname}" removido.`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al remover acceso.');
    }
  }

  return (
    <div className="mt-4 rounded-xl p-5" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
      <p className="text-sm font-semibold mb-3" style={{ color: '#111827' }}>Usuarios con acceso</p>

      {loading ? (
        <p className="text-xs" style={{ color: '#9CA3AF' }}>Cargando...</p>
      ) : (
        <div className="space-y-2 mb-4">
          {accesos.length === 0 && (
            <p className="text-xs" style={{ color: '#9CA3AF' }}>Sin usuarios asignados.</p>
          )}
          {accesos.map(a => (
            <div key={a.id} className="flex items-center gap-3 rounded-lg px-3 py-2 bg-white" style={{ border: '1px solid #E5E7EB' }}>
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium" style={{ color: '#111827' }}>{a.full_name || a.username}</span>
                <span className="text-xs ml-2" style={{ color: '#9CA3AF' }}>@{a.username}</span>
              </div>
              <select
                value={a.rol}
                onChange={e => handleChangeRol(a.user_id, e.target.value as RolEmpresa)}
                className="text-xs rounded-lg px-2 py-1 border focus:outline-none focus:ring-1 focus:ring-blue-500"
                style={{ borderColor: '#E5E7EB', color: '#374151' }}
              >
                {(Object.keys(ROL_LABELS) as RolEmpresa[]).map(r => (
                  <option key={r} value={r}>{ROL_LABELS[r]}</option>
                ))}
              </select>
              <button
                onClick={() => handleRemove(a.user_id, a.username)}
                className="text-xs px-2 py-1 rounded-lg border hover:bg-red-50 transition"
                style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
              >
                Remover
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Invitar usuario (username)</label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleAdd(); }}
            placeholder="Ej: jperez"
            className="w-full px-3 py-1.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: '#E5E7EB' }}
          />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Rol</label>
          <select
            value={rol}
            onChange={e => setRol(e.target.value as RolEmpresa)}
            className="px-3 py-1.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            {(Object.keys(ROL_LABELS) as RolEmpresa[]).map(r => (
              <option key={r} value={r}>{ROL_LABELS[r]}</option>
            ))}
          </select>
        </div>
        <button
          onClick={handleAdd}
          disabled={adding}
          className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
          style={{ background: '#2563EB' }}
        >
          {adding ? '...' : 'Agregar'}
        </button>
      </div>
    </div>
  );
}
