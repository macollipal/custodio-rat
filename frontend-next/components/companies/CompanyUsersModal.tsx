'use client';

import { useEffect, useState } from 'react';
import * as api from '@/lib/api';
import type { UserCompany } from '@/types';

interface CompanyUsersModalProps {
  companyId: number;
  onClose: () => void;
}

export function CompanyUsersModal({ companyId, onClose }: CompanyUsersModalProps) {
  const [usuarios, setUsuarios] = useState<UserCompany[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.listarAccesos(companyId)
      .then((data) => {
        setUsuarios(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [companyId]);

  function rolBadge(rol: string) {
    if (rol === 'admin') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#DBEAFE', color: '#2563EB' }}>Admin</span>;
    if (rol === 'editor') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#D1FAE5', color: '#059669' }}>Editor</span>;
    return <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#F3F4F6', color: '#6B7280' }}>Viewer</span>;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 w-[560px] shadow-2xl max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold" style={{ color: '#111827' }}>Usuarios de la empresa</h3>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-sm font-bold" style={{ color: '#6B7280' }}>✕</button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
        ) : usuarios.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-2xl mb-2">👤</div>
            <p className="text-sm" style={{ color: '#6B7280' }}>No hay usuarios asignados a esta empresa.</p>
          </div>
        ) : (
          <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #D1D5DB' }}>
            <table className="w-full">
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #D1D5DB' }}>
                  <th className="px-4 py-3 text-left">Usuario</th>
                  <th className="px-4 py-3 text-right">Rol empresa</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u, i) => (
                  <tr key={u.id} style={{ borderTop: i > 0 ? '1px solid #F3F4F6' : 'none' }}>
                    <td className="px-4 py-3">
                      <div className="text-sm font-bold" style={{ color: '#111827' }}>{u.username}</div>
                      <div className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{u.full_name}</div>
                      <div className="text-xs" style={{ color: '#9CA3AF' }}>{u.email}</div>
                    </td>
                    <td className="px-4 py-3 text-right align-middle">
                      {rolBadge(u.rol)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex justify-end mt-4">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm border transition hover:bg-gray-50" style={{ borderColor: '#D1D5DB', color: '#374151' }}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
