-- =============================================================================
-- Script de Pruebas: 44 RATs para Custodio RAT Manager v1.6.5
-- =============================================================================
-- Generado: 2026-07-02
-- Propósito: Set de datos de prueba para validar todos los flujos legales
--            de la Ley 21.719 (RAT, EIPD, Consentimientos, Encargados, etc.)
--
-- EJECUCIÓN:
-- 1. Conectar a Neon PostgreSQL (custodio_qa o custodio_test):
--    psql "postgresql://user:pass@host/db?sslmode=require"
-- 2. Reemplazar :company_id y :user_id con valores reales:
--    SELECT id, nombre FROM companies LIMIT 5;
--    SELECT id, username FROM users LIMIT 5;
-- 3. Ejecutar el script
-- 4. Verificar: SELECT count(*) FROM rats WHERE nombre_proceso LIKE 'RAT-%';
--
-- =============================================================================

\set company_id 1
\set user_id 1

-- =============================================================================
-- NORMALES (N1-N6) — Casos simples, sin datos sensibles ni transferencias
-- =============================================================================

-- N1: Cliente web básico
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N1-Cliente-Web',
  'Datos identificativos (nombre, email, teléfono), datos de navegación y comportamiento online',
  'Clientes y usuarios del servicio web',
  'Gestión de cuenta de usuario y entrega del servicio',
  'Consentimiento del titular',
  'Formularios de registro del sitio web',
  '3 años desde último contacto',
  false, false, 'no_requerida',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- N2: Empleado (ejecución contrato)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N2-Empleado',
  'Datos identificativos, laborales, remuneracionales',
  'Trabajadores y ex-trabajadores de la organización',
  'Cumplimiento de obligaciones laborales y previsionales',
  'Ejecución de contrato',
  'Sistema de Recursos Humanos',
  '10 años desde término de relación laboral',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- N3: Marketing
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N3-Marketing',
  'Datos identificativos, preferencias, historial de compras',
  'Clientes que otorgaron consentimiento para comunicaciones comerciales',
  'Envío de comunicaciones comerciales y promociones',
  'Consentimiento del titular',
  'Formularios de suscripción y bases de datos de clientes',
  '5 años desde último consentimiento',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- N4: Proveedores
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N4-Proveedores',
  'Datos identificativos de contacto, datos tributarios (RUT, actividad económica)',
  'Proveedores de bienes y servicios (personas naturales o contactos de personas jurídicas)',
  'Gestión de relación comercial y pagos',
  'Ejecución de contrato',
  'Sistema de compras y contabilidad',
  '5 años desde última transacción',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- N5: RRHH - Interés legítimo (requiere test IL)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  test_interes_legitimo,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N5-RRHH-InteresLegitimo',
  'Datos identificativos, evaluaciones de desempeño, historial laboral',
  'Trabajadores de la organización',
  'Monitoreo de productividad y gestión de talento',
  'Interés legítimo',
  'Sistema de RRHH y evaluaciones de desempeño',
  '3 años desde término de relación laboral',
  '1. La empresa tiene interes legitimo en conocer el rendimiento de sus trabajadores para mejorar la productividad y competitividad. 2. El tratamiento es necesario porque permite identificar areas de mejora, tomar decisiones de capacitacion y planificar carrera profesional. 3. El interes de la empresa prevalece sobre el derecho a la privacidad del trabajador dado que se trata de datos profesionales y no personales intimos, y los trabajadores fueron informados previamente.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- N6: Contabilidad - Obligación legal
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-N6-Contabilidad',
  'Datos identificativos tributarios (RUT), datos de contacto comercial, datos de transacciones comerciales',
  'Clientes, proveedores y terceros con quienes se emiten o reciben documentos tributarios',
  'Cumplimiento de obligaciones tributarias y contables',
  'Obligación legal',
  'Sistema contable y facturación electrónica',
  '10 años según normativa tributaria',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- CRÍTICOS (C1-C8) — Casos que activan todos los flujos legales
