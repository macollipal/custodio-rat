import { useApp } from '@/context/AppContext';

/** Slice de autenticación — token, usuario, logout, rol global. */
export function useAuth() {
  const { token, user, setToken, setUser, logout, isAuthenticated, rolGlobal } = useApp();
  return { token, user, setToken, setUser, logout, isAuthenticated, rolGlobal };
}
