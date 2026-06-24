'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';

const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

interface CreateUserModalProps {
  onClose: () => void;
  onCreated?: () => void;
}

export function CreateUserModal({ onClose, onCreated }: CreateUserModalProps) {
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', rol_global: 'usuario' });
  const [saving, setSaving] = useState(false);

  function set(k: string, v: string | boolean) { setForm(f => ({ ...f, [k]: v })); }

  async function handleSave() {
    if (!form.username.trim() || !form.email.trim() || !form.password.trim()) {
      toast.error('Username, email y contraseña son obligatorios.');
      return;
    }
    if (form.password.length < 6) { toast.error('La contraseña debe tener al menos 6 caracteres.'); return; }
    const emailValid = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(form.email.trim());
    if (!emailValid) { toast.error('El email no es valido.'); return; }
    setSaving(true);
    try {
      await api.crearUsuario({ ...form, full_name: form.full_name.trim() || form.username });
      toast.success(`Usuario "${form.username}" creado correctamente.`);
      onCreated?.();
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
