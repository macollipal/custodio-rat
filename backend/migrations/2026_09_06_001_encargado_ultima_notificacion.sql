-- Migración: agregar columna ultima_notificacion_at a encargados_contrato
-- Propósito: throttle de 24h para evitar email spam en _notificar_si_cerca_vencer
-- Nullable, sin valor por defecto (contratos existentes sin envíos previos quedan en NULL)

ALTER TABLE encargados_contrato
  ADD COLUMN IF NOT EXISTS ultima_notificacion_at TIMESTAMP WITH TIME ZONE;
