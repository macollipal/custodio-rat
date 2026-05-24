'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import KPICard from '@/components/dashboard/KPICard';
import AlertBanner, { AlertCard } from '@/components/dashboard/AlertBanner';
import StatusChart from '@/components/dashboard/StatusChart';
import CompletitudBar from '@/components/ui/CompletitudBar';
import Badge from '@/components/ui/Badge';

export default function DashboardPage() {
  const router = useRouter();
  const { company, rats, dashboardStats, setRats, setDashboardStats, actualizarStatsEnCache } = useApp();
  const [refreshing, setRefreshing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [tourStep, setTourStep] = useState(0);
  const [showTour, setShowTour] = useState(false);

  const hasCache = dashboardStats !== null;

  useEffect(() => {
    const tourDone = localStorage.getItem('custodio_tour_completed');
    if (tourDone === 'false' && company) {
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
    ]).then(([s, ratList]) => {
      setDashboardStats(s);
      setRats(ratList);
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
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400 text-sm">Cargando...</p>
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
  } = dashboardStats;
  const completos  = por_estado?.completo  ?? 0;
  const borradores = por_estado?.borrador  ?? 0;

  const recientes = [...rats]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 6);

  const sinRevision = rats.filter(r => {
    const dias = (Date.now() - new Date(r.updated_at).getTime()) / 86_400_000;
    return dias > 180;
  }).length;

  const alertas: { message: string; type: 'warning' | 'danger' | 'info' | 'success' }[] = [];
  if (procesos_con_datos_sensibles > 0)
    alertas.push({ type: 'warning', message: `<strong>${procesos_con_datos_sensibles} proceso(s)</strong> tratan datos sensibles. Verifique base legal expresa y medidas de seguridad reforzadas.` });
  if (requieren_eipd > 0)
    alertas.push({ type: 'danger', message: `<strong>${requieren_eipd} proceso(s)</strong> requieren EIPD. No pueden iniciarse sin completar la evaluación.` });
  if (transferencias_internacionales > 0)
    alertas.push({ type: 'info', message: `<strong>${transferencias_internacionales}</strong> transferencia(s) internacional(es). Verifique las garantías del Art. 28 Ley 21.719.` });
  if (sinRevision > 0)
    alertas.push({ type: 'warning', message: `<strong>${sinRevision} proceso(s)</strong> sin actualización hace más de 6 meses. La Ley 21.719 exige revisión periódica del RAT.` });
  if (completitud_promedio < 60)
    alertas.push({ type: 'warning', message: `Completitud del RAT en <strong>${completitud_promedio}%</strong>. Complete los campos obligatorios para estar preparado ante fiscalización.` });
  if (eipd_pendientes > 0)
    alertas.push({ type: 'danger', message: `<strong>${eipd_pendientes} EIPD(s)</strong> pendientes de completar. No puede iniciarse el tratamiento hasta completar la evaluación (Art. 15 bis).` });
  if (transferencias_sin_garantias > 0)
    alertas.push({ type: 'warning', message: `<strong>${transferencias_sin_garantias} transferencia(s)</strong> internacional(es) sin garantías documentadas. Documente SCC, BCR u otras garantías (Art. 28).` });
  if (interes_legitimo_sin_test > 0)
    alertas.push({ type: 'warning', message: `<strong>${interes_legitimo_sin_test} proceso(s)</strong> con base legal "Interés legítimo" sin test de 3 pasos documentado. La base no sirve como defensa ante la APDC sin esto.` });
  if (encargados_sin_contrato > 0)
    alertas.push({ type: 'info', message: `<strong>${encargados_sin_contrato} encargado(s)</strong> del tratamiento sin contrato de encargo (Art. 14 quáter Ley 21.719).` });

  const kpiColor = completitud_promedio >= 75 ? '#059669' : completitud_promedio >= 50 ? '#D97706' : '#DC2626';

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
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

      {/* KPIs principales */}
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

      {/* KPIs de riesgo adicional */}
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

      {/* Gráfico + Alertas */}
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

      {/* Procesos recientes */}
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
          <div className="space-y-0 overflow-x-auto">
            <div
              className="grid text-xs font-semibold uppercase tracking-wide py-2 px-3 rounded-t-lg overflow-x-auto whitespace-nowrap"
              style={{ gridTemplateColumns: 'minmax(150px,3fr) minmax(100px,2fr) minmax(80px,1.5fr) 120px', color: '#6B7280', background: '#F9FAFB', border: '1px solid #E5E7EB', borderBottom: 'none' }}
            >
              <span>Proceso</span>
              <span>Base legal</span>
              <span>Estado</span>
              <span>Completitud</span>
            </div>
            {recientes.map((rat, i) => (
              <div
                key={rat.id}
                className="grid items-center py-3 px-3 overflow-x-auto whitespace-nowrap"
                style={{
                  gridTemplateColumns: 'minmax(150px,3fr) minmax(100px,2fr) minmax(80px,1.5fr) 120px',
                  background: i % 2 === 0 ? 'white' : '#FAFAFA',
                  border: '1px solid #E5E7EB',
                  borderTop: 'none',
                  borderRadius: i === recientes.length - 1 ? '0 0 8px 8px' : 0,
                }}
              >
                <div>
                  <div className="text-sm font-semibold" style={{ color: '#111827' }}>
                    {rat.nombre_proceso}
                  </div>
                  <div className="text-xs" style={{ color: '#9CA3AF' }}>
                    ID #{rat.id} · {rat.updated_at?.slice(0, 10)}
                  </div>
                </div>
                <div className="text-xs" style={{ color: '#6B7280' }}>
                  {(rat.base_legal ?? '—').slice(0, 30)}
                </div>
                <div><Badge estado={rat.estado} /></div>
                <div><CompletitudBar pct={rat.completitud ?? 0} /></div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tour guiado */}
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