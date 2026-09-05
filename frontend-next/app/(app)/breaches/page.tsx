'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { useApp } from '@/context/AppContext';
import * as api from '@/lib/api';
import AlertBanner from '@/components/dashboard/AlertBanner';
import { Button } from '@/components/ui/Button';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import type { SecurityBreach } from '@/types';
import { inputCls, inputStyle, labelCls, labelStyle, panelStyles, panelWrapperCls, btnPrimaryCls, btnPrimaryStyle, btnSecondaryCls, btnSecondaryStyle, gridResponsive1to2 } from '@/lib/styles';

const PLAZO_APDC_HORAS = 72;

function PlazoBadge({ hours }: { hours: number }) {
  const remaining = PLAZO_APDC_HORAS - hours;
  if (remaining <= 0) {
    return <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#DC2626' }}>⏰ VENCIDO</span>;
  }
  if (remaining <= 12) {
    return <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEF3C7', color: '#D97706' }}>⚠️ {remaining}h restantes</span>;
  }
  return <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#D1FAE5', color: '#065F46' }}>✓ {Math.round(remaining)}h restantes</span>;
}

interface BreachFormData {
  descripcion: string;
  fecha_deteccion: string;
  rats_afectados: string;
  datos_comprometidos: string;
  medidas_adoptadas: string;
  naturaleza: 'confidencialidad' | 'integridad' | 'disponibilidad' | undefined;
  notificado_apdc: boolean;
  notificado_titulares: boolean;
  volumen_titulares_afectados: number;
  incluye_datos_sensibles: boolean;
  incluye_datos_nna: boolean;
  incluye_datos_financieros: boolean;
  // Campos nuevos gaps Ley 21.719 (Iter 10)
  fecha_ocurrencia_estimada?: string;
  efectos_probables?: string;
  causa_raiz?: string;
  evidencia_notificacion_apdc_folio?: string;
  estado_cierre?: string;
  fecha_cierre?: string;
  // Ley 21.719 Art. 14 bis
  fecha_conocimiento?: string;
}

