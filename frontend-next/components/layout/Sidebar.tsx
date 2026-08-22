'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import PasswordModal from '@/components/layout/PasswordModal';
import Select from '@/components/ui/Select';
import type { Company } from '@/types';

type Page =
  | 'dashboard'
  | 'rat'
  | 'companies'
  | 'breaches'
  | 'reportes'
  | 'usuarios'
  | 'rubros'
  | 'configuracion'
  | 'tkt_solicitud_derecho'
  | 'transparencia'
  | 'encargados-contrato'
  | 'consentimientos'
  | 'eipd'
  | 'asesor'
  ;

type NavItem = { key: Page; label: string; icon: string; roles: string[]; moduleKey?: string };
type NavGroup = { title: string; items: NavItem[] };

const NAV_GROUPS: NavGroup[] = [
  {
    title: 'Operaciones',
    items: [
      { key: 'dashboard', label: 'Dashboard', icon: '▣', roles: ['superadmin', 'admin_empresa', 'usuario'] },
      { key: 'rat', label: 'Procesos RAT', icon: '≡', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'RAT' },
      { key: 'tkt_solicitud_derecho', label: 'Tickets ARCOP+', icon: '📋', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'ARCO' },
      { key: 'breaches', label: 'Brechas', icon: '🛡', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'BRECHAS' },
    ],
  },
  {
    title: 'Cumplimiento',
    items: [
      { key: 'transparencia', label: 'Transparencia', icon: '📄', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'TRANSPARENCIA' },
      { key: 'encargados-contrato', label: 'Enc. Contrato', icon: '📝', roles: ['superadmin', 'admin_empresa'], moduleKey: 'ENCARGADOS' },
      { key: 'consentimientos', label: 'Consentimientos', icon: '✅', roles: ['superadmin', 'admin_empresa'], moduleKey: 'CONSENTIMIENTOS' },
      { key: 'eipd', label: 'EIPD', icon: '📑', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'EIPD' },
    ],
  },
  {
    title: 'Análisis',
    items: [
      { key: 'reportes', label: 'Reportes', icon: '📊', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'REPORTES' },
      { key: 'asesor', label: 'Asesor IA', icon: '🤖', roles: ['superadmin', 'admin_empresa', 'usuario'], moduleKey: 'ASESOR' },
    ],
  },
  {
    title: 'Administración',
    items: [
      { key: 'companies', label: 'Empresas', icon: '🏢', roles: ['superadmin', 'admin_empresa'] },
      { key: 'usuarios', label: 'Usuarios', icon: '👤', roles: ['superadmin'] },
      // { key: 'rubros', label: 'Rubros', icon: '🏷', roles: ['superadmin', 'admin_empresa'] }, // wizard por sector sin implementar
      { key: 'configuracion', label: 'Configuración', icon: '⚙', roles: ['superadmin', 'admin_empresa'] },
    ],
  },
];

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  companies: Company[];
  onClose?: () => void;
}

const SIDEBAR_PALETTE = {
  light: {
    bg: '#111827', border: 'rgba(55,65,81,0.5)',
    textInactive: '#9CA3AF', textActive: '#FFFFFF',
    activeBg: '#2563EB', hoverBg: '#1F2937',
    groupTitle: '#6B7280',
    selectBg: '#1F2937', selectColor: '#E5E7EB', selectBorder: '#374151',
    userText: '#E5E7EB', userRole: '#6B7280', avatarBg: '#2563EB',
    logoBg: 'linear-gradient(135deg, #2563EB, #7C3AED)',
    actionText: '#9CA3AF', actionHoverText: '#FFFFFF', actionHoverBg: '#374151',
  },
  dark: {
    bg: '#0D1117', border: 'rgba(30,41,59,0.8)',
    textInactive: '#94A3B8', textActive: '#FFFFFF',
    activeBg: '#2563EB', hoverBg: '#1E293B',
    groupTitle: '#64748B',
    selectBg: '#1E293B', selectColor: '#F1F5F9', selectBorder: '#334155',
    userText: '#F1F5F9', userRole: '#64748B', avatarBg: '#2563EB',
    logoBg: 'linear-gradient(135deg, #2563EB, #7C3AED)',
    actionText: '#94A3B8', actionHoverText: '#FFFFFF', actionHoverBg: '#334155',
  },
  mac: {
    bg: '#D4D4D4', border: 'rgba(171,171,171,0.6)',
    textInactive: '#333333', textActive: '#FFFFFF',
    activeBg: '#5EA0D7', hoverBg: '#C0C0C0',
    groupTitle: '#666666',
    selectBg: '#C8C8C8', selectColor: '#000000', selectBorder: '#ABABAB',
    userText: '#000000', userRole: '#555555', avatarBg: '#5EA0D7',
    logoBg: 'linear-gradient(135deg, #5EA0D7, #3075D1)',
    actionText: '#555555', actionHoverText: '#000000', actionHoverBg: '#B8B8B8',
  },
};

