'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { Company, User } from '@/types';
import {
  CompanyForm,
  CompanyEditForm,
  UserAccessPanel,
  CreateUserModal,
  CompanyUsersModal,
} from '@/components/companies';

type View = 'list' | 'create';

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
      if (user?.rol_global === 'superadmin') {
        await api.eliminarEmpresa(id);
        toast.success('Empresa eliminada.');
      } else {
        await api.desactivarEmpresa(id);
        toast.success('Empresa desactivada.');
      }
      setConfirmDelId(null);
      if (activeCompany?.id === id) setCompany(companies.find(c => c.id !== id) ?? null as unknown as Company);
      await loadCompanies();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al desactivar.');
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
                        {user?.rol_global === 'superadmin' ? (
                          <span className="px-3 py-1.5 rounded-lg text-xs font-semibold" style={{ color: '#9CA3AF', background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                            Gestión en Configuración
                          </span>
                        ) : (
                          <button
                            onClick={() => setConfirmDelId(emp.id)}
                            className="px-3 py-1.5 rounded-lg text-xs font-semibold border transition hover:bg-red-50"
                            style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
                          >
                            Desactivar
                          </button>
                        )}
                      </div>

                      {confirmDelId === emp.id && (
                        <div className="mt-3 rounded-lg p-3" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
                          <p className="text-sm font-medium mb-2" style={{ color: '#7F1D1D' }}>
                            ¿Desactivar <strong>{emp.nombre}</strong>? La empresa dejará de aparecer en los listados.
                          </p>
                          <div className="flex gap-2">
                            <button onClick={() => handleDelete(emp.id)} className="px-3 py-1 rounded text-xs font-semibold text-white" style={{ background: '#DC2626' }}>
                              Confirmar desactivación
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
