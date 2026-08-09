import { useApp } from '@/context/AppContext';

/** Slice de RATs — caché de registros y stats del dashboard. */
export function useRat() {
  const {
    rats,
    dashboardStats,
    setRats,
    setDashboardStats,
    actualizarRatEnCache,
    agregarRatEnCache,
    eliminarRatDeCache,
    actualizarStatsEnCache,
  } = useApp();
  return {
    rats,
    dashboardStats,
    setRats,
    setDashboardStats,
    actualizarRatEnCache,
    agregarRatEnCache,
    eliminarRatDeCache,
    actualizarStatsEnCache,
  };
}
