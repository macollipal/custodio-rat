'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import * as api from '@/lib/api';

interface PdfPreviewProps {
  ratId: number;
  filename?: string;
}

export default function PdfPreview({ ratId, filename }: PdfPreviewProps) {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let currentUrl: string | null = null;

    api.descargarArchivoRAT(ratId)
      .then(blob => {
        if (cancelled) return;
        currentUrl = URL.createObjectURL(blob);
        setBlobUrl(currentUrl);
        setError(false);
      })
      .catch(() => {
        if (cancelled) return;
        setError(true);
        setBlobUrl(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      if (currentUrl) URL.revokeObjectURL(currentUrl);
    };
  }, [ratId]);

  return (
    <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #E5E7EB', background: '#F9FAFB' }}>
      <div className="px-3 py-2 flex items-center justify-between" style={{ borderBottom: '1px solid #E5E7EB', background: '#F3F4F6' }}>
        <span className="text-xs font-medium" style={{ color: '#374151' }}>
          📄 {filename || 'Documento base legal'}
        </span>
        {blobUrl && (
          <a
            href={blobUrl}
            download={filename || `RAT_${ratId}_base_legal.pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-semibold px-2 py-1 rounded transition hover:bg-gray-200"
            style={{ color: '#2563EB' }}
          >
            Descargar ↗
          </a>
        )}
      </div>
      {loading && (
        <div className="flex items-center justify-center" style={{ height: 200 }}>
          <div className="text-xs" style={{ color: '#9CA3AF' }}>Cargando documento...</div>
        </div>
      )}
      {error && (
        <div className="flex flex-col items-center justify-center gap-2 p-4" style={{ height: 200 }}>
          <div className="text-xs font-medium" style={{ color: '#DC2626' }}>No se pudo cargar el documento</div>
          <a
            href={`${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8002'}/rats/${ratId}/archivo`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs px-3 py-1.5 rounded-lg font-semibold text-white transition"
            style={{ background: '#2563EB' }}
          >
            Abrir en nueva pestaña
          </a>
        </div>
      )}
      {blobUrl && !loading && !error && (
        <iframe
          src={blobUrl}
          className="w-full"
          style={{ height: 320, border: 'none' }}
          title="Vista previa del documento"
        />
      )}
    </div>
  );
}
