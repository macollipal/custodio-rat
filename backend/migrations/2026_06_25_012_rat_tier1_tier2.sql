-- Migration: 2026_06_25_012_rat_tier1_tier2.sql
-- Descripcion: Agrega 15 campos nuevos al modelo RAT para cerrar gaps criticos y operativos de compliance con Ley 21.719
-- Iteracion: Iter 11 - Gaps Tier 1 (criticos) + Tier 2 (operativos) - Analisis ProBest
-- Tier 1: datos_nna, nivel_confidencialidad, estructura_dato, datos_anonimizados, datos_seudonimizados
-- Tier 2: ciclo_procesamiento, automatizacion, frecuencia, transferencia_nacional, doc_clausulas, medidas_organizativas, mecanismos_eliminacion, tecnica_anonimizacion, origen_dato_portabilidad, fecha_levantamiento

BEGIN;

-- ============================================================
-- TIER 1: GAPS CRITICOS (Camposminimos Ley 21.719 / ProBest)
-- ============================================================

-- Tratamiento de datos de Ninos, Ninas y Adolescentes (NNA)
-- Valor: ninguno | ninos (<14) | adolescentes (14-17) | ambos
-- Relevancia: Art. 12 y 17 Ley 21.719 - proteccion reforzada para menores
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_nna VARCHAR(50);
COMMENT ON COLUMN rats.datos_nna IS 'Tratamiento de NNA: ninguno, ninos (<14), adolescentes (14-17), ambos - Ley 21.719 Art. 12 y 17';

-- Nivel de confidencialidad del dato segun metodologia DC (Datos Confidenciales)
-- DC0: Publico / DC1: Uso Interno / DC2: Uso Restringido / DC3: Confidencial
-- Relevancia: Art. 26 Ley 21.719 - proporcionalidad en el tratamiento
ALTER TABLE rats ADD COLUMN IF NOT EXISTS nivel_confidencialidad VARCHAR(20);
COMMENT ON COLUMN rats.nivel_confidencialidad IS 'Clasificacion DC0-DC3 - DC0: Publico, DC1: Uso Interno, DC2: Uso Restringido, DC3: Confidencial - Ley 21.719 Art. 26';

-- Forma en que esta estructurada la informacion del tratamiento
-- Relevancia: Determinacion del tipo de datos (estructurado, semi, no estructurado, fisico)
ALTER TABLE rats ADD COLUMN IF NOT EXISTS estructura_dato VARCHAR(50);
COMMENT ON COLUMN rats.estructura_dato IS 'Forma de estructuracion del dato: estructurado, semiestructurado, no_estructurado, fisico - Relevante para portabilidad y gestion';

-- Indica si los datos han pasado por un proceso irreversible de anonimizacion
-- Relevancia: Art. 2 Ley 21.719 - datos anonimos no estan sujetos a la ley
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_anonimizados BOOLEAN DEFAULT FALSE;
COMMENT ON COLUMN rats.datos_anonimizados IS 'Datos pasaron por proceso irreversible de anonimizacion - Ley 21.719 Art. 2 - datos anonimos no estan sujetos a la ley';

-- Indica si los datos estan seudonimizados (separacion reversible de identificadores)
-- Relevancia: Art. 2 Ley 21.719 - datos seudonimizados siguen sujetos a la ley
ALTER TABLE rats ADD COLUMN IF NOT EXISTS datos_seudonimizados BOOLEAN DEFAULT FALSE;
COMMENT ON COLUMN rats.datos_seudonimizados IS 'Datos seudonimizados (separacion reversible de identificadores) - Ley 21.719 Art. 2 - siguen sujetos a la ley';

-- ============================================================
-- TIER 2: GAPS OPERATIVOS (ProBest template)
-- ============================================================

-- Etapa o fase del ciclo de vida del tratamiento de datos
-- Ejemplos: recopilacion, almacenamiento, uso, comunicacion, eliminacion, archivo
ALTER TABLE rats ADD COLUMN IF NOT EXISTS ciclo_procesamiento VARCHAR(100);
COMMENT ON COLUMN rats.ciclo_procesamiento IS 'Etapa del ciclo de vida del tratamiento: recopilacion, almacenamiento, uso, comunicacion, eliminacion, archivo - ProBest template';

