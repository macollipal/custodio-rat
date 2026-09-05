'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { User } from '@/types';
import { inputCls, inputStyle } from '@/lib/styles';
import { Button } from '@/components/ui/Button';
import ConfirmDialog from '@/components/ui/ConfirmDialog';

const ROL_GLOBAL_OPTIONS = [
  { value: 'superadmin', label: 'Superadministrador' },
  { value: 'admin_empresa', label: 'Admin empresa' },
  { value: 'usuario', label: 'Usuario' },
];

const ROL_CONFIG: Record<string, { label: string; bg: string; color: string; avatarBg: string }> = {
  superadmin:   { label: 'Superadmin',   bg: '#F3E8FF', color: '#7C3AED', avatarBg: '#7C3AED' },
  admin_empresa:{ label: 'Admin empresa', bg: '#DBEAFE', color: '#2563EB', avatarBg: '#2563EB' },
  usuario:      { label: 'Usuario',       bg: '#F3F4F6', color: '#6B7280', avatarBg: '#9CA3AF' },
};

function initials(u: User) {
  const name = u.full_name?.trim() || u.username;
  const parts = name.split(' ').filter(Boolean);
  return parts.length >= 2
    ? (parts[0][0] + parts[1][0]).toUpperCase()
    : name.slice(0, 2).toUpperCase();
}

function Avatar({ u }: { u: User }) {
  const cfg = ROL_CONFIG[u.rol_global] ?? ROL_CONFIG.usuario;
  return (
    <div
      className="w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0 select-none"
      style={{ background: cfg.avatarBg }}
      aria-hidden="true"
    >
      {initials(u)}
    </div>
  );
}

function RolBadge({ rol }: { rol: string }) {
  const cfg = ROL_CONFIG[rol] ?? ROL_CONFIG.usuario;
  return (
    <span className="text-xs font-semibold px-2 py-0.5 rounded-full whitespace-nowrap"
      style={{ background: cfg.bg, color: cfg.color }}>
      {cfg.label}
    </span>
  );
}

function StatusDot({ active }: { active?: boolean }) {
  const on = active !== false;
  return (
    <span className="flex items-center gap-1.5 text-xs font-medium whitespace-nowrap"
      style={{ color: on ? '#059669' : '#DC2626' }}>
      <span className="w-2 h-2 rounded-full flex-shrink-0"
        style={{ background: on ? '#059669' : '#DC2626' }} />
      {on ? 'Activo' : 'Inactivo'}
    </span>
  );
}

function formatDate(iso?: string) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' });
}

function KpiCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-white rounded-xl px-5 py-4 flex flex-col gap-0.5" style={{ border: '1px solid #E5E7EB' }}>
      <span className="text-2xl font-bold" style={{ color }}>{value}</span>
      <span className="text-xs" style={{ color: '#6B7280' }}>{label}</span>
    </div>
  );
}

