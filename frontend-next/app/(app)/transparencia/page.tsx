'use client';

import { useEffect, useState } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import { getPoliticaTransparencia, type PoliticaTransparencia } from '@/lib/api';

const ITEM_LABELS: Record<string, string> = {
  item_a_politica: 'a) Política de Tratamiento',
  item_b_responsable: 'b) Responsable del Tratamiento',
  item_c_domicilio: 'c) Domicilio y Canal',
  item_d_categorias: 'd) Categorías de Datos y Titulares',
  item_e_medidas: 'e) Medidas de Seguridad',
  item_f_derechos_arco: 'f) Derechos ARCO',
  item_g_recurir_apdc: 'g) Cómo Recurrir a la APDC',
  item_h_transferencias: 'h) Transferencias Internacionales',
  item_i_conservacion: 'i) Conservación de Datos',
  item_j_fuente: 'j) Fuente de Datos',
  item_k_retirar_consentimiento: 'k) Retirar Consentimiento',
  item_l_decisiones_automatizadas: 'l) Decisiones Automatizadas',
};

export default function TransparenciaPage() {
  const { company } = useApp();
  const [politica, setPolitica] = useState<PoliticaTransparencia | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!company?.id) return;
    setLoading(true);
    getPoliticaTransparencia(company.id)
      .then(setPolitica)
      .catch(() => toast.error('No se pudo cargar la política de transparencia.'))
      .finally(() => setLoading(false));
  }, [company?.id]);

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-64 rounded animate-pulse" style={{ background: '#E5E7EB' }} />
        <div className="h-4 w-96 rounded animate-pulse" style={{ background: '#E5E7EB' }} />
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-24 rounded-xl animate-pulse" style={{ background: '#E5E7EB' }} />
        ))}
      </div>
    );
  }

  if (!politica) {
    return (
      <div className="p-6 text-center">
        <p style={{ color: '#6B7280' }}>No hay política de transparencia disponible para esta empresa.</p>
      </div>
    );
  }

  const itemKeys = Object.keys(ITEM_LABELS).filter(k => k.startsWith('item_'));

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Política de Transparencia</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
            {politica.nombre_empresa} · Versión {politica.version}
</p>
        </div>
        <div className="text-right">
          <p className="text-xs" style={{ color: '#9CA3AF' }}>Hash SHA-256</p>
          <p className="text-xs font-mono" style={{ color: '#6B7280' }}>{politica.hash_sha256}</p>
        </div>
      </div>

      <div
        className="rounded-xl p-4 flex items-center gap-3"
        style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}
      >
        <div>
          <p className="font-semibold text-white text-sm">Ley 21.719 — Art. 14 ter</p>
          <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.7)' }}>
            Política pública de tratamiento de datos personales · Generada automáticamente
</p>
        </div>
      </div>

      <div className="grid gap-4">
        {itemKeys.map(key => {
          const label = ITEM_LABELS[key];
          const value = (politica as unknown as Record<string, string>)[key];
          return (
            <div
              key={key}
              className="rounded-xl p-5"
              style={{ background: 'white', border: '1px solid #E5E7EB' }}
            >
              <h3 className="text-sm font-bold mb-2" style={{ color: '#1E40AF' }}>{label}</h3>
              <p className="text-sm whitespace-pre-line" style={{ color: '#374151' }}>
                {value || '—'}
              </p>
            </div>
          );
        })}
      </div>

      <div className="text-center text-xs" style={{ color: '#9CA3AF' }}>
        <p>Esta política fue generada automáticamente el {new Date(politica.fecha_generacion).toLocaleDateString('es-CL')}</p>
        <p className="mt-1">Artículo 14 ter — Ley 21.719 de Chile</p>
      </div>
    </div>
  );
}
