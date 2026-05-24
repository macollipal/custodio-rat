'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const { setToken, setUser } = useApp();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      toast.error('Ingresa tu usuario y contraseña.');
      return;
    }
    setLoading(true);
    try {
      const result = await api.login(username.trim(), password.trim());
      setToken(result.access_token);
      setUser(result.user);
      const empresas = await api.listarEmpresas();
      if (empresas.length === 0) {
        router.push('/onboarding');
      } else {
        router.push('/dashboard');
      }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="h-screen flex items-center justify-center p-4"
      style={{ background: 'linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%)' }}
    >
      <div className="w-full max-w-md px-4">
        {/* Logo */}
        <div className="text-center mb-6 sm:mb-8">
          <div
            className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl mx-auto mb-3 sm:mb-4 flex items-center justify-center text-2xl sm:text-3xl shadow-lg"
            style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)' }}
          >
            🛡
          </div>
          <h1 className="text-white text-xl sm:text-2xl font-bold tracking-tight mb-1">Custodio</h1>
          <p className="text-slate-400 text-xs sm:text-sm">
            Gestión inteligente del Registro de Actividades<br />
            de Tratamiento · <span className="text-blue-400 font-semibold">Ley 21.719</span>
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-5 sm:p-9">
          <h2 className="text-gray-900 text-lg sm:text-xl font-bold mb-1">Iniciar sesión</h2>
          <p className="text-gray-500 text-xs sm:text-sm mb-4 sm:mb-6">Ingresa tus credenciales para continuar</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Usuario</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="tu.usuario"
                autoComplete="username"
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-gray-900 placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold text-sm transition mt-2"
            >
              {loading ? 'Verificando...' : 'Ingresar al sistema'}
            </button>
          </form>

          <p className="text-center text-xs text-gray-400 mt-5">
            Acceso restringido · Ley 21.719 de Protección de Datos
          </p>
        </div>
      </div>
    </div>
  );
}