-- =============================================================================

-- C1: Biometría + Transferencia Internacional + EIPD Pendiente (OK)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  transferencia_internacional, pais_destino, garantias_transferencia_int,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C1-Biometrico-TransIntl',
  'Datos biométricos de identificación (huella dactilar, facial o equivalente), registro de hora de entrada/salida',
  'Trabajadores sujetos a control de asistencia',
  'Control de horario y asistencia del personal para cumplimiento de jornada laboral',
  'Datos biométricos de identificación (Art. 16 BIS)',
  'Relojes biométricos de huella dactilar en todas las sedes',
  '5 años desde último registro (según normativa laboral)',
  true, 'Datos biométricos de identificación (Art. 16 BIS)', true, 'pendiente',
  true, 'Estados Unidos', 'Cláusulas Contractuales Tipo (SCC)',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C2: Biometría + Encargado SIN contrato (debe fallar al editar)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  nombre_encargado, tiene_contrato_encargado,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C2-Biometrico-Encargado-Sin-Contrato',
  'Datos biométricos de identificación (reconocimiento facial), registro de accesos',
  'Trabajadores con acceso a zonas restringidas',
  'Control biométrico de acceso a instalaciones de alta seguridad',
  'Datos biométricos de identificación (Art. 16 BIS)',
  'Cámaras de reconocimiento facial en accesos',
  '5 años desde último acceso',
  true, 'Datos biométricos de identificación (Art. 16 BIS)', true, 'pendiente',
  'CloudTech S.A.', false,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C3: Salud (debe alertar sobre consentimiento expreso)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C3-Salud-Pacientes',
  'Datos de salud, datos identificativos, historial clínico, datos de tratamientos y medicamentos',
  'Pacientes y beneficiarios del servicio de salud',
  'Prestación de servicios de salud, medicina preventiva y seguimiento de tratamientos',
  'Obligación legal',
  'Sistema de historia clínica electrónica (HCE)',
  '15 años desde última atención (Ley 20.584)',
  true, 'Salud (física o mental)', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C4: Datos sensibles SIN consentimiento (falla al guardar desde wizard sin consent)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C4-Sensible-Sin-Consentimiento',
  'Datos de situación socioeconómica del hogar y composición familiar',
  'Familiares de trabajadores (para beneficios sociales)',
  'Otorgamiento de beneficios sociales y asignaciones familiares',
  'Ejecución de contrato',
  'Formularios de postulación a beneficios',
  '3 años desde término del beneficio',
  true, 'Situación socioeconómica', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C5: Transferencia Internacional SIN EIPD (falla al crear)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  transferencia_internacional, pais_destino, garantias_transferencia_int,
  evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C5-TransIntl-Sin-EIPD',
  'Datos identificativos y datos de transacciones comerciales',
  'Clientes y proveedores internacionales',
  'Gestión de relaciones comerciales con partners en México',
  'Obligación legal',
  'Sistema CRM y correos electrónicos corporativos',
  '5 años desde última transacción',
  true, 'México', 'Nivel adecuado de protección (decisión APDC o UE)',
  false, 'no_requerida',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C6: Transferencia Internacional + EIPD Pendiente + IL (OK con alerta)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  transferencia_internacional, pais_destino, garantias_transferencia_int,
  evaluacion_impacto, estado_eipd, test_interes_legitimo,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C6-TransIntl-EIPD-Pendiente-IL',
  'Datos identificativos, datos de rendimiento del servicio',
  'Clientes del servicio en España',
  'Prestación de servicios de consultoría y soporte técnico',
  'Interés legítimo',
  'Sistema de gestión de clientes y correos electrónicos',
  '5 años desde última prestación',
  true, 'España', 'Cláusulas Contractuales Tipo (SCC)',
  true, 'pendiente',
  '1. La empresa tiene interes legitimo en prestar servicios en Espana y necesita transferir datos de clientes para operar el servicio. 2. El tratamiento es necesario para la prestacion del servicio contratado y cumplimiento de SLA. 3. Se implementan garantias adecuadas mediante CCT y se cumple con RGPD UE.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C7: Biométrico + EIPD completada (escenario ideal, todo OK)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd, fecha_eipd,
  decisiones_automatizadas, logica_automatizada,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C7-Biometrico-EIPD-Completa',
  'Datos biométricos de identificación (huella dactilar), registro de hora de entrada/salida',
  'Trabajadores sujetos a control de asistencia',
  'Control de horario y asistencia del personal con identificación biométrica',
  'Datos biométricos de identificación (Art. 16 BIS)',
  'Relojes biométricos de huella dactilar con encriptación AES-256',
  '5 años desde último registro',
  true, 'Datos biométricos de identificación (Art. 16 BIS)', true, 'completada', '2026-07-01',
  true, 'Identificación inequívoca del trabajador mediante huella dactilar para control de asistencia y tiempo. El sistema compara la huella capturada contra la plantilla almacenada (1:1) sin capacidad de reconocimiento masivo.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- C8: Sensibles + Consentimiento + EIPD pendiente
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-C8-Salud-ConSentimiento-EIPD-Pendiente',
  'Datos de salud, datos identificativos, historial clínico y tratamientos',
  'Pacientes y beneficiarios del servicio de salud',
  'Prestación de servicios de salud, medicina preventiva y seguimiento de tratamientos',
  'Consentimiento del titular',
  'Sistema de historia clínica electrónica y formularios de consentimiento expreso',
  '15 años desde última atención',
  true, 'Salud (física o mental)', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- SENSIBLES (S1-S6) — Tipos de dato sensible (7 menos C1/C3/C7/C8 ya cubiertos)
