-- ============================================================
-- CUSTODIO RAT MANAGER - Migración PROD MVP → v1.3
-- Fecha: 2026-06-11
-- ============================================================

BEGIN;

-- ============================================================
-- PARTE 1: SECUENCIAS PARA TABLAS NUEVAS
-- ============================================================

CREATE SEQUENCE IF NOT EXISTS encargados_contrato_id_seq;
CREATE SEQUENCE IF NOT EXISTS feriados_id_seq;
CREATE SEQUENCE IF NOT EXISTS politicas_transparencia_id_seq;
CREATE SEQUENCE IF NOT EXISTS task_queue_id_seq;

-- ============================================================
-- PARTE 2: TABLAS NUEVAS
-- ============================================================

-- 2.1 ENCARGADOS CONTRATO (Art. 14 quater)
CREATE TABLE encargados_contrato (
    id integer NOT NULL DEFAULT nextval('encargados_contrato_id_seq'::regclass),
    company_id integer NOT NULL,
    rat_id integer,
    nombre_encargado character varying NOT NULL,
    objeto text NOT NULL,
    duracion_inicio timestamp with time zone NOT NULL,
    duracion_fin timestamp with time zone,
    finalidad text NOT NULL,
    tipo_datos text NOT NULL,
    categorias_titulares text NOT NULL,
    derechos_obligaciones text NOT NULL,
    archivo_pdf_datos bytea,
    archivo_pdf_nombre character varying,
    archivo_pdf_tipo character varying,
    archivo_hash character varying,
    activo boolean NOT NULL DEFAULT true,
    fecha_alerta_vencimiento timestamp with time zone,
    created_by character varying,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

ALTER TABLE encargados_contrato ADD CONSTRAINT encargados_contrato_company_id_fkey
    FOREIGN KEY (company_id) REFERENCES companies(id);
ALTER TABLE encargados_contrato ADD CONSTRAINT encargados_contrato_rat_id_fkey
    FOREIGN KEY (rat_id) REFERENCES rats(id);

-- 2.2 FERIADOS
CREATE TABLE feriados (
    id integer NOT NULL DEFAULT nextval('feriados_id_seq'::regclass),
    anio integer NOT NULL,
    mes integer NOT NULL,
    dia integer NOT NULL,
    nombre character varying NOT NULL,
    tipo character varying NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

-- 2.3 POLITICAS TRANSPARENCIA (Art. 14 ter)
CREATE TABLE politicas_transparencia (
    id integer NOT NULL DEFAULT nextval('politicas_transparencia_id_seq'::regclass),
    company_id integer NOT NULL,
    version character varying NOT NULL,
    fecha_generacion timestamp with time zone NOT NULL,
    hash_sha256 character varying,
    generado_por character varying,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

ALTER TABLE politicas_transparencia ADD CONSTRAINT politicas_transparencia_company_id_fkey
    FOREIGN KEY (company_id) REFERENCES companies(id);

-- 2.4 TASK QUEUE
DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('pending', 'running', 'done', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE task_queue (
    id integer NOT NULL DEFAULT nextval('task_queue_id_seq'::regclass),
    task_type character varying NOT NULL,
    status task_status NOT NULL DEFAULT 'pending',
    payload text,
    attempts integer NOT NULL DEFAULT 0,
    max_attempts integer NOT NULL DEFAULT 3,
    last_error text,
    scheduled_for timestamp with time zone NOT NULL DEFAULT now(),
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- PARTE 3: COLUMNAS NUEVAS EN TABLAS EXISTENTES
-- ============================================================

-- 3.1 audit_logs: Hash chain SHA256
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS prev_hash character varying NOT NULL DEFAULT '0000000000000000000000000000000000000000000000000000000000000000';
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS hash character varying NOT NULL DEFAULT '0000000000000000000000000000000000000000000000000000000000000000';

-- 3.2 rats: Flag de bloqueo
ALTER TABLE rats ADD COLUMN IF NOT EXISTS bloqueado boolean NOT NULL DEFAULT false;

-- 3.3 security_breaches: Campos calculados
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS volumen_titulares_afectados integer NOT NULL DEFAULT 0;
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS reportable_apdc_calculado boolean NOT NULL DEFAULT false;
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS incluye_datos_nna boolean NOT NULL DEFAULT false;
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS incluye_datos_financieros boolean NOT NULL DEFAULT false;
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS incluye_datos_sensibles boolean NOT NULL DEFAULT false;
ALTER TABLE security_breaches ADD COLUMN IF NOT EXISTS nivel_riesgo character varying NOT NULL DEFAULT 'bajo';

-- 3.4 solicitudes_derecho: Plazo y vínculo RAT
ALTER TABLE solicitudes_derecho ADD COLUMN IF NOT EXISTS plazo_bloqueo_vencimiento timestamp with time zone;
ALTER TABLE solicitudes_derecho ADD COLUMN IF NOT EXISTS rat_id integer;
ALTER TABLE solicitudes_derecho ADD CONSTRAINT solicitudes_derecho_rat_id_fkey
    FOREIGN KEY (rat_id) REFERENCES rats(id);

-- 3.5 tkt_solicitud_derecho: Timestamps y estado
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS prioridad character varying NOT NULL DEFAULT 'normal';
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS created_at timestamp without time zone DEFAULT now();
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS updated_at timestamp without time zone DEFAULT now();
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS estado character varying DEFAULT 'abierto';
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS fecha_recepcion timestamp without time zone NOT NULL DEFAULT now();
ALTER TABLE tkt_solicitud_derecho ADD COLUMN IF NOT EXISTS origen character varying NOT NULL DEFAULT 'web';

-- 3.6 tkt_notas
ALTER TABLE tkt_notas ADD COLUMN IF NOT EXISTS created_at timestamp without time zone DEFAULT now();

-- 3.7 tkt_adjuntos
ALTER TABLE tkt_adjuntos ADD COLUMN IF NOT EXISTS created_at timestamp without time zone DEFAULT now();

-- 3.8 tkt_historial
ALTER TABLE tkt_historial ADD COLUMN IF NOT EXISTS created_at timestamp without time zone DEFAULT now();

COMMIT;

-- ============================================================
-- VERIFICACION POST-MIGRACION
-- ============================================================
SELECT 'Tablas totales despues de migracion:' as info, count(*) as total
FROM information_schema.tables WHERE table_schema = 'public';

SELECT 'Verificacion de tablas nuevas:' as info;
SELECT 'encargados_contrato' as tabla, EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'encargados_contrato') as existe
UNION ALL SELECT 'feriados', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'feriados')
UNION ALL SELECT 'politicas_transparencia', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'politicas_transparencia')
UNION ALL SELECT 'task_queue', EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'task_queue');