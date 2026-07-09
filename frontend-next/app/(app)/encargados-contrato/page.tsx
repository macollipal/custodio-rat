'use client';

import { useEffect, useState, useCallback } from 'react';
import { useApp } from '@/context/AppContext';
import { toast } from 'sonner';
import {
  listarEncargadosContrato,
  crearEncargadoContrato,
  actualizarEncargadoContrato,
  eliminarEncargadoContrato,
  listarRats,
  type EncargadoContrato,

} from '@/lib/api';
import type { RAT } from '@/types';
import Drawer from '@/components/ui/Drawer';

import { inputCls, inputStyle, labelCls, labelStyle, panelStyles, panelWrapperCls, panelTitleStyles, btnPrimaryCls, btnPrimaryStyle, btnSecondaryCls, btnSecondaryStyle, gridResponsive1to2, modalHeaderStyle, modalHeaderCls, modalContentCls, formFooterCls } from '@/lib/styles';
import { Button } from '@/components/ui/Button';

function fmtDate(val: string | null | undefined): string {
  if (!val) return '—';
  const d = new Date(val);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-CL');
}

interface FormData {
  nombre_encargado: string;
  pais: string;
  direccion: string;
  objeto: string;
  duracion_inicio: string;
  duracion_fin: string;
  finalidad: string;
  tipo_datos: string;
  categorias_titulares: string;
  derechos_obligaciones: string;
  rat_id: string;
  activo: boolean;
}

