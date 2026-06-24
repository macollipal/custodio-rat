'use client';

import { useEffect, useState, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import { DIAS_REVISION } from '@/lib/constants';
import KPICard from '@/components/dashboard/KPICard';
import AlertBanner, { AlertCard } from '@/components/dashboard/AlertBanner';
import StatusChart from '@/components/dashboard/StatusChart';
import CompletitudBar from '@/components/ui/CompletitudBar';
import Badge from '@/components/ui/Badge';
import { SkeletonTable } from '@/components/ui/Skeleton';
import OnboardingChecklist from '@/components/dashboard/OnboardingChecklist';
import RatDetailModal from '@/components/rat/RatDetailModal';
import { useDashboardAlerts } from '@/hooks/useDashboardAlerts';
import type { RAT } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const { user, company, rats, dashboardStats, setRats, setDashboardStats } = useApp();
  const [refreshing, setRefreshing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [tourStep, setTourStep] = useState(0);
  const [showTour, setShowTour] = useState(false);
  const [brechaCount, setBrechaCount] = useState(0);
  const [hasPolitica, setHasPolitica] = useState(false);
  const [selectedRat, setSelectedRat] = useState<RAT | null>(null);
  const nowRef = useRef(Date.now());
  const now = nowRef.current;

  const hasCache = dashboardStats !== null;

  const recientes = useMemo(() =>
    [...rats]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 6),
    [rats]
  );

  const sinRevisionCount = useMemo(() =>
    rats.filter(r => {
      const dias = (now - new Date(r.updated_at).getTime()) / 86_400_000;
      return dias > DIAS_REVISION;
    }).length,
    [rats, now]
  );

  const alertas = useDashboardAlerts(dashboardStats, sinRevisionCount);

  useEffect(() => {
    const tourDone = localStorage.getItem('custodio_tour_completed');
    if (tourDone !== 'true' && company) {
      setShowTour(true);
    }
  }, [company]);

  const tourSteps = [
    { target: 'h1', title: 'Bienvenido al Dashboard', content: 'Este es tu centro de control RAT. Aquí verás todas las métricas de cumplimiento de tu organización.' },
    { target: '[style*="grid"]', title: 'KPIs de cumplimiento', content: 'Estas tarjetas muestran el resumen de tus procesos RAT: total de procesos, completitud promedio, datos sensibles y EIPDs pendientes.' },
    { target: 'button[style*="2563EB"]', title: 'Crear procesos RAT', content: 'Haz clic aquí para crear tu primer proceso RAT. Cada proceso documenta cómo tu organización trata datos personales.' },
    { target: '[style*="F9FAFB"]', title: 'Alertas de cumplimiento', content: 'Las alertas te avisan de problemas críticos que requieren atención inmediata, como EIPDs pendientes o transferencias sin garantías.' },
    { target: '.\\32 xl\\:grid-cols-4', title: 'Procesos recientes', content: 'Aquí puedes ver los últimos procesos RAT creados o modificados. Haz clic en cualquier proceso para ver su detalle completo.' },
  ];

  function nextStep() {
    if (tourStep < tourSteps.length - 1) {
      setTourStep(t => t + 1);
    } else {
      setShowTour(false);
      localStorage.setItem('custodio_tour_completed', 'true');
      toast.success('Tour completado. ¡Comenzaste tu camino hacia el cumplimiento!');
    }
  }

  function skipTour() {
    setShowTour(false);
    localStorage.setItem('custodio_tour_completed', 'true');
  }

  useEffect(() => {
    if (!company) return;
    if (!hasCache) setRefreshing(true);

    Promise.all([
      api.getDashboardStats(company.id),
      api.listarRats(company.id),
      api.listarBrechas(company.id).catch(() => []),
      api.getPoliticaTransparencia(company.id).then(p => !!p).catch(() => false),
    ]).then(([s, ratList, breaches, hasPoliticaVal]) => {
      setDashboardStats(s);
      setRats(ratList);
      setBrechaCount(Array.isArray(breaches) ? breaches.length : 0);
      setHasPolitica(hasPoliticaVal);
      setLastSync(new Date());
    }).catch(() => {
      if (!hasCache) toast.error('No se pudieron cargar las estadísticas.');
    }).finally(() => setRefreshing(false));
  }, [company?.id]);

  function formatLastSync(date: Date): string {
    const diff = Math.floor((Date.now() - date.getTime()) / 1000);
    if (diff < 60) return 'justo ahora';
    if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
    return `hace ${Math.floor(diff / 3600)}h`;
  }

  if (!company) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400 text-sm">Selecciona o crea una empresa para ver el dashboard.</p>
      </div>
    );
  }

  if (!hasCache && refreshing) {
    return (
      <div className="space-y-6" aria-busy="true" aria-label="Cargando dashboard">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="bg-white rounded-xl p-6 animate-pulse" style={{ border: '1px solid #E5E7EB' }}>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>)}
        </div>
        <SkeletonTable rows={4} />
      </div>
    );
  }

  if (!dashboardStats) return null;

  const {
    total_procesos, completitud_promedio, procesos_con_datos_sensibles,
    requieren_eipd, transferencias_internacionales, por_estado,
    eipd_pendientes = 0, transferencias_sin_garantias = 0,
    interes_legitimo_sin_test = 0, encargados_sin_contrato = 0,
    rats_por_vencer = 0, rats_vencidos = 0,
    rats_sin_doc_base_legal = 0,
  } = dashboardStats;
  const completos  = por_estado?.completo  ?? 0;
  const borradores = por_estado?.borrador  ?? 0;

  const kpiColor = completitud_promedio >= 75 ? '#059669' : completitud_promedio >= 50 ? '#D97706' : '#DC2626';

  return (
    <div className="p-8 space-y-6">
      {(!company?.contacto_dpo || !company?.email_dpo) && (
        <AlertBanner
          message={
            !company?.contacto_dpo && !company?.email_dpo
              ? '<strong>DPO no configurado.</strong> Complete el nombre y email del Delegado de Protección de Datos en la configuración de la empresa.'
              : !company?.contacto_dpo
              ? '<strong>Nombre del DPO no configurado.</strong> Complete el nombre del Delegado de Protección de Datos en la configuración de la empresa.'
              : '<strong>Email del DPO no configurado.</strong> Complete el email del Delegado de Protección de Datos en la configuración de la empresa.'
          }
          type="danger"
        />
      )}

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Dashboard</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
            Resumen de cumplimiento · <strong>{company.nombre}</strong>
            {refreshing && <span className="ml-2 text-xs" style={{ color: '#9CA3AF' }}>actualizando...</span>}
            {lastSync && !refreshing && (
              <span className="ml-2 text-xs" style={{ color: '#9CA3AF' }}>· Actualizado {formatLastSync(lastSync)}</span>
            )}
          </p>
        </div>
        <button
          onClick={() => router.push('/rat')}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition"
          style={{ background: '#2563EB' }}
          onMouseEnter={e => (e.currentTarget.style.background = '#1D4ED8')}
          onMouseLeave={e => (e.currentTarget.style.background = '#2563EB')}
        >
          + Nuevo proceso
        </button>
      </div>

      <OnboardingChecklist
        ratsCount={total_procesos}
        hasDpo={Boolean(company?.contacto_dpo && company?.email_dpo)}
        hasContratoEncargado={encargados_sin_contrato === 0 && total_procesos > 0}
        hasBrechaRegistrada={brechaCount > 0}
        hasPoliticaTransparencia={hasPolitica}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total de procesos" value={total_procesos}
          subtitle={`${completos} completos · ${borradores} en borrador`}
          icon="📋" color="#2563EB"
        />
        <KPICard
          title="Completitud promedio" value={`${completitud_promedio}%`}
          subtitle="Nivel de madurez del RAT"
          icon="📊" color={kpiColor}
        />
        <KPICard
          title="Datos sensibles" value={procesos_con_datos_sensibles}
          subtitle="Procesos con categoría especial"
          icon="⚠️" color={procesos_con_datos_sensibles > 0 ? '#DC2626' : '#059669'}
        />
        <KPICard
          title="Requieren EIPD" value={requieren_eipd}
          subtitle="Evaluaciones de impacto pendientes"
          icon="🔍" color={requieren_eipd > 0 ? '#DC2626' : '#059669'}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="EIPDs pendientes" value={eipd_pendientes}
          subtitle="No iniciadas / en proceso"
          icon="📋" color={eipd_pendientes > 0 ? '#DC2626' : '#059669'}
        />
        <KPICard
          title="Transf. sin garantías" value={transferencias_sin_garantias}
          subtitle="Sin documentación SCC/BCR"
          icon="🌐" color={transferencias_sin_garantias > 0 ? '#D97706' : '#059669'}
        />
        <KPICard
          title="Int. legítimo sin test" value={interes_legitimo_sin_test}
          subtitle="Base legal incompleta"
          icon="⚖️" color={interes_legitimo_sin_test > 0 ? '#D97706' : '#059669'}
        />
        <KPICard
          title="Encargados sin contrato" value={encargados_sin_contrato}
          subtitle="Sin contrato Art. 14 quáter"
          icon="📄" color={encargados_sin_contrato > 0 ? '#D97706' : '#059669'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3 space-y-4">
          <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
            <h3 className="font-semibold text-sm mb-4" style={{ color: '#111827' }}>
              Distribución por estado
            </h3>
            <StatusChart data={por_estado ?? {}} />
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
            <h3 className="font-semibold text-sm mb-3" style={{ color: '#111827' }}>
              Nivel de completitud global
            </h3>
            <CompletitudBar pct={completitud_promedio} />
            <p className="text-xs mt-3" style={{ color: '#9CA3AF' }}>
              Promedio de {total_procesos} proceso(s) registrado(s) en el RAT de {company.nombre}.
            </p>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl p-6 shadow-sm h-full" style={{ border: '1px solid #E5E7EB' }}>
            <h3 className="font-semibold text-sm mb-4" style={{ color: '#111827' }}>
              Alertas de cumplimiento
            </h3>
            {alertas.length > 0
              ? alertas.map((a, i) => <AlertBanner key={i} message={a.message} type={a.type} />)
              : <AlertBanner
                  message="Sin alertas críticas. El RAT está en buenas condiciones de cumplimiento."
                  type="success"
                />
            }
            {(rats_vencidos > 0 || rats_por_vencer > 0) && (
              <div className="mt-3 space-y-2">
                {rats_vencidos > 0 && (
                  <AlertCard title="RATs vencidos" value={rats_vencidos} type="danger" />
                )}
                {rats_por_vencer > 0 && (
                  <AlertCard title="RATs por vencer (90 días)" value={rats_por_vencer} type="warning" />
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm" style={{ border: '1px solid #E5E7EB' }}>
        <h3 className="font-semibold text-sm mb-4" style={{ color: '#111827' }}>
          Procesos recientes
        </h3>
        {recientes.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-3xl mb-2">📋</div>
            <p className="text-sm font-medium" style={{ color: '#374151' }}>Sin procesos registrados</p>
            <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
              Crea el primer proceso de tratamiento de datos para esta empresa.
            </p>
          </div>
        ) : (
          <div className="space-y-0">
            <div
              className="hidden sm:grid text-xs font-semibold uppercase tracking-wide py-2 px-3 rounded-t-lg whitespace-nowrap"
              style={{ gridTemplateColumns: '3fr 2fr 1.5fr 120px', color: '#6B7280', background: '#F9FAFB', border: '1px solid #E5E7EB', borderBottom: 'none' }}
            >
              <span>Proceso</span>
              <span>Base legal</span>
              <span>Estado</span>
              <span>Completitud</span>
            </div>
            <div className="hidden sm:block">
              {recientes.map((rat, i) => (
                <button
                  key={rat.id}
                  onClick={() => setSelectedRat(rat)}
                  className="grid items-center py-3 px-3 whitespace-nowrap w-full text-left cursor-pointer transition-colors"
                  style={{
                    gridTemplateColumns: '3fr 2fr 1.5fr 120px',
                    background: i % 2 === 0 ? 'white' : '#FAFAFA',
                    border: '1px solid #E5E7EB',
                    borderTop: 'none',
                  }}
                >
                  <div>
                    <div className="text-sm font-semibold" style={{ color: '#111827' }}>{rat.nombre_proceso}</div>
                    <div className="text-xs" style={{ color: '#9CA3AF' }}>ID #{rat.id} · {rat.created_at?.slice(0, 10)}</div>
                  </div>
                  <div className="text-xs" style={{ color: '#6B7280' }}>{(rat.base_legal ?? '—').slice(0, 30)}</div>
                  <div><Badge estado={rat.estado} /></div>
                  <div><CompletitudBar pct={rat.completitud ?? 0} /></div>
                </button>
              ))}
            </div>
            <div className="sm:hidden divide-y" style={{ border: '1px solid #E5E7EB', borderRadius: '0 0 8px 8px' }}>
              {recientes.map((rat, i) => (
                <button
                  key={rat.id}
                  onClick={() => setSelectedRat(rat)}
                  className="px-4 py-3 w-full text-left cursor-pointer transition-colors"
                  style={{ background: i % 2 === 0 ? 'white' : '#FAFAFA' }}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold truncate" style={{ color: '#111827' }}>{rat.nombre_proceso}</div>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <Badge estado={rat.estado} />
                        <CompletitudBar pct={rat.completitud ?? 0} />
                        <span className="text-xs" style={{ color: '#9CA3AF' }}>ID #{rat.id}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-xs" style={{ color: '#6B7280' }}>{(rat.base_legal ?? '—').slice(0, 40)}{rat.base_legal && rat.base_legal.length > 40 ? '...' : ''}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedRat && (
        <RatDetailModal
          rat={selectedRat}
          mode="view"
          onClose={() => setSelectedRat(null)}
          onSwitchToEdit={() => router.push('/rat')}
          onDuplicate={async (rat) => {
            try {
              await api.duplicarRat(rat);
              toast.success(`"${rat.nombre_proceso}" duplicado correctamente.`);
              const [newStats, ratList] = await Promise.all([
                api.getDashboardStats(company!.id),
                api.listarRats(company!.id),
              ]);
              setDashboardStats(newStats);
              setRats(ratList);
              setSelectedRat(null);
            } catch (e) {
              toast.error(e instanceof Error ? e.message : 'Error al duplicar.');
            }
          }}
          onDelete={async (id) => {
            try {
              await api.eliminarRat(id);
              toast.success('RAT eliminado.');
              setSelectedRat(null);
              const [stats, ratList] = await Promise.all([
                api.getDashboardStats(company!.id),
                api.listarRats(company!.id),
              ]);
              setDashboardStats(stats);
              setRats(ratList);
            } catch (e) {
              toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
            }
          }}
          onRefresh={async () => {
            const [stats, ratList] = await Promise.all([
              api.getDashboardStats(company!.id),
              api.listarRats(company!.id),
            ]);
            setDashboardStats(stats);
            setRats(ratList);
          }}
          puedeEditar={user?.rol_global !== 'usuario'}
        />
      )}

      {showTour && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl max-w-sm mx-4 overflow-hidden">
            <div className="px-6 py-5" style={{ background: 'linear-gradient(135deg, #2563EB, #7C3AED)' }}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">🛡</span>
                <div>
                  <h3 className="text-white font-bold text-base">Tour guiado de Custodio</h3>
                  <p className="text-blue-200 text-xs">Paso {tourStep + 1} de {tourSteps.length}</p>
                </div>
              </div>
            </div>
            <div className="p-6">
              <h4 className="font-bold text-base mb-2" style={{ color: '#111827' }}>{tourSteps[tourStep].title}</h4>
              <p className="text-sm mb-5" style={{ color: '#6B7280' }}>{tourSteps[tourStep].content}</p>
              <div className="flex gap-2 justify-end">
                <button onClick={skipTour} className="px-4 py-2 rounded-lg text-xs font-medium border transition hover:bg-gray-50" style={{ borderColor: '#E5E7EB', color: '#6B7280' }}>
                  Omitir tour
                </button>
                <button onClick={nextStep} className="px-4 py-2 rounded-lg text-xs font-semibold text-white transition" style={{ background: '#2563EB' }}>
                  {tourStep < tourSteps.length - 1 ? 'Siguiente →' : '¡Comenzar!'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
