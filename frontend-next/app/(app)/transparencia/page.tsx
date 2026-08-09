'use client';

import { useEffect, useState } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import { getPoliticaTransparencia, updatePoliticaTransparencia, type PoliticaTransparencia } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import AlertBanner from '@/components/dashboard/AlertBanner';

const ITEM_LABELS: Record<string, string> = {
  item_a_politica: 'a) Política de Tratamiento',
  item_b_responsable: 'b) Responsable del Tratamiento',
  item_c_domicilio: 'c) Domicilio y Canal',
  item_d_categorias: 'd) Categorías de Datos y Titulares',
  item_e_medidas: 'e) Medidas de Seguridad',
  item_f_derechos_arco: 'f) Derechos ARCO',
  item_g_recurir_apdc: 'g) Cómo Recurrir a la APDC',
  item_h_transferencias: 'h) Transferencias Internacionales',
  item_i_conservacion: 'i) Conservación de Datos',
  item_j_fuente: 'j) Fuente de Datos',
  item_k_retirar_consentimiento: 'k) Retirar Consentimiento',
  item_l_decisiones_automatizadas: 'l) Decisiones Automatizadas',
};

const ITEM_KEYS = Object.keys(ITEM_LABELS);

type Overrides = Partial<Record<string, string>>;
type EditingItem = string | null;

