'use client';

import { useState, useEffect } from 'react';
import { API_BASE } from '@/lib/constants';

function StorageTab() {
  const [loading, setLoading] = useState(false);
  const [storageInfo, setStorageInfo] = useState<{
    backend: string;
    bucket: string;
    archive_bucket: string;
    region: string;
    namespace: string;
  } | null>(null);

  async function fetchStorageInfo() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/debug/oci`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('custodio_token')}` },
      });
      const data = await res.json();
      if (data.oci_config_parsed) {
        setStorageInfo({
          backend: data.oci_config_parsed.backend || 'local',
          bucket: data.oci_config_parsed.bucket || '—',
          archive_bucket: data.oci_config_parsed.archive_bucket || 'No configurado',
          region: data.oci_config_parsed.region || '—',
          namespace: data.oci_config_parsed.namespace || '—',
        });
      } else {
        setStorageInfo({ backend: 'local', bucket: '—', archive_bucket: '—', region: '—', namespace: '—' });
      }
    } catch {
      setStorageInfo({ backend: 'local', bucket: '—', archive_bucket: '—', region: '—', namespace: '—' });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchStorageInfo();
  }, []);

  const cardCls = 'bg-white rounded-xl p-6 shadow-sm';
  const labelCls = 'text-sm font-medium';
  const valueCls = 'text-sm font-mono';

  const STORAGE_RULES = [
    {
      category: 'Limites de archivos',
      icon: '📎',
      rules: [
        { label: 'Tamano maximo PDF', value: '5 MB', legal: 'Archivo tecnico' },
        { label: 'Formatos permitidos', value: 'PDF, DOCX, TXT', legal: 'Comodidad' },
      ],
    },
    {
      category: 'Vigencia y expiracion',
      icon: '⏱',
      rules: [
        { label: 'URL de descarga expira', value: '5 minutos', legal: 'Seguridad' },
        { label: 'Retencion en Archive', value: '30 dias', legal: 'Art. 11 Ley 21.719' },
      ],
    },
    {
      category: 'Eliminacion de datos (Art. 11 - Ley 21.719)',
      icon: '🗑',
      rules: [
        { label: 'Al eliminar RAT', value: 'Archivo mueve a Archive bucket', legal: 'Conservacion temporal' },
        { label: 'Retencion en Archive', value: '30 dias', legal: 'Periodo de retencion' },
        { label: 'Eliminacion definitiva', value: 'Despues de 30 dias en Archive', legal: 'Art. 11 Ley 21.719' },
      ],
    },
    {
      category: 'Log de accesos (Art. 12 - Ley 21.719)',
      icon: '📋',
      rules: [
        { label: 'Registro de descargas', value: 'Habilitado', legal: 'Trazabilidad' },
        { label: 'Que se registra', value: 'Usuario, fecha, archivo, RAT', legal: 'Art. 12' },
      ],
    },
    {
      category: 'Limpieza de archivos huerfanos',
      icon: '🧹',
      rules: [
        { label: 'Script de limpieza', value: 'scripts/cleanup_orphaned_files.py', legal: 'Mantenimiento' },
        { label: 'Ejecucion', value: 'Manual (cuando sea necesario)', legal: 'Cuidado' },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="rounded-xl p-4" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
        <div className="flex items-start gap-3">
          <span className="text-xl flex-shrink-0">⚖️</span>
          <div>
            <p className="text-sm font-semibold" style={{ color: '#1E40AF' }}>Cumplimiento Ley 21.719</p>
            <p className="text-xs mt-1" style={{ color: '#3B82F6' }}>
              El almacenamiento de archivos RAT en Custodio cumple con los articulos 11 y 12 de la Ley 21.719 de Proteccion de Datos Personales de Chile.
              Los archivos se eliminan conforme al principio de conservacion minima, y todos los accesos quedan registrados para auditoria.
            </p>
          </div>
        </div>
      </div>

      <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
        <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Estado del almacenamiento</h2>
        {loading ? (
          <p className="text-sm" style={{ color: '#9CA3AF' }}>Cargando...</p>
        ) : storageInfo ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className={labelCls} style={{ color: '#6B7280' }}>Backend</span>
              <span className={labelCls} style={{ color: storageInfo.backend === 'oci' ? '#059669' : '#6B7280' }}>
                {storageInfo.backend === 'oci' ? 'OCI Object Storage' : 'Local (BYTEA)'}
              </span>
            </div>
            {storageInfo.backend === 'oci' && (
              <>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Bucket activo</span>
                  <span className={valueCls} style={{ color: '#374151' }}>{storageInfo.bucket}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Bucket archive</span>
                  <span className={valueCls} style={{ color: '#374151' }}>{storageInfo.archive_bucket}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Region</span>
                  <span className={valueCls} style={{ color: '#374151' }}>{storageInfo.region}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className={labelCls} style={{ color: '#6B7280' }}>Namespace</span>
                  <span className={valueCls} style={{ color: '#374151' }}>{storageInfo.namespace}</span>
                </div>
              </>
            )}
          </div>
        ) : null}
      </div>

      <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
        <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Reglas de almacenamiento</h2>
        <div className="space-y-6">
          {STORAGE_RULES.map(section => (
            <div key={section.category}>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">{section.icon}</span>
                <h3 className="text-sm font-semibold" style={{ color: '#374151' }}>{section.category}</h3>
              </div>
              <div className="space-y-2">
                {section.rules.map(rule => (
                  <div key={rule.label} className="flex items-start justify-between gap-4 py-2" style={{ borderBottom: '1px solid #F3F4F6' }}>
                    <div className="flex-1">
                      <p className="text-sm" style={{ color: '#374151' }}>{rule.label}</p>
                      <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>{rule.legal}</p>
                    </div>
                    <span className="text-sm font-mono font-medium flex-shrink-0" style={{ color: '#059669' }}>{rule.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className={cardCls} style={{ border: '1px solid #E5E7EB' }}>
        <h2 className="text-base font-semibold mb-4" style={{ color: '#111827' }}>Flujo de eliminacion de archivos</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: '#2563EB' }}>1</div>
            <div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Usuario elimina RAT</p>
              <p className="text-xs" style={{ color: '#9CA3AF' }}>El archivo se mueve al bucket de Archive para custodia temporal</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: '#7C3AED' }}>2</div>
            <div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Periodo de retencion (30 dias)</p>
              <p className="text-xs" style={{ color: '#9CA3AF' }}>El archivo permanece en Archive bucket para cumplimiento legal</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: '#DC2626' }}>3</div>
            <div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Eliminacion definitiva</p>
              <p className="text-xs" style={{ color: '#9CA3AF' }}>
                Ejecutar{' '}
                <code className="px-1 py-0.5 rounded text-xs" style={{ background: '#F3F4F6', color: '#374151' }}>
                  python scripts/cleanup_orphaned_files.py --expired
                </code>{' '}
                para eliminar archivos vencidos
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
        <h3 className="text-sm font-semibold mb-3" style={{ color: '#374151' }}>Referencia legal</h3>
        <div className="space-y-2 text-xs" style={{ color: '#6B7280' }}>
          <p><strong>Art. 11 Ley 21.719</strong> — Los datos personales deben ser eliminados cuando cesa la finalidad del tratamiento o cuando el titular ejerce su derecho de eliminacion.</p>
          <p><strong>Art. 12 Ley 21.719</strong> — El responsable debe registrar las operaciones de tratamiento realizadas, incluyendo las eliminaciones.</p>
          <p><strong>Art. 14 quater Ley 21.719</strong> — El contrato de encargado del tratamiento debe establecer las condiciones para la subcontratacion y eliminacion de datos.</p>
        </div>
      </div>
    </div>
  );
}

export default StorageTab;