export default function UsersPage() {
  const { user: currentUser, companies, company } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState<User | null>(null);
  const [confirmDel, setConfirmDel] = useState<number | null>(null);
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setUsers(await api.listarUsuarios(company?.id));
    } catch {
      toast.error('No se pudieron cargar los usuarios.');
    } finally {
      setLoading(false);
    }
  }, [company?.id]);

  useEffect(() => { load(); }, [load]);

  const sorted = [...users].sort((a, b) => b.id - a.id);
  const filtered = sorted.filter(u => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return u.username.toLowerCase().includes(q)
      || u.full_name.toLowerCase().includes(q)
      || u.email.toLowerCase().includes(q);
  });

  const nSuper = users.filter(u => u.rol_global === 'superadmin').length;
  const nAdmin = users.filter(u => u.rol_global === 'admin_empresa').length;
  const nUser  = users.filter(u => u.rol_global === 'usuario').length;

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
    const u = users.find(x => x.id === userId);
    try {
      await api.eliminarUsuario(userId);
      toast.success(`Usuario "${u?.username}" eliminado.`);
      setConfirmDel(null);
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
    }
  }

  if (currentUser?.rol_global !== 'superadmin') {
    return (
      <div className="p-8 text-center">
        <p className="text-sm" style={{ color: '#6B7280' }}>No tienes permisos para acceder a esta sección.</p>
      </div>
    );
  }

  return (
    <div className="p-6 sm:p-8 max-w-7xl mx-auto">

      {/* Header */}
      <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Gestión de usuarios</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
            {users.length} usuario{users.length !== 1 ? 's' : ''}
            {company ? ` en ${company.nombre}` : ' en el sistema'}
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>+ Nuevo usuario</Button>
      </div>

      {/* KPIs */}
      {!loading && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <KpiCard label="Superadmins"    value={nSuper} color="#7C3AED" />
          <KpiCard label="Admins empresa" value={nAdmin} color="#2563EB" />
          <KpiCard label="Usuarios"       value={nUser}  color="#6B7280" />
        </div>
      )}

      {/* Buscador */}
      <div className="relative mb-4" style={{ maxWidth: 320 }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Buscar por nombre, usuario o email..."
          className="w-full pl-9 pr-4 py-2 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
          style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' }}
        />
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" aria-hidden="true">🔍</span>
      </div>

      {/* Tabla */}
      {loading ? (
        <div className="text-center py-20 text-sm" style={{ color: '#9CA3AF' }}>Cargando usuarios...</div>
      ) : (
        <div className="rounded-xl overflow-hidden bg-white" style={{ border: '1px solid #E5E7EB' }}>
          <div className="overflow-x-auto">
            <table className="w-full" style={{ minWidth: 680 }}>
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide"
                  style={{ color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                  <th className="px-4 py-3 text-left">Usuario</th>
                  <th className="px-4 py-3 text-left">Email</th>
                  <th className="px-4 py-3 text-center">Rol</th>
                  <th className="px-4 py-3 text-left">Empresa</th>
                  <th className="px-4 py-3 text-center">Estado</th>
                  <th className="px-4 py-3 text-left">Creado</th>
                  <th className="px-4 py-3 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-16 text-center text-sm" style={{ color: '#9CA3AF' }}>
                      {search ? `Sin resultados para "${search}"` : 'No hay usuarios registrados.'}
                    </td>
                  </tr>
                ) : filtered.map((u, i) => (
                  <tr key={u.id}
                    style={{ borderTop: i > 0 ? '1px solid #F3F4F6' : 'none', background: i % 2 === 0 ? 'white' : '#FAFAFA' }}>

                    {/* Avatar + nombre */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <Avatar u={u} />
                        <div>
                          <div className="text-sm font-semibold" style={{ color: '#111827' }}>{u.username}</div>
                          <div className="text-xs" style={{ color: '#9CA3AF' }}>{u.full_name || '—'}</div>
                        </div>
                      </div>
                    </td>

                    <td className="px-4 py-3 text-sm" style={{ color: '#6B7280' }}>{u.email}</td>

                    <td className="px-4 py-3 text-center">
                      <RolBadge rol={u.rol_global} />
                    </td>

                    <td className="px-4 py-3">
                      {u.empresa_nombre
                        ? <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#ECFDF5', color: '#059669' }}>{u.empresa_nombre}</span>
                        : <span className="text-xs" style={{ color: '#D1D5DB' }}>Sin asignar</span>}
                    </td>

                    <td className="px-4 py-3 text-center">
                      <StatusDot active={u.is_active} />
                    </td>

                    <td className="px-4 py-3 text-xs" style={{ color: '#9CA3AF' }}>
                      {formatDate(u.created_at)}
                    </td>

                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 justify-center">
                        <button
                          onClick={() => setShowEdit(u)}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border transition hover:bg-gray-50"
                          style={{ borderColor: '#D1D5DB', color: '#374151' }}
                        >
                          Editar
                        </button>
                        {u.id !== currentUser?.id && (
                          <button
                            onClick={() => setConfirmDel(u.id)}
                            className="px-3 py-1.5 rounded-lg text-xs font-medium border transition hover:bg-red-50"
                            style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
                          >
                            Eliminar
                          </button>
                        )}
                      </div>
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
          title={`Editar · ${showEdit.username}`}
          user={showEdit}
          companies={companies}
          onClose={() => setShowEdit(null)}
          onSubmit={(form) => handleEdit(showEdit.id, form)}
          onResetPw={(pw) => handleResetPw(showEdit.id, pw)}
        />
      )}

      <ConfirmDialog
        open={confirmDel !== null}
        onClose={() => setConfirmDel(null)}
        onConfirm={() => confirmDel !== null && handleDelete(confirmDel)}
        title="Eliminar usuario"
        message={`¿Eliminar a "${users.find(u => u.id === confirmDel)?.username}"? Esta acción es irreversible.`}
        confirmText="Eliminar"
        variant="danger"
      />
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
      const payload: Record<string, unknown> = {
        username: form.username,
        email: form.email,
        full_name: form.full_name,
        rol_global: form.rol_global,
      };
      if (!user) payload.password = form.password;
      if (necesitaEmpresa()) payload.company_id = Number(form.empresa_id);
      await onSubmit(payload as Parameters<typeof onSubmit>[0]);
    } finally {
      setSaving(false);
    }
  }

  const rolCfg = ROL_CONFIG[form.rol_global] ?? ROL_CONFIG.usuario;
  const rolDesc: Record<string, string> = {
    superadmin: 'Acceso total al sistema, todas las empresas.',
    admin_empresa: 'Administra usuarios y RATs de su empresa asignada.',
    usuario: 'Accede a los RATs de su empresa asignada (solo lectura).',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl w-[500px] shadow-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>

        {/* Header con avatar preview */}
        <div className="px-6 pt-5 pb-4 flex items-center gap-4" style={{ borderBottom: '1px solid #E5E7EB' }}>
          <div className="w-12 h-12 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
            style={{ background: rolCfg.avatarBg }}>
            {form.full_name?.trim()
              ? form.full_name.trim().split(' ').filter(Boolean).slice(0, 2).map(p => p[0]).join('').toUpperCase()
              : (form.username.slice(0, 2).toUpperCase() || '?')}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-bold truncate" style={{ color: '#111827' }}>{title}</h3>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
              style={{ background: rolCfg.bg, color: rolCfg.color }}>
              {rolCfg.label}
            </span>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-sm font-bold flex-shrink-0"
            style={{ color: '#6B7280' }}>✕</button>
        </div>

        <div className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Usuario *</label>
              <input type="text" value={form.username} onChange={e => set('username', e.target.value)}
                disabled={!!user} autoComplete="off" className={inputCls}
                style={{ ...inputStyle, background: user ? '#F9FAFB' : undefined }} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nombre completo</label>
              <input type="text" value={form.full_name} onChange={e => set('full_name', e.target.value)}
                autoComplete="off" className={inputCls} style={inputStyle} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Email *</label>
            <input type="email" value={form.email} onChange={e => set('email', e.target.value)}
              autoComplete="off" className={inputCls} style={inputStyle} />
          </div>

          {!user && (
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Contraseña *</label>
              <input type="password" value={form.password} onChange={e => set('password', e.target.value)}
                autoComplete="new-password" className={inputCls} style={inputStyle} />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Rol global</label>
            <select value={form.rol_global} onChange={e => set('rol_global', e.target.value)}
              className={inputCls} style={inputStyle}>
              {ROL_GLOBAL_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <p className="text-xs mt-1.5 px-1" style={{ color: '#6B7280' }}>{rolDesc[form.rol_global]}</p>
          </div>

          {necesitaEmpresa() && (
            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Empresa asignada *</label>
              <select value={form.empresa_id} onChange={e => set('empresa_id', e.target.value)}
                className={inputCls} style={inputStyle}>
                <option value="">Seleccionar empresa...</option>
                {companies.map(c => <option key={c.id} value={String(c.id)}>{c.nombre}</option>)}
              </select>
            </div>
          )}

          {user && onResetPw && (
            <div className="rounded-xl p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
              <p className="text-sm font-medium mb-2" style={{ color: '#374151' }}>Cambiar contraseña</p>
              <div className="flex gap-2">
                <input type="password" value={newPw} onChange={e => setNewPw(e.target.value)}
                  placeholder="Nueva contraseña..." className={inputCls} style={{ ...inputStyle, flex: 1 }} />
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={!newPw.trim()}
                  onClick={() => { if (newPw.trim()) { onResetPw(newPw); setNewPw(''); } }}
                >
                  Cambiar
                </Button>
              </div>
            </div>
          )}
        </div>

        <div className="px-6 pb-5 flex gap-2 justify-end" style={{ borderTop: '1px solid #F3F4F6', paddingTop: 16 }}>
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSubmit} disabled={saving} loading={saving}>
            {user ? 'Guardar cambios' : 'Crear usuario'}
          </Button>
        </div>
      </div>
    </div>
  );
}