function BreachForm({
  initial,
  onSave,
  onCancel,
  saving,
}: {
  initial?: Partial<BreachFormData>;
  onSave: (data: BreachFormData) => void;
  onCancel: () => void;
  saving: boolean;
}) {
  const [form, setForm] = useState<BreachFormData>({
    descripcion: initial?.descripcion ?? '',
    fecha_deteccion: initial?.fecha_deteccion ?? new Date().toISOString().slice(0, 16),
    rats_afectados: initial?.rats_afectados ?? '',
    datos_comprometidos: initial?.datos_comprometidos ?? '',
    medidas_adoptadas: initial?.medidas_adoptadas ?? '',
    naturaleza: initial?.naturaleza ?? undefined,
    notificado_apdc: initial?.notificado_apdc ?? false,
    notificado_titulares: initial?.notificado_titulares ?? false,
    volumen_titulares_afectados: initial?.volumen_titulares_afectados ?? 0,
    incluye_datos_sensibles: initial?.incluye_datos_sensibles ?? false,
    incluye_datos_nna: initial?.incluye_datos_nna ?? false,
    incluye_datos_financieros: initial?.incluye_datos_financieros ?? false,
    // Campos nuevos gaps Ley 21.719 (Iter 10)
    fecha_ocurrencia_estimada: initial?.fecha_ocurrencia_estimada ?? '',
    efectos_probables: initial?.efectos_probables ?? '',
    causa_raiz: initial?.causa_raiz ?? '',
    evidencia_notificacion_apdc_folio: initial?.evidencia_notificacion_apdc_folio ?? '',
    estado_cierre: initial?.estado_cierre ?? '',
    fecha_cierre: initial?.fecha_cierre ?? '',
    fecha_conocimiento: initial?.fecha_conocimiento ?? '',
  });

  function set(k: keyof BreachFormData, v: string | number | boolean | undefined) {
    setForm(f => ({ ...f, [k]: v }));
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm space-y-5" style={{ border: '1px solid #E5E7EB' }}>
      <div>
        <h3 className="text-base font-bold mb-1" style={{ color: '#111827' }}>
          {initial?.descripcion ? 'Editar brecha' : 'Registrar nueva brecha de seguridad'}
        </h3>
        <p className="text-sm" style={{ color: '#6B7280' }}>Art. 14 sexies Ley 21.719 — Notificación obligatoria a la APDP en 72 horas.</p>
      </div>

      <div className="rounded-lg p-4" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
        <AlertBanner
          message={<>Las brechas de seguridad que afecten datos personales deben ser reportadas a la Agencia de Protección de Datos Personales (APDP) dentro de las <strong>72 horas</strong> desde su detección. Si la brecha afecta datos sensibles, menores o información financiera, también debe notificarse a los titulares afectados sin dilación.</>}
          type="danger"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Descripción de la brecha *</label>
        <textarea
          value={form.descripcion}
          onChange={e => set('descripcion', e.target.value)}
          rows={3}
          placeholder="Detalle qué ocurrió: tipo de incidente, cómo se descubrió, alcance estimado..."
          className={inputCls}
          style={inputStyle}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Fecha y hora de detección *</label>
          <input
            type="datetime-local"
            value={form.fecha_deteccion}
            onChange={e => set('fecha_deteccion', e.target.value)}
            className={inputCls}
            style={inputStyle}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Procesos RAT afectados</label>
          <input
            type="text"
            value={form.rats_afectados}
            onChange={e => set('rats_afectados', e.target.value)}
            placeholder="Ej: Gestión de nóminas, CRM de clientes"
            className={inputCls}
            style={inputStyle}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Datos comprometidos</label>
        <textarea
          value={form.datos_comprometidos}
          onChange={e => set('datos_comprometidos', e.target.value)}
          rows={2}
          placeholder="Ej: Nombres, RUT y emails de 1.200 clientes"
          className={inputCls}
          style={inputStyle}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Medidas adoptadas</label>
        <textarea
          value={form.medidas_adoptadas}
          onChange={e => set('medidas_adoptadas', e.target.value)}
          rows={2}
          placeholder="Ej: Contención inmediata, bloqueo de accesos, notificación a afectados..."
          className={inputCls}
          style={inputStyle}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1.5" style={{ color: '#374151' }}>Naturaleza de la brecha (Art. 14 sexies) *</label>
        <select
          value={form.naturaleza ?? ''}
          onChange={e => {
            const v = e.target.value;
            set('naturaleza', (v === '' ? undefined : v) as BreachFormData['naturaleza']);
          }}
          className={inputCls}
          style={inputStyle}
          aria-label="Naturaleza de la brecha"
        >
          <option value="">— Seleccione la naturaleza —</option>
          <option value="confidencialidad">Confidencialidad — acceso no autorizado a datos</option>
          <option value="integridad">Integridad — modificación no autorizada de datos</option>
          <option value="disponibilidad">Disponibilidad — indisponibilidad de datos/sistemas</option>
        </select>
        <p className="text-xs mt-1" style={{ color: '#6B7280' }}>Requerido por Art. 14 sexies para notificación APDP.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-3 rounded-lg p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
          <label className="flex items-start gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={form.notificado_apdc}
              onChange={e => set('notificado_apdc', e.target.checked)}
              className="mt-0.5 rounded"
            />
            <div>
              <span className="text-sm font-semibold" style={{ color: '#111827' }}>Notificado a la APDP</span>
              <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>Marcar cuando ya se envió la notificación dentro de las 72 horas.</p>
            </div>
          </label>
        </div>
        <div className="space-y-3 rounded-lg p-4" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB' }}>
          <label className="flex items-start gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={form.notificado_titulares}
              onChange={e => set('notificado_titulares', e.target.checked)}
              className="mt-0.5 rounded"
            />
            <div>
              <span className="text-sm font-semibold" style={{ color: '#111827' }}>Notificado a los titulares</span>
              <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>Obligatorio sin dilación si hay datos sensibles, menores o financieros.</p>
            </div>
          </label>
        </div>
      </div>

      {/* B-05: Filtro de riesgo razonable (Art. 14 sexies) */}
      <div className="rounded-lg p-4 space-y-3" style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}>
        <p className="text-sm font-semibold" style={{ color: '#991B1B' }}>Evaluación de Riesgo (Art. 14 sexies)</p>
        <div>
          <label className={labelCls} style={labelStyle}>Volumen de titulares afectados</label>
          <input
            type="number"
            min={0}
            value={form.volumen_titulares_afectados}
            onChange={e => set('volumen_titulares_afectados', Number(e.target.value))}
            className={inputCls}
            style={{ borderColor: '#E5E7EB' }}
            placeholder="Ej: 150"
          />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label className="flex items-center gap-2 text-sm" style={{ color: '#374151' }}>
            <input type="checkbox" checked={form.incluye_datos_sensibles} onChange={e => set('incluye_datos_sensibles', e.target.checked)} className="rounded" />
            Datos sensibles
          </label>
          <label className="flex items-center gap-2 text-sm" style={{ color: '#374151' }}>
            <input type="checkbox" checked={form.incluye_datos_nna} onChange={e => set('incluye_datos_nna', e.target.checked)} className="rounded" />
            Menores (NNA)
          </label>
          <label className="flex items-center gap-2 text-sm" style={{ color: '#374151' }}>
            <input type="checkbox" checked={form.incluye_datos_financieros} onChange={e => set('incluye_datos_financieros', e.target.checked)} className="rounded" />
            Datos financieros
          </label>
        </div>
      </div>

      {/* Campos nuevos gaps Ley 21.719 (Iter 10) */}
      <div className="rounded-lg p-4 space-y-3" style={{ background: '#F0F9FF', border: '1px solid #BAE6FD' }}>
        <p className="text-sm font-semibold" style={{ color: '#0369A1' }}>📋 Compliance · Ley 21.719</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls} style={labelStyle}>Fecha de conocimiento (Art. 14 bis) *</label>
            <input
              type="datetime-local"
              value={form.fecha_conocimiento ?? ''}
              onChange={e => set('fecha_conocimiento', e.target.value || undefined)}
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            />
            <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>Momento exacto en que el responsable tomó conocimiento de la brecha. El plazo de 72 h para notificar a la APDP corre desde esta fecha.</p>
          </div>
          <div>
            <label className={labelCls} style={labelStyle}>Fecha ocurrencia estimada</label>
            <input
              type="datetime-local"
              value={form.fecha_ocurrencia_estimada ?? ''}
              onChange={e => set('fecha_ocurrencia_estimada', e.target.value || undefined)}
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls} style={labelStyle}>Causa raíz</label>
            <select
              value={form.causa_raiz ?? ''}
              onChange={e => set('causa_raiz', e.target.value || undefined)}
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            >
              <option value="">— No especificada —</option>
              <option value="error_humano">Error humano</option>
              <option value="malware">Malware</option>
              <option value="acceso_no_autorizado">Acceso no autorizado</option>
              <option value="proveedor">Proveedor</option>
              <option value="perdida_equipo">Pérdida de equipo</option>
              <option value="otro">Otro</option>
            </select>
          </div>
        </div>
        <div>
          <label className={labelCls} style={labelStyle}>Efectos probables para los titulares</label>
          <textarea
            value={form.efectos_probables ?? ''}
            onChange={e => set('efectos_probables', e.target.value || undefined)}
            rows={2}
            placeholder="Ej: Robo de identidad, fraude financiero, daño reputacional..."
            className={inputCls}
            style={{ borderColor: '#E5E7EB' }}
          />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls} style={labelStyle}>Folio notificación APDC</label>
            <input
              type="text"
              value={form.evidencia_notificacion_apdc_folio ?? ''}
              onChange={e => set('evidencia_notificacion_apdc_folio', e.target.value || undefined)}
              placeholder="Ej: APDC-2026-001234"
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            />
          </div>
          <div>
            <label className={labelCls} style={labelStyle}>Estado de cierre</label>
            <select
              value={form.estado_cierre ?? ''}
              onChange={e => set('estado_cierre', e.target.value || undefined)}
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            >
              <option value="">— No especificado —</option>
              <option value="abierta">Abierta</option>
              <option value="investigando">Investigando</option>
              <option value="contenida">Contenida</option>
              <option value="notificada">Notificada</option>
              <option value="cerrada">Cerrada</option>
            </select>
          </div>
        </div>
        {form.estado_cierre === 'cerrada' && (
          <div>
            <label className={labelCls} style={labelStyle}>Fecha de cierre</label>
            <input
              type="datetime-local"
              value={form.fecha_cierre ?? ''}
              onChange={e => set('fecha_cierre', e.target.value || undefined)}
              className={inputCls}
              style={{ borderColor: '#E5E7EB' }}
            />
          </div>
        )}
      </div>

      <div className="flex justify-between pt-2">
        <Button variant="secondary" size="lg" onClick={onCancel}>
          Cancelar
        </Button>
        <Button
          variant="danger"
          size="lg"
          onClick={() => {
            if (!form.descripcion.trim()) { toast.error('La descripción es obligatoria.'); return; }
            if (!form.fecha_deteccion) { toast.error('La fecha de detección es obligatoria.'); return; }
            if (!form.naturaleza) { toast.error('Debe seleccionar la naturaleza de la brecha.'); return; }
            onSave(form);
          }}
          loading={saving}
        >
          ✓ Guardar brecha
        </Button>
      </div>
    </div>
  );
}