-- =============================================================================

-- S1: Origen racial/étnico
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-S1-Origen-Racial',
  'Datos identificativos, origen étnico y cultural',
  'Participantes de programas sociales de inclusión',
  'Gestión de programas de diversidad e inclusión social',
  'Consentimiento del titular',
  'Formularios de postulación a programas',
  '5 años desde término del programa',
  true, 'Origen racial o étnico', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- S4: Vida sexual, orientación sexual
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-S4-Vida-Sexual',
  'Datos de orientación sexual, historia clínica',
  'Pacientes del programa de salud sexual',
  'Prestaciones de salud sexual y reproductiva',
  'Consentimiento del titular',
  'Sistema de historia clínica',
  '15 años',
  true, 'Vida sexual, orientación sexual e identidad de género', true, 'completada',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- S5: Opiniones políticas
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-S5-Opiniones-Politicas',
  'Datos de afiliación política, creencias religiosas',
  'Miembros de juntas directivas',
  'Gestión de gobierno corporativo y relaciones institucionales',
  'Consentimiento del titular',
  'Formularios de declaración jurada',
  '10 años desde cese del cargo',
  true, 'Opiniones políticas, creencias religiosas o filosóficas', true, 'completada',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- S6: Afiliación sindical
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  test_interes_legitimo,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-S6-Afiliacion-Sindical',
  'Datos de afiliación sindical y gremial',
  'Trabajadores afiliados a sindicatos',
  'Cumplimiento de obligaciones con organizaciones sindicales',
  'Interés legítimo',
  'Registro sindical y relatorías con gremios',
  '5 años desde término de la relación laboral',
  true, 'Afiliación sindical', true, 'pendiente',
  '1. La empresa tiene interes legitimo en mantener relaciones armoniosas con las organizaciones sindicales y cumplir con las obligaciones convencionales. 2. El tratamiento es necesario para cumplir con las obligaciones legales y convencionales de la empresa. 3. Prevalecen los derechos del trabajador sobre su afiliacion sindical y se limita a lo estrictamente necesario.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- ENCARGADO (EN1-EN3) — Combinaciones con encargado del tratamiento
