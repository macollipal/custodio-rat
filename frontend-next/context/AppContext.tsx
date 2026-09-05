'use client';

import { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react';
import type { User, Company, RAT, DashboardStats, RolEmpresa, RolGlobal } from '@/types';

export type Theme = 'light' | 'dark' | 'mac';
import { STORAGE_KEYS, API_BASE, DRAFT_KEY_PREFIX } from '@/lib/constants';
import { listarBaseLegalOptions, getActiveCompanyModules } from '@/lib/api';

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
  theme: Theme;
  darkMode: boolean;
  baseLegalOptions: string[];
  baseLegalDescripciones: Record<string, string>;
  activeModules: string[];
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  setCompany: (company: Company) => void;
  setCompanies: (companies: Company[]) => void;
  setRats: (rats: RAT[]) => void;
  setDashboardStats: (stats: DashboardStats) => void;
  cycleTheme: () => void;
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
  const [theme, setTheme] = useState<Theme>('light');
  const [baseLegalOptions, setBaseLegalOptions] = useState<string[]>([]);
  const [baseLegalDescripciones, setBaseLegalDescripciones] = useState<Record<string, string>>({});
  const [activeModules, setActiveModules] = useState<string[]>([
    'RAT', 'ARCO', 'BRECHAS', 'EIPD', 'CONSENTIMIENTOS', 'ENCARGADOS', 'TRANSPARENCIA', 'REPORTES', 'ASESOR',
  ]);

  useEffect(() => {
    try {
      const t = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const u = localStorage.getItem(STORAGE_KEYS.USER);
      const c = localStorage.getItem(STORAGE_KEYS.COMPANY);
      const cs = localStorage.getItem(STORAGE_KEYS.COMPANIES);
      if (t) setTokenState(t);
      if (u) try { setUserState(JSON.parse(u)); } catch {}
      if (c) try { setCompanyState(JSON.parse(c)); } catch {}
      if (cs) try { setCompaniesState(JSON.parse(cs)); } catch {}
    } catch {}
  }, []);

  useEffect(() => {
    const stored = (() => { try { return localStorage.getItem('custodio_theme') as Theme | null; } catch { return null; } })();
    if (stored === 'dark' || stored === 'mac') {
      setTheme(stored);
      document.documentElement.classList.add(stored);
    } else if (!stored) {
      // migración: leer clave legacy
      const legacy = (() => { try { return localStorage.getItem('custodio_dark_mode'); } catch { return null; } })();
      if (legacy === 'true') {
        setTheme('dark');
        document.documentElement.classList.add('dark');
      }
    }
  }, []);

  const ALL_MODULES = ['RAT', 'ARCO', 'BRECHAS', 'EIPD', 'CONSENTIMIENTOS', 'ENCARGADOS', 'TRANSPARENCIA', 'REPORTES', 'ASESOR'];

  useEffect(() => {
    if (!token || !company?.id) return;
    if (user?.rol_global === 'superadmin') {
      setActiveModules(ALL_MODULES);
      return;
    }
    getActiveCompanyModules(company.id)
      .then(res => setActiveModules(res.active_modules))
      .catch(() => setActiveModules(ALL_MODULES));
  }, [token, company?.id, user?.rol_global]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!token) return;
    listarBaseLegalOptions()
      .then(data => {
        setBaseLegalOptions(data.opciones);
        setBaseLegalDescripciones(data.descripciones);
      })
      .catch(() => {});
  }, [token]);

  const cycleTheme = useCallback(() => {
    setTheme(prev => {
      const next: Theme = prev === 'light' ? 'dark' : prev === 'dark' ? 'mac' : 'light';
      try { localStorage.setItem('custodio_theme', next); } catch {}
      document.documentElement.classList.remove('dark', 'mac');
      if (next !== 'light') document.documentElement.classList.add(next);
      return next;
    });
  }, []);

  const toggleDarkMode = cycleTheme;

  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => {
      if (!r.ok) throw new Error();
    }).catch(() => {
      try {
        localStorage.removeItem(STORAGE_KEYS.TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.removeItem(STORAGE_KEYS.COMPANY);
        localStorage.removeItem(STORAGE_KEYS.COMPANIES);
      } catch {}
      setTokenState(null);
      setUserState(null);
      setCompanyState(null);
      setCompaniesState([]);
    });
  }, [token]);

  const setToken = useCallback((t: string) => {
    try { localStorage.setItem(STORAGE_KEYS.TOKEN, t); } catch {}
    setTokenState(t);
  }, []);

  const setUser = useCallback((u: User) => {
    try { localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(u)); } catch {}
    setUserState(u);
  }, []);

  const setCompany = useCallback((c: Company) => {
    setCompanyState(prev => {
      if (prev?.id && prev.id !== c.id) {
        try { localStorage.removeItem(`${DRAFT_KEY_PREFIX}${prev.id}`); } catch {}
      }
      return c;
    });
    try { localStorage.setItem(STORAGE_KEYS.COMPANY, JSON.stringify(c)); } catch {}
    setRatsState([]);
    setDashboardStatsState(null);
  }, []);

  const setCompanies = useCallback((cs: Company[]) => {
    try { localStorage.setItem(STORAGE_KEYS.COMPANIES, JSON.stringify(cs)); } catch {}
    setCompaniesState(cs);
  }, []);

  const setRats = useCallback((r: RAT[]) => {
    setRatsState(r);
  }, []);

  const setDashboardStats = useCallback((s: DashboardStats) => {
    setDashboardStatsState(s);
  }, []);

  const logout = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
      localStorage.removeItem(STORAGE_KEYS.COMPANY);
    } catch {}
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

  const value = useMemo<AppState>(() => ({
    token,
    user,
    company,
    companies,
    rats,
    dashboardStats,
    rolEnEmpresa,
    puedeEditar,
    rolGlobal,
    theme,
    darkMode: theme === 'dark',
    baseLegalOptions,
    baseLegalDescripciones,
    activeModules,
    cycleTheme,
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
  }), [
    token, user, company, companies, rats, dashboardStats, theme,
    baseLegalOptions, baseLegalDescripciones, activeModules,
    cycleTheme, toggleDarkMode, setToken, setUser, setCompany, setCompanies,
    setRats, setDashboardStats, logout,
    actualizarRatEnCache, agregarRatEnCache, eliminarRatDeCache, actualizarStatsEnCache,
    rolEnEmpresa, rolGlobal, puedeEditar,
  ]);

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}