export default function BreachesPage() {
  const { company, puedeEditar } = useApp();
  const [brechas, setBrechas] = useState<SecurityBreach[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'list' | 'create' | 'edit'>('list');
  const [editingBreach, setEditingBreach] = useState<SecurityBreach | null>(null);
  const [saving, setSaving] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [breachToDelete, setBreachToDelete] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  async function load() {
    if (!company) return;
    setLoading(true);
    try {
      const data = await api.listarBrechas(company.id);
      setBrechas(
        Array.isArray(data)
          ? [...data].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          : []
      );
    } catch {
      toast.error('No se pudieron cargar las brechas.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [company?.id]);

  async function handleSave(data: BreachFormData) {
    if (!data.descripcion.trim()) { toast.error('La descripcion de la brecha es obligatoria.'); return; }
    if (!data.fecha_deteccion) { toast.error('La fecha de deteccion es obligatoria.'); return; }
    setSaving(true);
    try {
      const payload = {
        descripcion: data.descripcion,
        fecha_deteccion: new Date(data.fecha_deteccion).toISOString(),
        rats_afectados: data.rats_afectados || undefined,
        datos_comprometidos: data.datos_comprometidos || undefined,
        medidas_adoptadas: data.medidas_adoptadas || undefined,
        naturaleza: data.naturaleza,
        notificado_apdc: data.notificado_apdc,
        notificado_titulares: data.notificado_titulares,
        volumen_titulares_afectados: data.volumen_titulares_afectados,
        incluye_datos_sensibles: data.incluye_datos_sensibles,
        incluye_datos_nna: data.incluye_datos_nna,
        incluye_datos_financieros: data.incluye_datos_financieros,
        // Campos nuevos gaps Ley 21.719 (Iter 10)
        fecha_ocurrencia_estimada: data.fecha_ocurrencia_estimada ? new Date(data.fecha_ocurrencia_estimada).toISOString() : undefined,
        efectos_probables: data.efectos_probables || undefined,
        causa_raiz: data.causa_raiz || undefined,
        evidencia_notificacion_apdc_folio: data.evidencia_notificacion_apdc_folio || undefined,
        estado_cierre: data.estado_cierre || undefined,
        fecha_cierre: data.fecha_cierre ? new Date(data.fecha_cierre).toISOString() : undefined,
      };
      if (editingBreach) {
        await api.actualizarBrecha(editingBreach.id, payload);
        await api.evaluarRiesgoBrecha(editingBreach.id, {
          volumen_titulares_afectados: data.volumen_titulares_afectados,
          incluye_datos_sensibles: data.incluye_datos_sensibles,
          incluye_datos_nna: data.incluye_datos_nna,
          incluye_datos_financieros: data.incluye_datos_financieros,
        });
        toast.success('Brecha actualizada.');
      } else {
        const nueva = await api.crearBrecha({ ...payload, company_id: company!.id });
        await api.evaluarRiesgoBrecha(nueva.id, {
          volumen_titulares_afectados: data.volumen_titulares_afectados,
          incluye_datos_sensibles: data.incluye_datos_sensibles,
          incluye_datos_nna: data.incluye_datos_nna,
          incluye_datos_financieros: data.incluye_datos_financieros,
        });
        toast.success('Brecha registrada y evaluada exitosamente.');
      }
      setView('list');
      setEditingBreach(null);
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await api.eliminarBrecha(id);
      toast.success('Brecha eliminada.');
      load();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar.');
    }
  }

  if (!company) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-400 text-sm">Selecciona una empresa para gestionar brechas de seguridad.</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      {view === 'list' && (
        <>
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight" style={{ color: '#111827' }}>Brechas de Seguridad</h1>
              <p className="text-sm mt-1" style={{ color: '#6B7280' }}>
                Registro de incidentes · Art. 14 sexies Ley 21.719
                {loading && <span className="ml-2 text-xs" style={{ color: '#9CA3AF' }}>cargando...</span>}
              </p>
            </div>
            {puedeEditar && (
              <Button
                variant="danger"
                onClick={() => { setEditingBreach(null); setView('create'); }}
              >
                + Registrar brecha
              </Button>
            )}
          </div>

          {loading ? (
            <div className="text-center py-16 text-sm" style={{ color: '#9CA3AF' }}>Cargando...</div>
          ) : brechas.length === 0 ? (
            <div className="text-center py-14 bg-white rounded-xl" style={{ border: '1px solid #E5E7EB' }}>
              <div className="text-3xl mb-2">🛡️</div>
              <p className="text-sm font-medium" style={{ color: '#374151' }}>Sin brechas registradas</p>
              <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
                Si ocurre un incidente de seguridad, regístralo aquí para gestionar la notificación a la APDP.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {brechas.map(b => {
                const horas = b.horas_desde_deteccion ?? 0;
                const plazoVencido = horas > PLAZO_APDC_HORAS;
                return (
                  <div
                    key={b.id}
                    className="bg-white rounded-xl p-5 shadow-sm"
                    style={{
                      border: `1px solid ${plazoVencido ? '#FCA5A5' : '#E5E7EB'}`,
                      borderLeft: `4px solid ${plazoVencido ? '#DC2626' : b.notificado_apdc ? '#059669' : '#D97706'}`,
                    }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="text-sm font-semibold" style={{ color: '#111827' }}>{b.descripcion}</div>
                        <div className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>
                          Detectada: {new Date(b.fecha_deteccion).toLocaleString('es-CL')}
                          {b.creado_por && ` · Por: ${b.creado_por}`}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <PlazoBadge hours={horas} />
                        {b.nivel_riesgo && (
                          <span
                            className="text-xs font-bold px-2 py-0.5 rounded"
                            style={{
                              background: b.nivel_riesgo === 'critico' ? '#FEE2E2' : b.nivel_riesgo === 'alto' ? '#FEF3C7' : b.nivel_riesgo === 'medio' ? '#DBEAFE' : '#D1FAE5',
                              color: b.nivel_riesgo === 'critico' ? '#991B1B' : b.nivel_riesgo === 'alto' ? '#92400E' : b.nivel_riesgo === 'medio' ? '#1E40AF' : '#065F46',
                            }}
                          >
                            {b.nivel_riesgo.toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>

                    {b.datos_comprometidos && (
                      <div className="text-xs mb-2" style={{ color: '#6B7280' }}>
                        <span className="font-semibold">Datos comprometidos: </span>{b.datos_comprometidos}
                      </div>
                    )}
                    {b.rats_afectados && (
                      <div className="text-xs mb-2" style={{ color: '#6B7280' }}>
                        <span className="font-semibold">RATs afectados: </span>{b.rats_afectados}
                      </div>
                    )}
                    {b.medidas_adoptadas && (
                      <div className="text-xs mb-3" style={{ color: '#6B7280' }}>
                        <span className="font-semibold">Medidas adoptadas: </span>{b.medidas_adoptadas}
                      </div>
                    )}

                    {/* Indicadores de notificación */}
                    <div className="flex gap-3 mb-3 flex-wrap">
                      <div className="flex items-center gap-1.5" aria-label={`APDP ${b.notificado_apdc ? 'notificada' : 'pendiente'}`}>
                        <div className="w-3 h-3 rounded-full" style={{ background: b.notificado_apdc ? '#059669' : '#D97706' }} />
                        <span className="text-xs" style={{ color: '#6B7280' }}>
                          APDP {b.notificado_apdc ? 'notificada' : 'pendiente'}
                          {b.fecha_notificacion_apdc && ` (${new Date(b.fecha_notificacion_apdc).toLocaleDateString('es-CL')})`}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5" aria-label={`Titulares ${b.notificado_titulares ? 'notificados' : 'pendiente'}`}>
                        <div className="w-3 h-3 rounded-full" style={{ background: b.notificado_titulares ? '#059669' : '#D97706' }} />
                        <span className="text-xs" style={{ color: '#6B7280' }}>
                          Titulares {b.notificado_titulares ? 'notificados' : 'pendiente'}
                        </span>
                      </div>
                    </div>

                    {/* Panel expandible — detalle legal Art. 14 sexies */}
                    <button
                      className="text-xs font-semibold mb-2 flex items-center gap-1 transition hover:underline"
                      style={{ color: '#2563EB', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                      onClick={() => setExpandedId(expandedId === b.id ? null : b.id)}
                      aria-expanded={expandedId === b.id}
                    >
                      {expandedId === b.id ? '▾ Ocultar detalle legal' : '▸ Ver detalle legal (Art. 14 sexies)'}
                    </button>

                    {expandedId === b.id && (
                      <div className="mt-2 rounded-xl overflow-hidden text-xs" style={{ border: '1px solid #DBEAFE', background: '#EFF6FF' }}>
                        <div className="px-4 py-2 font-bold" style={{ background: '#2563EB', color: 'white' }}>
                          Campos requeridos para notificación APDP — Art. 14 sexies Ley 21.719
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-0 divide-y divide-blue-200 sm:divide-y-0 sm:divide-x sm:divide-blue-200">
                          {[
                            { label: 'Naturaleza de la brecha', value: b.naturaleza ? { confidencialidad: 'Confidencialidad (acceso no autorizado)', integridad: 'Integridad (modificación no autorizada)', disponibilidad: 'Disponibilidad (datos inaccesibles)' }[b.naturaleza] ?? b.naturaleza : null },
                            { label: 'Fecha detección', value: new Date(b.fecha_deteccion).toLocaleString('es-CL') },
                            { label: 'Fecha ocurrencia estimada', value: b.fecha_ocurrencia_estimada ? new Date(b.fecha_ocurrencia_estimada).toLocaleString('es-CL') : null },
                            { label: 'Titulares afectados (estimado)', value: b.volumen_titulares_afectados != null ? b.volumen_titulares_afectados.toLocaleString('es-CL') : null },
                            { label: 'Datos comprometidos', value: b.datos_comprometidos },
                            { label: 'Tratamientos (RATs) afectados', value: b.rats_afectados },
                            { label: 'Incluye datos sensibles', value: b.incluye_datos_sensibles != null ? (b.incluye_datos_sensibles ? 'Sí' : 'No') : null },
                            { label: 'Incluye datos NNA', value: b.incluye_datos_nna != null ? (b.incluye_datos_nna ? 'Sí' : 'No') : null },
                            { label: 'Incluye datos financieros', value: b.incluye_datos_financieros != null ? (b.incluye_datos_financieros ? 'Sí' : 'No') : null },
                            { label: 'Efectos y consecuencias probables', value: b.efectos_probables },
                            { label: 'Medidas adoptadas', value: b.medidas_adoptadas },
                            { label: 'Causa raíz', value: b.causa_raiz },
                            { label: 'Notificación APDP', value: b.notificado_apdc ? `Notificada${b.fecha_notificacion_apdc ? ` el ${new Date(b.fecha_notificacion_apdc).toLocaleDateString('es-CL')}` : ''}${b.evidencia_notificacion_apdc_folio ? ` · Folio: ${b.evidencia_notificacion_apdc_folio}` : ''}` : 'Pendiente' },
                            { label: 'Notificación titulares', value: b.notificado_titulares ? `Notificados${b.fecha_notificacion_titulares ? ` el ${new Date(b.fecha_notificacion_titulares).toLocaleDateString('es-CL')}` : ''}` : 'Pendiente' },
                            { label: 'Estado de cierre', value: b.estado_cierre ?? null },
                          ].map(({ label, value }) => (
                            <div key={label} className="px-4 py-2.5" style={{ borderBottom: '1px solid #DBEAFE' }}>
                              <p className="font-semibold mb-0.5" style={{ color: '#1D4ED8' }}>{label}</p>
                              <p style={{ color: value ? '#111827' : '#9CA3AF' }}>{value ?? '— no registrado —'}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2 flex-wrap mt-3">
                      {puedeEditar && (
                        <>
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => { setEditingBreach(b); setView('edit'); }}
                          >
                            ✏️ Editar
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => { setBreachToDelete(b.id); setConfirmDeleteOpen(true); }}
                            style={{ color: '#DC2626' }}
                          >
                            🗑 Eliminar
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {(view === 'create' || view === 'edit') && (
        <div>
          <div className="flex items-center gap-3 mb-6">
            <button
              onClick={() => { setView('list'); setEditingBreach(null); }}
              className="text-sm font-medium px-4 py-2 rounded-lg border transition hover:bg-gray-50"
              style={{ color: '#6B7280', borderColor: '#E5E7EB' }}
            >
              ← Volver al listado
            </button>
            <h2 className="text-lg font-bold" style={{ color: '#111827' }}>
              {editingBreach ? 'Editar brecha' : 'Nueva brecha de seguridad'}
            </h2>
          </div>
          <BreachForm
            initial={editingBreach ? {
              descripcion: editingBreach.descripcion,
              fecha_deteccion: new Date(editingBreach.fecha_deteccion).toISOString().slice(0, 16),
              rats_afectados: editingBreach.rats_afectados ?? '',
              datos_comprometidos: editingBreach.datos_comprometidos ?? '',
              medidas_adoptadas: editingBreach.medidas_adoptadas ?? '',
              notificado_apdc: editingBreach.notificado_apdc,
              notificado_titulares: editingBreach.notificado_titulares,
              // Campos nuevos gaps Ley 21.719 (Iter 10)
              fecha_ocurrencia_estimada: editingBreach.fecha_ocurrencia_estimada ? new Date(editingBreach.fecha_ocurrencia_estimada).toISOString().slice(0, 16) : '',
              efectos_probables: editingBreach.efectos_probables ?? '',
              causa_raiz: editingBreach.causa_raiz ?? '',
              evidencia_notificacion_apdc_folio: editingBreach.evidencia_notificacion_apdc_folio ?? '',
              estado_cierre: editingBreach.estado_cierre ?? '',
              fecha_cierre: editingBreach.fecha_cierre ? new Date(editingBreach.fecha_cierre).toISOString().slice(0, 16) : '',
            } : undefined}
            onSave={handleSave}
            onCancel={() => { setView('list'); setEditingBreach(null); }}
            saving={saving}
          />
        </div>
      )}

      <ConfirmDialog
        open={confirmDeleteOpen}
        onClose={() => { setConfirmDeleteOpen(false); setBreachToDelete(null); }}
        onConfirm={() => { if (breachToDelete) handleDelete(breachToDelete); setConfirmDeleteOpen(false); setBreachToDelete(null); }}
        title="Eliminar brecha"
        message="¿Estás seguro que quieres eliminar esta brecha de seguridad? Esta acción no se puede deshacer."
        confirmText="Eliminar"
        variant="danger"
      />
    </div>
  );
}