export default function EncargadosContratoPage() {
  const { company } = useApp();
  const [contratos, setContratos] = useState<EncargadoContrato[]>([]);
  const [rats, setRats] = useState<RAT[]>([]);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editItem, setEditItem] = useState<EncargadoContrato | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<FormData>({
    nombre_encargado: '', pais: '', direccion: '', objeto: '', duracion_inicio: '', duracion_fin: '',
    finalidad: '', tipo_datos: '', categorias_titulares: '', derechos_obligaciones: '',
    rat_id: '', activo: true,
  });

  const fetchData = useCallback(async () => {
    if (!company?.id) return;
    setLoading(true);
    try {
      const [data, ratsData] = await Promise.all([
        listarEncargadosContrato(company.id),
        listarRats(company.id),
      ]);
      setContratos(
        Array.isArray(data)
          ? [...data].sort((a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime())
          : []
      );
      setRats(Array.isArray(ratsData) ? ratsData : []);
    } catch {
      toast.error('Error al cargar contratos');
    } finally {
      setLoading(false);
    }
  }, [company?.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  function openNew() {
    setEditItem(null);
    setForm({
      nombre_encargado: '', pais: '', direccion: '', objeto: '', duracion_inicio: '', duracion_fin: '',
      finalidad: '', tipo_datos: '', categorias_titulares: '', derechos_obligaciones: '',
      rat_id: '', activo: true,
    });
    setDrawerOpen(true);
  }

  function openEdit(c: EncargadoContrato) {
    setEditItem(c);
    setForm({
      nombre_encargado: c.nombre_encargado,
      pais: c.pais ?? '',
      direccion: c.direccion ?? '',
      objeto: c.objeto,
      duracion_inicio: c.duracion_inicio ? c.duracion_inicio.split('T')[0] : '',
      duracion_fin: c.duracion_fin ? c.duracion_fin.split('T')[0] : '',
      finalidad: c.finalidad,
      tipo_datos: c.tipo_datos,
      categorias_titulares: c.categorias_titulares,
      derechos_obligaciones: c.derechos_obligaciones,
      rat_id: c.rat_id ? String(c.rat_id) : '',
      activo: c.activo,
    });
    setDrawerOpen(true);
  }

  async function handleSave() {
    if (!form.nombre_encargado.trim()) { toast.error('El nombre del encargado es obligatorio.'); return; }
    if (!form.pais.trim()) { toast.error('El pais del encargado es obligatorio.'); return; }
    if (!form.direccion.trim()) { toast.error('La direccion del encargado es obligatoria.'); return; }
    if (!form.objeto.trim()) { toast.error('El objeto del contrato es obligatorio.'); return; }
    if (!form.duracion_inicio) { toast.error('La fecha de inicio es obligatoria.'); return; }
    if (!form.finalidad.trim()) { toast.error('La finalidad es obligatoria.'); return; }
    if (!form.tipo_datos.trim()) { toast.error('El tipo de datos es obligatorio.'); return; }
    if (!form.categorias_titulares.trim()) { toast.error('Las categorias de titulares son obligatorias.'); return; }
    if (!form.derechos_obligaciones.trim()) { toast.error('Los derechos y obligaciones son obligatorios.'); return; }
    setSaving(true);
    try {
      const payload = {
        company_id: company!.id,
        nombre_encargado: form.nombre_encargado.trim(),
        pais: form.pais.trim(),
        direccion: form.direccion.trim(),
        objeto: form.objeto.trim(),
        duracion_inicio: new Date(form.duracion_inicio).toISOString(),
        duracion_fin: form.duracion_fin ? new Date(form.duracion_fin).toISOString() : undefined,
        finalidad: form.finalidad.trim(),
        tipo_datos: form.tipo_datos.trim(),
        categorias_titulares: form.categorias_titulares.trim(),
        derechos_obligaciones: form.derechos_obligaciones.trim(),
        rat_id: form.rat_id ? Number(form.rat_id) : undefined,
        activo: form.activo,
      };
      if (editItem) {
        await actualizarEncargadoContrato(editItem.id, payload);
        toast.success('Contrato actualizado');
      } else {
        await crearEncargadoContrato(payload as Parameters<typeof crearEncargadoContrato>[0]);
        toast.success('Contrato creado');
      }
      setDrawerOpen(false);
      fetchData();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('¿Eliminar este contrato?')) return;
    try {
      await eliminarEncargadoContrato(id);
      toast.success('Contrato eliminado');
      fetchData();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al eliminar');
    }
  }

  function set(field: keyof FormData, value: string | boolean) {
    setForm(f => ({ ...f, [field]: value }));
  }

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: '#111827' }}>Contratos de Encargado</h1>
          <p className="text-sm mt-1" style={{ color: '#6B7280' }}>Art. 14 quater — Ley 21.719</p>
        </div>
        <Button
          onClick={openNew}
          aria-label="Crear nuevo contrato de encargado"
        >
          + Nuevo Contrato
        </Button>
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 rounded-xl animate-pulse" style={{ background: '#E5E7EB' }} />
        ))}</div>
      ) : contratos.length === 0 ? (
        <div className="text-center py-12 rounded-xl" style={{ background: 'white', border: '1px solid #E5E7EB' }}>
          <p className="text-lg font-medium" style={{ color: '#9CA3AF' }}>Sin contratos de encargado</p>
          <p className="text-sm mt-1" style={{ color: '#D1D5DB' }}>Crea el primero para cumplir con el Art. 14 quater.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {contratos.map(c => (
            <div
              key={c.id}
              className="rounded-xl p-4 flex items-start gap-4"
              style={{ background: 'white', border: '1px solid #E5E7EB' }}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="font-semibold text-sm" style={{ color: '#111827' }}>{c.nombre_encargado}</p>
                  <span
                    className="px-2 py-0.5 rounded text-xs font-medium"
                    style={{ background: c.activo ? '#DCFCE7' : '#FEE2E2', color: c.activo ? '#166534' : '#991B1B' }}
                  >
                    {c.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
                <p className="text-xs mt-1" style={{ color: '#6B7280' }}>
                  {c.tipo_datos} · Inicio: {fmtDate(c.duracion_inicio)}
 {c.duracion_fin ? ` · Fin: ${fmtDate(c.duracion_fin)}` : ''}
                </p>
                <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>{c.finalidad}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm" onClick={() => openEdit(c)} aria-label={`Editar contrato ${c.nombre_encargado}`}>Editar</Button>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(c.id)} aria-label={`Eliminar contrato ${c.nombre_encargado}`} style={{ color: '#DC2626', borderColor: '#FCA5A5', borderWidth: '1px', borderStyle: 'solid' }}>Eliminar</Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Contrato de Encargado" size="md">
        <div className="space-y-4">
          <div className="rounded-xl p-4" style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}>
            <p className="font-semibold text-white text-sm">{editItem ? 'Editar Contrato' : 'Nuevo Contrato de Encargado'}</p>
            <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.7)' }}>Art. 14 quater — Ley 21.719</p>
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Nombre del Encargado *</label>
            <input value={form.nombre_encargado} onChange={e => set('nombre_encargado', e.target.value)} aria-label="Nombre del encargado" aria-required="true" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Razón social o nombre completo" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className={labelCls} style={labelStyle}>Pais *</label>
              <select value={form.pais} onChange={e => set('pais', e.target.value)} aria-label="Pais del encargado" aria-required="true" className={inputCls} style={{ borderColor: '#E5E7EB' }}>
                <option value="">Seleccionar pais</option>
                <option value="CL">Chile</option>
                <option value="AR">Argentina</option>
                <option value="BR">Brasil</option>
                <option value="CO">Colombia</option>
                <option value="ES">Espana</option>
                <option value="MX">Mexico</option>
                <option value="PE">Peru</option>
                <option value="US">Estados Unidos</option>
                <option value="OT">Otro</option>
              </select>
            </div>
            <div>
              <label className={labelCls} style={labelStyle}>Direccion *</label>
              <input value={form.direccion} onChange={e => set('direccion', e.target.value)} aria-label="Direccion del encargado" aria-required="true" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Calle, numero, ciudad" />
            </div>
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Objeto del Tratamiento *</label>
            <textarea value={form.objeto} onChange={e => set('objeto', e.target.value)} rows={3} aria-label="Objeto del tratamiento" aria-required="true" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Describe el objeto del contrato de encargo..." />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className={labelCls} style={labelStyle}>Fecha Inicio *</label>
              <input type="date" value={form.duracion_inicio} onChange={e => set('duracion_inicio', e.target.value)} aria-label="Fecha de inicio del contrato" aria-required="true" className={inputCls} style={{ borderColor: '#E5E7EB' }} />
            </div>
            <div>
              <label className={labelCls} style={labelStyle}>Fecha Fin</label>
              <input type="date" value={form.duracion_fin} onChange={e => set('duracion_fin', e.target.value)} aria-label="Fecha de fin del contrato" className={inputCls} style={{ borderColor: '#E5E7EB' }} />
            </div>
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Finalidad</label>
            <input value={form.finalidad} onChange={e => set('finalidad', e.target.value)} aria-label="Finalidad del tratamiento" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Finalidad del tratamiento" />
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Tipo de Datos</label>
            <input value={form.tipo_datos} onChange={e => set('tipo_datos', e.target.value)} aria-label="Tipo de datos tratados" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Ej: Datos identificativos, financieros..." />
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Categorías de Titulares</label>
            <input value={form.categorias_titulares} onChange={e => set('categorias_titulares', e.target.value)} aria-label="Categorias de titulares" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Ej: Trabajadores, clientes..." />
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>Derechos y Obligaciones</label>
            <textarea value={form.derechos_obligaciones} onChange={e => set('derechos_obligaciones', e.target.value)} rows={2} aria-label="Derechos y obligaciones del contrato" className={inputCls} style={{ borderColor: '#E5E7EB' }} placeholder="Derechos del responsable y obligaciones del encargado..." />
          </div>

          <div>
            <label className={labelCls} style={labelStyle}>RAT Asociado</label>
            <select value={form.rat_id} onChange={e => set('rat_id', e.target.value)} aria-label="RAT asociado al contrato" className={inputCls} style={{ borderColor: '#E5E7EB' }}>
              <option value="">Sin RAT asociado</option>
              {rats.map(r => <option key={r.id} value={r.id}>{r.nombre_proceso}</option>)}
            </select>
          </div>

          <label className="flex items-center gap-2 text-sm" style={{ color: '#374151' }}>
            <input type="checkbox" checked={form.activo} onChange={e => set('activo', e.target.checked)} aria-label="Contrato activo" />
            Contrato activo
          </label>

          <div className="flex gap-3 pt-2">
            <Button variant="secondary" size="md" className="flex-1" onClick={() => setDrawerOpen(false)} aria-label="Cancelar creacion de contrato">Cancelar</Button>
            <Button size="md" className="flex-1" onClick={handleSave} disabled={saving} loading={saving} aria-label="Guardar contrato de encargado">
              Guardar
            </Button>
          </div>
        </div>
      </Drawer>
    </div>
  );
}

