'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import Drawer from '@/components/ui/Drawer';
import { FieldLabel } from './FieldLabel';
import { SectionHeader } from './SectionHeader';
import { TooltipIcon } from './TooltipIcon';
import { validarRUT } from '@/components/ui/validation';
import { crearTktTicket, listarRats, checkDuplicadoTkt, type TktTicket } from '@/lib/api';
import type { RAT } from '@/types';

const ARTICULOS: Record<string, string> = {
  acceso: 'Art. 12 — El titular puede solicitar información sobre sus datos tratados.',
  rectificacion: 'Art. 12 — El titular puede solicitar corrección de datos inexactos.',
  cancelacion: 'Art. 12 — El titular puede solicitar eliminación de sus datos.',
  oposicion: 'Art. 12 — El titular puede oponerse al tratamiento de sus datos.',
  bloqueo: 'Art. 12 bis — Suspensión temporal del tratamiento.',
  portabilidad: 'Art. 12 ter — El titular puede recibir sus datos en formato estructurado.',
};

const PLAZOS: Record<string, string> = {
  urgente: '2 días hábiles (Art. 14 bis)',
  normal: '10 días hábiles (plazo legal)',
  baja: 'Sin urgencia. Máximo plazo legal.',
};

interface CreateTicketFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  companyId: number;
  isAdmin: boolean;
}

function sanitize(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#039;');
}

