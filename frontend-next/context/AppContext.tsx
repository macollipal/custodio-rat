'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { User, Company, RAT, DashboardStats, RolEmpresa, RolGlobal, SecurityBreach } from '@/types';
import { STORAGE_KEYS, API_BASE } from '@/lib/constants';

interface AppState {
  token: string | null;
  user: User | null;
  company: Company | null;
  companies: Company[];
  rats: RAT[];
  dashboardStats: DashboardStats | null;
  rolEnEmpresa: RolEmpresa | null;
  puedeEditar: boolean;
  rolGlobal: RolGlobal | null;
  darkMode: boolean;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  setCompany: (company: Company) => void;
  setCompanies: (companies: Company[]) => void;
  setRats: (rats: RAT[]) => void;
  setDashboardStats: (stats: DashboardStats) => void;
  toggleDarkMode: () => void;
  logout: () => void;
  isAuthenticated: boolean;

  actualizarRatEnCache: (rat: RAT) => void;
  agregarRatEnCache: (rat: RAT) => void;
  eliminarRatDeCache: (ratId: number) => void;
  actualizarStatsEnCache: (stats: DashboardStats) => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUserState] = useState<User | null>(null);
  const [company, setCompanyState] = useState<Company | null>(null);
  const [companies, setCompaniesState] = useState<Company[]>([]);
  const [rats, setRatsState] = useState<RAT[]>([]);
  const [dashboardStats, setDashboardStatsState] = useState<DashboardStats | null>(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem(STORAGE_KEYS.TOKEN);
    const u = localStorage.getItem(STORAGE_KEYS.USER);
    const c = localStorage.getItem(STORAGE_KEYS.COMPANY);
    if (t) setTokenState(t);
    if (u) try { setUserState(JSON.parse(u)); } catch {}
    if (c) try { setCompanyState(JSON.parse(c)); } catch {}
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem('custodio_dark_mode');
    if (stored === 'true') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = useCallback(() => {
    setDarkMode(prev => {
      const next = !prev;
      localStorage.setItem('custodio_dark_mode', String(next));
      if (next) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return next;
    });
  }, []);

  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => {
      if (!r.ok) throw new Error();
    }).catch(() => {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
      localStorage.removeItem(STORAGE_KEYS.COMPANY);
      setTokenState(null);
      setUserState(null);
      setCompanyState(null);
    });
  }, [token]);

  const setToken = useCallback((t: string) => {
    localStorage.setItem(STORAGE_KEYS.TOKEN, t);
    setTokenState(t);
  }, []);

  const setUser = useCallback((u: User) => {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(u));
    setUserState(u);
  }, []);

  const setCompany = useCallback((c: Company) => {
    localStorage.setItem(STORAGE_KEYS.COMPANY, JSON.stringify(c));
    setCompanyState(c);
    setRatsState([]);
    setDashboardStatsState(null);
  }, []);

  const setCompanies = useCallback((cs: Company[]) => {
    setCompaniesState(cs);
  }, []);

  const setRats = useCallback((r: RAT[]) => {
    setRatsState(r);
  }, []);

  const setDashboardStats = useCallback((s: DashboardStats) => {
    setDashboardStatsState(s);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    localStorage.removeItem(STORAGE_KEYS.COMPANY);
    setTokenState(null);
    setUserState(null);
    setCompanyState(null);
    setCompaniesState([]);
    setRatsState([]);
    setDashboardStatsState(null);
  }, []);

  const actualizarRatEnCache = useCallback((updated: RAT) => {
    setRatsState(prev => prev.map(r => r.id === updated.id ? updated : r));
  }, []);

  const agregarRatEnCache = useCallback((rat: RAT) => {
    setRatsState(prev => {
      if (prev.some(r => r.id === rat.id)) return prev;
      return [...prev, rat];
    });
  }, []);

  const eliminarRatDeCache = useCallback((ratId: number) => {
    setRatsState(prev => prev.filter(r => r.id !== ratId));
  }, []);

  const actualizarStatsEnCache = useCallback((stats: DashboardStats) => {
    setDashboardStatsState(stats);
  }, []);

  const rolEnEmpresa = (company?.mi_rol ?? null) as RolEmpresa | null;
  const rolGlobal = user?.rol_global ?? null;
  const puedeEditar = rolGlobal !== null && rolGlobal !== 'usuario' ? true : rolEnEmpresa === 'admin' || rolEnEmpresa === 'editor';

  return (
    <AppContext.Provider
      value={{
        token,
        user,
        company,
        companies,
        rats,
        dashboardStats,
        rolEnEmpresa,
        puedeEditar,
        rolGlobal,
        darkMode,
        toggleDarkMode,
        setToken,
        setUser,
        setCompany,
        setCompanies,
        setRats,
        setDashboardStats,
        logout,
        isAuthenticated: !!token,
        actualizarRatEnCache,
        agregarRatEnCache,
        eliminarRatDeCache,
        actualizarStatsEnCache,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}