-- =============================================================================

-- EN1: Sin encargado
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-EN1-Sin-Encargado',
  'Datos identificativos y datos de contacto',
  'Clientes',
  'Gestión de cartera de clientes y atención',
  'Consentimiento del titular',
  'Sistema CRM corporativo',
  '3 años desde último contacto',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- EN2: Con encargado + contrato (Art. 14 quater OK)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  nombre_encargado, tiene_contrato_encargado,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-EN2-Encargado-Con-Contrato',
  'Datos identificativos, datos laborales, datos previsionales',
  'Empleados',
  'Procesamiento de nómina y beneficios laborales mediante servicio externo',
  'Ejecución de contrato',
  'Sistema de RRHH y servicio externo de payroll',
  '10 años desde término de relación laboral',
  'PayrollPro Chile SpA', true,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- EN3: Con encargado SIN contrato (debe fallar al editar)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  nombre_encargado, tiene_contrato_encargado,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-EN3-Encargado-Sin-Contrato',
  'Datos identificativos, datos laborales',
  'Empleados',
  'Procesamiento de nómina mediante servicio externo (sin contrato formal)',
  'Ejecución de contrato',
  'Sistema de RRHH',
  '10 años desde término de relación laboral',
  'ExternalPayrollServices SpA', false,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- DECISIONES AUTOMATIZADAS (A1-A3) — Algoritmos y perfilamiento
-- =============================================================================

-- A1: Sin decisiones automatizadas
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  decisiones_automatizadas,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-A1-Sin-Decisiones',
  'Datos identificativos y datos de contacto',
  'Clientes',
  'Atención personalizada de consultas y soporte técnico',
  'Consentimiento del titular',
  'Sistema de tickets de soporte',
  '3 años desde cierre del ticket',
  false,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- A2: Con decisiones + lógica documentada
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  decisiones_automatizadas, logica_automatizada,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-A2-Con-Decisiones-Y-Logica',
  'Datos financieros, historial crediticio, ingresos declarados',
  'Clientes y solicitantes de crédito',
  'Evaluación crediticia automatizada para aprobación de crédito',
  'Ejecución de contrato',
  'Sistema de scoring crediticio y bureau',
  '7 años según normativa financiera',
  true,
  'Algoritmo de scoring que analiza historial crediticio (40%), ingresos declarados (30%) y comportamiento de pago (30%) para generar un score de riesgo crediticio de 0-1000 que determina si se aprueba o rechaza automaticamente el credito solicitado. Umbral de aprobacion: 650.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- A3: Con decisiones SIN documentar la lógica (alerta)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  decisiones_automatizadas,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-A3-Con-Decisiones-Sin-Logica',
  'Datos financieros y transaccionales',
  'Clientes',
  'Clasificación automática de riesgo transaccional',
  'Ejecución de contrato',
  'Sistema de clasificación de riesgo',
  '5 años',
  true,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- FRONTERA (F1-F7) — Edge cases
-- =============================================================================