export function CreateTicketForm({ open, onClose, onSuccess, companyId }: CreateTicketFormProps) {
  const [tipo, setTipo] = useState('acceso');
  const [prioridad, setPrioridad] = useState('normal');
  const [origen, setOrigen] = useState('web');
  const [titularNombre, setTitularNombre] = useState('');
  const [titularEmail, setTitularEmail] = useState('');
  const [confirmarEmail, setConfirmarEmail] = useState('');
  const [titularRut, setTitularRut] = useState('');
  const [rutError, setRutError] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [guardando, setGuardando] = useState(false);
  const [telefono, setTelefono] = useState('');
  const [fechaNacimiento, setFechaNacimiento] = useState('');
  const [pais, setPais] = useState('');
  const [reprNombre, setReprNombre] = useState('');
  const [reprRut, setReprRut] = useState('');
  const [reprCollapsed, setReprCollapsed] = useState(true);
  const [ratId, setRatId] = useState<number | undefined>(undefined);
  const [ratSearch, setRatSearch] = useState('');
  const [rats, setRats] = useState<{ id: number; nombre_proceso: string }[]>([]);
  const [ratsOpen, setRatsOpen] = useState(false);
  const [duplicateWarning, setDuplicateWarning] = useState('');
  const [showDuplicados, setShowDuplicados] = useState(false);
  const [duplicados, setDuplicados] = useState<TktTicket[]>([]);

  useEffect(() => {
    if (open) {
      setTipo('acceso');
      setPrioridad('normal');
      setOrigen('web');
      setTitularNombre('');
      setTitularEmail('');
      setConfirmarEmail('');
      setTitularRut('');
      setRutError('');
      setDescripcion('');
      setTelefono('');
      setFechaNacimiento('');
      setPais('');
      setReprNombre('');
      setReprRut('');
      setRatId(undefined);
      setRatSearch('');
      setDuplicateWarning('');
      setShowDuplicados(false);
      setDuplicados([]);
      setReprCollapsed(true);
    }
  }, [open]);

  useEffect(() => {
    if (!ratSearch.trim()) { setRats([]); return; }
    const timer = setTimeout(async () => {
      try {
        const allRats = await listarRats(companyId);
        const filtered = allRats.filter((r: RAT) =>
          r.nombre_proceso.toLowerCase().includes(ratSearch.toLowerCase())
        );
        setRats(filtered.slice(0, 10).map((r: RAT) => ({ id: r.id, nombre_proceso: r.nombre_proceso })));
      } catch { /* ignore */ }
    }, 300);
    return () => clearTimeout(timer);
  }, [ratSearch, companyId]);

  useEffect(() => {
    if (!titularEmail || !tipo) return;
    const timer = setTimeout(async () => {
      try {
        const result = await checkDuplicadoTkt(titularEmail, tipo, companyId);
        if (result.es_duplicado) {
          setDuplicateWarning(`⚠️ Posible solicitud duplicada (${result.cantidad} en los últimos 90 días)`);
          setDuplicados(result.solicitudes);
        } else {
          setDuplicateWarning('');
          setDuplicados([]);
        }
      } catch { /* ignore */ }
    }, 800);
    return () => clearTimeout(timer);
  }, [titularEmail, tipo, companyId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!titularNombre.trim() || !titularEmail.trim()) {
      toast.error('Nombre y email del titular son obligatorios');
      return;
    }
    const emailValid = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/.test(titularEmail.trim());
    if (!emailValid) { toast.error('El email del titular no es valido.'); return; }
    if (confirmarEmail && titularEmail !== confirmarEmail) {
      toast.error('Los emails no coinciden');
      return;
    }
    if (titularRut && rutError) {
      toast.error('El RUT no es valido');
      return;
    }
    setGuardando(true);
    try {
      await crearTktTicket({
        company_id: companyId,
        tipo,
        prioridad,
        origen,
        titular_nombre: sanitize(titularNombre),
        titular_email: sanitize(titularEmail),
        titular_rut: titularRut ? sanitize(titularRut) : undefined,
        descripcion: descripcion ? sanitize(descripcion) : undefined,
        rat_id: ratId,
        representante_nombre: reprNombre ? sanitize(reprNombre) : undefined,
        representante_rut: reprRut ? sanitize(reprRut) : undefined,
        telefono: telefono ? sanitize(telefono) : undefined,
        fecha_nacimiento: fechaNacimiento || undefined,
        pais: pais || undefined,
      });
      toast.success('Solicitud creada');
      onSuccess();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Error al crear solicitud');
    } finally {
      setGuardando(false);
    }
  }

  if (!open) return null;

  return (
    <Drawer open={open} onClose={onClose} title="" size="lg">
      <form onSubmit={handleSubmit} className="space-y-0">
        <div
          className="rounded-xl p-4 flex items-center gap-3 mb-5"
          style={{ background: 'linear-gradient(135deg, #1E40AF, #3730A3)' }}
        >
          <span
            className="inline-flex items-center justify-center w-10 h-10 rounded-lg font-bold text-sm flex-shrink-0"
            style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
          >
            + NUEVA
          </span>
          <div>
            <p className="font-semibold text-white text-sm">Nueva Solicitud ARCO</p>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.7)' }}>Complete los datos del titular</p>
          </div>
        </div>

        {duplicateWarning && (
          <div className="mb-5 rounded-lg p-3 text-sm" style={{ background: '#FEF9C3', border: '1px solid #EAB308' }}>
            <p className="font-medium" style={{ color: '#854D0E' }}>{duplicateWarning}</p>
            {showDuplicados && duplicados.length > 0 && (
              <div className="mt-2">
                {duplicados.map(d => (
                  <div key={d.id} className="text-xs mt-1" style={{ color: '#854D0E' }}>
                    #{d.id} — {d.tipo} — {d.estado} — {new Date(d.fecha_recepcion || '').toLocaleDateString('es-CL')}
                  </div>
                ))}
                <button type="button" onClick={() => setShowDuplicados(false)} className="text-xs mt-1 underline" style={{ color: '#854D0E' }}>Ocultar</button>
              </div>
            )}
            {!showDuplicados && duplicados.length > 0 && (
              <button type="button" onClick={() => setShowDuplicados(true)} className="text-xs mt-1 underline" style={{ color: '#854D0E' }}>Ver detalle</button>
            )}
          </div>
        )}

        <SectionHeader label="Clasificación" />

        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <div className="flex items-center mb-1">
              <FieldLabel htmlFor="tipo-select" label="Tipo" required />
              <TooltipIcon text={ARTICULOS[tipo]} />
            </div>
            <select
              id="tipo-select"
              value={tipo}
              onChange={e => setTipo(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              aria-label="Tipo de solicitud ARCO"
              aria-required="true"
            >
              <option value="acceso">Acceso</option>
              <option value="rectificacion">Rectificación</option>
              <option value="cancelacion">Cancelación</option>
              <option value="oposicion">Oposición</option>
              <option value="bloqueo">Bloqueo temporal</option>
              <option value="portabilidad">Portabilidad</option>
            </select>
          </div>
          <div>
            <div className="flex items-center mb-1">
              <FieldLabel htmlFor="prioridad-select" label="Prioridad" />
              <TooltipIcon text={`Plazo según prioridad: ${PLAZOS[prioridad]}`} />
            </div>
            <select
              id="prioridad-select"
              value={prioridad}
              onChange={e => setPrioridad(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              aria-label="Prioridad de la solicitud"
            >
              <option value="urgente">Urgente</option>
              <option value="normal">Normal</option>
              <option value="baja">Baja</option>
            </select>
          </div>
        </div>

        <SectionHeader label="Datos del titular" />

        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <FieldLabel htmlFor="nombre-titular" label="Nombre completo" required />
            <input
              id="nombre-titular"
              type="text"
              value={titularNombre}
              onChange={e => setTitularNombre(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              placeholder="Nombre completo"
              aria-label="Nombre del titular"
              aria-required="true"
            />
          </div>
          <div>
            <FieldLabel htmlFor="rut-titular" label="RUT del titular" />
            <input
              id="rut-titular"
              type="text"
              value={titularRut}
              onChange={e => {
                const formatted = e.target.value.toUpperCase().replace(/[^0-9K\-]/g, '').replace(/^(\d{1,2})(\d{3})(\d{3})([\dkK])$/, '$1.$2.$3-$4').replace(/--/g, '-');
                setTitularRut(formatted);
                if (formatted) {
                  const { valido, mensaje } = validarRUT(formatted);
                  setRutError(valido ? '' : mensaje);
                } else { setRutError(''); }
              }}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: rutError ? '#DC2626' : '#E5E7EB' }}
              placeholder="12.345.678-9"
              aria-label="RUT del titular"
            />
            {rutError && <p className="text-xs mt-1" style={{ color: '#DC2626' }}>{rutError}</p>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <FieldLabel htmlFor="email-titular" label="Email" required />
            <input
              id="email-titular"
              type="email"
              value={titularEmail}
              onChange={e => setTitularEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              placeholder="email@ejemplo.cl"
              aria-label="Email del titular"
              aria-required="true"
            />
          </div>
          <div>
            <FieldLabel htmlFor="email-confirmar" label="Confirmar email" />
            <input
              id="email-confirmar"
              type="email"
              value={confirmarEmail}
              onChange={e => setConfirmarEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: confirmarEmail && titularEmail !== confirmarEmail ? '#DC2626' : '#E5E7EB' }}
              placeholder="Repita el email"
              aria-label="Confirmar email del titular"
            />
            {confirmarEmail && titularEmail !== confirmarEmail && (
              <p className="text-xs mt-1" style={{ color: '#DC2626' }}>Los emails no coinciden</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-5">
          <div>
            <FieldLabel htmlFor="telefono-titular" label="Teléfono" />
            <input
              id="telefono-titular"
              type="tel"
              value={telefono}
              onChange={e => setTelefono(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              placeholder="+56 9 1234 5678"
              aria-label="Teléfono del titular"
            />
          </div>
          <div>
            <FieldLabel htmlFor="pais-titular" label="País" />
            <input
              id="pais-titular"
              type="text"
              value={pais}
              onChange={e => setPais(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              placeholder="Chile"
              aria-label="País del titular"
            />
          </div>
          <div>
            <FieldLabel htmlFor="fecha-nac-titular" label="Fecha nacimiento" />
            <input
              id="fecha-nac-titular"
              type="date"
              value={fechaNacimiento}
              onChange={e => setFechaNacimiento(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              aria-label="Fecha de nacimiento del titular"
            />
          </div>
        </div>

        <SectionHeader label="Contexto" />

        <div className="mb-5">
          <FieldLabel htmlFor="rat-search" label="RAT asociado" />
          <div className="relative">
            <input
              id="rat-search"
              type="text"
              value={ratSearch}
              onChange={e => { setRatSearch(e.target.value); setRatsOpen(true); }}
              onFocus={() => setRatsOpen(true)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              placeholder="Buscar RAT..."
              aria-label="Buscar RAT asociado"
            />
            {ratsOpen && rats.length > 0 && (
              <div className="absolute z-10 w-full mt-1 border rounded-lg shadow-lg" style={{ background: 'white', borderColor: '#E5E7EB' }}>
                {rats.map(r => (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => { setRatId(r.id); setRatSearch(r.nombre_proceso); setRatsOpen(false); }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition"
                  >
                    {r.nombre_proceso}
                  </button>
                ))}
              </div>
            )}
            {ratId && (
              <button
                type="button"
                onClick={() => { setRatId(undefined); setRatSearch(''); }}
                className="text-xs mt-1"
                style={{ color: '#2563EB' }}
              >
                ✕ Quitar RAT
              </button>
            )}
          </div>
        </div>

        <SectionHeader label="Representante legal" />

        <div className="mb-5">
          <button
            type="button"
            onClick={() => setReprCollapsed(!reprCollapsed)}
            className="flex items-center gap-2 text-xs font-medium mb-3 transition-colors"
            style={{ color: '#2563EB' }}
          >
            <span className="text-[10px]">{reprCollapsed ? '▶' : '▼'}</span>
            {reprCollapsed ? 'Agregar datos de representante' : 'Ocultar datos de representante'}
          </button>
          {!reprCollapsed && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <FieldLabel htmlFor="repr-nombre" label="Nombre representante" />
                <input
                  id="repr-nombre"
                  type="text"
                  value={reprNombre}
                  onChange={e => setReprNombre(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm border"
                  style={{ borderColor: '#E5E7EB' }}
                  placeholder="Nombre del representante legal"
                  aria-label="Nombre del representante"
                />
              </div>
              <div>
                <FieldLabel htmlFor="repr-rut" label="RUT representante" />
                <input
                  id="repr-rut"
                  type="text"
                  value={reprRut}
                  onChange={e => setReprRut(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-sm border"
                  style={{ borderColor: '#E5E7EB' }}
                  placeholder="RUT del representante"
                  aria-label="RUT del representante"
                />
              </div>
            </div>
          )}
        </div>

        <SectionHeader label="Detalle" />

        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <FieldLabel htmlFor="origen-select" label="Origen" />
            <select
              id="origen-select"
              value={origen}
              onChange={e => setOrigen(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              aria-label="Origen de la solicitud"
            >
              <option value="web">Web</option>
              <option value="email">Email</option>
              <option value="telefono">Teléfono</option>
              <option value="presencial">Presencial</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div>
            <FieldLabel htmlFor="descripcion-input" label="Descripción" />
            <textarea
              id="descripcion-input"
              value={descripcion}
              onChange={e => setDescripcion(e.target.value)}
              className="w-full px-3 py-2 rounded-lg text-sm border"
              style={{ borderColor: '#E5E7EB' }}
              rows={3}
              placeholder="Detalle de la solicitud..."
              aria-label="Descripción de la solicitud"
            />
          </div>
        </div>

        <div className="flex gap-3 pt-3" style={{ borderTop: '1px solid #E5E7EB' }}>
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium border transition hover:bg-gray-50"
            style={{ borderColor: '#E5E7EB', color: '#374151' }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={guardando}
            className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium text-white transition"
            style={{ background: '#2563EB' }}
          >
            {guardando ? 'Guardando...' : 'Crear Solicitud'}
          </button>
        </div>
      </form>
    </Drawer>
  );
}
