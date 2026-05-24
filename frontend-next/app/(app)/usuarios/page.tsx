'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { User } from '@/types';

const ROL_GLOBAL_OPTIONS = [
  { value: 'superadmin', label: 'Superadministrador' },
  { value: 'admin_empresa', label: 'Admin empresa' },
  { value: 'usuario', label: 'Usuario' },
];

export default function UsersPage() {
  const { user: currentUser, companies } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState<User | null>(null);
  const [confirmDel, setConfirmDel] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listarUsuarios();
      setUsers(data);
    } catch {
      toast.error('No se pudieron cargar los usuarios.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleCreate(form: { username: string; email: string; full_name: string; password: string; rol_global: string; empresa_id?: number }) {
    try {
      await api.crearUsuario(form);
      toast.success('Usuario creado correctamente.');
      setShowCreate(false);
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al crear usuario.');
    }
  }

  async function handleEdit(userId: number, form: { email: string; full_name: string; rol_global: string; empresa_id?: number }) {
    try {
      await api.actualizarUsuario(userId, form);
      toast.success('Usuario actualizado.');
      setShowEdit(null);
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al actualizar.');
    }
  }

  async function handleResetPw(userId: number, newPassword: string) {
    try {
      await api.cambiarPasswordOtro(userId, newPassword);
      toast.success('Contraseña actualizada.');
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al cambiar contraseña.');
    }
  }

  async function handleDelete(userId: number) {
    const userToDelete = users.find(u => u.id === userId);
    try {
      await api.eliminarUsuario(userId);
      toast.success('Usuario eliminado.', {
        duration: 5000,
        action: {
          label: 'Deshacer',
          onClick: () => handleCreate({
            username: userToDelete?.username ?? '',
            email: userToDelete?.email ?? '',
            full_name: userToDelete?.full_name ?? '',
            password: '',
            rol_global: userToDelete?.rol_global ?? 'usuario',
            empresa_id: userToDelete?.empresa_id,
          }),
        },
      });
      setConfirmDel(null);
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
    }
  }

  function rolBadge(rol: string) {
    if (rol === 'superadmin') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#F3E8FF', color: '#7C3AED' }}>Superadmin</span>;
    if (rol === 'admin_empresa') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#DBEAFE', color: '#2563EB' }}>Admin empresa</span>;
    return <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#F3F4F6', color: '#6B7280' }}>Usuario</span>;
  }

  if (currentUser?.rol_global !== 'superadmin') {
    return (
      <div className="p-8 text-center">
        <p className="text-sm" style={{ color: '#6B7280' }}>No tienes permisos para acceder a esta sección.</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Gestión de usuarios</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>{users.length} usuario(s) registrado(s)</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition"
          style={{ background: '#2563EB' }}
        >
          + Nuevo usuario
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
      ) : (
        <div className="rounded-xl overflow-hidden bg-white sm:overflow-visible" style={{ border: '1px solid #D1D5DB' }}>
          <div className="overflow-x-auto">
            <table className="w-full" style={{ minWidth: 700 }}>
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide hidden sm:table-row" style={{ color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #D1D5DB' }}>
                  <th className="px-4 py-3 text-left">Usuario</th>
                  <th className="px-4 py-3 text-left">Email</th>
                  <th className="px-4 py-3 text-left">Nombre completo</th>
                  <th className="px-4 py-3 text-left">Empresa asignada</th>
                  <th className="px-4 py-3 text-center">Rol global</th>
                  <th className="px-4 py-3 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="sm:table-row-group">
                {users.map((u, i) => (
                  <tr key={u.id} className="sm:table-row" style={{ borderTop: i > 0 ? '1px solid #F3F4F6' : 'none', background: i % 2 === 0 ? 'white' : '#FAFAFA' }}>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      <div className="text-sm font-semibold" style={{ color: '#111827' }}>{u.username}</div>
                    </td>
                    <td className="sm:hidden px-4 py-3 border-b" style={{ borderColor: '#F3F4F6' }}>
                      <div className="text-sm font-semibold" style={{ color: '#111827' }}>{u.username}</div>
                      <div className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>{u.email} · {u.full_name}</div>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell text-sm" style={{ color: '#6B7280' }}>{u.email}</td>
                    <td className="px-4 py-3 hidden sm:table-cell text-sm" style={{ color: '#6B7280' }}>{u.full_name}</td>
                    <td className="px-4 py-3 hidden sm:table-cell">
                      {u.empresa_nombre
                        ? <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#ECFDF5', color: '#059669' }}>{u.empresa_nombre}</span>
                        : <span className="text-xs" style={{ color: '#9CA3AF' }}>Sin asignar</span>
                      }
                    </td>
                    <td className="sm:hidden px-4 py-3 border-b" style={{ borderColor: '#F3F4F6' }}>
                      <div className="flex items-center gap-2 flex-wrap mt-1">
                        {u.empresa_nombre
                          ? <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#ECFDF5', color: '#059669' }}>{u.empresa_nombre}</span>
                          : <span className="text-xs" style={{ color: '#9CA3AF' }}>Sin asignar</span>
                        }
                        {rolBadge(u.rol_global)}
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden sm:table-cell text-center">{rolBadge(u.rol_global)}</td>
                    <td className="px-4 py-3 flex gap-1 justify-start sm:justify-center flex-wrap sm:table-cell">
                      <button
                        onClick={() => setShowEdit(u)}
                        className="px-3 py-1 rounded-lg text-xs font-medium border transition hover:bg-gray-50"
                        style={{ borderColor: '#D1D5DB', color: '#374151' }}
                      >
                        ✏️
                      </button>
                      {u.id !== currentUser?.id && (
                        <button
                          onClick={() => setConfirmDel(u.id)}
                          className="px-3 py-1 rounded-lg text-xs font-medium border transition hover:bg-red-50"
                          style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
                        >
                          🗑
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showCreate && (
        <UserModal
          key="create"
          title="Nuevo usuario"
          companies={companies}
          onClose={() => setShowCreate(false)}
          onSubmit={handleCreate}
        />
      )}

      {showEdit && (
        <UserModal
          key={`edit-${showEdit.id}`}
          title={`Editar ${showEdit.username}`}
          user={showEdit}
          companies={companies}
          onClose={() => setShowEdit(null)}
          onSubmit={(form) => handleEdit(showEdit.id, form)}
          onResetPw={(pw) => handleResetPw(showEdit.id, pw)}
        />
      )}

      {confirmDel !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={() => setConfirmDel(null)}>
          <div className="bg-white rounded-2xl p-6 w-96 shadow-2xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-base font-bold mb-2" style={{ color: '#111827' }}>¿Eliminar usuario?</h3>
            <p className="text-sm mb-5" style={{ color: '#6B7280' }}>Esta acción es irreversible.</p>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setConfirmDel(null)} className="px-4 py-2 rounded-lg text-sm border transition hover:bg-gray-50" style={{ borderColor: '#D1D5DB', color: '#374151' }}>Cancelar</button>
              <button onClick={() => handleDelete(confirmDel)} className="px-4 py-2 rounded-lg text-sm font-semibold text-white" style={{ background: '#DC2626' }}>Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function UserModal({
  title, user, onClose, onSubmit, onResetPw, companies,
}: {
  title: string;
  user?: User;
  companies: Array<{ id: number; nombre: string }>;
  onClose: () => void;
  onSubmit: (form: { username: string; email: string; full_name: string; password: string; rol_global: string; empresa_id?: number }) => void;
  onResetPw?: (pw: string) => void;
}) {
  const [form, setForm] = useState({
    username: user?.username ?? '',
    email: user?.email ?? '',
    full_name: user?.full_name ?? '',
    password: '',
    rol_global: user?.rol_global ?? 'usuario',
    empresa_id: user?.empresa_id ?? '',
  });
  const [newPw, setNewPw] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setForm({
      username: user?.username ?? '',
      email: user?.email ?? '',
      full_name: user?.full_name ?? '',
      password: '',
      rol_global: user?.rol_global ?? 'usuario',
      empresa_id: user?.empresa_id ?? '',
    });
    setNewPw('');
  }, [user]);

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  function set(k: keyof typeof form, v: string) {
    setForm(f => ({ ...f, [k]: v }));
  }

  function necesitaEmpresa() {
    return form.rol_global === 'admin_empresa' || form.rol_global === 'usuario';
  }

  async function handleSubmit() {
    if (!form.username.trim()) { toast.error('El usuario es obligatorio.'); return; }
    if (!form.email.trim()) { toast.error('El email es obligatorio.'); return; }
    if (!user && !form.password.trim()) { toast.error('La contraseña es obligatoria.'); return; }
    if (necesitaEmpresa() && !form.empresa_id) { toast.error('Selecciona la empresa asignada.'); return; }
    setSaving(true);
    try {
      const payload: any = {
        username: form.username,
        email: form.email,
        full_name: form.full_name,
        rol_global: form.rol_global,
      };
      if (!user) payload.password = form.password;
      if (necesitaEmpresa()) payload.company_id = Number(form.empresa_id);
      await onSubmit(payload);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 w-[480px] shadow-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold" style={{ color: '#111827' }}>{title}</h3>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-sm font-bold" style={{ color: '#6B7280' }}>✕</button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Usuario *</label>
            <input type="text" value={form.username} onChange={e => set('username', e.target.value)} disabled={!!user} autoComplete="off" className={inputCls} style={{ ...inputStyle, background: user ? '#F9FAFB' : undefined }} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Email *</label>
            <input type="email" value={form.email} onChange={e => set('email', e.target.value)} autoComplete="off" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nombre completo</label>
            <input type="text" value={form.full_name} onChange={e => set('full_name', e.target.value)} autoComplete="off" className={inputCls} style={inputStyle} />
          </div>
          {!user && (
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Contraseña *</label>
              <input type="password" value={form.password} onChange={e => set('password', e.target.value)} autoComplete="new-password" className={inputCls} style={inputStyle} />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Rol global</label>
            <select
              value={form.rol_global}
              onChange={e => set('rol_global', e.target.value)}
              className={inputCls}
              style={inputStyle}
            >
              {ROL_GLOBAL_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
              {form.rol_global === 'superadmin' ? 'Acceso total a todo el sistema' :
               form.rol_global === 'admin_empresa' ? 'Administra su empresa asignada' :
               'Accede a RATs de su empresa asignada'}
            </p>
          </div>
          {necesitaEmpresa() && (
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Empresa asignada *</label>
              <select
                value={form.empresa_id}
                onChange={e => set('empresa_id', e.target.value)}
                className={inputCls}
                style={inputStyle}
              >
                <option value="">Seleccionar empresa...</option>
                {companies.map(c => <option key={c.id} value={String(c.id)}>{c.nombre}</option>)}
              </select>
            </div>
          )}
          {user && onResetPw && (
            <div className="rounded-lg p-4" style={{ background: '#F9FAFB', border: '1px solid #D1D5DB' }}>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nueva contraseña</label>
              <div className="flex gap-2">
                <input type="password" value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="Nueva contraseña" className={inputCls} style={inputStyle} />
                <button
                  onClick={() => { if (newPw.trim()) { onResetPw(newPw); setNewPw(''); } }}
                  disabled={!newPw.trim()}
                  className="px-4 py-2 rounded-lg text-sm font-semibold border transition disabled:opacity-50"
                  style={{ borderColor: '#D1D5DB', color: '#374151' }}
                >
                  Cambiar
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="flex gap-2 justify-end mt-5">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm border transition hover:bg-gray-50" style={{ borderColor: '#D1D5DB', color: '#374151' }}>Cancelar</button>
          <button onClick={handleSubmit} disabled={saving} className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60" style={{ background: '#2563EB' }}>
            {saving ? 'Guardando...' : user ? 'Guardar cambios' : 'Crear usuario'}
          </button>
        </div>
      </div>
    </div>
  );
}