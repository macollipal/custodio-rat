import { useApp } from '@/context/AppContext';

/** Slice de empresa activa — empresa seleccionada, lista de empresas y permisos de rol. */
export function useCompany() {
  const { company, companies, setCompany, setCompanies, rolEnEmpresa, puedeEditar } = useApp();
  return { company, companies, setCompany, setCompanies, rolEnEmpresa, puedeEditar };
}