-- Grado de automatizacion del tratamiento
-- Ejemplos: 100% manual, mayoritariamente manual, mayoritariamente automatizado, 100% automatizado
ALTER TABLE rats ADD COLUMN IF NOT EXISTS automatizacion VARCHAR(100);
COMMENT ON COLUMN rats.automatizacion IS 'Grado de automatizacion: 100% manual, mayoritariamente manual, mayoritariamente automatizado, 100% automatizado - ProBest template';

-- Frecuencia con que se realizan las operaciones de tratamiento
-- Ejemplos: diaria, semanal, mensual, trimestral, anual, puntual
ALTER TABLE rats ADD COLUMN IF NOT EXISTS frecuencia VARCHAR(100);
COMMENT ON COLUMN rats.frecuencia IS 'Frecuencia del tratamiento: diaria, semanal, mensual, trimestral, anual, puntual - ProBest template';

-- Indica si hay transferencia de datos dentro del territorio nacional
-- Relevancia: Diferenciar transferencias internacionales (Art. 28) de nacionales
ALTER TABLE rats ADD COLUMN IF NOT EXISTS transferencia_nacional BOOLEAN DEFAULT FALSE;
COMMENT ON COLUMN rats.transferencia_nacional IS 'Transferencia de datos dentro del territorio nacional (diferenciar de internacional Art. 28) - ProBest template';

-- Documentacion de clausulas informativas entregadas a los titulares
-- Ejemplos: Politica de privacidad, aviso de privacidad, clausulas de consentimiento
ALTER TABLE rats ADD COLUMN IF NOT EXISTS doc_clausulas TEXT;
COMMENT ON COLUMN rats.doc_clausulas IS 'Documentacion de clausulas informativas: Politica de privacidad, aviso de privacidad, clausulas de consentimiento - ProBest template';

-- Medidas organizativas implementadas para la proteccion de datos
-- Ejemplos: Designacion de RAI/DPO, procedimientos de acceso, politicas internas
ALTER TABLE rats ADD COLUMN IF NOT EXISTS medidas_organizativas TEXT;
COMMENT ON COLUMN rats.medidas_organizativas IS 'Medidas organizativas: Designacion RAI/DPO, procedimientos acceso, politicas internas - ProBest template';

-- Mecanismos de eliminacion o destruccion segura de datos
-- Ejemplos: borrado seguro, destruccion fisica, retencion hasta fin del plazo
ALTER TABLE rats ADD COLUMN IF NOT EXISTS mecanismos_eliminacion TEXT;
COMMENT ON COLUMN rats.mecanismos_eliminacion IS 'Mecanismos de eliminacion: borrado seguro, destruccion fisica, retencion hasta fin plazo - ProBest template';

-- Tecnica de anonimizacion aplicada (si corresponde)
-- Ejemplos: seudonimizacion, k-anonimidad, agregacion, perturbacion
ALTER TABLE rats ADD COLUMN IF NOT EXISTS tecnica_anonimizacion VARCHAR(100);
COMMENT ON COLUMN rats.tecnica_anonimizacion IS 'Tecnica de anonimizacion: seudonimizacion, k-anonimidad, agregacion, perturbacion - ProBest template';

-- Origen de los datos en caso de ejercicios de portabilidad
-- Ejemplos: directamente del titular, de otro responsable, de fuentes publicas
ALTER TABLE rats ADD COLUMN IF NOT EXISTS origen_dato_portabilidad VARCHAR(200);
COMMENT ON COLUMN rats.origen_dato_portabilidad IS 'Origen de los datos para portabilidad: directamente del titular, de otro responsable, fuentes publicas - ProBest template';

-- Fecha de elaboracion o levantamiento inicial del RAT
ALTER TABLE rats ADD COLUMN IF NOT EXISTS fecha_levantamiento DATE;
COMMENT ON COLUMN rats.fecha_levantamiento IS 'Fecha de elaboracion o levantamiento inicial del RAT - ProBest template';

COMMIT;
