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
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const mermaidRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mermaidReady, setMermaidReady] = useState(false);
  const renderKeyRef = useRef(0);

  useEffect(() => {
    if (!open) return;

    const init = async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: 'base',
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#fff',
            primaryBorderColor: '#1d4ed8',
            lineColor: '#6b7280',
            secondaryColor: '#f3f4f6',
            tertiaryColor: '#f9fafb',
            fontFamily: 'inherit'
          },
          flowchart: {
            htmlLabels: true,
            curve: 'basis',
            nodeSpacing: 50,
            rankSpacing: 80
          },
          securityLevel: 'loose'
        } as any);
        mermaidRef.current = mermaid;
        setMermaidReady(true);
      } catch (err) {
        console.error('[FlujoModal] Error cargando mermaid:', err);
        setError('Error al cargar el visualizador de diagramas');
      }
    };

    init();
  }, [open]);

  const renderDiagrama = useCallback(async () => {
    if (!mermaidRef.current || !svgContainerRef.current) return;

    setLoading(true);
    setError(null);

    try {
      const diagrama = getDiagramaPorTipo(tipo);
      const nodosAnteriores = getNodosAnteriores(estadoActual, tipo);
      const { codigo } = aplicarColores(diagrama, estadoActual, nodosAnteriores);

      const id = `mermaid-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const { svg } = await mermaidRef.current.render(id, codigo);

      if (svgContainerRef.current) {
        svgContainerRef.current.innerHTML = svg;
      }
    } catch (err: any) {
      console.error('[FlujoModal] Error renderizando:', err);
      setError(`Error al renderizar: ${err?.message || 'intente cerrar y abrir de nuevo'}`);
    } finally {
      setLoading(false);
    }
  }, [tipo, estadoActual]);

  useEffect(() => {
    if (!open || !mermaidReady) return;
    renderKeyRef.current += 1;
    renderDiagrama();
  }, [open, mermaidReady, tipo, estadoActual, renderDiagrama]);

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
              <p className="text-sm text-red-600 text-center px-4">{error}</p>
              <button
                onClick={renderDiagrama}
                className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
              >
                Reintentar
              </button>
            </div>
          )}

          {!loading && !error && (
            <div
              ref={svgContainerRef}
              className="flex justify-center"
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
