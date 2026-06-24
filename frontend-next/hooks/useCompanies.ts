'use client';

import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { Company } from '@/types';

export interface UseCompaniesReturn {
  companies: Company[];
  loading: boolean;
  activeCompany: Company | null;
  loadCompanies: () => Promise<void>;
  createCompany: (payload: Record<string, unknown>) => Promise<Company>;
  updateCompany: (id: number, payload: Partial<Company>) => Promise<Company>;
  deactivateCompany: (id: number) => Promise<void>;
  deleteCompany: (id: number) => Promise<void>;
  setActiveCompany: (company: Company) => void;
}

export function useCompanies(): UseCompaniesReturn {
  const { company: activeCompany, setCompany, companies, setCompanies } = useApp();
  const [loading, setLoading] = useState(false);

  const loadCompanies = useCallback(async () => {
    setLoading(true);
    try {
      setCompanies(await api.listarEmpresas());
    } catch {
      toast.error('No se pudieron cargar las empresas.');
    } finally {
      setLoading(false);
    }
  }, [setCompanies]);

  const createCompany = useCallback(async (payload: Record<string, unknown>): Promise<Company> => {
    const result = await api.crearEmpresa(payload);
    setCompanies([...companies, result]);
    return result;
  }, [companies, setCompanies]);

  const updateCompany = useCallback(async (id: number, payload: Partial<Company>): Promise<Company> => {
    const result = await api.actualizarEmpresa(id, payload);
    setCompanies(companies.map(c => c.id === id ? result : c));
    if (activeCompany?.id === id) setCompany(result);
    return result;
  }, [companies, activeCompany, setCompanies, setCompany]);

  const deactivateCompany = useCallback(async (id: number) => {
    await api.desactivarEmpresa(id);
    toast.success('Empresa desactivada.');
    await loadCompanies();
    if (activeCompany?.id === id) setCompany(companies.find(c => c.id !== id) ?? null as unknown as Company);
  }, [activeCompany, companies, loadCompanies, setCompany]);

  const deleteCompany = useCallback(async (id: number) => {
    await api.eliminarEmpresa(id);
    toast.success('Empresa eliminada.');
    await loadCompanies();
    if (activeCompany?.id === id) setCompany(companies.find(c => c.id !== id) ?? null as unknown as Company);
  }, [activeCompany, companies, loadCompanies, setCompany]);

  return {
    companies,
    loading,
    activeCompany,
    loadCompanies,
    createCompany,
    updateCompany,
    deactivateCompany,
    deleteCompany,
    setActiveCompany: setCompany,
  };
}
