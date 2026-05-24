'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import RatTable from '@/components/rat/RatTable';
import RatWizard from '@/components/rat/RatWizard';
import RatEditForm from '@/components/rat/RatEditForm';
import { SkeletonTable } from '@/components/ui/Skeleton';
import type { RAT } from '@/types';

type View = 'table' | 'wizard' | 'edit';

export default function RatPage() {
  const { company, rats, setRats, puedeEditar } = useApp();
  const [view, setView] = useState<View>('table');
  const [refreshing, setRefreshing] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [editingRat, setEditingRat] = useState<RAT | null>(null);

  const hasCache = rats.length > 0;

  async function loadRats() {
    if (!company) return;
    if (!hasCache) setRefreshing(true);
    try {
      const list = await api.listarRats(company.id);
      setRats(list);
    } catch {
      if (!hasCache) toast.error('No se pudieron cargar los procesos.');
    } finally {
      setRefreshing(false);
      setInitialLoading(false);
    }
  }

  useEffect(() => { setInitialLoading(true); loadRats(); }, [company?.id]);

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
      {view === 'table' && (
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
              onClick={() => setView('wizard')}
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

      {view === 'table' && (
        <RatTable
          rats={rats}
          company={company}
          onEdit={rat => { setEditingRat(rat); setView('edit'); }}
          onRefresh={loadRats}
          puedeEditar={puedeEditar}
        />
      )}

      {view === 'wizard' && (
        <RatWizard
          company={company}
          onDone={() => { setView('table'); loadRats(); }}
          onCancel={() => setView('table')}
        />
      )}

      {view === 'edit' && editingRat && (
        <RatEditForm
          rat={editingRat}
          onDone={() => { setView('table'); loadRats(); setEditingRat(null); }}
          onCancel={() => { setView('table'); setEditingRat(null); }}
        />
      )}
    </div>
  );
}
