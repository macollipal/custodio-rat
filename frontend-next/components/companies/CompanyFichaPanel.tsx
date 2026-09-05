'use client';

import { useState, useEffect } from 'react';
import * as api from '@/lib/api';
import type { Company, RAT, SecurityBreach } from '@/types';
import type { TktTicket } from '@/lib/api';
import { CompanyEditForm } from './CompanyEditForm';

type Tab = 'datos' | 'rats' | 'arco' | 'brechas';

const TABS: { id: Tab; label: string }[] = [
  { id: 'datos', label: 'Datos' },
  { id: 'rats', label: 'RATs' },
  { id: 'arco', label: 'ARCO' },
  { id: 'brechas', label: 'Brechas' },
];

const ESTADO_COLORS: Record<string, { color: string; bg: string }> = {
  abierto:    { color: '#2563EB', bg: '#DBEAFE' },
  en_proceso: { color: '#7C3AED', bg: '#EDE9FE' },
  pendiente:  { color: '#D97706', bg: '#FEF3C7' },
  resuelto:   { color: '#059669', bg: '#DCFCE7' },
  rechazado:  { color: '#991B1B', bg: '#FEE2E2' },
  bloqueado:  { color: '#DC2626', bg: '#FEE2E2' },
  subsanacion:{ color: '#D97706', bg: '#FEF3C7' },
  prorroga:   { color: '#7C3AED', bg: '#EDE9FE' },
  borrador:   { color: '#6B7280', bg: '#F3F4F6' },
  completo:   { color: '#059669', bg: '#DCFCE7' },
  en_revision:{ color: '#D97706', bg: '#FEF3C7' },
  aprobado:   { color: '#059669', bg: '#DCFCE7' },
};

interface Props {
  empresa: Company;
  onUpdated: (updated: Company) => void;
}

export function CompanyFichaPanel({ empresa, onUpdated }: Props) {
  const [tab, setTab] = useState<Tab>('datos');
  const [rats, setRats] = useState<RAT[]>([]);
  const [tickets, setTickets] = useState<TktTicket[]>([]);
  const [brechas, setBrechas] = useState<SecurityBreach[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (tab === 'rats') {
      setLoading(true);
      api.listarRats(empresa.id)
        .then(r => setRats(Array.isArray(r) ? r : []))
        .catch(() => setRats([]))
        .finally(() => setLoading(false));
    }
    if (tab === 'arco') {
      setLoading(true);
      api.listarTktTickets(empresa.id)
        .then(r => setTickets(Array.isArray(r.tickets) ? r.tickets : []))
        .catch(() => setTickets([]))
        .finally(() => setLoading(false));
    }
    if (tab === 'brechas') {
      setLoading(true);
      api.listarBrechas(empresa.id)
        .then(r => setBrechas(Array.isArray(r) ? r : []))
        .catch(() => setBrechas([]))
        .finally(() => setLoading(false));
    }
  }, [tab, empresa.id]);

  const tabCls = (id: Tab) =>
    `px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
      tab === id
        ? 'border-blue-600 text-blue-700'
        : 'border-transparent text-gray-500 hover:text-gray-700'
    }`;

  return (
    <div className="mt-2 rounded-xl border" style={{ borderColor: '#E5E7EB', background: '#FAFAFA' }}>
      {/* Tab bar */}
      <div className="flex border-b" style={{ borderColor: '#E5E7EB', background: '#FFFFFF', borderRadius: '12px 12px 0 0' }}>
        {TABS.map(t => (
          <button key={t.id} className={tabCls(t.id)} onClick={() => setTab(t.id)}>
            {t.label}
            {t.id === 'rats' && empresa.total_rats ? (
              <span className="ml-1.5 text-xs rounded-full px-1.5" style={{ background: '#E5E7EB', color: '#374151' }}>
                {empresa.total_rats}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        {tab === 'datos' && (
          <>
            {empresa.requiere_dpo && (
              <div className="mb-4 flex items-start gap-3 rounded-lg px-4 py-3" style={{ background: '#FEF3C7', border: '1px solid #FDE68A' }}>
                <span className="text-lg flex-shrink-0">⚠️</span>
                <div>
                  <p className="text-sm font-semibold" style={{ color: '#92400E' }}>DPO obligatorio — Art. 14 Ley 21.719</p>
                  <p className="text-xs mt-0.5" style={{ color: '#78350F' }}>Esta empresa trata datos sensibles o de alto riesgo que exigen la designación de un Delegado de Protección de Datos (DPO). Asigne un nombre y email de DPO en el formulario.</p>
                </div>
              </div>
            )}
            <CompanyEditForm
              empresa={empresa}
              onDone={onUpdated}
              onCancel={() => {}}
            />
          </>
        )}

        {tab === 'rats' && (
          loading ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : rats.length === 0 ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Sin RATs registrados.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {rats.map(r => {
                const ec = ESTADO_COLORS[r.estado] ?? { color: '#6B7280', bg: '#F3F4F6' };
                return (
                  <div key={r.id} className="flex items-center justify-between py-2.5 gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>{r.nombre_proceso}</p>
                      <p className="text-xs truncate" style={{ color: '#9CA3AF' }}>{r.categoria_datos || '—'}</p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {r.completitud != null && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
                          style={{
                            background: r.completitud >= 75 ? '#DCFCE7' : r.completitud >= 50 ? '#FEF9C8' : '#FEE2E2',
                            color: r.completitud >= 75 ? '#166534' : r.completitud >= 50 ? '#854D0E' : '#DC2626',
                          }}>
                          {r.completitud}%
                        </span>
                      )}
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ background: ec.bg, color: ec.color }}>
                        {r.estado}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )
        )}

        {tab === 'arco' && (
          loading ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : tickets.length === 0 ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Sin solicitudes ARCO.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {tickets.map(t => {
                const ec = ESTADO_COLORS[t.estado] ?? { color: '#6B7280', bg: '#F3F4F6' };
                return (
                  <div key={t.id} className="flex items-center justify-between py-2.5 gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>
                        #{t.id} — {t.tipo} — {t.titular_nombre || '—'}
                      </p>
                      <p className="text-xs" style={{ color: '#9CA3AF' }}>
                        {t.fecha_recepcion ? new Date(t.fecha_recepcion).toLocaleDateString('es-CL') : ''}
                      </p>
                    </div>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0" style={{ background: ec.bg, color: ec.color }}>
                      {t.estado}
                    </span>
                  </div>
                );
              })}
            </div>
          )
        )}

        {tab === 'brechas' && (
          loading ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Cargando...</p>
          ) : brechas.length === 0 ? (
            <p className="text-sm py-4 text-center" style={{ color: '#9CA3AF' }}>Sin brechas registradas.</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {brechas.map(b => (
                <div key={b.id} className="flex items-center justify-between py-2.5 gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>
                      {b.descripcion?.slice(0, 60) || `Brecha #${b.id}`}
                    </p>
                    <p className="text-xs" style={{ color: '#9CA3AF' }}>
                      Detectada: {b.fecha_deteccion ? new Date(b.fecha_deteccion).toLocaleDateString('es-CL') : '—'}
                    </p>
                  </div>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0"
                    style={{ background: b.notificado_apdc ? '#DCFCE7' : '#FEF9C8', color: b.notificado_apdc ? '#166534' : '#854D0E' }}>
                    {b.notificado_apdc ? 'Notificada' : 'Pendiente'}
                  </span>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  );
}