export default function Sidebar({ currentPage, onNavigate, companies, onClose }: SidebarProps) {
  const { user, company, setCompany, logout, theme, activeModules } = useApp();
  const isSuperadmin = user?.rol_global === 'superadmin';
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  const p = SIDEBAR_PALETTE[theme];

  const inicial = user?.full_name?.[0]?.toUpperCase() ?? 'U';
  const nombre = user?.full_name ?? 'Usuario';
  const rolLabel = user?.rol_global === 'superadmin' ? 'Superadmin' : user?.rol_global === 'admin_empresa' ? 'Admin empresa' : 'Usuario';

  return (
    <aside
      className="w-60 flex-shrink-0 flex flex-col h-full overflow-y-auto"
      style={{ background: p.bg }}
    >
      {/* Logo */}
      <div className="px-5 py-5 flex items-center justify-between" style={{ borderBottom: `1px solid ${p.border}` }}>
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
            style={{ background: p.logoBg }}
          >
            <span aria-hidden="true" style={{ fontSize: 18 }}>🛡</span>
          </div>
          <div>
            <div className="font-bold text-sm leading-tight" style={{ color: p.textActive }}>Custodio</div>
            <div className="text-xs" style={{ color: p.groupTitle }}>Ley 21.719</div>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition text-lg"
            style={{ color: p.groupTitle }}
            aria-label="Cerrar menú"
          >
            ←
          </button>
        )}
      </div>

      {/* Empresa activa */}
      <div className="px-4 pt-4 pb-2">
        <div className="text-xs font-semibold uppercase tracking-widest mb-2 px-1" style={{ color: p.groupTitle }}>
          Empresa activa
        </div>
        {companies.length > 0 ? (
          <Select
            aria-label="Seleccionar empresa activa"
            value={String(company?.id ?? '')}
            onChange={e => {
              const emp = companies.find(c => c.id === Number(e.target.value));
              if (emp) setCompany(emp);
            }}
            options={companies.map(c => ({ value: String(c.id), label: c.nombre }))}
            className="text-xs font-medium"
            style={{ backgroundColor: p.selectBg, color: p.selectColor, border: `1px solid ${p.selectBorder}` }}
          />
        ) : (
          <p className="text-xs px-1" style={{ color: p.groupTitle }}>Sin empresas. Crea una primero.</p>
        )}
      </div>

      {/* Navegación agrupada */}
      <div className="px-4 pt-3 pb-2 flex-1">
        <nav className="space-y-3">
          {NAV_GROUPS.map((group) => {
            const visibleItems = group.items.filter(item =>
              item.roles.includes(user?.rol_global ?? '') &&
              (isSuperadmin || !item.moduleKey || activeModules.includes(item.moduleKey))
            );
            if (visibleItems.length === 0) return null;
            return (
              <div key={group.title}>
                <div
                  className="text-[10px] font-bold uppercase mb-1.5 px-3"
                  style={{ letterSpacing: '0.08em', color: p.groupTitle }}
                >
                  {group.title}
                </div>
                <div className="space-y-0.5">
                  {visibleItems.map(item => {
                    const active = currentPage === item.key;
                    return (
                      <button
                        key={item.key}
                        onClick={() => onNavigate(item.key)}
                        aria-current={active ? 'page' : undefined}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left"
                        style={{
                          background: active ? p.activeBg : 'transparent',
                          color: active ? p.textActive : p.textInactive,
                        }}
                        onMouseEnter={e => {
                          if (!active) (e.currentTarget as HTMLElement).style.background = p.hoverBg;
                        }}
                        onMouseLeave={e => {
                          if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent';
                        }}
                      >
                        <span aria-hidden="true" className="text-base w-5 text-center">{item.icon}</span>
                        {item.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </nav>
      </div>

      {/* Usuario + logout */}
      <div className="p-4 flex-shrink-0" style={{ borderTop: `1px solid ${p.border}` }}>
        <div className="flex items-center gap-2.5 mb-3">
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
            style={{ background: p.avatarBg }}
          >
            {inicial}
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold truncate" style={{ color: p.userText }}>{nombre}</div>
            <div className="text-xs" style={{ color: p.userRole }}>{rolLabel}</div>
          </div>
        </div>
        <button
          onClick={() => setShowPasswordModal(true)}
          className="w-full py-1.5 px-3 rounded-lg text-xs font-medium transition-colors text-left"
          style={{ color: p.actionText }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.actionHoverBg; (e.currentTarget as HTMLElement).style.color = p.actionHoverText; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; (e.currentTarget as HTMLElement).style.color = p.actionText; }}
        >
          Cambiar contraseña
        </button>
        <button
          onClick={logout}
          className="w-full py-1.5 px-3 rounded-lg text-xs font-medium transition-colors text-left"
          style={{ color: p.actionText }}
          onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = p.actionHoverBg; (e.currentTarget as HTMLElement).style.color = p.actionHoverText; }}
          onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'transparent'; (e.currentTarget as HTMLElement).style.color = p.actionText; }}
        >
          Cerrar sesión
        </button>
      </div>

      {showPasswordModal && <PasswordModal onClose={() => setShowPasswordModal(false)} />}
    </aside>
  );
}
