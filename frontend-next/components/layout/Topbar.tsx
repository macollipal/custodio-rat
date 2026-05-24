'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';

interface TopbarProps {
  onMenuClick: () => void;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { user, company, companies, setCompany, dashboardStats, darkMode, toggleDarkMode } = useApp();
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  const filtered = companies.filter(c =>
    c.nombre.toLowerCase().includes(search.toLowerCase()) ||
    (c.rut ?? '').toLowerCase().includes(search.toLowerCase())
  );

  const alertCount = dashboardStats
    ? (dashboardStats.eipd_pendientes ?? 0) +
      (dashboardStats.interes_legitimo_sin_test ?? 0) +
      (dashboardStats.encargados_sin_contrato ?? 0) +
      (dashboardStats.rats_vencidos ?? 0) +
      (dashboardStats.transferencias_sin_garantias ?? 0)
    : 0;

  const alertItems = [
    dashboardStats?.eipd_pendientes ? { label: `${dashboardStats.eipd_pendientes} EIPD(s) pendiente(s)`, type: 'danger' } : null,
    dashboardStats?.interes_legitimo_sin_test ? { label: `${dashboardStats.interes_legitimo_sin_test} proceso(s) sin test interés legítimo`, type: 'warning' } : null,
    dashboardStats?.encargados_sin_contrato ? { label: `${dashboardStats.encargados_sin_contrato} encargado(s) sin contrato`, type: 'warning' } : null,
    dashboardStats?.rats_vencidos ? { label: `${dashboardStats.rats_vencidos} RAT(s) vencido(s)`, type: 'danger' } : null,
    dashboardStats?.transferencias_sin_garantias ? { label: `${dashboardStats.transferencias_sin_garantias} transferencia(s) sin garantías`, type: 'warning' } : null,
  ].filter(Boolean) as { label: string; type: 'danger' | 'warning' }[];

