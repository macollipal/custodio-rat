'use client';

import type { Company } from '@/types';

interface AlertItem {
  icon: string;
  titulo: string;
  detalle: string;
  color: string;
  bg: string;
  border: string;
}

export function computeCompanyAlerts(companies: Company[]): AlertItem[] {
  const totalRatsVencidos = companies.reduce((s, c) => s + (c.rats_vencidos ?? 0), 0);
  const totalSolicitudesVencidas = companies.reduce(
    (s, c) => s + (c.solicitudes_vencidas_sla ?? 0),
    0,
  );
  const totalSolicitudesPendientes = companies.reduce(
    (s, c) => s + (c.solicitudes_pendientes ?? 0),
    0,
  );
  const empresasBajaCompletitud = companies.filter(
    (c) => (c.total_rats ?? 0) > 0 && (c.completitud_promedio ?? 0) < 50,
  ).length;
  const empresasSinDpo = companies.filter((c) => !c.contacto_dpo || !c.email_dpo).length;
  const empresasSinPolitica = companies.filter((c) => c.has_politica_transparencia === false).length;

  const alerts: AlertItem[] = [];

  if (totalRatsVencidos > 0) {
    alerts.push({
      icon: '⚠️',
      titulo: `${totalRatsVencidos} RAT${totalRatsVencidos !== 1 ? 's' : ''} vencido${totalRatsVencidos !== 1 ? 's' : ''}`,
      detalle: 'Procesos de tratamiento que superaron el plazo de retención declarado.',
      color: '#92400E',
      bg: '#FEF3C7',
      border: '#FCD34D',
    });
  }
  if (totalSolicitudesVencidas > 0) {
    alerts.push({
      icon: '📋',
      titulo: `${totalSolicitudesVencidas} solicitud${totalSolicitudesVencidas !== 1 ? 'es' : ''} ARCO vencida${totalSolicitudesVencidas !== 1 ? 's' : ''}`,
      detalle: `Han superado el plazo legal de respuesta (Art. 14 Ley 21.719). ${totalSolicitudesPendientes} pendiente${totalSolicitudesPendientes !== 1 ? 's' : ''} en total.`,
      color: '#7F1D1D',
      bg: '#FEE2E2',
      border: '#FCA5A5',
    });
  }
  if (empresasBajaCompletitud > 0) {
    alerts.push({
      icon: '📉',
      titulo: `${empresasBajaCompletitud} empresa${empresasBajaCompletitud !== 1 ? 's' : ''} con completitud < 50%`,
      detalle: 'RATs con campos obligatorios faltantes o poco documentados.',
      color: '#1E40AF',
      bg: '#DBEAFE',
      border: '#93C5FD',
    });
  }
  if (empresasSinDpo > 0) {
    alerts.push({
      icon: '👤',
      titulo: `${empresasSinDpo} empresa${empresasSinDpo !== 1 ? 's' : ''} sin DPO definido`,
      detalle: 'Falta contacto o email del Delegado de Protección de Datos (Art. 21).',
      color: '#5B21B6',
      bg: '#EDE9FE',
      border: '#C4B5FD',
    });
  }
  if (empresasSinPolitica > 0) {
    alerts.push({
      icon: '📄',
      titulo: `${empresasSinPolitica} empresa${empresasSinPolitica !== 1 ? 's' : ''} sin política de transparencia`,
      detalle: 'Art. 14 ter — Publicar la política de transparencia en el sitio web.',
      color: '#854D0E',
      bg: '#FEF9C8',
      border: '#FDE68A',
    });
  }

  return alerts;
}

export default function CompanyAlertsBanner({ companies }: { companies: Company[] }) {
  const alerts = computeCompanyAlerts(companies);
  if (alerts.length === 0) return null;

  return (
    <div
      className="rounded-xl p-4 mb-6"
      style={{ background: '#FFFBEB', border: '1px solid #FCD34D' }}
      role="region"
      aria-label="Alertas de cumplimiento"
    >
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">🚨</span>
        <h2 className="text-sm font-bold" style={{ color: '#92400E' }}>
          {alerts.length} alerta{alerts.length !== 1 ? 's' : ''} de cumplimiento
        </h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {alerts.map((a, i) => (
          <div
            key={i}
            className="rounded-lg p-3"
            style={{ background: a.bg, border: `1px solid ${a.border}` }}
          >
            <div className="flex items-center gap-2 mb-1">
              <span aria-hidden="true">{a.icon}</span>
              <span className="text-xs font-bold" style={{ color: a.color }}>
                {a.titulo}
              </span>
            </div>
            <p className="text-xs" style={{ color: a.color }}>
              {a.detalle}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}