-- F1: no_requerida_justificada (OK)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, evaluacion_impacto, estado_eipd, justificacion_no_aplica,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F1-NoRequerida-Justificada',
  'Datos identificativos básicos (nombre, RUT, hora de ingreso)',
  'Empleados',
  'Control de acceso físico a instalaciones mediante tarjeta',
  'Obligación legal',
  'Sistema de registro de acceso con tarjeta',
  '2 años desde último acceso',
  true, false, 'no_requerida_justificada',
  'El tratamiento involve solo datos identificativos basicos que no representan un riesgo alto para los derechos de los titulares ya que se limitan a control de acceso fisico mediante tarjeta sin perfilamiento, sin toma de decisiones automatizadas y sin tratamiento masivo.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F2: no_requerida_justificada corta (falla)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, evaluacion_impacto, estado_eipd, justificacion_no_aplica,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F2-NoRequerida-Corta',
  'Datos identificativos',
  'Empleados',
  'Control de acceso',
  'Obligación legal',
  'Sistema de acceso',
  '2 años',
  true, false, 'no_requerida_justificada',
  'Solo datos basicos',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F3: Trans.Intl. sin país (alerta)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  transferencia_internacional,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F3-TransIntl-SinPais',
  'Datos identificativos',
  'Clientes',
  'Atención de clientes internacionales',
  'Consentimiento del titular',
  'Sistema CRM',
  '3 años',
  true,
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F4: Trans.Intl. sin garantías (alerta)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  transferencia_internacional, pais_destino,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F4-TransIntl-SinGarantias',
  'Datos identificativos',
  'Clientes',
  'Soporte técnico remoto',
  'Consentimiento del titular',
  'Sistema de tickets',
  '3 años',
  true, 'Argentina',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F5: NNA - Niños (< 14 años)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, datos_nna, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F5-NNA-Ninos',
  'Datos identificativos, datos académicos, datos de contacto de tutores o apoderados',
  'Niños menores de 14 años',
  'Gestión académica y administrativa de estudiantes',
  'Obligación legal',
  'Sistema escolar (SIGE)',
  '10 años desde egreso',
  true, 'ninos', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F6: NNA - Adolescentes (14-17 años)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, datos_nna, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F6-NNA-Adolescentes',
  'Datos identificativos, rendimiento académico',
  'Estudiantes de 14 a 17 años',
  'Gestión académica y bienestar estudiantil',
  'Consentimiento del titular',
  'Sistema escolar',
  '10 años desde egreso',
  true, 'adolescentes', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- F7: NNA - Ambos (ninos + adolescentes)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, datos_nna, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-F7-NNA-Ambos',
  'Datos identificativos, datos académicos, datos médicos básicos',
  'Niños y adolescentes (menores de 18 años)',
  'Gestión integral de estudiantes de enseñanza básica y media',
  'Obligación legal',
  'Sistema escolar integral',
  '10 años desde egreso',
  true, 'ambos', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- EIPD (E1-E4) — Estados de EIPD
-- =============================================================================

-- E1: EIPD no requerida (sin sensibles ni trans)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-E1-EIPD-NoRequerida',
  'Datos identificativos y de contacto',
  'Clientes',
  'Atención al cliente y gestión de consultas',
  'Consentimiento del titular',
  'Sistema CRM',
  '3 años',
  false, 'no_requerida',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- E2: EIPD pendiente
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-E2-EIPD-Pendiente',
  'Datos de salud',
  'Pacientes',
  'Gestión clínica',
  'Consentimiento del titular',
  'HCE',
  '15 años',
  true, 'Salud (física o mental)', true, 'pendiente',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- E3: EIPD en proceso
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  transferencia_internacional, pais_destino, garantias_transferencia_int,
  evaluacion_impacto, estado_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-E3-EIPD-EnProceso',
  'Datos identificativos y de pago',
  'Clientes internacionales',
  'Procesamiento de pagos internacionales',
  'Ejecución de contrato',
  'Sistema de pagos',
  '7 años',
  true, 'Brasil', 'Nivel adecuado de protección',
  true, 'en_proceso',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- E4: EIPD completada (todo OK, aprueba-ready)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  datos_sensibles, tipo_dato_sensible, evaluacion_impacto, estado_eipd, fecha_eipd,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-E4-EIPD-Completada',
  'Datos biométricos',
  'Trabajadores',
  'Control biométrico de acceso',
  'Datos biométricos de identificación (Art. 16 BIS)',
  'Reloj biométrico',
  '5 años',
  true, 'Datos biométricos de identificación (Art. 16 BIS)', true, 'completada', '2026-06-15',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- BASES LEGALES (B1-B7) — Las 7 opciones
-- =============================================================================

