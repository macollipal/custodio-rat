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
  EstadoTicket,
} from '@/lib/flujos-arco';
import { getSubPaso, SubPaso } from '@/lib/flujos-arco-detalle';

interface FlujoModalProps {
  open: boolean;
  onClose: () => void;
  tipo: TipoArco;
  estadoActual: EstadoTicket;
  trackingToken?: string;
  fechaRecepcion?: string | null;
  fechaVencimiento?: string | null;
  diasRestantes?: number | null;
  prioridad?: string | null;
  priorrogaDias?: number | null;
}

const ESTADO_ICON: Record<EstadoTicket, React.ReactNode> = {
  abierto:    <HelpCircle   className="w-4 h-4 text-blue-500" />,
  en_proceso: <Clock        className="w-4 h-4 text-indigo-500" />,
  pendiente:  <Clock        className="w-4 h-4 text-amber-500" />,
  subsanacion:<HelpCircle   className="w-4 h-4 text-purple-500" />,
  prorroga:   <Clock        className="w-4 h-4 text-amber-500" />,
  bloqueado:  <Ban          className="w-4 h-4 text-red-500" />,
  resuelto:   <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
  rechazado:  <XCircle      className="w-4 h-4 text-rose-500" />,
};

const LEGEND = [
  { color: '#4F46E5', label: 'Actual' },
  { color: '#0F172A', label: 'Completado' },
  { color: '#F8FAFC', border: '#E2E8F0', label: 'Pendiente' },
  { color: '#059669', label: 'Resuelto' },
  { color: '#E11D48', label: 'Rechazado' },
  { color: '#D97706', label: 'Decisión' },
] as const;

// Inyecta estilos CSS en el SVG generado por mermaid para normalizar tipografía
function postProcessSvg(svg: string): string {
  const customCss = `
    .nodeLabel, .label {
      font-family: Inter, system-ui, -apple-system, sans-serif !important;
      font-size: 12px !important;
    }
    .edgeLabel .label {
      font-size: 11px !important;
      font-weight: 500 !important;
      color: #475569 !important;
    }
    .edgeLabel rect {
      fill: #fff !important;
      opacity: 0.92 !important;
    }
    .node .label {
      line-height: 1.4 !important;
    }
  `;
  const inject = `<style>${customCss}</style>`;
  if (svg.includes('</defs>')) return svg.replace('</defs>', `${inject}</defs>`);
  return svg.replace('<svg', `${inject}<svg`);
}

