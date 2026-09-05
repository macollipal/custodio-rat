'use client';

import { useState, useEffect, useRef } from 'react';
import { toast } from 'sonner';
import {
  listAsesorDocuments,
  uploadAsesorDocument,
  deleteAsesorDocument,
  getAsesorDocumentDownloadUrl,
  type AsesorCorpusDocument,
  type AsesorDocumentsListResponse,
} from '@/lib/asesor-api';
import { getToken } from '@/lib/api';

function fmtBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function fmtDate(dateStr: string): string {
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CL', { dateStyle: 'medium' });
}

const SOURCE_TYPE_LABELS: Record<string, { label: string; color: string; bg: string }> = {
  ley: { label: 'Ley', color: '#2563EB', bg: '#DBEAFE' },
  caso_uso: { label: 'Caso de uso', color: '#7C3AED', bg: '#EDE9FE' },
  auditoria: { label: 'Auditoría', color: '#D97706', bg: '#FEF3C7' },
  manual: { label: 'Manual', color: '#059669', bg: '#DCFCE7' },
  otros: { label: 'Otros', color: '#6B7280', bg: '#F3F4F6' },
};

const SOURCE_TYPE_ICONS: Record<string, string> = {
  ley: '⚖️',
  caso_uso: '📋',
  auditoria: '🔍',
  manual: '📖',
  otros: '📄',
};

