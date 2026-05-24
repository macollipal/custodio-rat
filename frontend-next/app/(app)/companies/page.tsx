'use client';

import { useEffect, useState, useCallback } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import { validarRUT, formatearRUT } from '@/components/ui/validation';
import type { Company, UserCompany, RolEmpresa, Rubro } from '@/types';

type View = 'list' | 'create';

const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

const ROL_LABELS: Record<RolEmpresa, string> = {
  admin: 'Administrador',
  editor: 'Editor',
  viewer: 'Solo lectura',
};

// ── Panel gestión de usuarios por empresa ───────────────────────────────────

function UserAccessPanel({ companyId }: { companyId: number }) {
  const [accesos, setAccesos] = useState<UserCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [rol, setRol] = useState<RolEmpresa>('viewer');
  const [adding, setAdding] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setAccesos(await api.listarAccesos(companyId));
    } catch {
      toast.error('No se pudieron cargar los accesos.');
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => { load(); }, [load]);

  async function handleAdd() {
    if (!username.trim()) { toast.error('Ingresa un nombre de usuario.'); return; }
    setAdding(true);
    try {
      const uc = await api.agregarAcceso(companyId, username.trim(), rol);
      setAccesos(prev => [...prev, uc]);
      setUsername('');
      toast.success(`Acceso otorgado a "${uc.username}".`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al agregar acceso.');
    } finally {
      setAdding(false);
    }
  }

  async function handleChangeRol(userId: number, newRol: RolEmpresa) {
    try {
      const updated = await api.actualizarRolAcceso(companyId, userId, newRol);
      setAccesos(prev => prev.map(a => a.user_id === userId ? updated : a));
      toast.success('Rol actualizado.');
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al cambiar rol.');
    }
  }

  async function handleRemove(userId: number, uname: string) {
    try {
      await api.removerAcceso(companyId, userId);
      setAccesos(prev => prev.filter(a => a.user_id !== userId));
      toast.success(`Acceso de "${uname}" removido.`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al remover acceso.');
    }
  }

  return (
    <div className="mt-4 rounded-xl p-5" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
      <p className="text-sm font-semibold mb-3" style={{ color: '#111827' }}>Usuarios con acceso</p>

      {loading ? (
        <p className="text-xs" style={{ color: '#9CA3AF' }}>Cargando...</p>
      ) : (
        <div className="space-y-2 mb-4">
          {accesos.length === 0 && (
            <p className="text-xs" style={{ color: '#9CA3AF' }}>Sin usuarios asignados.</p>
          )}
          {accesos.map(a => (
            <div key={a.id} className="flex items-center gap-3 rounded-lg px-3 py-2 bg-white" style={{ border: '1px solid #E5E7EB' }}>
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium" style={{ color: '#111827' }}>{a.full_name || a.username}</span>
                <span className="text-xs ml-2" style={{ color: '#9CA3AF' }}>@{a.username}</span>
              </div>
              <select
                value={a.rol}
                onChange={e => handleChangeRol(a.user_id, e.target.value as RolEmpresa)}
                className="text-xs rounded-lg px-2 py-1 border focus:outline-none focus:ring-1 focus:ring-blue-500"
                style={{ borderColor: '#E5E7EB', color: '#374151' }}
              >
                {(Object.keys(ROL_LABELS) as RolEmpresa[]).map(r => (
                  <option key={r} value={r}>{ROL_LABELS[r]}</option>
                ))}
              </select>
              <button
                onClick={() => handleRemove(a.user_id, a.username)}
                className="text-xs px-2 py-1 rounded-lg border hover:bg-red-50 transition"
                style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
              >
                Remover
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Invitar usuario (username)</label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleAdd(); }}
            placeholder="Ej: jperez"
            className="w-full px-3 py-1.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: '#E5E7EB' }}
          />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Rol</label>
          <select
            value={rol}
            onChange={e => setRol(e.target.value as RolEmpresa)}
            className="px-3 py-1.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            {(Object.keys(ROL_LABELS) as RolEmpresa[]).map(r => (
              <option key={r} value={r}>{ROL_LABELS[r]}</option>
            ))}
          </select>
        </div>
        <button
          onClick={handleAdd}
          disabled={adding}
          className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white disabled:opacity-60"
          style={{ background: '#2563EB' }}
        >
          {adding ? '...' : 'Agregar'}
        </button>
      </div>
    </div>
  );
}

// ── Formularios empresa ───────────────────────────────────────────────────────

function CompanyForm({ onDone, onCancel }: { onDone: () => void; onCancel: () => void }) {
  const { setCompany, setCompanies, companies } = useApp();
  const [form, setForm] = useState({
    nombre: '', rut: '', rubro: '', direccion: '', contacto_dpo: '', email_dpo: '', descripcion: '',
  });
  const [rutError, setRutError] = useState('');
  const [saving, setSaving] = useState(false);

  function set(k: string, v: string) { setForm(f => ({ ...f, [k]: v })); }

  function handleRutChange(v: string) {
    const fmt = formatearRUT(v);
    setForm(f => ({ ...f, rut: fmt }));
    if (fmt.replace(/[^0-9kK]/gi, '').length >= 8) {
      const result = validarRUT(fmt);
      setRutError(result.valido ? '' : result.mensaje);
    } else {
      setRutError('');
    }
  }

  async function handleSave() {
    if (!form.nombre.trim()) { toast.error('La razón social es obligatoria.'); return; }
    if (!form.rut.trim()) { toast.error('El RUT es obligatorio.'); return; }
    const rutValid = validarRUT(form.rut);
    if (!rutValid.valido) { toast.error(rutValid.mensaje); return; }
    setSaving(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v.trim() || null])
      );
      const result = await api.crearEmpresa(payload);
      setCompany(result);
      setCompanies([...companies, result]);
      toast.success(`Empresa "${result.nombre}" registrada correctamente.`);
      onDone();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al crear empresa.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button onClick={onCancel} className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50" style={{ color: '#6B7280', borderColor: '#E5E7EB' }}>
          ← Volver al listado
        </button>
        <h2 className="text-lg font-bold" style={{ color: '#111827' }}>Nueva empresa responsable del tratamiento</h2>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm space-y-5" style={{ border: '1px solid #E5E7EB' }}>
        <p className="text-sm" style={{ color: '#6B7280' }}>
          Complete los datos del responsable conforme al Art. 5 de la Ley 21.719.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Razón social *</label>
            <input type="text" value={form.nombre} onChange={e => set('nombre', e.target.value)} placeholder="Ej: Empresa Ejemplo SpA" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>RUT *</label>
            <input
              type="text"
              value={form.rut}
              onChange={e => handleRutChange(e.target.value)}
              placeholder="Ej: 76.123.456-7"
              className={inputCls}
              style={{ borderColor: rutError ? '#DC2626' : '#E5E7EB' }}
            />
            {rutError && <p className="text-xs mt-1" style={{ color: '#DC2626' }}>{rutError}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Rubro / Sector</label>
            <input type="text" value={form.rubro} onChange={e => set('rubro', e.target.value)} placeholder="Ej: Retail, Salud, Tecnología" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Dirección</label>
            <input type="text" value={form.direccion} onChange={e => set('direccion', e.target.value)} placeholder="Ej: Av. Providencia 1234, Santiago" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Nombre del DPO (opcional)</label>
            <input type="text" value={form.contacto_dpo} onChange={e => set('contacto_dpo', e.target.value)} placeholder="Ej: Juan Pérez" className={inputCls} style={inputStyle} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Email del DPO</label>
            <input type="email" value={form.email_dpo} onChange={e => set('email_dpo', e.target.value)} placeholder="dpo@empresa.cl" className={inputCls} style={inputStyle} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Descripción (opcional)</label>
          <textarea value={form.descripcion} onChange={e => set('descripcion', e.target.value)} rows={2} placeholder="Breve descripción de la empresa y sus actividades principales." className={inputCls} style={inputStyle} />
        </div>

        <div className="rounded-lg px-4 py-3 text-sm" style={{ background: '#DBEAFE', borderLeft: '3px solid #2563EB', color: '#1E3A8A' }}>
          El DPO es la persona responsable de velar por el cumplimiento de la normativa de protección de datos al interior de la organización.
        </div>

        <div className="flex justify-end">
          <button onClick={handleSave} disabled={saving} className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition disabled:opacity-60" style={{ background: '#2563EB' }}>
            {saving ? 'Registrando...' : 'Registrar empresa'}
          </button>
        </div>
      </div>
    </div>
  );
}

