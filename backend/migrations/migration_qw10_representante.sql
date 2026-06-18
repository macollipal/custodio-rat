-- QW10: Agregar representante_nombre y representante_rut a tkt_solicitud_derecho
-- Scope: Formulario público mejorado — campos de representante legal

ALTER TABLE tkt_solicitud_derecho
ADD COLUMN IF NOT EXISTS representante_nombre VARCHAR(255),
ADD COLUMN IF NOT EXISTS representante_rut VARCHAR(20);