export default function AsesorCorpusTab() {
  const [docs, setDocs] = useState<AsesorCorpusDocument[]>([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [draggingOver, setDraggingOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function loadDocuments() {
    setLoading(true);
    try {
      const data: AsesorDocumentsListResponse = await listAsesorDocuments();
      setDocs(data.documents);
      setTotalChunks(data.documents.reduce((sum, d) => sum + d.chunks_indexed, 0));
    } catch {
      toast.error('No se pudieron cargar los documentos del corpus');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(file: File) {
    if (uploading) return;
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'md' && ext !== 'txt' && ext !== 'markdown') {
      toast.error('Solo se permiten archivos .md, .txt o .markdown');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('El archivo excede el tamaño máximo de 5MB');
      return;
    }
    setUploading(true);
    try {
      const result = await uploadAsesorDocument(file);
      toast.success(
        `✓ "${result.original_filename}" — ${result.chunks_indexed} chunks indexados`
      );
      await loadDocuments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al subir';
      toast.error(msg);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) await handleUpload(file);
  }

  async function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDraggingOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) await handleUpload(file);
  }

  async function handleDelete(docId: number) {
    setDeletingId(docId);
    try {
      const result = await deleteAsesorDocument(docId);
      toast.success(`"${result.original_filename}" eliminado — ${result.chunks_removed} chunks removidos`);
      setConfirmDeleteId(null);
      await loadDocuments();
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar';
      toast.error(msg);
    } finally {
      setDeletingId(null);
    }
  }

  async function handleDownload(docId: number, filename: string) {
    try {
      const { download_url } = await getAsesorDocumentDownloadUrl(docId);
      const a = document.createElement('a');
      a.href = download_url;
      a.download = filename;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al descargar';
      toast.error(msg);
    }
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl p-4" style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
        <div className="flex items-start gap-3">
          <span className="text-xl flex-shrink-0">🧠</span>
          <div>
            <p className="text-sm font-semibold" style={{ color: '#1E40AF' }}>Corpus del Asesor</p>
            <p className="text-xs mt-1" style={{ color: '#3B82F6' }}>
              Subí archivos .md o .txt para que el Asesor pueda responder preguntas con contexto adicional.
              Los documentos se guardan en OCI Object Storage y se indexan automáticamente con embeddings de Cohere.
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold" style={{ color: '#111827' }}>
            Documentos del corpus
          </h2>
          <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>
            {docs.length} {docs.length === 1 ? 'archivo' : 'archivos'} · {totalChunks} chunks
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadDocuments}
            className="px-3 py-1.5 rounded-lg text-xs font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            🔄
          </button>
          <label className="px-4 py-2 rounded-lg text-sm font-semibold text-white cursor-pointer transition hover:opacity-90 disabled:opacity-60 flex items-center gap-2"
            style={{ background: uploading ? '#9CA3AF' : '#059669' }}>
            {uploading ? (
              <>⏳ Subiendo...</>
            ) : (
              <>
                📁 Subir archivo
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".md,.txt,.markdown"
                  className="hidden"
                  onChange={handleFileSelect}
                  disabled={uploading}
                />
              </>
            )}
          </label>
        </div>
      </div>

      <div
        className="rounded-xl border-2 border-dashed p-8 text-center transition-colors"
        style={{
          borderColor: draggingOver ? '#2563EB' : '#E5E7EB',
          background: draggingOver ? '#EFF6FF' : '#FAFAFA',
        }}
        onDragOver={e => { e.preventDefault(); setDraggingOver(true); }}
        onDragLeave={() => setDraggingOver(false)}
        onDrop={handleDrop}
      >
        <p className="text-sm" style={{ color: '#9CA3AF' }}>
          Arrastrá un archivo .md o .txt acá, o hacé click en "Subir archivo"
        </p>
        <p className="text-xs mt-1" style={{ color: '#D1D5DB' }}>
          Máximo 5MB por archivo
        </p>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 rounded-xl animate-pulse" style={{ background: '#F3F4F6' }} />
          ))}
        </div>
      ) : docs.length === 0 ? (
        <div className="text-center py-12 rounded-xl" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
          <p className="text-sm" style={{ color: '#9CA3AF' }}>No hay documentos en el corpus.</p>
          <p className="text-xs mt-1" style={{ color: '#D1D5DB' }}>Subí tu primer archivo .md para que el Asesor pueda usarlo como contexto.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map(doc => {
            const st = SOURCE_TYPE_LABELS[doc.source_type] ?? SOURCE_TYPE_LABELS.otros;
            const icon = SOURCE_TYPE_ICONS[doc.source_type] ?? '📄';
            const isDeleting = deletingId === doc.id;
            const confirm = confirmDeleteId === doc.id;

            return (
              <div
                key={doc.id}
                className="rounded-xl p-4 transition-colors"
                style={{ background: '#FFFFFF', border: '1px solid #E5E7EB' }}
              >
                {confirm ? (
                  <div className="space-y-3">
                    <p className="text-sm" style={{ color: '#374151' }}>
                      ¿Eliminar <strong>"{doc.original_filename}"</strong> y sus{' '}
                      <strong>{doc.chunks_indexed} chunks</strong>? Esta acción no se puede deshacer.
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        disabled={isDeleting}
                        className="px-3 py-1.5 rounded-lg text-xs font-semibold text-white disabled:opacity-60"
                        style={{ background: '#DC2626' }}
                      >
                        {isDeleting ? 'Eliminando...' : 'Sí, eliminar'}
                      </button>
                      <button
                        onClick={() => setConfirmDeleteId(null)}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium border"
                        style={{ borderColor: '#E5E7EB', color: '#374151' }}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0 mt-0.5">{icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-sm font-semibold truncate" style={{ color: '#111827' }} title={doc.original_filename}>
                          {doc.original_filename}
                        </p>
                        <span
                          className="px-2 py-0.5 rounded text-xs font-medium flex-shrink-0"
                          style={{ background: st.bg, color: st.color }}
                        >
                          {st.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs" style={{ color: '#9CA3AF' }}>
                        <span>{fmtBytes(doc.size_bytes)}</span>
                        <span>·</span>
                        <span>{doc.chunks_indexed} {doc.chunks_indexed === 1 ? 'chunk' : 'chunks'}</span>
                        {doc.uploaded_by_username && (
                          <>
                            <span>·</span>
                            <span>{doc.uploaded_by_username}</span>
                            <span>·</span>
                            <span>{fmtDate(doc.created_at)}</span>
                          </>
                        )}
                      </div>
                      {doc.title && doc.title !== doc.original_filename && (
                        <p className="text-xs mt-1 truncate" style={{ color: '#6B7280' }} title={doc.title}>
                          Título: {doc.title}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1 flex-shrink-0">
                      <button
                        onClick={() => handleDownload(doc.id, doc.original_filename)}
                        className="p-2 rounded-lg text-sm transition hover:bg-gray-100"
                        style={{ color: '#6B7280' }}
                        title="Descargar"
                      >
                        ⬇️
                      </button>
                      <button
                        onClick={() => setConfirmDeleteId(doc.id)}
                        className="p-2 rounded-lg text-sm transition hover:bg-red-50"
                        style={{ color: '#DC2626' }}
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
