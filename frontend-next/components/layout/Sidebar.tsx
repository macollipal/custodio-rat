'use client';

import { useState } from 'react';
import { useApp } from '@/context/AppContext';
import PasswordModal from '@/components/layout/PasswordModal';
import type { Company } from '@/types';

type Page = 'dashboard' | 'rat' | 'companies' | 'breaches' | 'reportes';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  companies: Company[];
}

const NAV_ITEMS: { key: Page; label: string; icon: string }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: '▣' },
  { key: 'rat', label: 'Procesos RAT', icon: '≡' },
  { key: 'reportes', label: 'Reportes', icon: '📊' },
  { key: 'breaches', label: 'Brechas', icon: '🛡' },
  { key: 'companies', label: 'Empresas', icon: '🏢' },
  { key: 'usuarios', label: 'Usuarios', icon: '👤' },
];

export default function Sidebar({ currentPage, onNavigate, companies }: SidebarProps) {
  const { user, company, setCompany, logout, darkMode, toggleDarkMode } = useApp();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [ratInfoOpen, setRatInfoOpen] = useState(false);

  const inicial = user?.full_name?.[0]?.toUpperCase() ?? 'U';
  const nombre = user?.full_name ?? 'Usuario';
  const rolLabel = user?.rol_global === 'superadmin' ? 'Superadmin' : user?.rol_global === 'admin_empresa' ? 'Admin empresa' : 'Usuario';

  const allNavItems: { key: Page; label: string; icon: string; roles: string[] }[] = [
    { key: 'dashboard', label: 'Dashboard', icon: '▣', roles: ['superadmin', 'admin_empresa', 'usuario'] },
    { key: 'rat', label: 'Procesos RAT', icon: '≡', roles: ['superadmin', 'admin_empresa', 'usuario'] },
    { key: 'reportes', label: 'Reportes', icon: '📊', roles: ['superadmin', 'admin_empresa', 'usuario'] },
    { key: 'breaches', label: 'Brechas', icon: '🛡', roles: ['superadmin', 'admin_empresa', 'usuario'] },
    { key: 'companies', label: 'Empresas', icon: '🏢', roles: ['superadmin', 'admin_empresa'] },
    { key: 'usuarios', label: 'Usuarios', icon: '👤', roles: ['superadmin'] },
  ];

  return (
    <aside
      className="w-60 flex-shrink-0 flex flex-col h-full"
      style={{ background: '#111827' }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-700/50">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)' }}
          >
            🛡
          </div>
          <div>
            <div className="text-white font-bold text-sm leading-tight">Custodio</div>
            <div className="text-gray-500 text-xs">Ley 21.719</div>
          </div>
        </div>
      </div>

      {/* Empresa activa */}
      <div className="px-4 pt-4 pb-2">
        <div className="text-gray-500 text-xs font-semibold uppercase tracking-widest mb-2 px-1">
          Empresa activa
        </div>
        {companies.length > 0 ? (
          <select
            value={company?.id ?? ''}
            onChange={e => {
              const emp = companies.find(c => c.id === Number(e.target.value));
              if (emp) setCompany(emp);
            }}
            className="w-full px-3 py-2 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            style={{
              background: '#1F2937',
              color: '#E5E7EB',
              border: '1px solid #374151',
            }}
          >
            {companies.map(c => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
        ) : (
          <p className="text-gray-600 text-xs px-1">Sin empresas. Crea una primero.</p>
        )}
      </div>

      {/* Navegación */}
      <div className="px-4 pt-3 pb-2 flex-1">
        <div className="text-gray-500 text-xs font-semibold uppercase tracking-widest mb-2 px-1">
          Navegación
        </div>
        <nav className="space-y-0.5">
          {allNavItems.filter(item => item.roles.includes(user?.rol_global ?? '')).map(item => {
            const active = currentPage === item.key;
            return (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-left"
                style={{
                  background: active ? '#2563EB' : 'transparent',
                  color: active ? 'white' : '#9CA3AF',
                }}
                onMouseEnter={e => {
                  if (!active) (e.currentTarget as HTMLElement).style.background = '#1F2937';
                }}
                onMouseLeave={e => {
                  if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent';
                }}
              >
                <span className="text-base w-5 text-center">{item.icon}</span>
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Info RAT */}
      <div className="px-4 pb-2">
        <div className="relative">
          <button
            onClick={() => setRatInfoOpen(v => !v)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors"
            style={{ color: '#9CA3AF', background: ratInfoOpen ? '#1F2937' : 'transparent' }}
            onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = '#1F2937'; }}
            onMouseLeave={e => { if (!ratInfoOpen) (e.currentTarget as HTMLElement).style.background = 'transparent'; }}
          >
            <span className="text-sm">❓</span> ¿Qué es un RAT?
          </button>
          {ratInfoOpen && (
            <div
              className="absolute left-full top-0 ml-2 bg-white rounded-xl shadow-2xl z-50 overflow-hidden"
              style={{ border: '1px solid #E5E7EB', width: 320, color: '#374151' }}
              onClick={e => e.stopPropagation()}
            >
              <div className="px-4 py-3 border-b font-semibold text-sm" style={{ borderColor: '#E5E7EB', color: '#111827', background: '#F9FAFB' }}>
                📋 ¿Qué es un RAT?
              </div>
              <div className="p-4 text-xs leading-relaxed" style={{ color: '#6B7280', maxHeight: 360, overflowY: 'auto' }}>
                <p className="mb-2">
                  <strong style={{ color: '#111827' }}>Registro de Actividades de Tratamiento</strong> — Art. 16 Ley 21.719.
                  Todo responsable que trata datos personales debe mantener un registro que documente:
                </p>
                <ul className="list-disc list-inside mb-3 space-y-1">
                  <li>Qué datos se tratan</li>
                  <li>Para qué finalidad</li>
                  <li>Con qué base legal</li>
                  <li>Cuánto tiempo se conservan</li>
                  <li>Si se transfieren internacionalmente</li>
                </ul>
                <p className="mb-2" style={{ color: '#111827' }}>
                  <strong>7 campos obligatorios mínimo:</strong> nombre_proceso, categoria_datos, categoria_titulares, finalidad, base_legal, fuente_datos, plazo_retencion.
                </p>
                <p className="mb-2" style={{ color: '#111827' }}>
                  <strong>Ejemplos de procesos RAT:</strong>
                </p>
                <ul className="list-disc list-inside space-y-1">
                  <li>"Gestión de nómina" → obligación legal</li>
                  <li>"Marketing por email" → consentimiento</li>
                  <li>"Control de acceso biométrico" → obligación legal + EIPD</li>
                  <li>"Videovigilancia" → interés legítimo</li>
                  <li>"Facturación electrónica" → obligación legal</li>
                </ul>
                <div className="mt-3 p-2 rounded-lg text-center" style={{ background: '#EFF6FF', color: '#2563EB' }}>
                  Cuando termines tu primer RAT, puedes duplicarlo como plantilla para crear más rápidamente.
                </div>
              </div>
              <div className="px-4 py-2 border-t text-center" style={{ borderColor: '#E5E7EB' }}>
                <button
                  onClick={() => setRatInfoOpen(false)}
                  className="text-xs px-3 py-1 rounded-lg hover:bg-gray-100 transition"
                  style={{ color: '#6B7280' }}
                >
                  Cerrar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Usuario + logout */}
      <div className="border-t border-gray-700/50 p-4">
        <div className="flex items-center gap-2.5 mb-3">
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
            style={{ background: '#2563EB' }}
          >
            {inicial}
          </div>
          <div className="min-w-0">
            <div className="text-gray-200 text-xs font-semibold truncate">{nombre}</div>
            <div className="text-gray-500 text-xs">{rolLabel}</div>
          </div>
        </div>
        <button
          onClick={() => setShowPasswordModal(true)}
          className="w-full py-1.5 px-3 rounded-lg text-xs font-medium text-gray-400 hover:text-white hover:bg-gray-700 transition-colors text-left"
        >
          Cambiar contraseña
        </button>
        <button
          onClick={logout}
          className="w-full py-1.5 px-3 rounded-lg text-xs font-medium text-gray-400 hover:text-white hover:bg-gray-700 transition-colors text-left"
        >
          Cerrar sesión
        </button>
      </div>

      {showPasswordModal && <PasswordModal onClose={() => setShowPasswordModal(false)} />}
    </aside>
  );
}
