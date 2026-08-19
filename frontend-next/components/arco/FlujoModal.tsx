'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { X, Loader2, AlertCircle, CheckCircle2, XCircle, Clock, Ban, HelpCircle } from 'lucide-react';
import Button from '@/components/ui/Button';
import {
  getDiagramaPorTipo,
  getNodosAnteriores,
  aplicarColores,
  getTituloPorTipo,
  getDescripcionPorTipo,
  getIdNodoPorEstado,
  TipoArco,
  EstadoTicket
} from '@/lib/flujos-arco';
import { getSubPaso, SubPaso } from '@/lib/flujos-arco-detalle';

interface FlujoModalProps {
  open: boolean;
  onClose: () => void;
  tipo: TipoArco;
  estadoActual: EstadoTicket;
  trackingToken?: string;
}

const ESTADO_ICON: Record<EstadoTicket, React.ReactNode> = {
  abierto: <HelpCircle className="w-4 h-4 text-blue-500" />,
  en_proceso: <Clock className="w-4 h-4 text-yellow-600" />,
  pendiente: <Clock className="w-4 h-4 text-orange-500" />,
  subsanacion: <HelpCircle className="w-4 h-4 text-purple-500" />,
  prorroga: <Clock className="w-4 h-4 text-orange-500" />,
  bloqueado: <Ban className="w-4 h-4 text-red-500" />,
  resuelto: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
  rechazado: <XCircle className="w-4 h-4 text-gray-500" />
};

function SubPasoPanel({ subPaso, tipo, estadoActual }: { subPaso: SubPaso; tipo: TipoArco; estadoActual: EstadoTicket }) {
  const nodoActual = getIdNodoPorEstado(tipo, estadoActual);

  return (
    <div className="px-4 py-3 bg-yellow-50 border-b border-yellow-200">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 shrink-0">
          <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-yellow-400 text-yellow-900 text-sm font-bold">
            {nodoActual}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-yellow-800 mb-0.5">{subPaso.titulo}</p>
          <p className="text-xs text-yellow-700 leading-relaxed">{subPaso.accion}</p>

          {subPaso.opciones && subPaso.opciones.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {subPaso.opciones.map((op, i) => {
                const isPositive = op.startsWith('✓');
                const isNegative = op.startsWith('✗');
                return (
                  <span
                    key={i}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${
                      isPositive
                        ? 'bg-emerald-100 text-emerald-700'
                        : isNegative
                        ? 'bg-red-100 text-red-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {op}
                  </span>
                );
              })}
            </div>
          )}

          {subPaso.proximos && subPaso.proximos.length > 0 && (
            <div className="mt-1.5 flex items-center gap-1 flex-wrap">
              <span className="text-xs text-yellow-600">Próximos:</span>
              {subPaso.proximos.map((p) => (
                <span key={p} className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-white border border-yellow-300 rounded text-xs text-yellow-700">
                  {p.replace('_', ' ')}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function FlujoModal({ open, onClose, tipo, estadoActual }: FlujoModalProps) {
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const mermaidRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mermaidReady, setMermaidReady] = useState(false);

  const subPaso = open ? getSubPaso(tipo, estadoActual) : null;

  useEffect(() => {
    if (!open) return;

    const init = async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: 'base',
          themeVariables: {
            primaryColor: '#EFF6FF',
            primaryTextColor: '#1E3A5F',
            primaryBorderColor: '#93C5FD',
            lineColor: '#94A3B8',
            secondaryColor: '#F8FAFC',
            tertiaryColor: '#F1F5F9',
            fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
            fontSize: '13px',
            edgeLabelBackground: '#FFFFFF',
          },
          flowchart: {
            htmlLabels: true,
            curve: 'basis',
            nodeSpacing: 40,
            rankSpacing: 50,
            padding: 20,
          },
          securityLevel: 'loose',
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
      const { codigo } = aplicarColores(diagrama, tipo, estadoActual, nodosAnteriores);

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
    renderDiagrama();
  }, [open, mermaidReady, tipo, estadoActual, renderDiagrama]);

  if (!open) return null;

  const nodosAnteriores = getNodosAnteriores(estadoActual, tipo);

  return (
    <div className="fixed inset-0 z-[200] bg-black/60 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
          <div className="flex items-center gap-3">
            <div className="shrink-0">
              {ESTADO_ICON[estadoActual]}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {getTituloPorTipo(tipo)}
              </h2>
              <p className="text-xs text-gray-500 mt-0.5">
                {getDescripcionPorTipo(tipo)}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Cerrar"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {subPaso && <SubPasoPanel subPaso={subPaso} tipo={tipo} estadoActual={estadoActual} />}

        <div className="flex-1 overflow-auto px-6 py-4 bg-gray-50 relative">
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-50/95 z-10">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
              <p className="text-sm text-gray-500">Renderizando flujo...</p>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-50/95 z-10">
              <AlertCircle className="w-8 h-8 text-red-500 mb-3" />
              <p className="text-sm text-red-600 text-center px-4">{error}</p>
              <Button variant="primary" size="sm" onClick={renderDiagrama} className="mt-3">
                Reintentar
              </Button>
            </div>
          )}

          <div
            ref={svgContainerRef}
            className="flex justify-center min-h-[200px]"
          />
        </div>

        <div className="px-6 py-3 border-t border-gray-100 bg-white shrink-0">
          <div className="flex items-center gap-5 flex-wrap text-xs">
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded" style={{ background: '#4F46E5' }}></span>
              <span className="font-semibold text-indigo-700">★ Actual: {estadoActual.replace(/_/g, ' ')}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded" style={{ background: '#1E293B' }}></span>
              <span className="text-gray-500">Completado ({nodosAnteriores.length})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded border border-dashed" style={{ background: '#F8FAFC', borderColor: '#E2E8F0' }}></span>
              <span className="text-gray-500">Pendiente</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded" style={{ background: '#10B981' }}></span>
              <span className="text-gray-500">Resuelto</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded" style={{ background: '#FB7185' }}></span>
              <span className="text-gray-500">Rechazado</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded" style={{ background: '#FEF9C3', border: '1.5px solid #F59E0B' }}></span>
              <span className="text-gray-500">Decisión</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