export default function TransparenciaPage() {
  const { company, user } = useApp();
  const [politica, setPolitica] = useState<PoliticaTransparencia | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editingItem, setEditingItem] = useState<EditingItem>(null);
  const [drafts, setDrafts] = useState<Overrides>({});
  const [saving, setSaving] = useState(false);

  const canEdit = user?.rol_global === 'superadmin' || user?.rol_global === 'admin_empresa';

  function load() {
    if (!company?.id) return;
    setLoading(true);
    getPoliticaTransparencia(company.id)
      .then(p => { setPolitica(p); setDrafts({}); setEditingItem(null); })
      .catch(() => toast.error('No se pudo cargar la política de transparencia.'))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, [company?.id]);

  async function handleSave() {
    if (!company?.id || !Object.keys(drafts).length) { setEditMode(false); return; }
    setSaving(true);
    try {
      const updated = await updatePoliticaTransparencia(company.id, drafts);
      setPolitica(updated);
      setDrafts({});
      setEditingItem(null);
      setEditMode(false);
      toast.success('Política actualizada y hash recalculado.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  }

  async function handleResetItem(key: string) {
    if (!company?.id) return;
    setSaving(true);
    try {
      const updated = await updatePoliticaTransparencia(company.id, { [key]: null });
      setPolitica(updated);
      setDrafts(d => { const n = { ...d }; delete n[key]; return n; });
      setEditingItem(null);
      toast.success('Ítem restaurado al texto automático.');
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al restaurar.');
    } finally {
      setSaving(false);
    }
  }

  function cancelEdit() {
    setDrafts({});
    setEditingItem(null);
    setEditMode(false);
  }

  if (loading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-64 rounded animate-pulse" style={{ background: '#E5E7EB' }} />
        <div className="h-4 w-96 rounded animate-pulse" style={{ background: '#E5E7EB' }} />
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-24 rounded-xl animate-pulse" style={{ background: '#E5E7EB' }} />
        ))}
      </div>
    );
  }

  if (!politica) {
    return (
      <div className="p-6 text-center">
        <p style={{ color: '#6B7280' }}>No hay política de transparencia disponible para esta empresa.</p>
      </div>
    );
  }

  const autoValues = politica as unknown as Record<string, string>;
  const hasDrafts = Object.keys(drafts).length > 0;

  return (
    <div className="p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Política de Transparencia</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
            {politica.nombre_empresa} · Versión {politica.version}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {canEdit && !editMode && (
            <Button variant="secondary" size="sm" onClick={() => setEditMode(true)}>
              ✏️ Editar
            </Button>
          )}
          {editMode && (
            <>
              <Button variant="secondary" size="sm" onClick={cancelEdit} disabled={saving}>
                Cancelar
              </Button>
              <Button size="sm" onClick={handleSave} disabled={saving || !hasDrafts}>
                {saving ? 'Guardando…' : 'Guardar cambios'}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Banner legal */}
      <div
        className="rounded-xl p-4 flex items-center gap-3"
        style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}
      >
        <div>
          <p className="font-semibold text-white text-sm">Ley 21.719 — Art. 14 ter</p>
          <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.7)' }}>
            Política pública de tratamiento de datos personales · Los ítems marcados con ⚡ se generan automáticamente desde tus RATs
          </p>
        </div>
      </div>

      {editMode && (
        <AlertBanner
          message="Modo edición: haz clic en cualquier ítem para personalizarlo. Los cambios no se publican hasta que hagas clic en «Guardar cambios». Un ítem personalizado reemplaza el texto auto-generado; puedes restaurarlo con «↩ Automático»."
          type="info"
        />
      )}

      {/* Ítems */}
      <div className="grid gap-4">
        {ITEM_KEYS.map(key => {
          const label = ITEM_LABELS[key];
          const currentText = autoValues[key] || '—';
          const draftText = drafts[key];
          const isEditing = editingItem === key;
          const isCustomized = draftText !== undefined;

          const AUTO_KEYS = ['item_d_categorias', 'item_e_medidas', 'item_h_transferencias',
            'item_i_conservacion', 'item_j_fuente', 'item_l_decisiones_automatizadas'];
          const isAutoGenerated = AUTO_KEYS.includes(key);

          return (
            <div
              key={key}
              className="rounded-xl p-5 transition-shadow"
              style={{
                background: 'white',
                border: `1px solid ${isEditing ? '#2563EB' : isCustomized ? '#7C3AED' : '#E5E7EB'}`,
                boxShadow: isEditing ? '0 0 0 2px #DBEAFE' : undefined,
              }}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h3 className="text-sm font-bold" style={{ color: '#1E40AF' }}>
                  {label}
                  {isAutoGenerated && <span className="ml-1.5 text-xs font-normal" style={{ color: '#9CA3AF' }}>⚡ automático</span>}
                  {isCustomized && <span className="ml-1.5 text-xs font-medium px-1.5 py-0.5 rounded-full" style={{ background: '#EDE9FE', color: '#6D28D9' }}>personalizado</span>}
                </h3>
                {editMode && (
                  <div className="flex gap-1.5 flex-shrink-0">
                    {!isEditing && (
                      <button
                        onClick={() => {
                          setEditingItem(key);
                          if (drafts[key] === undefined) {
                            setDrafts(d => ({ ...d, [key]: currentText }));
                          }
                        }}
                        className="text-xs px-2 py-1 rounded-lg transition"
                        style={{ color: '#2563EB', background: '#EFF6FF' }}
                      >
                        ✏️ Editar
                      </button>
                    )}
                    {isCustomized && (
                      <button
                        onClick={() => handleResetItem(key)}
                        disabled={saving}
                        className="text-xs px-2 py-1 rounded-lg transition"
                        style={{ color: '#7C3AED', background: '#F5F3FF' }}
                      >
                        ↩ Automático
                      </button>
                    )}
                  </div>
                )}
              </div>

              {isEditing ? (
                <div className="space-y-2">
                  <textarea
                    value={drafts[key] ?? currentText}
                    onChange={e => setDrafts(d => ({ ...d, [key]: e.target.value }))}
                    rows={6}
                    className="w-full px-3 py-2 rounded-lg text-sm border resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{ borderColor: '#2563EB', color: '#374151', lineHeight: 1.6 }}
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        setDrafts(d => { const n = { ...d }; delete n[key]; return n; });
                        setEditingItem(null);
                      }}
                    >
                      Cancelar
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => setEditingItem(null)}
                      disabled={!drafts[key]?.trim()}
                    >
                      Confirmar
                    </Button>
                  </div>
                </div>
              ) : (
                <p
                  className="text-sm whitespace-pre-line cursor-default"
                  style={{ color: '#374151', lineHeight: 1.7 }}
                  onClick={() => {
                    if (!editMode) return;
                    setEditingItem(key);
                    if (drafts[key] === undefined) setDrafts(d => ({ ...d, [key]: currentText }));
                  }}
                >
                  {isCustomized ? (drafts[key] || currentText) : currentText}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="text-center text-xs" style={{ color: '#9CA3AF' }}>
        <p>Última actualización: {new Date(politica.fecha_generacion).toLocaleDateString('es-CL')}</p>
        <p className="mt-0.5 font-mono">{politica.hash_sha256}</p>
        <p className="mt-1">Artículo 14 ter — Ley 21.719 de Chile</p>
      </div>
    </div>
  );
}