  return (
    <div
      className="flex items-center justify-between px-4 lg:px-8 py-3 border-b"
      style={{ background: 'white', borderColor: '#E5E7EB' }}
    >
      <div className="flex items-center gap-3 relative">
        {/* Hamburger button - mobile only */}
        <button
          onClick={onMenuClick}
          aria-label="Abrir menú de navegación"
          aria-controls="main-sidebar"
          className="flex items-center justify-center w-10 h-10 rounded-lg hover:bg-gray-100 transition border border-gray-200 lg:hidden"
        >
          <span aria-hidden="true" className="text-gray-600 text-xl">☰</span>
        </button>
        <span className="text-sm" style={{ color: '#6B7280' }}>Empresa activa:</span>
        <button
          onClick={() => setOpen(o => !o)}
          aria-expanded={open}
          aria-haspopup="listbox"
          aria-label="Cambiar empresa activa"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold transition hover:bg-gray-50"
          style={{ color: '#111827', border: '1px solid #E5E7EB' }}
        >
          {company?.nombre ?? 'Sin empresa'}
          <span style={{ color: '#9CA3AF', fontSize: 10 }}>▼</span>
        </button>

        {open && (
          <div
            className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-lg z-50 overflow-hidden"
            style={{ border: '1px solid #E5E7EB', minWidth: 260, maxWidth: 340 }}
          >
            <div className="p-2 border-b" style={{ borderColor: '#E5E7EB' }}>
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Buscar empresa..."
                className="w-full px-3 py-1.5 rounded-lg text-xs border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ borderColor: '#E5E7EB' }}
                autoFocus
                onClick={e => e.stopPropagation()}
              />
            </div>
            <div className="max-h-64 overflow-y-auto py-1">
              {filtered.length === 0 ? (
                <p className="text-xs px-3 py-2" style={{ color: '#9CA3AF' }}>Sin resultados</p>
              ) : (
                filtered.map(emp => (
                  <button
                    key={emp.id}
                    onClick={() => {
                      setCompany(emp);
                      setOpen(false);
                      setSearch('');
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-gray-50 transition"
                    style={{ background: emp.id === company?.id ? '#EFF6FF' : undefined }}
                  >
                    <div>
                      <div className="text-sm font-medium" style={{ color: '#111827' }}>{emp.nombre}</div>
                      <div className="text-xs" style={{ color: '#9CA3AF' }}>{emp.rut}</div>
                    </div>
                    {emp.id === company?.id && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#DBEAFE', color: '#2563EB' }}>✓</span>
                    )}
                  </button>
                ))
              )}
            </div>
            <div className="p-2 border-t text-center" style={{ borderColor: '#E5E7EB' }}>
              <button
                onClick={() => { setOpen(false); setSearch(''); }}
                className="text-xs px-3 py-1 rounded-lg hover:bg-gray-100 transition"
                style={{ color: '#6B7280' }}
              >
                Cerrar
              </button>
            </div>
          </div>
        )}
      </div>

<div className="flex items-center gap-3">
        <button
          onClick={toggleDarkMode}
          aria-label={darkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          className="p-2 rounded-lg transition hover:bg-gray-100"
        >
          <span aria-hidden="true" role="img" style={{ fontSize: 16 }}>{darkMode ? '☀️' : '🌙'}</span>
        </button>
        {alertCount > 0 && (
          <div className="relative">
            <button
              onClick={() => setNotifOpen(o => !o)}
              aria-label={`Alertas de cumplimiento: ${alertCount} alerta${alertCount !== 1 ? 's' : ''}`}
              aria-expanded={notifOpen}
              aria-haspopup="menu"
              className="relative p-2 rounded-lg transition hover:bg-gray-100"
            >
              <span aria-hidden="true" role="img" style={{ fontSize: 18 }}>🔔</span>
              <span
                className="absolute top-1 right-1 w-4 h-4 rounded-full text-xs font-bold flex items-center justify-center"
                style={{ background: '#B91C1C', color: 'white', fontSize: 9 }}
                aria-hidden="true"
              >
                {alertCount > 9 ? '9+' : alertCount}
              </span>
            </button>
            {notifOpen && (
              <div
                role="menu"
                aria-label="Alertas de cumplimiento"
                className="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-lg z-50 overflow-hidden"
                style={{ border: '1px solid #E5E7EB', minWidth: 280, maxWidth: 'calc(100vw - 32px)' }}
                onKeyDown={e => { if (e.key === 'Escape') setNotifOpen(false); }}
              >
                <div className="px-4 py-3 border-b font-semibold text-sm" style={{ borderColor: '#E5E7EB', color: '#111827' }}>
                  Alertas de cumplimiento
                </div>
                <div className="py-1 max-h-64 overflow-y-auto">
                  {alertItems.length === 0 ? (
                    <p className="text-xs px-4 py-3" style={{ color: '#9CA3AF' }}>Sin alertas</p>
                  ) : (
                    alertItems.map((item, i) => (
                      <div key={i} className="flex items-start gap-2 px-4 py-2 hover:bg-gray-50">
                        <span>{item.type === 'danger' ? '🔴' : '🟡'}</span>
                        <span className="text-xs" style={{ color: '#374151' }}>{item.label}</span>
                      </div>
                    ))
                  )}
                </div>
                <div className="px-4 py-2 border-t text-center" style={{ borderColor: '#E5E7EB' }}>
                  <button
                    onClick={() => setNotifOpen(false)}
                    className="text-xs px-3 py-1 rounded-lg hover:bg-gray-100 transition"
                    style={{ color: '#6B7280' }}
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold" style={{ color: '#111827' }}>
            {user?.full_name ?? user?.username}
          </span>
          {user?.rol_global === 'superadmin' && (
            <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: '#F3E8FF', color: '#7C3AED' }}>
              Superadmin
            </span>
          )}
          {user?.rol_global === 'admin_empresa' && (
            <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: '#DBEAFE', color: '#2563EB' }}>
              Admin empresa
            </span>
          )}
          {user?.rol_global === 'usuario' && (
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#F3F4F6', color: '#6B7280' }}>
              Usuario
            </span>
          )}
        </div>
      </div>
    </div>
  );
}