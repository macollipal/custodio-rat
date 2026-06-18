'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { X, Loader2, AlertCircle } from 'lucide-react';
import {
  getDiagramaPorTipo,
  getNodosAnteriores,
  aplicarColores,
  getTituloPorTipo,
  getDescripcionPorTipo,
  TipoArco,
  EstadoTicket
} from '@/lib/flujos-arco';

interface FlujoModalProps {
  open: boolean;
  onClose: () => void;
  tipo: TipoArco;
  estadoActual: EstadoTicket;
  trackingToken?: string;
}

export function FlujoModal({ open, onClose, tipo, estadoActual }: FlujoModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mermaidLoaded, setMermaidLoaded] = useState(false);
  const mermaidApiRef = useRef<any>(null);

  useEffect(() => {
    if (!open) return;

    const loadMermaid = async () => {
      if (mermaidLoaded && mermaidApiRef.current) return;

      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          flowchart: {
            htmlLabels: true,
            curve: 'basis',
            nodeSpacing: 50,
            rankSpacing: 80
          }
        } as any);
        mermaidApiRef.current = mermaid;
        setMermaidLoaded(true);
      } catch (err) {
        console.error('Error cargando mermaid:', err);
        setError('Error al cargar el visualizador de diagramas');
      }
    };

    loadMermaid();
  }, [open, mermaidLoaded]);

  const renderDiagrama = useCallback(async () => {
    if (!mermaidApiRef.current || !containerRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const diagrama = getDiagramaPorTipo(tipo);
      const nodosAnteriores = getNodosAnteriores(estadoActual, tipo);
      const { codigo } = aplicarColores(diagrama, estadoActual, nodosAnteriores);

      const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const { svg: svgResult } = await mermaidApiRef.current.render(id, codigo);
      setSvg(svgResult);
    } catch (err: any) {
      console.error('Error renderizando mermaid:', err);
      setError(`Error al renderizar: ${err.message || 'verifique el tipo de solicitud'}`);
    } finally {
      setLoading(false);
    }
  }, [tipo, estadoActual]);

  useEffect(() => {
    if (!open || !mermaidLoaded) return;
    renderDiagrama();
  }, [open, mermaidLoaded, renderDiagrama]);

  if (!open) return null;

  const nodosAnteriores = getNodosAnteriores(estadoActual, tipo);

  return (
    <div className="fixed inset-0 z-[200] bg-black/60 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {getTituloPorTipo(tipo)}
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              {getDescripcionPorTipo(tipo)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Cerrar"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="flex-1 overflow-auto px-6 py-4 bg-gray-50">
          {loading && (
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
              <p className="text-sm text-gray-500">Renderizando flujo...</p>
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center h-64">
              <AlertCircle className="w-8 h-8 text-red-500 mb-3" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {!loading && !error && svg && (
            <div
              ref={containerRef}
              className="flex justify-center"
              dangerouslySetInnerHTML={{ __html: svg }}
            />
          )}
        </div>

        <div className="px-6 py-3 border-t border-gray-200 bg-white shrink-0">
          <div className="flex items-center gap-6 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 bg-blue-500 rounded-full"></span>
              <span className="text-gray-700 font-medium">
                Estado actual: <span className="uppercase">{estadoActual.replace('_', ' ')}</span>
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 bg-gray-800 rounded-full"></span>
              <span className="text-gray-600">Completado ({nodosAnteriores.length})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 bg-gray-300 rounded-full"></span>
              <span className="text-gray-600">Pendiente</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 bg-emerald-500 rounded-full"></span>
              <span className="text-gray-600">Resuelto</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
