'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import type { Rubro, RATSugerido } from '@/types';

export default function RubrosPage() {
  const { user } = useApp();
  const [rubros, setRubros] = useState<Rubro[]>([]);
  const [sugerencias, setSugerencias] = useState<Record<number, RATSugerido[]>>({});
  const [selectedRubro, setSelectedRubro] = useState<Rubro | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listarRubros().then(setRubros).catch(() => toast.error('Error al cargar rubros')).finally(() => setLoading(false));
  }, []);

  function selectRubro(r: Rubro) {
    setSelectedRubro(r);
    if (!sugerencias[r.id]) {
      api.sugerenciasPorRubro(r.id).then(sugs => {
        setSugerencias(prev => ({ ...prev, [r.id]: sugs }));
      }).catch(() => {});
    }
  }

  async function guardarOrden(actual: Rubro[], fromIdx: number, toIdx: number) {
    const nuevo = [...actual];
    const [item] = nuevo.splice(fromIdx, 1);
    nuevo.splice(toIdx, 0, item);
    const updates = nuevo.map((r, i) => ({ id: r.id, orden: nuevo.length - i }));
    setRubros(nuevo);
    for (const u of updates) {
      try {
        await api.actualizarRubro(u.id, { orden: u.orden });
      } catch {
        toast.error(`Error al reordenar rubro ${u.id}`);
      }
    }
    toast.success('Orden actualizado');
  }

  const isSuperadmin = user?.rol_global === 'superadmin';

  if (loading) {
    return <div className="p-8 text-gray-400">Cargando...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Rubros y sugerencias</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>Reordena rubros y gestiona las plantillas de RAT sugeridas por rubro</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lista de rubros */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl p-4 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
            <p className="text-xs font-bold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Rubros ({rubros.length})</p>
            <p className="text-xs mb-3" style={{ color: '#6B7280' }}>Superadmin puede reordenar arrastrando. Admin empresa ve su rubro.</p>
            <div className="space-y-2">
              {rubros.map((r, i) => (
                <div
                  key={r.id}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition ${selectedRubro?.id === r.id ? 'ring-2' : ''}`}
                  style={{
                    background: selectedRubro?.id === r.id ? '#EFF6FF' : '#F9FAFB',
                    border: `1px solid ${selectedRubro?.id === r.id ? '#2563EB' : '#E5E7EB'}`,
                    color: selectedRubro?.id === r.id ? '#1D4ED8' : '#374151',
                  }}
                  onClick={() => selectRubro(r)}
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium">{r.nombre}</p>
                    <p className="text-xs" style={{ color: '#9CA3AF' }}>{r.total_sugerencias ?? 0} sugerencias</p>
                  </div>
                  {isSuperadmin && (
                    <div className="flex gap-1">
                      {i > 0 && (
                        <button
                          onClick={e => { e.stopPropagation(); guardarOrden(rubros, i, i - 1); }}
                          className="w-6 h-6 rounded text-xs font-bold hover:bg-gray-200 flex items-center justify-center"
                          style={{ color: '#6B7280' }}
                          title="Subir"
                        >↑</button>
                      )}
                      {i < rubros.length - 1 && (
                        <button
                          onClick={e => { e.stopPropagation(); guardarOrden(rubros, i, i + 1); }}
                          className="w-6 h-6 rounded text-xs font-bold hover:bg-gray-200 flex items-center justify-center"
                          style={{ color: '#6B7280' }}
                          title="Bajar"
                        >↓</button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Detalle de sugerencias */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl p-4 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
            {!selectedRubro ? (
              <p className="text-sm text-center py-8" style={{ color: '#9CA3AF' }}>
                Selecciona un rubro para ver sus plantillas de RAT
              </p>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm font-bold" style={{ color: '#111827' }}>{selectedRubro.nombre}</p>
                    <p className="text-xs" style={{ color: '#6B7280' }}>
                      {(sugerencias[selectedRubro.id] || []).length} plantillas
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  {(sugerencias[selectedRubro.id] || []).map(sug => (
                    <div
                      key={sug.id}
                      className="rounded-lg p-3"
                      style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-semibold" style={{ color: '#111827' }}>{sug.nombre_proceso}</p>
                          <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>{sug.categoria_datos}</p>
                          {sug.categoria_titulares && (
                            <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>Titulares: {sug.categoria_titulares}</p>
                          )}
                          <div className="flex gap-1 flex-wrap mt-2">
                            {sug.datos_sensibles && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#FEF3C7', color: '#92400E' }}>⚠️ Sensibles</span>}
                            {sug.evaluacion_impacto && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#DBEAFE', color: '#1E3A8A' }}>📋 EIPD</span>}
                            {sug.decisiones_automatizadas && <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ background: '#F3F4F6', color: '#374151' }}>🤖 Dec. auto</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {(sugerencias[selectedRubro.id] || []).length === 0 && (
                    <p className="text-sm text-center py-4" style={{ color: '#9CA3AF' }}>
                      Sin sugerencias para este rubro
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}