function SubPasoPanel({
  subPaso, tipo, estadoActual,
}: { subPaso: SubPaso; tipo: TipoArco; estadoActual: EstadoTicket }) {
  const nodoActual = getIdNodoPorEstado(tipo, estadoActual);
  return (
    <div className="px-5 py-3 border-b shrink-0"
      style={{ background: '#EEF2FF', borderColor: '#C7D2FE' }}>
      <div className="flex items-start gap-3">
        <span className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold text-white flex-shrink-0"
          style={{ background: '#4F46E5' }}>
          {nodoActual}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold mb-0.5" style={{ color: '#312E81' }}>
            {subPaso.titulo}
          </p>
          <p className="text-xs leading-relaxed" style={{ color: '#4338CA' }}>
            {subPaso.accion}
          </p>

          {subPaso.opciones && subPaso.opciones.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {subPaso.opciones.map((op, i) => {
                const isOk  = op.startsWith('✓');
                const isNok = op.startsWith('✗');
                return (
                  <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
                    style={
                      isOk  ? { background: '#ECFDF5', color: '#065F46' }
                    : isNok ? { background: '#FFF1F2', color: '#881337' }
                    :         { background: '#E0E7FF', color: '#3730A3' }
                    }>
                    {op}
                  </span>
                );
              })}
            </div>
          )}

          {subPaso.proximos && subPaso.proximos.length > 0 && (
            <div className="mt-1.5 flex items-center gap-1 flex-wrap">
              <span className="text-xs" style={{ color: '#6366F1' }}>Próximos:</span>
              {subPaso.proximos.map(p => (
                <span key={p} className="inline-flex px-1.5 py-0.5 rounded text-xs"
                  style={{ background: '#fff', border: '1px solid #C7D2FE', color: '#4338CA' }}>
                  {p.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function FlujoModal({
  open, onClose, tipo, estadoActual,
  fechaRecepcion, fechaVencimiento, diasRestantes, prioridad, priorrogaDias,
}: FlujoModalProps) {
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const mermaidRef      = useRef<any>(null);
  const [loading, setLoading]           = useState(false);
  const [error,   setError]             = useState<string | null>(null);
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
            primaryColor:       '#EFF6FF',
            primaryTextColor:   '#1E3A5F',
            primaryBorderColor: '#BFDBFE',
            lineColor:          '#CBD5E1',
            secondaryColor:     '#F8FAFC',
            tertiaryColor:      '#F1F5F9',
            fontFamily:         'Inter, system-ui, -apple-system, sans-serif',
            fontSize:           '13px',
            edgeLabelBackground:'#FFFFFF',
          },
          flowchart: {
            htmlLabels:  true,
            curve:       'linear',   // líneas rectas → más ordenado
            nodeSpacing: 50,
            rankSpacing: 60,
            padding:     24,
            useMaxWidth: true,
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
      const diagrama       = getDiagramaPorTipo(tipo);
      const nodosAnteriores = getNodosAnteriores(estadoActual, tipo);
      const { codigo }     = aplicarColores(diagrama, tipo, estadoActual, nodosAnteriores);
      const id             = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
      const { svg }        = await mermaidRef.current.render(id, codigo);
      if (svgContainerRef.current) {
        svgContainerRef.current.innerHTML = postProcessSvg(svg);
      }
    } catch (err: any) {
      console.error('[FlujoModal] Error renderizando:', err);
      setError(`Error al renderizar: ${err?.message ?? 'intente cerrar y abrir de nuevo'}`);
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
    <div className="fixed inset-0 z-[200] bg-black/50 flex items-center justify-center p-4"
      onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: '#EEF2FF' }}>
              {ESTADO_ICON[estadoActual]}
            </div>
            <div>
              <h2 className="text-sm font-bold" style={{ color: '#111827' }}>
                {getTituloPorTipo(tipo)}
              </h2>
              <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>
                {getDescripcionPorTipo(tipo)}
              </p>
            </div>
          </div>
          <button onClick={onClose} aria-label="Cerrar"
            className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 transition"
            style={{ color: '#6B7280' }}>
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Paso actual */}
        {subPaso && <SubPasoPanel subPaso={subPaso} tipo={tipo} estadoActual={estadoActual} />}

        {/* Tiempos reales */}
        {(fechaRecepcion || fechaVencimiento || diasRestantes != null) && (
          <div className="px-5 py-2.5 border-b shrink-0 flex flex-wrap gap-4"
            style={{ background: '#FFFBEB', borderColor: '#FDE68A' }}>
            {fechaRecepcion && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium" style={{ color: '#92400E' }}>Recibido:</span>
                <span className="text-xs font-mono" style={{ color: '#111827' }}>
                  {new Date(fechaRecepcion).toLocaleDateString('es-CL', { dateStyle: 'short' })}
                </span>
              </div>
            )}
            {fechaVencimiento && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium" style={{ color: '#92400E' }}>Vence:</span>
                <span className="text-xs font-mono" style={{ color: '#111827' }}>
                  {new Date(fechaVencimiento).toLocaleDateString('es-CL', { dateStyle: 'short' })}
                </span>
              </div>
            )}
            {diasRestantes != null && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium" style={{ color: '#92400E' }}>Días hábiles:</span>
                <span className="text-xs font-bold px-1.5 py-0.5 rounded"
                  style={{
                    background: diasRestantes <= 0 ? '#FEE2E2' : diasRestantes <= 3 ? '#FEF3C7' : '#DCFCE7',
                    color: diasRestantes <= 0 ? '#991B1B' : diasRestantes <= 3 ? '#92400E' : '#166534',
                  }}>
                  {diasRestantes <= 0 ? `${Math.abs(diasRestantes)}d vencido` : `${diasRestantes}d restantes`}
                </span>
              </div>
            )}
            {priorrogaDias && priorrogaDias > 0 && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium" style={{ color: '#92400E' }}>Prórroga:</span>
                <span className="text-xs font-mono" style={{ color: '#7C3AED' }}>+{priorrogaDias}d</span>
              </div>
            )}
            {prioridad && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium" style={{ color: '#92400E' }}>Prioridad:</span>
                <span className="text-xs capitalize font-medium"
                  style={{ color: prioridad === 'urgente' ? '#DC2626' : prioridad === 'alta' ? '#D97706' : '#374151' }}>
                  {prioridad}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Diagrama */}
        <div className="flex-1 overflow-auto relative" style={{ background: '#FAFAFA', minHeight: 220 }}>
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10"
              style={{ background: 'rgba(250,250,250,0.95)' }}>
              <Loader2 className="w-7 h-7 animate-spin mb-2" style={{ color: '#4F46E5' }} />
              <p className="text-sm" style={{ color: '#6B7280' }}>Renderizando flujo...</p>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center z-10"
              style={{ background: 'rgba(250,250,250,0.95)' }}>
              <AlertCircle className="w-7 h-7 mb-2 text-red-500" />
              <p className="text-sm text-red-600 text-center px-6 mb-3">{error}</p>
              <Button variant="primary" size="sm" onClick={renderDiagrama}>Reintentar</Button>
            </div>
          )}
          <div ref={svgContainerRef} className="flex justify-center py-6 px-4 min-h-[220px]" />
        </div>

        {/* Leyenda */}
        <div className="px-6 py-3 border-t border-gray-100 bg-white shrink-0">
          <div className="flex items-center gap-4 flex-wrap">
            {LEGEND.map(({ color, label, ...rest }) => {
              const border = 'border' in rest ? (rest as any).border : undefined;
              return (
                <div key={label} className="flex items-center gap-1.5">
                  <span className="inline-block w-3 h-3 rounded-sm flex-shrink-0"
                    style={{
                      background: color,
                      ...(border ? { border: `1.5px solid ${border}` } : {}),
                    }} />
                  <span className="text-xs" style={{ color: '#6B7280' }}>
                    {label === 'Actual'
                      ? <><strong style={{ color: '#4F46E5' }}>★ {estadoActual.replace(/_/g, ' ')}</strong></>
                      : label}
                  </span>
                </div>
              );
            })}
            <span className="ml-auto text-xs" style={{ color: '#9CA3AF' }}>
              {nodosAnteriores.length} paso{nodosAnteriores.length !== 1 ? 's' : ''} completado{nodosAnteriores.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
