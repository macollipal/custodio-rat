'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';

interface Props {
  onClose: () => void;
}

export default function PasswordModal({ onClose }: Props) {
  const [form, setForm] = useState({ current: '', next: '', confirm: '' });
  const [saving, setSaving] = useState(false);
  const inputCls = 'w-full px-3.5 py-2.5 rounded-lg text-sm border focus:outline-none focus:ring-2 focus:ring-blue-500 transition text-gray-900 placeholder-gray-400';
  const inputStyle = { borderColor: '#D1D5DB', backgroundColor: '#FFFFFF' };

  function set(k: keyof typeof form, v: string) {
    setForm(f => ({ ...f, [k]: v }));
  }

  async function handleSave() {
    if (!form.current) { toast.error('Ingresa tu contraseña actual.'); return; }
    if (form.next.length < 6) { toast.error('La nueva contraseña debe tener al menos 6 caracteres.'); return; }
    if (form.next !== form.confirm) { toast.error('Las contraseñas no coinciden.'); return; }
    setSaving(true);
    try {
      await api.cambiarPassword(form.current, form.next);
      toast.success('Contraseña actualizada correctamente.');
      onClose();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al cambiar la contraseña.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.5)' }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-white rounded-2xl shadow-2xl p-7 w-full max-w-sm mx-4">
        <h2 className="text-base font-bold mb-1" style={{ color: '#111827' }}>Cambiar contraseña</h2>
        <p className="text-xs mb-5" style={{ color: '#9CA3AF' }}>Mínimo 6 caracteres.</p>

        <div className="space-y-3">
          {([
            { k: 'current' as const, label: 'Contraseña actual', placeholder: '••••••••' },
            { k: 'next'    as const, label: 'Nueva contraseña',  placeholder: '••••••••' },
            { k: 'confirm' as const, label: 'Confirmar nueva',   placeholder: '••••••••' },
          ]).map(({ k, label, placeholder }) => (
            <div key={k}>
              <label className="block text-xs font-medium mb-1" style={{ color: '#374151' }}>{label}</label>
              <input
                type="password"
                value={form[k]}
                onChange={e => set(k, e.target.value)}
                placeholder={placeholder}
                className={inputCls}
                style={inputStyle}
                onKeyDown={e => e.key === 'Enter' && handleSave()}
              />
            </div>
          ))}
        </div>

        <div className="flex gap-2 mt-5 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-semibold border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-white disabled:opacity-60 transition"
            style={{ background: '#2563EB' }}
          >
            {saving ? 'Guardando...' : 'Cambiar contraseña'}
          </button>
        </div>
      </div>
    </div>
  );
}
