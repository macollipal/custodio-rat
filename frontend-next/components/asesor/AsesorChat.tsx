'use client';

import { useEffect, useRef, useState } from 'react';
import SourceChip from './SourceChip';
import type { AsesorSource } from '@/lib/asesor-api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: AsesorSource[];
  provider?: string;
  embedding_provider?: string;
  latency_ms?: number;
  fallback?: boolean;
  ts: number;
}

interface AsesorChatProps {
  messages: ChatMessage[];
  onSend: (question: string) => Promise<void>;
  loading: boolean;
}

export default function AsesorChat({ messages, onSend, loading }: AsesorChatProps) {
  const [input, setInput] = useState('');
  const [selectedSource, setSelectedSource] = useState<AsesorSource | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;
    setInput('');
    await onSend(q);
  }

  return (
    <div className="flex flex-col h-full">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-3 py-4 sm:px-6 sm:py-6 space-y-4"
        style={{ background: '#F9FAFB' }}
      >
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto text-center py-10">
            <div
              className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
              style={{ background: 'linear-gradient(135deg, #0D4F3C, #C8A951)' }}
            >
              <span aria-hidden="true" style={{ fontSize: 30 }}>⚖️</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold mb-2" style={{ color: '#0D4F3C' }}>
              Custodio Asesor
            </h2>
            <p className="text-sm sm:text-base" style={{ color: '#6B7280' }}>
              Tu asesor experto en protección de datos. Pregúntame sobre la Ley 21.719, los RATs, EIPD, brechas, transferencias internacionales o el uso de Custodio.
            </p>
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
              {[
                '¿Qué es una EIPD y cuándo es obligatoria?',
                '¿Cuál es el plazo para notificar una brecha a la APDP?',
                '¿Qué base legal aplica para videovigilancia laboral?',
                '¿Cuándo se requiere consentimiento expreso?',
              ].map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => onSend(q)}
                  disabled={loading}
                  className="text-xs sm:text-sm px-3 py-2.5 rounded-lg text-left transition disabled:opacity-50"
                  style={{ background: '#FFFFFF', color: '#374151', border: '1px solid #E5E7EB' }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className="max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm"
              style={{
                background: m.role === 'user' ? '#0D4F3C' : '#FFFFFF',
                color: m.role === 'user' ? '#FFFFFF' : '#111827',
                border: m.role === 'user' ? 'none' : '1px solid #E5E7EB',
              }}
            >
              {m.role === 'user' ? (
                <p className="text-sm whitespace-pre-wrap break-words">{m.content}</p>
              ) : (
                <>
                  {m.fallback && (
                    <div
                      className="mb-2 px-2.5 py-1.5 rounded text-xs"
                      style={{ background: '#FEF3C7', color: '#92400E' }}
                    >
                      ⚠️ No encontré información suficiente en el corpus. La respuesta puede ser genérica.
                    </div>
                  )}
                  <p className="text-sm whitespace-pre-wrap break-words">{m.content}</p>
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-3 pt-3" style={{ borderTop: '1px solid #E5E7EB' }}>
                      <div className="text-[10px] font-semibold uppercase tracking-widest mb-2" style={{ color: '#6B7280' }}>
                        Fuentes citadas ({m.sources.length})
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {m.sources.map((s, idx) => (
                          <SourceChip
                            key={`${idx}-${s.chunk_index}-${s.source}`}
                            source={s}
                            onClick={setSelectedSource}
                          />
                        ))}
                      </div>
                      {m.provider && (
                        <div className="mt-2 text-[10px]" style={{ color: '#9CA3AF' }}>
                          Proveedor: {m.provider} · Embeddings: {m.embedding_provider} · {m.latency_ms}ms
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl px-4 py-3 shadow-sm" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB' }}>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: '#0D4F3C', animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: '#0D4F3C', animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: '#0D4F3C', animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="px-3 py-3 sm:px-6 sm:py-4 flex gap-2"
        style={{ background: '#FFFFFF', borderTop: '1px solid #E5E7EB' }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Pregúntale al Asesor sobre la Ley 21.719..."
          disabled={loading}
          maxLength={2000}
          className="flex-1 px-3 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 disabled:opacity-50"
          style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', color: '#111827' }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 py-2.5 rounded-lg text-sm font-semibold transition disabled:opacity-50"
          style={{ background: '#0D4F3C', color: '#FFFFFF' }}
        >
          Enviar
        </button>
      </form>

      {selectedSource && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedSource(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-5 py-3 flex items-center justify-between" style={{ background: '#0D4F3C' }}>
              <div>
                <div className="text-white font-semibold text-sm">
                  {selectedSource.source.split(/[\\\/]/).pop()}
                </div>
                {selectedSource.title && (
                  <div className="text-xs" style={{ color: '#C8A951' }}>
                    {selectedSource.title}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => setSelectedSource(null)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white hover:bg-white/10"
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>
            <div className="px-5 py-4 overflow-y-auto flex-1">
              <div className="text-xs mb-2" style={{ color: '#6B7280' }}>
                Score: {selectedSource.score} · Chunk #{selectedSource.chunk_index} · Tipo: {selectedSource.source_type}
              </div>
              <p className="text-sm whitespace-pre-wrap" style={{ color: '#111827' }}>
                {selectedSource.snippet}…
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
