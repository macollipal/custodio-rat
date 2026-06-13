'use client';

import { useState, useEffect } from 'react';
import AsesorChat from '@/components/asesor/AsesorChat';
import type { ChatMessage } from '@/components/asesor/AsesorChat';
import { askAsesor, getAsesorStats, indexAsesor } from '@/lib/asesor-api';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';

const STORAGE_KEY = 'custodio_asesor_history';

export default function AsesorPage() {
  const { user } = useApp();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<{ total_chunks: number; total_documents: number; provider: string } | null>(null);
  const [indexing, setIndexing] = useState(false);
  const isSuperadmin = user?.rol_global === 'superadmin';

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setMessages(JSON.parse(raw));
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-20)));
    } catch {
      // ignore
    }
  }, [messages]);

  useEffect(() => {
    if (isSuperadmin) {
      getAsesorStats()
        .then((s) => setStats({ total_chunks: s.total_chunks, total_documents: s.total_documents, provider: s.provider }))
        .catch(() => setStats(null));
    }
  }, [isSuperadmin]);

  async function handleSend(question: string) {
    const userMsg: ChatMessage = { role: 'user', content: question, ts: Date.now() };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);
    try {
      const result = await askAsesor(question);
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: result.answer,
        sources: result.sources,
        provider: result.provider,
        embedding_provider: result.embedding_provider,
        latency_ms: result.latency_ms,
        fallback: result.sources.length === 0,
        ts: Date.now(),
      };
      setMessages((m) => [...m, assistantMsg]);
    } catch (e: any) {
      const errMsg: ChatMessage = {
        role: 'assistant',
        content: `Lo siento, ocurrió un error: ${e?.message || 'desconocido'}. Intenta de nuevo o contacta al administrador.`,
        ts: Date.now(),
      };
      setMessages((m) => [...m, errMsg]);
      toast.error('Error al consultar el Asesor');
    } finally {
      setLoading(false);
    }
  }

  async function handleReindex() {
    setIndexing(true);
    try {
      const result = await indexAsesor(undefined, false);
      toast.success(`Indexado: ${result.indexed} nuevos · ${result.skipped} ya existían · ${result.errors.length} errores`);
      const s = await getAsesorStats();
      setStats({ total_chunks: s.total_chunks, total_documents: s.total_documents, provider: s.provider });
    } catch (e: any) {
      toast.error(`Error al indexar: ${e?.message || 'desconocido'}`);
    } finally {
      setIndexing(false);
    }
  }

  function clearHistory() {
    if (!confirm('¿Borrar el historial de la sesión?')) return;
    setMessages([]);
  }

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] sm:h-[calc(100vh-72px)]">
      <div
        className="px-4 py-3 sm:px-6 sm:py-4 flex items-center justify-between flex-wrap gap-2"
        style={{ background: 'linear-gradient(135deg, #0D4F3C, #0a3d2e)', color: '#FFFFFF' }}
      >
        <div>
          <h1 className="text-base sm:text-lg font-bold flex items-center gap-2">
            <span aria-hidden="true">⚖️</span>
            Custodio Asesor
            <span
              className="ml-2 px-2 py-0.5 rounded-full text-[10px] font-semibold"
              style={{ background: '#C8A951', color: '#0D4F3C' }}
            >
              MÓDULO RAG
            </span>
          </h1>
          <p className="text-xs sm:text-sm" style={{ color: '#C8A951' }}>
            Asistente IA especializado en la Ley 21.719 con citas a fuentes
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isSuperadmin && stats && (
            <div
              className="text-xs px-3 py-1.5 rounded-lg"
              style={{ background: 'rgba(255,255,255,0.1)', color: '#FFFFFF' }}
            >
              📚 {stats.total_chunks} chunks · 📄 {stats.total_documents} docs · ⚡ {stats.provider}
            </div>
          )}
          {isSuperadmin && (
            <button
              type="button"
              onClick={handleReindex}
              disabled={indexing}
              className="text-xs px-3 py-1.5 rounded-lg font-medium transition disabled:opacity-50"
              style={{ background: '#C8A951', color: '#0D4F3C' }}
            >
              {indexing ? 'Indexando…' : 'Reindexar corpus'}
            </button>
          )}
          <button
            type="button"
            onClick={clearHistory}
            className="text-xs px-3 py-1.5 rounded-lg font-medium transition"
            style={{ background: 'rgba(255,255,255,0.1)', color: '#FFFFFF' }}
          >
            Limpiar
          </button>
        </div>
      </div>

      <AsesorChat messages={messages} onSend={handleSend} loading={loading} />
    </div>
  );
}
