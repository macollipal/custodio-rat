'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useApp } from '@/context/AppContext';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import * as api from '@/lib/api';
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
  ;

function pathToPage(pathname: string): Page {
  if (pathname.startsWith('/rat')) return 'rat';
  if (pathname.startsWith('/companies')) return 'companies';
  if (pathname.startsWith('/breaches')) return 'breaches';
  if (pathname.startsWith('/reportes')) return 'reportes';
  if (pathname.startsWith('/usuarios')) return 'usuarios';
  if (pathname.startsWith('/rubros')) return 'rubros';
  if (pathname.startsWith('/configuracion')) return 'configuracion';
  if (pathname.startsWith('/tkt_solicitud_derecho')) return 'tkt_solicitud_derecho';
  if (pathname.startsWith('/transparencia')) return 'transparencia';
  if (pathname.startsWith('/encargados-contrato')) return 'encargados-contrato';
  if (pathname.startsWith('/consentimientos')) return 'consentimientos';
  if (pathname.startsWith('/eipd')) return 'eipd';
  
  return 'dashboard';
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { token, company, setCompany, setCompanies, companies, user } = useApp();
  const [hydrated, setHydrated] = useState(false);
  const [empresasCargadas, setEmpresasCargadas] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => setHydrated(true), []);

  useEffect(() => {
    function handleResize() {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false);
      }
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    if (!token) {
      router.replace('/login');
      return;
    }
    if (pathname.includes('/usuarios') && user?.rol_global !== 'superadmin') {
      router.replace('/dashboard');
      return;
    }
    if (pathname.includes('/rubros') && user?.rol_global === 'usuario') {
      router.replace('/dashboard');
      return;
    }
    if (empresasCargadas && companies.length > 0) return;
    api.listarEmpresas().then((list: Company[]) => {
      setCompanies(list);
      setEmpresasCargadas(true);
      if (!company && list.length > 0) {
        setCompany(list[0]);
      } else if (!company && list.length === 0) {
        router.replace('/onboarding');
      }
    }).catch(() => {
      setEmpresasCargadas(true);
    });
  }, [hydrated, token, router, pathname, user?.rol_global, empresasCargadas, companies.length, company]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'n') {
          e.preventDefault();
          if (company) router.push('/rat');
        }
        if (e.key === 'f') {
          e.preventDefault();
          if (pathname.includes('/rat') || pathname.includes('/reportes')) {
            const searchInput = document.querySelector<HTMLInputElement>('input[placeholder*="Buscar"]');
            searchInput?.focus();
          }
        }
      }
      if (e.key === 'Escape') {
        const drawer = document.querySelector<HTMLElement>('[data-drawer-close]');
        if (drawer) drawer.click();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [pathname, company, router]);

  const currentPage = pathToPage(pathname);

  function handleNavigate(page: Page) {
    router.push(`/${page}`);
    setSidebarOpen(false);
  }

  if (!hydrated || !token) return null;

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: '#F9FAFB' }}>
      {/* Backdrop for mobile sidebar */}
      {sidebarOpen && (
        <div
          role="presentation"
          aria-hidden="true"
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      {/* Sidebar: fixed overlay on mobile, visible on desktop */}
      <div
        id="main-sidebar"
        className={`
          fixed inset-y-0 left-0 z-50
          transition-transform duration-300 ease-in-out
          lg:static
          lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <Sidebar
          currentPage={currentPage}
          onNavigate={handleNavigate}
          companies={companies}
          onClose={() => setSidebarOpen(false)}
        />
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar onMenuClick={() => setSidebarOpen(o => !o)} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
