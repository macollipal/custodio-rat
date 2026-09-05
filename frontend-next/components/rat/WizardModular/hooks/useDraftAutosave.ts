'use client';

import { useEffect, useRef } from 'react';
import { RATWizardData } from '@/types';
import { DRAFT_KEY } from '../types';

/**
 * Auto-save RAT wizard draft to localStorage every 30 seconds.
 * Pure side-effect: persists data, never returns.
 */
export function useDraftAutosave(
  companyId: number,
  data: RATWizardData,
  enabled: boolean = true,
): void {
  const lastSaved = useRef<string>('');

  useEffect(() => {
    if (!enabled) return;
    const key = DRAFT_KEY(companyId);
    const interval = setInterval(() => {
      const serialized = JSON.stringify(data);
      if (serialized === lastSaved.current) return;
      const snap = { data, savedAt: Date.now() };
      try {
        localStorage.setItem(key, JSON.stringify(snap));
        lastSaved.current = serialized;
      } catch {
        // quota exceeded — silently ignore
      }
    }, 30_000);
    return () => clearInterval(interval);
  }, [companyId, data, enabled]);
}