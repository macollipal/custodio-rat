'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import RatTable from '@/components/rat/RatTable';
import RatWizard from '@/components/rat/RatWizard';
import RatDetailModal from '@/components/rat/RatDetailModal';
import { SkeletonTable } from '@/components/ui/Skeleton';
import type { RAT } from '@/types';

export default function RatPage() {
  const { company, rats, setRats, puedeEditar } = useApp();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [selectedRat, setSelectedRat] = useState<RAT | null>(null);
  const [modalMode, setModalMode] = useState<'view' | 'edit'>('view');
  const [wizardOpen, setWizardOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  const hasCache = rats.length > 0;

  async function loadRats() {
    if (!company) return;
    if (!hasCache) setRefreshing(true);
    try {
      const list = await api.listarRats(company.id);
      setRats(Array.isArray(list) ? list : []);
    } catch {
      if (!hasCache) toast.error('No se pudieron cargar los procesos.');
    } finally {
      setRefreshing(false);
      setInitialLoading(false);
    }
  }

  useEffect(() => { setInitialLoading(true); loadRats(); }, [company?.id]);

  // Sincronizar selectedRat cuando la lista se refresca tras una edición
  useEffect(() => {
    if (selectedRat) {
      const updated = rats.find(r => r.id === selectedRat.id);
      if (updated) setSelectedRat(updated);
    }
  }, [rats]);

  // Abrir drawer del RAT cuando se llega con ?selected=<id> (deep-link desde /eipd).
  useEffect(() => {
    const selectedId = Number(searchParams.get('selected'));
    if (!selectedId || Number.isNaN(selectedId)) return;
    const target = rats.find((r) => r.id === selectedId);
    if (target) {
      setSelectedRat(target);
      setModalMode('view');
      const url = new URL(window.location.href);
      url.searchParams.delete('selected');
      router.replace(url.pathname + (url.search ? url.search : ''));
    }
  }, [rats, searchParams, router]);

  function handleSelectRat(rat: RAT) {
    setSelectedRat(rat);
    setModalMode('view');
  }

  function handleSwitchToEdit() {
    setModalMode('edit');
  }

  function handleCloseModal() {
    setSelectedRat(null);
    setModalMode('view');
  }

  async function handleDuplicate(rat: RAT) {
    try {
      const nuevo = await api.duplicarRat(rat);
      toast.success(`RAT "Copia de ${rat.nombre_proceso}" creado · ID #${nuevo.id}`);
      await loadRats();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al duplicar.');
    }
  }

  async function handleDelete(id: number) {
    const ratToDelete = rats.find(r => r.id === id);
    try {
      await api.eliminarRat(id);
      toast.success('Proceso eliminado.', {
        duration: 5000,
        action: {
          label: 'Deshacer',
          onClick: () => {
            if (ratToDelete) {
              api.crearRat({
                company_id: ratToDelete.company_id,
                nombre_proceso: ratToDelete.nombre_proceso,
                categoria_datos: ratToDelete.categoria_datos ?? '',
                categoria_titulares: ratToDelete.categoria_titulares ?? '',
                finalidad: ratToDelete.finalidad ?? '',
                base_legal: ratToDelete.base_legal ?? 'Otra',
                fuente_datos: ratToDelete.fuente_datos ?? '',
                plazo_retencion: ratToDelete.plazo_retencion ?? '',
                transferencia_datos: ratToDelete.transferencia_datos,
                medidas_seguridad: ratToDelete.medidas_seguridad,
                destinatarios: ratToDelete.destinatarios,
                transferencia_internacional: ratToDelete.transferencia_internacional,
                pais_destino: ratToDelete.pais_destino,
                garantias_transferencia_int: ratToDelete.garantias_transferencia_int,
                datos_sensibles: ratToDelete.datos_sensibles,
                tipo_dato_sensible: ratToDelete.tipo_dato_sensible,
                evaluacion_impacto: ratToDelete.evaluacion_impacto,
                decisiones_automatizadas: ratToDelete.decisiones_automatizadas,
                test_interes_legitimo: ratToDelete.test_interes_legitimo,
                nombre_encargado: ratToDelete.nombre_encargado,
                tiene_contrato_encargado: ratToDelete.tiene_contrato_encargado,
                estado_eipd: ratToDelete.estado_eipd,
                fecha_eipd: ratToDelete.fecha_eipd,
                estado: ratToDelete.estado,
                observaciones_auditoria: ratToDelete.observaciones_auditoria,
              }).then(() => {
                toast.success('Proceso restaurado correctamente.');
                loadRats();
              }).catch(() => toast.error('Error al restaurar el proceso.'));
            }
          },
        },
      });
      setSelectedRat(null);
      loadRats();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
    }
  }

  if (!company) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400 text-sm">Selecciona una empresa para gestionar el RAT.</p>
      </div>
    );
  }

  if (initialLoading) {
    return (
      <div className="p-4 sm:p-8 space-y-4">
        <div className="flex items-start justify-between mb-6 flex-col sm:flex-row gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Procesos RAT</h1>
            <p className="text-sm mt-1" style={{ color: '#6B7280' }}>Registro de Actividades de Tratamiento · Art. 16 Ley 21.719</p>
          </div>
        </div>
        <SkeletonTable rows={5} />
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-8">
      {!wizardOpen && (
        <div className="flex items-start justify-between mb-6 flex-col sm:flex-row gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Procesos RAT</h1>
            <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
              Registro de Actividades de Tratamiento · Art. 16 Ley 21.719
              {refreshing && <span className="ml-2 text-xs" style={{ color: '#9CA3AF' }}>actualizando...</span>}
            </p>
          </div>
          {puedeEditar && (
            <button
              onClick={() => setWizardOpen(true)}
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition"
              style={{ background: '#2563EB' }}
              onMouseEnter={e => (e.currentTarget.style.background = '#1D4ED8')}
              onMouseLeave={e => (e.currentTarget.style.background = '#2563EB')}
            >
              + Nuevo proceso
            </button>
          )}
        </div>
      )}

      {!wizardOpen && (
        <RatTable
          rats={rats}
          company={company}
          onSelect={handleSelectRat}
          onRefresh={loadRats}
          puedeEditar={puedeEditar}
        />
      )}

      {wizardOpen && (
        <RatWizard
          company={company}
          onDone={() => { setWizardOpen(false); loadRats(); }}
          onCancel={() => setWizardOpen(false)}
        />
      )}

      <RatDetailModal
        rat={selectedRat}
        mode={modalMode}
        onClose={handleCloseModal}
        onSwitchToEdit={handleSwitchToEdit}
        onDuplicate={handleDuplicate}
        onDelete={handleDelete}
        onRefresh={loadRats}
        puedeEditar={puedeEditar ?? false}
      />
    </div>
  );
}
