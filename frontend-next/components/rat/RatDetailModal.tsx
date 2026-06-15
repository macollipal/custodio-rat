'use client';

import { useState, useEffect, useReducer } from 'react';
import Drawer from '@/components/ui/Drawer';
import RatDetailView from './RatDetailView';
import RatEditForm from './RatEditForm';
import * as api from '@/lib/api';
import type { RAT } from '@/types';

interface AuditLog { accion: string; usuario: string; timestamp: string; }

interface RatDetailModalProps {
  rat: RAT | null;
  mode: 'view' | 'edit';
  onClose: () => void;
  onSwitchToEdit: () => void;
  onDuplicate: (rat: RAT) => void;
  onDelete: (id: number) => void;
  onRefresh: () => void;
  puedeEditar: boolean;
}

type AuditAction = { type: 'SET'; logs: AuditLog[] } | { type: 'CLEAR' };

function auditReducer(_: AuditLog[], action: AuditAction): AuditLog[] {
  if (action.type === 'SET') return action.logs;
  return [];
}

export default function RatDetailModal({
  rat,
  mode,
  onClose,
  onSwitchToEdit,
  onDuplicate,
  onDelete,
  onRefresh,
  puedeEditar,
}: RatDetailModalProps) {
  const [currentMode, setCurrentMode] = useState<'view' | 'edit'>(mode);
  const [auditLogs, auditDispatch] = useReducer(auditReducer, []);

  useEffect(() => { setCurrentMode(mode); }, [mode]);

  useEffect(() => {
    if (!rat) {
      auditDispatch({ type: 'CLEAR' });
      return;
    }
    let cancelled = false;
    api.getAuditoria(rat.id)
      .then(logs => { if (!cancelled) auditDispatch({ type: 'SET', logs }); })
      .catch(() => { if (!cancelled) auditDispatch({ type: 'CLEAR' }); });
    return () => { cancelled = true; };
  }, [rat?.id]);

  function handleClose() {
    setCurrentMode('view');
    onClose();
  }

  function handleSwitchToEdit() {
    setCurrentMode('edit');
    onSwitchToEdit();
  }

  async function handleFormSaved() {
    setCurrentMode('view');
    await onRefresh();
  }

  function handleCancel() {
    setCurrentMode('view');
  }

  if (!rat) return null;

  const tabsCls = 'px-4 py-2 text-sm font-medium rounded-lg transition';
  const activeTabCls = tabsCls + ' text-white';
  const inactiveTabCls = tabsCls + ' text-gray-500 hover:text-gray-700';

  return (
    <Drawer
      open={!!rat}
      onClose={handleClose}
      title={`RAT #${rat.id} — ${rat.nombre_proceso}`}
      extraAction={
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentMode('view')}
            className={currentMode === 'view' ? activeTabCls : inactiveTabCls}
            style={currentMode === 'view' ? { background: '#2563EB' } : {}}
          >
            Ver
          </button>
          {puedeEditar && (
            <button
              onClick={handleSwitchToEdit}
              className={currentMode === 'edit' ? activeTabCls : inactiveTabCls}
              style={currentMode === 'edit' ? { background: '#2563EB' } : {}}
            >
              Editar
            </button>
          )}
        </div>
      }
    >
      <div>
        <div
          className="px-4 py-3 rounded-xl mb-4"
          style={{ background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)' }}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-medium mb-0.5" style={{ color: 'rgba(255,255,255,0.7)' }}>
                RAT #{rat.id}
              </p>
              <h2 className="text-base font-bold text-white leading-tight">
                {rat.nombre_proceso}
              </h2>
            </div>
            <span
              className="px-2 py-0.5 rounded-full text-xs font-semibold flex-shrink-0 mt-0.5"
              style={{
                background: 'rgba(255,255,255,0.2)',
                color: 'white',
              }}
            >
              {rat.estado === 'borrador' ? 'Borrador' :
               rat.estado === 'completo' ? 'Completo' :
               rat.estado === 'en_revision' ? 'En revisión' : 'Aprobado'}
            </span>
          </div>
        </div>

        {currentMode === 'view' ? (
          <RatDetailView
            rat={rat}
            puedeEditar={puedeEditar}
            onEdit={handleSwitchToEdit}
            onDuplicate={onDuplicate}
            onDelete={onDelete}
            onRefresh={onRefresh}
            auditLogs={auditLogs}
          />
        ) : (
          <RatEditForm
            rat={rat}
            onDone={handleFormSaved}
            onCancel={handleCancel}
          />
        )}
      </div>
    </Drawer>
  );
}
