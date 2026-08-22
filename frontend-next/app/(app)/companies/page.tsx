'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
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
  CompanyAlertsBanner,
  CompanyAuditDrawer,
} from '@/components/companies';
import { Button } from '@/components/ui/Button';

type View = 'list' | 'create';

export default function CompaniesPage() {
  const { company: activeCompany, setCompany, companies, setCompanies, user } = useApp();
  const router = useRouter();
  const [view, setView] = useState<View>('list');
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [confirmDelId, setConfirmDelId] = useState<number | null>(null);
  const [accessPanelId, setAccessPanelId] = useState<number | null>(null);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showUsersModal, setShowUsersModal] = useState<number | null>(null);
  const [auditCompany, setAuditCompany] = useState<Company | null>(null);

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

  async function handleExportarApdc(emp: Company) {
    if ((emp.total_rats ?? 0) === 0) {
      toast.error('Esta empresa no tiene RATs para exportar.');
      return;
    }
    try {
      const blob = await api.exportarCni(emp.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const safeName = emp.nombre.replace(/[^a-zA-Z0-9-_]/g, '_').slice(0, 40);
      a.download = `RAT_APDP_${safeName}_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success(`Reporte APDP de ${emp.nombre} descargado.`);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al exportar reporte APDC.');
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
                <Button
                  variant="secondary"
                  size="md"
                  onClick={() => setShowCreateUser(true)}
                >
                  + Nuevo usuario
                </Button>
              )}
              <Button
                size="md"
                onClick={() => setView('create')}
              >
                + Nueva empresa
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-16 text-sm" style={{ color: '#6B7280' }}>Cargando...</div>
          ) : companies.length === 0 ? (
            <div className="text-center py-14 bg-white rounded-xl" style={{ border: '1px solid #E5E7EB' }}>
              <div className="text-3xl mb-2">🏢</div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Sin empresas registradas</p>
              <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
                Crea la primera empresa responsable del tratamiento para comenzar.
              </p>
            </div>
          ) : (
            <>
              <CompanyAlertsBanner companies={companies} />
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
                            {emp.rats_vencidos != null && emp.rats_vencidos > 0 && (
                              <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#DC2626' }}>
                                {emp.rats_vencidos} RAT{emp.rats_vencidos > 1 ? 's' : ''} vencid{emp.rats_vencidos > 1 ? 'os' : 'o'}
                              </span>
                            )}
                            {(emp.solicitudes_pendientes ?? 0) > 0 && (
                              <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEF9C8', color: '#854D0E' }} title="Solicitudes ARCO pendientes">
                                {emp.solicitudes_pendientes} ARCO pendiente{(emp.solicitudes_pendientes ?? 0) > 1 ? 's' : ''}
                              </span>
                            )}
                            {(emp.solicitudes_vencidas_sla ?? 0) > 0 && (
                              <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#991B1B' }} title="Solicitudes ARCO con SLA vencido">
                                {emp.solicitudes_vencidas_sla} SLA vencid{(emp.solicitudes_vencidas_sla ?? 0) > 1 ? 'os' : 'o'}
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
                        <div className="text-right flex-shrink-0 ml-4 space-y-1">
                          <div className="text-2xl font-bold" style={{ color: '#111827' }}>{emp.total_rats ?? 0}</div>
                          <div className="text-xs uppercase tracking-wide" style={{ color: '#9CA3AF' }}>procesos RAT</div>
                          {emp.completitud_promedio != null && (
                            <div
                              className="text-xs font-semibold px-2 py-0.5 rounded-full inline-block"
                              style={{
                                background: emp.completitud_promedio >= 75 ? '#DCFCE7' : emp.completitud_promedio >= 50 ? '#FEF9C8' : '#FEE2E2',
                                color: emp.completitud_promedio >= 75 ? '#166534' : emp.completitud_promedio >= 50 ? '#854D0E' : '#DC2626',
                              }}
                            >
                              {emp.completitud_promedio}% completo
                            </div>
                          )}
                          {emp.has_politica_transparencia === false && (
                            <div
                              className="text-xs font-semibold px-2 py-0.5 rounded-full"
                              style={{ background: '#FEF9C8', color: '#854D0E' }}
                              title="Art. 14 ter — Política de transparencia pendiente"
                            >
                              ⚠️ Sin política
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex gap-2 flex-wrap">
                        {!esActiva && (
                          <Button
                            size="sm"
                            onClick={() => setCompany(emp)}
                          >
                            Seleccionar
                          </Button>
                        )}
                        {esActiva && (
                          <span className="px-3 py-1.5 rounded-lg text-xs font-semibold" style={{ background: '#DBEAFE', color: '#2563EB' }}>
                            ✓ Activa
                          </span>
                        )}
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => { setCompany(emp); router.push('/rat'); }}
                          title="Ir al módulo RAT con esta empresa seleccionada"
                        >
                          Ver RATs →
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setEditingId(editingId === emp.id ? null : emp.id)}
                        >
                          Editar
                        </Button>
                        {user?.rol_global === 'superadmin' && (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => setAccessPanelId(panelAbierto ? null : emp.id)}
                            style={{
                              borderColor: panelAbierto ? '#2563EB' : '#D1D5DB',
                              color: panelAbierto ? '#2563EB' : '#374151',
                              background: panelAbierto ? '#EFF6FF' : undefined,
                            }}
                          >
                            Gestionar accesos
                          </Button>
                        )}
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setShowUsersModal(emp.id)}
                        >
                          Listado usuarios
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setAuditCompany(emp)}
                          title="Ver historial de auditoría de los RATs de esta empresa"
                        >
                          📋 Auditoría
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleExportarApdc(emp)}
                          style={{ background: '#7C3AED', color: '#FFFFFF' }}
                          title="Descargar reporte en formato APDC (Ley 21.719) — JSON estructurado para presentar ante la autoridad"
                        >
                          📄 Reporte APDP
                        </Button>
                        {user?.rol_global === 'superadmin' ? (
                          <Link href="/configuracion" className="px-3 py-1.5 rounded-lg text-xs font-semibold transition hover:bg-gray-100" style={{ color: '#6B7280', background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
                            Gestión en Configuración →
                          </Link>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setConfirmDelId(emp.id)}
                            style={{ color: '#DC2626', borderColor: '#FCA5A5', borderWidth: '1px', borderStyle: 'solid' }}
                          >
                            Desactivar
                          </Button>
                        )}
                      </div>

                      {confirmDelId === emp.id && (
                        <div className="mt-3 rounded-lg p-3" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
                          <p className="text-sm font-medium mb-2" style={{ color: '#7F1D1D' }}>
                            ¿Desactivar <strong>{emp.nombre}</strong>? La empresa dejará de aparecer en los listados.
                          </p>
                          <div className="flex gap-2">
                            <Button variant="danger" size="sm" onClick={() => handleDelete(emp.id)}>
                              Confirmar desactivación
                            </Button>
                            <Button variant="secondary" size="sm" onClick={() => setConfirmDelId(null)}>
                              Cancelar
                            </Button>
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
            </>
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

      <CompanyAuditDrawer
        company={auditCompany}
        open={auditCompany !== null}
        onClose={() => setAuditCompany(null)}
      />
    </div>
  );
}
