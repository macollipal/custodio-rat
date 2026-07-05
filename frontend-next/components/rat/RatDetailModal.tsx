'use client';

import { useEffect, useReducer } from 'react';
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
type ModeAction = { type: 'SET_MODE'; mode: 'view' | 'edit' } | { type: 'RESET' };

function auditReducer(_: AuditLog[], action: AuditAction): AuditLog[] {
  if (action.type === 'SET') return action.logs;
  return [];
}

function modeReducer(_: 'view' | 'edit', action: ModeAction): 'view' | 'edit' {
  switch (action.type) {
    case 'SET_MODE': return action.mode;
    case 'RESET': return 'view';
  }
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
  const [currentMode, modeDispatch] = useReducer(modeReducer, mode);
  const [auditLogs, auditDispatch] = useReducer(auditReducer, []);

  useEffect(() => { modeDispatch({ type: 'SET_MODE', mode }); }, [mode]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rat?.id]);

  function handleClose() {
    modeDispatch({ type: 'RESET' });
    onClose();
  }

  function handleSwitchToEdit() {
    modeDispatch({ type: 'SET_MODE', mode: 'edit' });
    onSwitchToEdit();
  }

  async function handleFormSaved() {
    modeDispatch({ type: 'SET_MODE', mode: 'view' });
    await onRefresh();
  }

  function handleCancel() {
    modeDispatch({ type: 'SET_MODE', mode: 'view' });
  }

  if (!rat) return null;

  const tabsCls = 'px-3 py-1.5 text-xs font-semibold rounded-lg transition';
  const activeTabCls = tabsCls + ' text-white';
  const inactiveTabCls = tabsCls + ' text-white/60 hover:text-white';

  return (
    <Drawer
      open={!!rat}
      onClose={handleClose}
      title="RAT"
      size="lg"
    >
      <div>
        <div
          className="rounded-2xl p-5 mb-4"
          style={{ background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)' }}
        >
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold flex-shrink-0"
                style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
              >
                #{rat.id}
              </div>
              <div>
                <p className="text-xs font-medium mb-0.5" style={{ color: 'rgba(255,255,255,0.6)' }}>
                  RAT · {rat.estado === 'borrador' ? 'Borrador' : rat.estado === 'completo' ? 'Completo' : rat.estado === 'en_revision' ? 'En revisión' : 'Aprobado'}
                </p>
                <h2 className="text-base font-bold text-white leading-tight">
                  {rat.nombre_proceso}
                </h2>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              {rat.completitud > 0 && (
                <div
                  className="flex items-center gap-1.5"
                  role="progressbar"
                  aria-valuenow={rat.completitud}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Completitud del RAT: ${rat.completitud}%`}
                >
                  <span className="text-xs font-semibold tabular-nums" style={{ color: 'rgba(255,255,255,0.9)' }}>
                    {rat.completitud}%
                  </span>
                  <div className="w-16 sm:w-20 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.2)' }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${rat.completitud}%`, background: rat.completitud >= 80 ? '#34D399' : rat.completitud >= 50 ? '#FBBF24' : '#F87171' }}
                    />
                  </div>
                </div>
              )}
              <span
                role="status"
                aria-label={`Estado del RAT: ${rat.estado}`}
                className="px-2.5 py-1 rounded-lg text-xs font-bold"
                style={{ background: 'rgba(255,255,255,0.2)', color: 'white' }}
              >
                {rat.estado === 'borrador' ? 'Borrador' : rat.estado === 'completo' ? 'Completo' : rat.estado === 'en_revision' ? 'En revisión' : 'Aprobado'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => modeDispatch({ type: 'SET_MODE', mode: 'view' })}
              className={currentMode === 'view' ? activeTabCls : inactiveTabCls}
            >
              Ver
            </button>
            {puedeEditar && (
              <button
                onClick={handleSwitchToEdit}
                className={currentMode === 'edit' ? activeTabCls : inactiveTabCls}
              >
                Editar
              </button>
            )}
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