-- B1: Interés legítimo con test IL OK
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  test_interes_legitimo,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B1-Interes-Legitimo-TestOK',
  'Datos de uso del servicio y patrones de navegación',
  'Usuarios de la plataforma',
  'Mejora del servicio mediante análisis de uso',
  'Interés legítimo',
  'Logs de la plataforma',
  '2 años',
  '1. La empresa tiene interes legitimo en mejorar su servicio mediante el analisis de patrones de uso. 2. El tratamiento es necesario porque sin estos datos no se pueden identificar areas de mejora. 3. Los datos son agregados y anonimizados antes del analisis, por lo que prevalecen sobre los derechos individuales.',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- B2: Interés legítimo SIN test IL (alerta fuerte)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B2-Interes-Legitimo-SinTest',
  'Datos de uso del servicio',
  'Usuarios',
  'Mejora del servicio',
  'Interés legítimo',
  'Logs',
  '2 años',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- B3: Ejecución de contrato
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B3-Ejecucion-Contrato',
  'Datos de entrega',
  'Clientes con contrato',
  'Entrega de productos',
  'Ejecución de contrato',
  'Sistema de logística',
  '5 años',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- B4: Obligación legal
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B4-Obligacion-Legal',
  'Datos tributarios',
  'Contribuyentes',
  'Declaraciones al SII',
  'Obligación legal',
  'Sistema contable',
  '10 años',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- B5: Interés vital
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B5-Interes-Vital',
  'Datos de salud críticos y contactos de emergencia',
  'Personas en emergencia médica',
  'Atención médica de urgencia',
  'Interés vital del titular',
  'Sistema de urgencias',
  '5 años',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- B7: Otra (texto libre)
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-B7-Otra',
  'Datos varios',
  'Varios',
  'Caso especial documentado en base legal personalizada',
  'Otra (base legal custom: Art. 13 d)',
  'Sistema legacy',
  '5 años',
  'borrador', 'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- AUDITORÍA (AUDIT-1) — Para probar log de auditoría
-- =============================================================================

-- AUDIT-1: RAT con muchos cambios para ver historial
INSERT INTO rats (
  company_id, nombre_proceso, categoria_datos, categoria_titulares,
  finalidad, base_legal, fuente_datos, plazo_retencion,
  estado, observaciones_auditoria,
  created_by, updated_by, created_at, updated_at
) VALUES (
  :'company_id', 'RAT-AUDIT-Cambios',
  'Datos identificativos',
  'Clientes',
  'Caso para prueba de auditoría',
  'Consentimiento del titular',
  'Sistema',
  '3 años',
  'borrador',
  'AUDITORÍA: RAT creado para verificar log de auditoría en detail view',
  'admin', 'admin', NOW(), NOW()
);

-- =============================================================================
-- CONSENTIMIENTOS — Para los RATs que requieren
-- =============================================================================

-- C1: Consentimiento para biometría (huella)
INSERT INTO consentimientos (
  company_id, rat_id, nombre_titular, email_titular, canal,
  texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
)
SELECT :'company_id', id, 'Juan Pérez González', 'juan.perez@empresa.com', 'firma_digital',
  'Consentimiento expreso conforme al Art. 16 BIS de la Ley 21.719 para tratamiento de datos biométricos de identificación mediante huella dactilar para control de asistencia y jornada laboral.',
  NOW(), true, '192.168.1.100', NOW()
FROM rats WHERE nombre_proceso = 'RAT-C1-Biometrico-TransIntl' LIMIT 1;

-- C3: Consentimiento para salud
INSERT INTO consentimientos (
  company_id, rat_id, nombre_titular, email_titular, canal,
  texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
)
SELECT :'company_id', id, 'María López Silva', 'maria.lopez@paciente.cl', 'firma_digital',
  'Consentimiento expreso para tratamiento de datos de salud en el marco de la prestación de servicios de salud conforme al Art. 16 de la Ley 21.719.',
  NOW(), true, '192.168.1.101', NOW()
FROM rats WHERE nombre_proceso = 'RAT-C3-Salud-Pacientes' LIMIT 1;

