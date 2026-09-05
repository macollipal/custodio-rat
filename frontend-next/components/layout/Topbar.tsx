'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';

interface TopbarProps {
  onMenuClick: () => void;
}

const TOPBAR_PALETTE = {
  light: {
    bg: '#FFFFFF', border: '#E5E7EB',
    textPrimary: '#111827', textSecondary: '#6B7280', textMuted: '#9CA3AF',
    inputBorder: '#E5E7EB', hoverBg: '#F9FAFB',
    activeBg: '#EFF6FF', accentText: '#2563EB', accentBg: '#DBEAFE',
    dropdownBg: '#FFFFFF',
  },
  dark: {
    bg: '#0F172A', border: '#334155',
    textPrimary: '#F1F5F9', textSecondary: '#94A3B8', textMuted: '#64748B',
    inputBorder: '#334155', hoverBg: '#1E293B',
    activeBg: '#1E3A5F', accentText: '#60A5FA', accentBg: '#1E3A5F',
    dropdownBg: '#1E293B',
  },
  mac: {
    bg: '#E8E8E8', border: '#ABABAB',
    textPrimary: '#000000', textSecondary: '#555555', textMuted: '#888888',
    inputBorder: '#ABABAB', hoverBg: '#D4D4D4',
    activeBg: '#C5E0F5', accentText: '#3075D1', accentBg: '#C5E0F5',
    dropdownBg: '#E8E8E8',
  },
};

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { user, company, companies, setCompany, dashboardStats, theme, cycleTheme } = useApp();
  const p = TOPBAR_PALETTE[theme];
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
      style={{ background: p.bg, borderColor: p.border }}
    >
      <div className="flex items-center gap-3 relative">
        {/* Hamburger button - mobile only */}
        <button
          onClick={onMenuClick}
          aria-label="Abrir menú de navegación"
          aria-controls="main-sidebar"
          className="flex items-center justify-center w-10 h-10 rounded-lg transition lg:hidden"
          style={{ border: `1px solid ${p.border}`, color: p.textSecondary }}
        >
          <span aria-hidden="true" className="text-xl">☰</span>
        </button>
        <span className="text-sm" style={{ color: p.textSecondary }}>Empresa activa:</span>
        <button
          onClick={() => setOpen(o => !o)}
          aria-expanded={open}
          aria-haspopup="listbox"
          aria-label="Cambiar empresa activa"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold transition"
          style={{ color: p.textPrimary, border: `1px solid ${p.border}` }}
        >
          {company?.nombre ?? 'Sin empresa'}
          <span style={{ color: p.textMuted, fontSize: 10 }}>▼</span>
        </button>

        {open && (
          <div
            className="absolute top-full left-0 mt-1 rounded-xl shadow-lg z-50 overflow-hidden"
            style={{ background: p.dropdownBg, border: `1px solid ${p.border}`, minWidth: 260, maxWidth: 340 }}
          >
            <div className="p-2 border-b" style={{ borderColor: p.border }}>
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Buscar empresa..."
                className="w-full px-3 py-1.5 rounded-lg text-xs border focus:outline-none focus:ring-2 focus:ring-blue-500"
                style={{ borderColor: p.inputBorder, background: p.hoverBg, color: p.textPrimary }}
                autoFocus
                onClick={e => e.stopPropagation()}
              />
            </div>
            <div className="max-h-64 overflow-y-auto py-1">
              {filtered.length === 0 ? (
                <p className="text-xs px-3 py-2" style={{ color: p.textSecondary }}>Sin resultados</p>
              ) : (
                filtered.map(emp => (
                  <button
                    key={emp.id}
                    onClick={() => {
                      setCompany(emp);
                      setOpen(false);
                      setSearch('');
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 text-left transition"
                    style={{ background: emp.id === company?.id ? p.activeBg : undefined }}
                    onMouseEnter={e => { if (emp.id !== company?.id) (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
                    onMouseLeave={e => { if (emp.id !== company?.id) (e.currentTarget as HTMLElement).style.background = ''; }}
                  >
                    <div>
                      <div className="text-sm font-medium" style={{ color: p.textPrimary }}>{emp.nombre}</div>
                      <div className="text-xs" style={{ color: p.textSecondary }}>{emp.rut}</div>
                    </div>
                    {emp.id === company?.id && (
                      <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: p.accentBg, color: p.accentText }}>✓</span>
                    )}
                  </button>
                ))
              )}
            </div>
            <div className="p-2 border-t text-center" style={{ borderColor: p.border }}>
              <button
                onClick={() => { setOpen(false); setSearch(''); }}
                className="text-xs px-3 py-1 rounded-lg transition"
                style={{ color: p.textSecondary }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
              >
                Cerrar
              </button>
            </div>
          </div>
        )}
      </div>

<div className="flex items-center gap-3">
        <button
          onClick={cycleTheme}
          aria-label={theme === 'light' ? 'Cambiar a modo oscuro' : theme === 'dark' ? 'Cambiar a tema Mac Aqua' : 'Cambiar a modo claro'}
          className="p-2 rounded-lg transition"
          style={{ color: p.textPrimary }}
          title={theme === 'light' ? 'Modo claro' : theme === 'dark' ? 'Modo oscuro' : 'Tema Mac Aqua'}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
        >
          <span aria-hidden="true" role="img" style={{ fontSize: 16 }}>
            {theme === 'light' ? '🌞' : theme === 'dark' ? '🌙' : '🍎'}
          </span>
        </button>
        {alertCount > 0 && (
          <div className="relative">
            <button
              onClick={() => setNotifOpen(o => !o)}
              aria-label={`Alertas de cumplimiento: ${alertCount} alerta${alertCount !== 1 ? 's' : ''}`}
              aria-expanded={notifOpen}
              aria-haspopup="menu"
              className="relative p-2 rounded-lg transition"
            style={{ color: p.textPrimary }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
            onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
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
                className="absolute right-0 top-full mt-1 rounded-xl shadow-lg z-50 overflow-hidden"
                style={{ background: p.dropdownBg, border: `1px solid ${p.border}`, minWidth: 280, maxWidth: 'calc(100vw - 32px)' }}
                onKeyDown={e => { if (e.key === 'Escape') setNotifOpen(false); }}
              >
                <div className="px-4 py-3 border-b font-semibold text-sm" style={{ borderColor: p.border, color: p.textPrimary }}>
                  Alertas de cumplimiento
                </div>
                <div className="py-1 max-h-64 overflow-y-auto">
                  {alertItems.length === 0 ? (
                    <p className="text-xs px-4 py-3" style={{ color: p.textSecondary }}>Sin alertas</p>
                  ) : (
                    alertItems.map((item, i) => (
                      <div key={i} className="flex items-start gap-2 px-4 py-2" style={{ color: p.textPrimary }}
                        onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
                        onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
                      >
                        <span>{item.type === 'danger' ? '🔴' : '🟡'}</span>
                        <span className="text-xs">{item.label}</span>
                      </div>
                    ))
                  )}
                </div>
                <div className="px-4 py-2 border-t text-center" style={{ borderColor: p.border }}>
                  <button
                    onClick={() => setNotifOpen(false)}
                    className="text-xs px-3 py-1 rounded-lg transition"
                    style={{ color: p.textSecondary }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.hoverBg; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = ''; }}
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold" style={{ color: p.textPrimary }}>
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