// Cliente HTTP del módulo Asesor (Custodio Asesor - RAG)

import { API_BASE } from './constants';

const ENDPOINTS = {
  ask: () => `${API_BASE}/asesor/ask`,
  index: () => `${API_BASE}/admin/asesor/index`,
  stats: () => `${API_BASE}/admin/asesor/stats`,
  deleteChunk: (id: number) => `${API_BASE}/admin/asesor/documents/${id}`,
};

function getToken(): string {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('custodio_token') || '';
}

function authHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getToken()}`,
  };
}

async function handle<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    localStorage.removeItem('custodio_token');
    localStorage.removeItem('custodio_user');
    localStorage.removeItem('custodio_company');
    window.location.replace('/login');
    throw new Error('Sesión expirada');
  }
  if (!res.ok) {
    let detail = 'Error desconocido';
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      detail = res.statusText;
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export interface AsesorSource {
  source: string;
  source_type: string;
  title: string | null;
  chunk_index: number;
  score: number;
  snippet: string;
}

export interface AsesorAskResponse {
  answer: string;
  sources: AsesorSource[];
  provider: string;
  embedding_provider: string;
  latency_ms: number;
}

export interface AsesorStats {
  total_chunks: number;
  total_documents: number;
  chunks_por_source: Record<string, number>;
  ultimo_indexado: string | null;
  provider: string;
}

export interface AsesorIndexResponse {
  indexed: number;
  skipped: number;
  errors: string[];
  duration_ms: number;
}

export async function askAsesor(question: string, context?: string): Promise<AsesorAskResponse> {
  const res = await fetch(ENDPOINTS.ask(), {
    method: 'POST',
    headers: authHeaders(),
    credentials: 'include',
    body: JSON.stringify({ question, context: context || null }),
  });
  return handle<AsesorAskResponse>(res);
}

export async function indexAsesor(paths?: string[], force = false): Promise<AsesorIndexResponse> {
  const res = await fetch(ENDPOINTS.index(), {
    method: 'POST',
    headers: authHeaders(),
    credentials: 'include',
    body: JSON.stringify({ paths: paths || null, force }),
  });
  return handle<AsesorIndexResponse>(res);
}

export async function getAsesorStats(): Promise<AsesorStats> {
  const res = await fetch(ENDPOINTS.stats(), {
    method: 'GET',
    headers: authHeaders(),
    credentials: 'include',
  });
  return handle<AsesorStats>(res);
}

export async function deleteAsesorChunk(id: number): Promise<{ ok: boolean; id: number }> {
  const res = await fetch(ENDPOINTS.deleteChunk(id), {
    method: 'DELETE',
    headers: authHeaders(),
    credentials: 'include',
  });
  return handle<{ ok: boolean; id: number }>(res);
}