-- C7: Consentimiento biometría completo
INSERT INTO consentimientos (
  company_id, rat_id, nombre_titular, email_titular, canal,
  texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
)
SELECT :'company_id', id, 'Pedro Gómez Soto', 'pedro.gomez@empresa.com', 'papel',
  'Yo, Pedro Gómez Soto, RUT 12.345.678-9, declaro haber sido informado y otorgo mi consentimiento expreso para que mi empleador trate mis datos biométricos de identificación (huella dactilar) para fines de control de asistencia conforme al Art. 16 BIS de la Ley 21.719.',
  NOW(), true, '192.168.1.102', NOW()
FROM rats WHERE nombre_proceso = 'RAT-C7-Biometrico-EIPD-Completa' LIMIT 1;

-- C8: Consentimiento salud + EIPD pendiente
INSERT INTO consentimientos (
  company_id, rat_id, nombre_titular, email_titular, canal,
  texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
)
SELECT :'company_id', id, 'Ana Martínez Rojas', 'ana.martinez@paciente.cl', 'web',
  'Consentimiento expreso para tratamiento de datos de salud para la prestación de servicios médicos conforme al Art. 12 y 16 de la Ley 21.719.',
  NOW(), true, '192.168.1.103', NOW()
FROM rats WHERE nombre_proceso = 'RAT-C8-Salud-ConSentimiento-EIPD-Pendiente' LIMIT 1;

-- EN2: Consentimiento para encargado
INSERT INTO consentimientos (
  company_id, rat_id, nombre_titular, email_titular, canal,
  texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
)
SELECT :'company_id', id, 'Carlos Rodríguez Vega', 'carlos.rodriguez@empresa.com', 'papel',
  'Consentimiento para tratamiento de datos laborales mediante encargado del tratamiento (PayrollPro Chile SpA) conforme al Art. 14 quater.',
  NOW(), true, '192.168.1.104', NOW()
FROM rats WHERE nombre_proceso = 'RAT-EN2-Encargado-Con-Contrato' LIMIT 1;

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================

-- Contar RATs insertados
SELECT count(*) AS total_rats_insertados
FROM rats WHERE nombre_proceso LIKE 'RAT-%';

-- Distribución por categoría
SELECT
  CASE
    WHEN datos_sensibles THEN 'Con datos sensibles'
    ELSE 'Sin datos sensibles'
  END AS categoria,
  CASE
    WHEN transferencia_internacional THEN 'Con transferencia intl'
    ELSE 'Sin transferencia intl'
  END AS trans,
  CASE
    WHEN estado_eipd = 'pendiente' THEN 'EIPD pendiente'
    WHEN estado_eipd = 'en_proceso' THEN 'EIPD en proceso'
    WHEN estado_eipd = 'completada' THEN 'EIPD completada'
    WHEN estado_eipd = 'no_requerida' THEN 'EIPD no requerida'
    WHEN estado_eipd = 'no_requerida_justificada' THEN 'EIPD no requerida (justificada)'
    ELSE 'Sin EIPD'
  END AS eipd,
  count(*) AS total
FROM rats WHERE nombre_proceso LIKE 'RAT-%'
GROUP BY categoria, trans, eipd
ORDER BY categoria, trans, eipd;

-- =============================================================================
-- NOTAS
-- =============================================================================
-- Total esperado: 41 RATs
--   - 6 normales (N1-N6)
--   - 8 críticos (C1-C8)
--   - 4 sensibles adicionales (S1, S4-S6)
--   - 3 encargado (EN1-EN3)
--   - 3 decisiones automatizadas (A1-A3)
--   - 7 frontera (F1-F7)
--   - 4 EIPD (E1-E4)
--   - 7 bases legales (B1-B5, B7)
--   - 1 auditoría (AUDIT-1)
--   - 5 consentimientos (C1, C3, C7, C8, EN2)
-- =============================================================================