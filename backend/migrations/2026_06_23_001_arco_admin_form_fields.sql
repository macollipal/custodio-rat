-- Migration: Agregar campos adicionales a tkt_solicitud_derecho para formulario admin mejorado
-- Fecha: 2026-06-23
-- Autor: opencode (Sprint 1 - FORMADMIN QW1-QW8)

BEGIN;

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS telefono VARCHAR(50),
ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE,
ADD COLUMN IF NOT EXISTS pais VARCHAR(100);

-- Comentario para documentación
COMMENT ON COLUMN tkt_solicitud_derecho.telefono IS 'Teléfono de contacto del titular para gestión de solicitud ARCO';
COMMENT ON COLUMN tkt_solicitud_derecho.fecha_nacimiento IS 'Fecha de nacimiento del titular para verificación de identidad';
COMMENT ON COLUMN tkt_solicitud_derecho.pais IS 'País de residencia del titular';

COMMIT;
