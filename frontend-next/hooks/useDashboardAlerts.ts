'use client';

import { useMemo } from 'react';
import type { DashboardStats } from '@/types';

export interface AlertItem {
  message: string;
  type: 'warning' | 'danger' | 'info' | 'success';
}

export function useDashboardAlerts(
  dashboardStats: DashboardStats | null,
  sinRevisionCount: number
): AlertItem[] {
  return useMemo(() => {
    if (!dashboardStats) return [];

    const {
      procesos_con_datos_sensibles,
      requieren_eipd,
      transferencias_internacionales,
      completitud_promedio,
      eipd_pendientes = 0,
      transferencias_sin_garantias = 0,
      interes_legitimo_sin_test = 0,
      encargados_sin_contrato = 0,
      rats_sin_doc_base_legal = 0,
    } = dashboardStats;

    const a: AlertItem[] = [];

    if (procesos_con_datos_sensibles > 0)
      a.push({ type: 'warning', message: `<strong>${procesos_con_datos_sensibles} proceso(s)</strong> tratan datos sensibles. Verifique base legal expresa y medidas de seguridad reforzadas.` });

    if (requieren_eipd > 0)
      a.push({ type: 'danger', message: `<strong>${requieren_eipd} proceso(s)</strong> requieren EIPD. No pueden iniciarse sin completar la evaluación.` });

    if (transferencias_internacionales > 0)
      a.push({ type: 'info', message: `<strong>${transferencias_internacionales}</strong> transferencia(s) internacional(es). Verifique las garantías del Art. 28 Ley 21.719.` });

    if (sinRevisionCount > 0)
      a.push({ type: 'warning', message: `<strong>${sinRevisionCount} proceso(s)</strong> sin actualización hace más de 6 meses. La Ley 21.719 exige revisión periódica del RAT.` });

    if (completitud_promedio < 60)
      a.push({ type: 'warning', message: `Completitud del RAT en <strong>${completitud_promedio}%</strong>. Complete los campos obligatorios para estar preparado ante fiscalización.` });

    if (eipd_pendientes > 0)
      a.push({ type: 'danger', message: `<strong>${eipd_pendientes} EIPD(s)</strong> pendientes de completar. No puede iniciarse el tratamiento hasta completar la evaluación (Art. 15 bis).` });

    if (transferencias_sin_garantias > 0)
      a.push({ type: 'warning', message: `<strong>${transferencias_sin_garantias} transferencia(s)</strong> internacional(es) sin garantías documentadas. Documente SCC, BCR u otras garantías (Art. 28).` });

    if (interes_legitimo_sin_test > 0)
      a.push({ type: 'warning', message: `<strong>${interes_legitimo_sin_test} proceso(s)</strong> con base legal "Interés legítimo" sin test de 3 pasos documentado. La base no sirve como defensa ante la APDC sin esto.` });

    if (encargados_sin_contrato > 0)
      a.push({ type: 'info', message: `<strong>${encargados_sin_contrato} encargado(s)</strong> del tratamiento sin contrato de encargo (Art. 14 quáter Ley 21.719).` });

    if (rats_sin_doc_base_legal > 0)
      a.push({ type: 'warning', message: `<strong>${rats_sin_doc_base_legal} proceso(s)</strong> sin documento de base legal adjunto. Para alcanzar el 100% de completitud, adjunte el documento que respalda la base legal.` });

    return a;
  }, [dashboardStats, sinRevisionCount]);
}