function CompanyEditForm({ empresa, onDone, onCancel }: { empresa: Company; onDone: (updated: Company) => void; onCancel: () => void }) {
  const [form, setFormState] = useState({
    nombre: empresa.nombre ?? '',
    rubro_id: empresa.rubro_id?.toString() ?? '',
    direccion: empresa.direccion ?? '',
    contacto_dpo: empresa.contacto_dpo ?? '',
    email_dpo: empresa.email_dpo ?? '',
    descripcion: empresa.descripcion ?? '',
  });
  const [saving, setSaving] = useState(false);
  const [rubros, setRubros] = useState<Rubro[]>([]);

  useEffect(() => { api.listarRubros().then(setRubros).catch(() => {}); }, []);

  function set(k: string, v: string) { setFormState(f => ({ ...f, [k]: v })); }

  async function handleSave() {
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (k === 'rubro_id') payload[k] = v ? Number(v) : null;
        else payload[k] = v.trim ? (v.trim() || null) : v;
      }
      const result = await api.actualizarEmpresa(empresa.id, payload as Partial<Company>);
      toast.success('Empresa actualizada correctamente.');
      onDone(result);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al actualizar.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="rounded-xl p-5 mt-4 space-y-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
      <p className="text-sm font-semibold" style={{ color: '#111827' }}>Editar: {empresa.nombre}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Razón social</label>
          <input type="text" value={form.nombre} onChange={e => set('nombre', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Rubro</label>
          <select value={form.rubro_id} onChange={e => set('rubro_id', e.target.value)} className={inputCls} style={inputStyle}>
            <option value="">— Sin rubro —</option>
            {rubros.map(r => <option key={r.id} value={String(r.id)}>{r.nombre}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Dirección</label>
          <input type="text" value={form.direccion} onChange={e => set('direccion', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>DPO</label>
          <input type="text" value={form.contacto_dpo} onChange={e => set('contacto_dpo', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Email DPO</label>
          <input type="email" value={form.email_dpo} onChange={e => set('email_dpo', e.target.value)} className={inputCls} style={inputStyle} />
        </div>
        <div className="col-span-2">
          <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>Descripción</label>
          <textarea value={form.descripcion} onChange={e => set('descripcion', e.target.value)} rows={2} className={inputCls} style={inputStyle} />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <button onClick={onCancel} className="px-4 py-1.5 rounded-lg text-xs font-semibold border hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#374151' }}>Cancelar</button>
        <button onClick={handleSave} disabled={saving} className="px-4 py-1.5 rounded-lg text-xs font-semibold text-white disabled:opacity-60" style={{ background: '#2563EB' }}>
          {saving ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </div>
    </div>
  );
}

// ── Modal crear usuario ───────────────────────────────────────────────────────

function CreateUserModal({ onClose }: { onClose: () => void }) {
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', rol_global: 'usuario' });
  const [saving, setSaving] = useState(false);

  function set(k: string, v: string | boolean) { setForm(f => ({ ...f, [k]: v })); }

  async function handleSave() {
    if (!form.username.trim() || !form.email.trim() || !form.password.trim()) {
      toast.error('Username, email y contraseña son obligatorios.');
      return;
    }
    if (form.password.length < 6) { toast.error('La contraseña debe tener al menos 6 caracteres.'); return; }
    setSaving(true);
    try {
      await api.crearUsuario({ ...form, full_name: form.full_name.trim() || form.username });
      toast.success(`Usuario "${form.username}" creado correctamente.`);
      onClose();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al crear usuario.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.4)' }}>
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl" style={{ border: '1px solid #E5E7EB' }}>
        <h2 className="text-lg font-bold mb-4" style={{ color: '#111827' }}>Nuevo usuario</h2>
        <div className="space-y-3">
          {[
            { k: 'username', label: 'Username *', type: 'text', placeholder: 'jperez' },
            { k: 'email', label: 'Email *', type: 'email', placeholder: 'jperez@empresa.cl' },
            { k: 'full_name', label: 'Nombre completo', type: 'text', placeholder: 'Juan Pérez' },
            { k: 'password', label: 'Contraseña *', type: 'password', placeholder: 'Mínimo 6 caracteres' },
          ].map(({ k, label, type, placeholder }) => (
            <div key={k}>
              <label className="block text-sm font-medium mb-1" style={{ color: '#374151' }}>{label}</label>
              <input
                type={type}
                value={(form as Record<string, unknown>)[k] as string}
                onChange={e => set(k, e.target.value)}
                placeholder={placeholder}
                className={inputCls}
                style={inputStyle}
              />
            </div>
          ))}
          <label className="flex items-center gap-2 cursor-pointer">
            <span className="text-sm" style={{ color: '#374151' }}>Rol global:</span>
            <select value={form.rol_global} onChange={e => set('rol_global', e.target.value)} className="px-2 py-1 rounded border text-sm" style={{ borderColor: '#E5E7EB' }}>
              <option value="usuario">Usuario</option>
              <option value="admin_empresa">Admin empresa</option>
              <option value="admin">Administrador</option>
            </select>
          </label>
        </div>
        <div className="flex gap-2 justify-end mt-5">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-semibold border hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#374151' }}>
            Cancelar
          </button>
          <button onClick={handleSave} disabled={saving} className="px-4 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-60" style={{ background: '#2563EB' }}>
            {saving ? 'Creando...' : 'Crear usuario'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────

export default function CompaniesPage() {
  const { company: activeCompany, setCompany, companies, setCompanies, user } = useApp();
  const [view, setView] = useState<View>('list');
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [confirmDelId, setConfirmDelId] = useState<number | null>(null);
  const [accessPanelId, setAccessPanelId] = useState<number | null>(null);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState<number | null>(null);

  async function loadCompanies() {
    setLoading(true);
    try {
      setCompanies(await api.listarEmpresas());
    } catch {
      toast.error('No se pudieron cargar las empresas.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadCompanies(); }, []);

  async function handleDelete(id: number) {
    try {
      await api.eliminarEmpresa(id);
      toast.success('Empresa eliminada.');
      setConfirmDelId(null);
      if (activeCompany?.id === id) setCompany(companies.find(c => c.id !== id) ?? null as unknown as Company);
      await loadCompanies();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
    }
  }

  return (
    <div className="p-8">
      {showCreateUser && <CreateUserModal onClose={() => setShowCreateUser(false)} />}

      {view === 'list' && (
        <>
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Empresas</h1>
              <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
                Responsables del tratamiento de datos personales registrados en Custodio
              </p>
            </div>
            <div className="flex gap-2">
              {user?.rol_global === 'superadmin' && (
                <button
                  onClick={() => setShowCreateUser(true)}
                  className="px-4 py-2 rounded-lg text-sm font-semibold border transition hover:bg-gray-50"
                  style={{ borderColor: '#E5E7EB', color: '#374151' }}
                >
                  + Nuevo usuario
                </button>
              )}
              <button
                onClick={() => setView('create')}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition"
                style={{ background: '#2563EB' }}
                onMouseEnter={e => (e.currentTarget.style.background = '#1D4ED8')}
                onMouseLeave={e => (e.currentTarget.style.background = '#2563EB')}
              >
                + Nueva empresa
              </button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-16 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
          ) : companies.length === 0 ? (
            <div className="text-center py-14 bg-white rounded-xl" style={{ border: '1px solid #E5E7EB' }}>
              <div className="text-3xl mb-2">🏢</div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Sin empresas registradas</p>
              <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                Crea la primera empresa responsable del tratamiento para comenzar.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {companies.map(emp => {
                const esActiva = emp.id === activeCompany?.id;
                const panelAbierto = accessPanelId === emp.id;
                return (
                  <div key={emp.id}>
                    <div
                      className="bg-white rounded-xl p-5 shadow-sm"
                      style={{
                        border: `1px solid ${esActiva ? '#2563EB' : '#E5E7EB'}`,
                        borderTop: esActiva ? '3px solid #2563EB' : '1px solid #E5E7EB',
                        boxShadow: esActiva ? '0 4px 12px rgba(37,99,235,0.1)' : '0 1px 3px rgba(0,0,0,0.04)',
                      }}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="flex items-center gap-2.5 mb-1">
                            <span className="font-bold text-base" style={{ color: '#111827' }}>{emp.nombre}</span>
                            {esActiva && (
                              <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#DBEAFE', color: '#2563EB' }}>
                                ACTIVA
                              </span>
                            )}
                          </div>
                          <p className="text-sm" style={{ color: '#6B7280' }}>
                            RUT: <strong>{emp.rut}</strong>
                            {emp.rubro && ` · Rubro: ${emp.rubro}`}
                            {emp.contacto_dpo && ` · DPO: ${emp.contacto_dpo}`}
                          </p>
                          {emp.descripcion && (
                            <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                              {emp.descripcion.slice(0, 80)}{emp.descripcion.length > 80 ? '...' : ''}
                            </p>
                          )}
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <div className="text-2xl font-bold" style={{ color: '#111827' }}>{emp.total_rats ?? 0}</div>
                          <div className="text-xs uppercase tracking-wide" style={{ color: '#9CA3AF' }}>procesos RAT</div>
                        </div>
                      </div>

                      <div className="flex gap-2 flex-wrap">
                        {!esActiva && (
                          <button
                            onClick={() => setCompany(emp)}
                            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white transition"
                            style={{ background: '#2563EB' }}
                          >
                            Seleccionar
                          </button>
                        )}
                        {esActiva && (
                          <span className="px-3 py-1.5 rounded-lg text-xs font-semibold" style={{ background: '#DBEAFE', color: '#2563EB' }}>
                            ✓ Activa
                          </span>
                        )}
                        <button
                          onClick={() => setEditingId(editingId === emp.id ? null : emp.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
                          style={{ borderColor: '#E5E7EB', color: '#374151' }}
                        >
                          Editar
                        </button>
                        {user?.rol_global === 'superadmin' && (
                          <button
                            onClick={() => setAccessPanelId(panelAbierto ? null : emp.id)}
                            className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
                            style={{
                              borderColor: panelAbierto ? '#2563EB' : '#D1D5DB',
                              color: panelAbierto ? '#2563EB' : '#374151',
                              background: panelAbierto ? '#EFF6FF' : undefined,
                            }}
                          >
                            Gestionar accesos
                          </button>
                        )}
                        <button
                          onClick={() => setShowUsersModal(emp.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
                          style={{ borderColor: '#D1D5DB', color: '#374151' }}
                        >
                          Listado usuarios
                        </button>
                        <button
                          onClick={() => setConfirmDelId(emp.id)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-red-50"
                          style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
                        >
                          Eliminar
                        </button>
                      </div>

                      {confirmDelId === emp.id && (
                        <div className="mt-3 rounded-lg p-3" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
                          <p className="text-sm font-medium mb-2" style={{ color: '#7F1D1D' }}>
                            ¿Eliminar <strong>{emp.nombre}</strong> y todos sus registros RAT? Esta acción es irreversible.
                          </p>
                          <div className="flex gap-2">
                            <button onClick={() => handleDelete(emp.id)} className="px-3 py-1 rounded text-xs font-semibold text-white" style={{ background: '#DC2626' }}>
                              Confirmar eliminación
                            </button>
                            <button onClick={() => setConfirmDelId(null)} className="px-3 py-1 rounded text-xs font-semibold border" style={{ borderColor: '#E5E7EB', color: '#374151' }}>
                              Cancelar
                            </button>
                          </div>
                        </div>
                      )}

                      {panelAbierto && <UserAccessPanel companyId={emp.id} />}
                    </div>

                    {editingId === emp.id && (
                      <CompanyEditForm
                        empresa={emp}
                        onDone={updated => {
                          setCompanies(companies.map(c => c.id === updated.id ? updated : c));
                          if (activeCompany?.id === updated.id) setCompany(updated);
                          setEditingId(null);
                        }}
                        onCancel={() => setEditingId(null)}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {view === 'create' && (
        <CompanyForm
          onDone={() => { setView('list'); loadCompanies(); }}
          onCancel={() => setView('list')}
        />
      )}

      {showUsersModal && (
        <CompanyUsersModal
          companyId={showUsersModal}
          onClose={() => setShowUsersModal(null)}
        />
      )}
    </div>
  );
}

function CompanyUsersModal({ companyId, onClose }: { companyId: number; onClose: () => void }) {
  const [usuarios, setUsuarios] = useState<Array<{ id: number; username: string; full_name: string; email: string; rol_global: string }>>([]);
  const [loading, setLoading] = useState(true);

  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  useEffect(() => {
    setLoading(true);
    api.listarUsuarios().then(data => {
      setUsuarios(data.filter((u: any) => u.empresa_id === companyId));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [companyId]);

  function rolBadge(rol: string) {
    if (rol === 'superadmin') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#F3E8FF', color: '#7C3AED' }}>Superadmin</span>;
    if (rol === 'admin_empresa') return <span className="text-xs font-semibold px-2 py-0.5 rounded-full" style={{ background: '#DBEAFE', color: '#2563EB' }}>Admin empresa</span>;
    return <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: '#F3F4F6', color: '#6B7280' }}>Usuario</span>;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl p-6 w-[560px] shadow-2xl max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-bold" style={{ color: '#111827' }}>Usuarios de la empresa</h3>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-sm font-bold" style={{ color: '#6B7280' }}>✕</button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
        ) : usuarios.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-2xl mb-2">👤</div>
            <p className="text-sm" style={{ color: '#6B7280' }}>No hay usuarios asignados a esta empresa.</p>
          </div>
        ) : (
          <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #D1D5DB' }}>
            <table className="w-full">
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#6B7280', background: '#F9FAFB', borderBottom: '1px solid #D1D5DB' }}>
                  <th className="px-4 py-3 text-left">Usuario</th>
                  <th className="px-4 py-3 text-right">Rol global</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((u, i) => (
                  <tr key={u.id} style={{ borderTop: i > 0 ? '1px solid #F3F4F6' : 'none' }}>
                    <td className="px-4 py-3">
                      <div className="text-sm font-bold" style={{ color: '#111827' }}>{u.username}</div>
                      <div className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{u.full_name}</div>
                      <div className="text-xs" style={{ color: '#9CA3AF' }}>{u.email}</div>
                    </td>
                    <td className="px-4 py-3 text-right align-middle">
                      {rolBadge(u.rol_global)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex justify-end mt-4">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm border transition hover:bg-gray-50" style={{ borderColor: '#D1D5DB', color: '#374151' }}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
