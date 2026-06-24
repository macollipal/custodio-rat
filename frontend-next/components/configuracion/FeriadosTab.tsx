'use client';

import { useState, useEffect } from 'react';
import { API_BASE } from '@/lib/constants';
import { getToken } from '@/lib/api';

interface FeriadoItem {
  id: number;
  mes: number;
  dia: number;
  nombre: string;
  tipo: string;
}

interface FeriadosTabProps {
  currentTab: string;
}

export function FeriadosTab({ currentTab }: FeriadosTabProps) {
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [years, setYears] = useState<number[]>([]);
  const [feriados, setFeriados] = useState<FeriadoItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  async function loadYears() {
    try {
      const res = await fetch(`${API_BASE}/admin/feriados/years`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      const data = await res.json();
      const currentYear = new Date().getFullYear();
      const allYears = [...new Set([currentYear, ...(data.anios || [])])].sort((a, b) => b - a);
      setYears(allYears);
    } catch {
      // ignore
    }
  }

  async function loadFeriados() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/admin/feriados/?anio=${selectedYear}`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      const data = await res.json();
      setFeriados(data.feriados || []);
    } catch {
      setFeriados([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadYears();
  }, []);

  useEffect(() => {
    if (currentTab === 'feriados') {
      loadFeriados();
    }
  }, [selectedYear, currentTab]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const uploadUrl = `${API_BASE}/admin/feriados/upload?anio=${selectedYear}`;
      const res = await fetch(uploadUrl, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setMessage({ type: 'error', text: data.detail || 'Error al subir feriados' });
      } else {
        setMessage({ type: 'success', text: `${data.total_cargados} feriados cargados para ${selectedYear}` });
        loadYears();
        loadFeriados();
      }
    } catch {
      setMessage({ type: 'error', text: 'Error de conexión' });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  }

  async function handleDelete() {
    if (!confirm(`¿Eliminar todos los feriados del año ${selectedYear}?`)) return;
    try {
      const res = await fetch(`${API_BASE}/admin/feriados/${selectedYear}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      const data = await res.json();
      setMessage({ type: 'success', text: data.mensaje });
      loadYears();
      loadFeriados();
    } catch {
      setMessage({ type: 'error', text: 'Error al eliminar' });
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium" style={{ color: '#374151' }}>Año:</label>
          <select
            value={selectedYear}
            onChange={e => setSelectedYear(Number(e.target.value))}
            className="px-3 py-2 rounded-lg text-sm border"
            style={{ borderColor: '#D1D5DB', backgroundColor: '#FFFFFF', minWidth: 120 }}
          >
            {years.map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-2 flex-wrap">
          <label className="px-4 py-2 rounded-lg text-sm font-semibold text-white cursor-pointer transition hover:opacity-90 disabled:opacity-60"
            style={{ background: '#059669' }}>
            {uploading ? 'Subiendo...' : '📁 Subir CSV'}
            <input type="file" accept=".csv" className="hidden" onChange={handleUpload} disabled={uploading} />
          </label>
          <a
            href={`${API_BASE}/admin/feriados/example`}
            download="feriados_ejemplo.csv"
            className="px-4 py-2 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            📥 Descargar CSV ejemplo
          </a>
          {feriados.length > 0 && (
            <button
              onClick={handleDelete}
              className="px-4 py-2 rounded-lg text-sm font-medium border transition hover:bg-red-50"
              style={{ borderColor: '#FCA5A5', color: '#DC2626' }}
            >
              🗑 Eliminar año
            </button>
          )}
        </div>
      </div>

      {message && (
        <div
          className="px-4 py-3 rounded-lg text-sm"
          style={{ background: message.type === 'success' ? '#DCFCE7' : '#FEE2E2', color: message.type === 'success' ? '#059669' : '#DC2626' }}
        >
          {message.text}
        </div>
      )}

      <div className="text-xs p-3 rounded-lg" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', color: '#6B7280' }}>
        Formato CSV: <code className="px-1 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#374151' }}>año,mes,día,nombre,tipo</code>. Ejemplo: <code className="px-1 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#374151' }}>2025,1,1,Año Nuevo,fijo</code>. Tipo: <code className="px-1 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#374151' }}>fijo</code> o <code className="px-1 py-0.5 rounded" style={{ background: '#E5E7EB', color: '#374151' }}>variable</code>.
      </div>

      {loading ? (
        <p className="text-sm py-8 text-center" style={{ color: '#9CA3AF' }}>Cargando...</p>
      ) : feriados.length === 0 ? (
        <div className="text-center py-12 rounded-xl" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
          <p className="text-sm" style={{ color: '#9CA3AF' }}>No hay feriados cargados para {selectedYear}.</p>
          <p className="text-xs mt-1" style={{ color: '#D1D5DB' }}>Subí un CSV para cargar los feriados.</p>
        </div>
      ) : (
        <div className="rounded-xl overflow-hidden" style={{ border: '1px solid #E5E7EB' }}>
          <table className="w-full text-sm">
            <thead>
              <tr style={{ background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                <th className="text-left px-4 py-2 text-xs font-semibold" style={{ color: '#6B7280' }}>Fecha</th>
                <th className="text-left px-4 py-2 text-xs font-semibold" style={{ color: '#6B7280' }}>Nombre</th>
                <th className="text-left px-4 py-2 text-xs font-semibold" style={{ color: '#6B7280' }}>Tipo</th>
              </tr>
            </thead>
            <tbody>
              {feriados.map(f => (
                <tr key={f.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                  <td className="px-4 py-2" style={{ color: '#374151' }}>
                    {f.dia.toString().padStart(2, '0')}/{f.mes.toString().padStart(2, '0')}/{selectedYear}
                  </td>
                  <td className="px-4 py-2 font-medium" style={{ color: '#111827' }}>{f.nombre}</td>
                  <td className="px-4 py-2">
                    <span
                      className="px-2 py-0.5 rounded text-xs font-medium"
                      style={{ background: f.tipo === 'fijo' ? '#DBEAFE' : '#FEF3C7', color: f.tipo === 'fijo' ? '#2563EB' : '#D97706' }}
                    >
                      {f.tipo}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
