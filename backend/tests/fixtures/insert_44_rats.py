"""
Script Python para ejecutar el set de pruebas de 44 RATs.
Usa CAST para enums y maneja correctamente los booleanos NOT NULL.

Uso:
    export DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
    python insert_44_rats.py

Opcionales:
    COMPANY_ID=2 python insert_44_rats.py
    USERNAME=admin_empresa python insert_44_rats.py
"""

import os
import psycopg2

DB_URL = os.environ["DATABASE_URL"]  # requerido, no hay default
COMPANY_ID = int(os.environ.get("COMPANY_ID", "1"))
USERNAME = os.environ.get("USERNAME", "admin")


def base_extras(nombre):
    """Devuelve los booleanos NOT NULL con defaults False."""
    return {
        "datos_sensibles": False,
        "evaluacion_impacto": False,
        "decisiones_automatizadas": False,
        "transferencia_internacional": False,
        "tiene_contrato_encargado": False,
        "bloqueado": False,
    }


def insert_rat(cur, nombre, categoria_datos, categoria_titulares,
               finalidad, base_legal, fuente_datos, plazo_retencion,
               extras, test_il=None, conn=None):
    """Inserta un RAT con manejo correcto de NOT NULL."""
    be = base_extras(nombre)
    # Solo agregar campos de be que no esten ya en extras
    for k, v in be.items():
        if k not in extras:
            extras[k] = v
    cols = [
        "company_id", "nombre_proceso", "categoria_datos", "categoria_titulares",
        "finalidad", "base_legal", "fuente_datos", "plazo_retencion",
    ]
    vals = [COMPANY_ID, nombre, categoria_datos, categoria_titulares,
            finalidad, base_legal, fuente_datos, plazo_retencion]
    for k, v in extras.items():
        cols.append(k)
        vals.append(v)
    cols.extend(["estado", "created_by", "updated_by", "created_at", "updated_at"])
    # cols ahora termina con 5 campos: estado, created_by, updated_by, created_at, updated_at
    # placeholders: (cols-5) %s + CAST('BORRADOR' AS estadorat) + 2 %s (USERNAME) + 2 NOW()
    placeholders = ",".join(["%s"] * (len(cols) - 5)) + ",CAST('BORRADOR' AS estadorat),%s,%s,NOW(),NOW()"
    vals.append(USERNAME)
    vals.append(USERNAME)
    sql = f"INSERT INTO rats ({','.join(cols)}) VALUES ({placeholders})"
    try:
        cur.execute(sql, vals)
        if conn:
            conn.commit()
        return True
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        print(f"  WARN {nombre}: {str(e)[:80]}")
        return False


def main():
    print("Conectando a BD...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # ========================================
    # NORMALES (N1-N6)
    # ========================================
    print("Insertando N1-N6 (normales)...")
    normales = [
        ("RAT-N1-Cliente-Web",
         "Datos identificativos (nombre, email, telefono), datos de navegacion y comportamiento online",
         "Clientes y usuarios del servicio web",
         "Gestion de cuenta de usuario y entrega del servicio",
         "Consentimiento del titular",
         "Formularios de registro del sitio web",
         "3 anos desde ultimo contacto",
         {}, None),
        ("RAT-N2-Empleado",
         "Datos identificativos, laborales, remuneracionales",
         "Trabajadores y ex-trabajadores de la organizacion",
         "Cumplimiento de obligaciones laborales y previsionales",
         "Ejecucion de contrato",
         "Sistema de Recursos Humanos",
         "10 anos desde termino de relacion laboral",
         {}, None),
        ("RAT-N3-Marketing",
         "Datos identificativos, preferencias, historial de compras",
         "Clientes que otorgaron consentimiento para comunicaciones comerciales",
         "Envio de comunicaciones comerciales y promociones",
         "Consentimiento del titular",
         "Formularios de suscripcion y bases de datos de clientes",
         "5 anos desde ultimo consentimiento",
         {}, None),
        ("RAT-N4-Proveedores",
         "Datos identificativos de contacto, datos tributarios (RUT, actividad economica)",
         "Proveedores de bienes y servicios (personas naturales o contactos de personas juridicas)",
         "Gestion de relacion comercial y pagos",
         "Ejecucion de contrato",
         "Sistema de compras y contabilidad",
         "5 anos desde ultima transaccion",
         {}, None),
        ("RAT-N5-RRHH-InteresLegitimo",
         "Datos identificativos, evaluaciones de desempeno, historial laboral",
         "Trabajadores de la organizacion",
         "Monitoreo de productividad y gestion de talento",
         "Interes legitimo",
         "Sistema de RRHH y evaluaciones de desempeno",
         "3 anos desde termino de relacion laboral",
         {},
         "1. La empresa tiene interes legitimo en conocer el rendimiento de sus trabajadores para mejorar la productividad y competitividad. 2. El tratamiento es necesario porque permite identificar areas de mejora, tomar decisiones de capacitacion y planificar carrera profesional. 3. El interes de la empresa prevalece sobre el derecho a la privacidad del trabajador dado que se trata de datos profesionales y no personales intimos."),
        ("RAT-N6-Contabilidad",
         "Datos identificativos tributarios (RUT), datos de contacto comercial, datos de transacciones comerciales",
         "Clientes, proveedores y terceros con quienes se emiten o reciben documentos tributarios",
         "Cumplimiento de obligaciones tributarias y contables",
         "Obligacion legal",
         "Sistema contable y facturacion electronica",
         "10 anos segun normativa tributaria",
         {}, None),
    ]
    for n in normales:
        ok = insert_rat(cur, n[0], n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], conn)
        print(f"  {'OK' if ok else 'WARN'} {n[0]}")

    # ========================================
    # CRÍTICOS (C1-C8)
    # ========================================
    print("\nInsertando C1-C8 (criticos)...")
    criticos = [
        ("RAT-C1-Biometrico-TransIntl",
         "Datos biometricos de identificacion (huella dactilar, facial o equivalente), registro de hora de entrada/salida",
         "Trabajadores sujetos a control de asistencia",
         "Control de horario y asistencia del personal para cumplimiento de jornada laboral",
         "Datos biometricos de identificacion (Art. 16 BIS)",
         "Relojes biometricos de huella dactilar en todas las sedes",
         "5 anos desde ultimo registro (segun normativa laboral)",
         {"datos_sensibles": True, "tipo_dato_sensible": "Datos biometricos de identificacion (Art. 16 BIS)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente",
          "transferencia_internacional": True, "pais_destino": "Estados Unidos",
          "garantias_transferencia_int": "Clausulas Contractuales Tipo (SCC)"}, None),
        ("RAT-C2-Biometrico-Encargado-Sin-Contrato",
         "Datos biometricos de identificacion (reconocimiento facial), registro de accesos",
         "Trabajadores con acceso a zonas restringidas",
         "Control biometrico de acceso a instalaciones de alta seguridad",
         "Datos biometricos de identificacion (Art. 16 BIS)",
         "Camaras de reconocimiento facial en accesos",
         "5 anos desde ultimo acceso",
         {"datos_sensibles": True, "tipo_dato_sensible": "Datos biometricos de identificacion (Art. 16 BIS)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente",
          "nombre_encargado": "CloudTech S.A.", "tiene_contrato_encargado": False}, None),
        ("RAT-C3-Salud-Pacientes",
         "Datos de salud, datos identificativos, historial clinico, datos de tratamientos y medicamentos",
         "Pacientes y beneficiarios del servicio de salud",
         "Prestracion de servicios de salud, medicina preventiva y seguimiento de tratamientos",
         "Obligacion legal",
         "Sistema de historia clinica electronica (HCE)",
         "15 anos desde ultima atencion (Ley 20.584)",
         {"datos_sensibles": True, "tipo_dato_sensible": "Salud (fisica o mental)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente"}, None),
        ("RAT-C4-Sensible-Sin-Consentimiento",
         "Datos de situacion socioeconomica del hogar y composicion familiar",
         "Familiares de trabajadores (para beneficios sociales)",
         "Otorgamiento de beneficios sociales y asignaciones familiares",
         "Ejecucion de contrato",
         "Formularios de postulacion a beneficios",
         "3 anos desde termino del beneficio",
         {"datos_sensibles": True, "tipo_dato_sensible": "Situacion socioeconomica",
          "evaluacion_impacto": True, "estado_eipd": "pendiente"}, None),
        ("RAT-C5-TransIntl-Sin-EIPD",
         "Datos identificativos y datos de transacciones comerciales",
         "Clientes y proveedores internacionales",
         "Gestion de relaciones comerciales con partners en Mexico",
         "Obligacion legal",
         "Sistema CRM y correos electronicos corporativos",
         "5 anos desde ultima transaccion",
         {"transferencia_internacional": True, "pais_destino": "Mexico",
          "garantias_transferencia_int": "Nivel adecuado de proteccion (decision APDC o UE)",
          "evaluacion_impacto": False, "estado_eipd": "no_requerida"}, None),
        ("RAT-C6-TransIntl-EIPD-Pendiente-IL",
         "Datos identificativos, datos de rendimiento del servicio",
         "Clientes del servicio en Espana",
         "Prestracion de servicios de consultoria y soporte tecnico",
         "Interes legitimo",
         "Sistema de gestion de clientes y correos electronicos",
         "5 anos desde ultima prestracion",
         {"transferencia_internacional": True, "pais_destino": "Espana",
          "garantias_transferencia_int": "Clausulas Contractuales Tipo (SCC)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente"},
         "1. La empresa tiene interes legitimo en prestar servicios en Espana y necesita transferir datos de clientes para operar el servicio. 2. El tratamiento es necesario para la prestracion del servicio contratado y cumplimiento de SLA. 3. Se implementan garantias adecuadas mediante CCT."),
        ("RAT-C7-Biometrico-EIPD-Completa",
         "Datos biometricos de identificacion (huella dactilar), registro de hora de entrada/salida",
         "Trabajadores sujetos a control de asistencia",
         "Control de horario y asistencia del personal con identificacion biometrica",
         "Datos biometricos de identificacion (Art. 16 BIS)",
         "Relojes biometricos de huella dactilar con encriptacion AES-256",
         "5 anos desde ultimo registro",
         {"datos_sensibles": True, "tipo_dato_sensible": "Datos biometricos de identificacion (Art. 16 BIS)",
          "evaluacion_impacto": True, "estado_eipd": "completada", "fecha_eipd": "2026-07-01",
          "decisiones_automatizadas": True,
          "logica_automatizada": "Identificacion inequivoca del trabajador mediante huella dactilar para control de asistencia y tiempo. Sistema 1:1 sin reconocimiento masivo."}, None),
        ("RAT-C8-Salud-ConSentimiento-EIPD-Pendiente",
         "Datos de salud, datos identificativos, historial clinico y tratamientos",
         "Pacientes y beneficiarios del servicio de salud",
         "Prestracion de servicios de salud, medicina preventiva y seguimiento de tratamientos",
         "Consentimiento del titular",
         "Sistema de historia clinica electronica y formularios de consentimiento expreso",
         "15 anos desde ultima atencion",
         {"datos_sensibles": True, "tipo_dato_sensible": "Salud (fisica o mental)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente"}, None),
    ]
    for c in criticos:
        ok = insert_rat(cur, c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], conn)
        print(f"  {'OK' if ok else 'WARN'} {c[0]}")

    # ========================================
    # SENSIBLES (S1, S4-S6)
    # ========================================
    print("\nInsertando S1, S4-S6 (sensibles adicionales)...")
    sensibles = [
        # (nombre, cat_datos, cat_tit, finalidad, base_legal, fuente, plazo, extras, test_il)
        ("RAT-S1-Origen-Racial",
         "Datos identificativos, origen etnico y cultural",
         "Participantes de programas sociales de inclusion",
         "Gestion de programas de diversidad e inclusion social",
         "Consentimiento del titular",
         "Formularios de postulacion a programas",
         "5 anos desde termino del programa",
         {"tipo_dato_sensible": "Origen racial o etnico", "estado_eipd": "pendiente"},
         None),
        ("RAT-S4-Vida-Sexual",
         "Datos de orientacion sexual, historia clinica",
         "Pacientes del programa de salud sexual",
         "Prestraciones de salud sexual y reproductiva",
         "Consentimiento del titular",
         "Sistema de historia clinica",
         "15 anos",
         {"tipo_dato_sensible": "Vida sexual, orientacion sexual e identidad de genero", "estado_eipd": "completada"},
         None),
        ("RAT-S5-Opiniones-Politicas",
         "Datos de afiliacion politica, creencias religiosas",
         "Miembros de juntas directivas",
         "Gestion de gobierno corporativo y relaciones institucionales",
         "Consentimiento del titular",
         "Formularios de declaracion jurada",
         "10 anos desde cese del cargo",
         {"tipo_dato_sensible": "Opiniones politicas, creencias religiosas o filosoficas", "estado_eipd": "completada"},
         None),
        ("RAT-S6-Afiliacion-Sindical",
         "Datos de afiliacion sindical y gremial",
         "Trabajadores afiliados a sindicatos",
         "Cumplimiento de obligaciones con organizaciones sindicales",
         "Interes legitimo",
         "Registro sindical y relatorias con gremios",
         "5 anos desde termino de la relacion laboral",
         {"tipo_dato_sensible": "Afiliacion sindical", "estado_eipd": "pendiente"},
         "1. La empresa tiene interes legitimo en mantener relaciones armoniosas con las organizaciones sindicales y cumplir con las obligaciones convencionales. 2. El tratamiento es necesario para cumplir con las obligaciones legales y convencionales de la empresa. 3. Prevalecen los derechos del trabajador sobre su afiliacion sindical."),
    ]
    for s in sensibles:
        ok = insert_rat(cur, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], conn)
        print(f"  {'OK' if ok else 'WARN'} {s[0]}")

    # ========================================
    # ENCARGADO (EN1-EN3)
    # ========================================
    print("\nInsertando EN1-EN3 (encargado)...")
    encargados = [
        ("RAT-EN1-Sin-Encargado", None, False),
        ("RAT-EN2-Encargado-Con-Contrato", "PayrollPro Chile SpA", True),
        ("RAT-EN3-Encargado-Sin-Contrato", "ExternalPayrollServices SpA", False),
    ]
    for nombre, encargado, tiene_contrato in encargados:
        ok = insert_rat(cur, nombre,
                        "Datos identificativos y datos de contacto",
                        "Clientes",
                        "Gestion de cartera de clientes y atencion",
                        "Consentimiento del titular",
                        "Sistema CRM corporativo",
                        "3 anos desde ultimo contacto",
                        {"nombre_encargado": encargado, "tiene_contrato_encargado": tiene_contrato},
                        None, conn)
        print(f"  {'OK' if ok else 'WARN'} {nombre}")

    # ========================================
    # DECISIONES AUTOMATIZADAS (A1-A3)
    # ========================================
    print("\nInsertando A1-A3 (decisiones automatizadas)...")
    decisiones = [
        ("RAT-A1-Sin-Decisiones", False, None,
         "Datos identificativos y datos de contacto",
         "Clientes",
         "Atencion personalizada de consultas y soporte tecnico",
         "Consentimiento del titular",
         "Sistema de tickets de soporte",
         "3 anos desde cierre del ticket"),
        ("RAT-A2-Con-Decisiones-Y-Logica", True,
         "Algoritmo de scoring que analiza historial crediticio (40%), ingresos declarados (30%) y comportamiento de pago (30%) para generar un score de riesgo crediticio de 0-1000. Umbral de aprobacion: 650.",
         "Datos financieros, historial crediticio, ingresos declarados",
         "Clientes y solicitantes de credito",
         "Evaluacion crediticia automatizada para aprobacion de credito",
         "Ejecucion de contrato",
         "Sistema de scoring crediticio y bureau",
         "7 anos segun normativa financiera"),
        ("RAT-A3-Con-Decisiones-Sin-Logica", True, None,
         "Datos financieros y transaccionales",
         "Clientes",
         "Clasificacion automatica de riesgo transaccional",
         "Ejecucion de contrato",
         "Sistema de clasificacion de riesgo",
         "5 anos"),
    ]
    for d in decisiones:
        ok = insert_rat(cur, d[0], d[3], d[4], d[5], d[6], d[7], d[8],
                        {"decisiones_automatizadas": d[1], "logica_automatizada": d[2]},
                        None, conn)
        print(f"  {'OK' if ok else 'WARN'} {d[0]}")

    # ========================================
    # FRONTERA (F1-F7)
    # ========================================
    print("\nInsertando F1-F7 (frontera)...")
    frontera = [
        ("RAT-F1-NoRequerida-Justificada", {
            "datos_sensibles": True, "evaluacion_impacto": False,
            "estado_eipd": "no_requerida_justificada",
        }, "Datos identificativos basicos (nombre, RUT, hora de ingreso)",
         "Empleados", "Control de acceso fisico a instalaciones mediante tarjeta",
         "Obligacion legal", "Sistema de registro de acceso con tarjeta",
         "2 anos desde ultimo acceso"),
        ("RAT-F2-NoRequerida-Corta", {
            "datos_sensibles": True, "evaluacion_impacto": False,
            "estado_eipd": "no_requerida_justificada",
        }, "Datos identificativos", "Empleados", "Control de acceso",
         "Obligacion legal", "Sistema de acceso", "2 anos"),
        ("RAT-F3-TransIntl-SinPais", {"transferencia_internacional": True},
         "Datos identificativos", "Clientes", "Atencion de clientes internacionales",
         "Consentimiento del titular", "Sistema CRM", "3 anos"),
        ("RAT-F4-TransIntl-SinGarantias", {"transferencia_internacional": True, "pais_destino": "Argentina"},
         "Datos identificativos", "Clientes", "Soporte tecnico remoto",
         "Consentimiento del titular", "Sistema de tickets", "3 anos"),
        ("RAT-F5-NNA-Ninos", {"datos_sensibles": True, "datos_nna": "ninos",
                               "evaluacion_impacto": True, "estado_eipd": "pendiente"},
         "Datos identificativos, datos academicos, datos de contacto de tutores o apoderados",
         "Ninos menores de 14 anos", "Gestion academica y administrativa de estudiantes",
         "Obligacion legal", "Sistema escolar (SIGE)", "10 anos desde egreso"),
        ("RAT-F6-NNA-Adolescentes", {"datos_sensibles": True, "datos_nna": "adolescentes",
                                      "evaluacion_impacto": True, "estado_eipd": "pendiente"},
         "Datos identificativos, rendimiento academico",
         "Estudiantes de 14 a 17 anos", "Gestion academica y bienestar estudiantil",
         "Consentimiento del titular", "Sistema escolar", "10 anos desde egreso"),
        ("RAT-F7-NNA-Ambos", {"datos_sensibles": True, "datos_nna": "ambos",
                               "evaluacion_impacto": True, "estado_eipd": "pendiente"},
         "Datos identificativos, datos academicos, datos medicos basicos",
         "Ninos y adolescentes (menores de 18 anos)", "Gestion integral de estudiantes",
         "Obligacion legal", "Sistema escolar integral", "10 anos desde egreso"),
    ]
    for f in frontera:
        ok = insert_rat(cur, f[0], f[2], f[3], f[4], f[5], f[6], f[7], f[1], None, conn)
        print(f"  {'OK' if ok else 'WARN'} {f[0]}")

    # ========================================
    # EIPD (E1-E4)
    # ========================================
    print("\nInsertando E1-E4 (estados EIPD)...")
    eipd_estados = [
        ("RAT-E1-EIPD-NoRequerida",
         "Datos identificativos y de contacto", "Clientes",
         "Atencion al cliente y gestion de consultas",
         "Consentimiento del titular", "Sistema CRM", "3 anos",
         {"evaluacion_impacto": False, "estado_eipd": "no_requerida"}, None),
        ("RAT-E2-EIPD-Pendiente",
         "Datos de salud", "Pacientes",
         "Gestion clinica",
         "Consentimiento del titular", "HCE", "15 anos",
         {"datos_sensibles": True, "tipo_dato_sensible": "Salud (fisica o mental)",
          "evaluacion_impacto": True, "estado_eipd": "pendiente"}, None),
        ("RAT-E3-EIPD-EnProceso",
         "Datos identificativos y de pago", "Clientes internacionales",
         "Procesamiento de pagos internacionales",
         "Ejecucion de contrato", "Sistema de pagos", "7 anos",
         {"transferencia_internacional": True, "pais_destino": "Brasil",
          "garantias_transferencia_int": "Nivel adecuado de proteccion",
          "evaluacion_impacto": True, "estado_eipd": "en_proceso"}, None),
        ("RAT-E4-EIPD-Completada",
         "Datos biometricos", "Trabajadores",
         "Control biometrico de acceso",
         "Datos biometricos de identificacion (Art. 16 BIS)", "Reloj biometrico", "5 anos",
         {"datos_sensibles": True, "tipo_dato_sensible": "Datos biometricos de identificacion (Art. 16 BIS)",
          "evaluacion_impacto": True, "estado_eipd": "completada", "fecha_eipd": "2026-06-15"}, None),
    ]
    for e in eipd_estados:
        ok = insert_rat(cur, e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8], conn)
        print(f"  {'OK' if ok else 'WARN'} {e[0]}")

    # ========================================
    # BASES LEGALES (B1-B5, B7)
    # ========================================
    print("\nInsertando B1-B5, B7 (bases legales)...")
    bases = [
        ("RAT-B1-Interes-Legitimo-TestOK",
         "Datos de uso del servicio y patrones de navegacion",
         "Usuarios de la plataforma",
         "Mejora del servicio mediante analisis de uso",
         "Interes legitimo", "Logs de la plataforma", "2 anos",
         {},
         "1. La empresa tiene interes legitimo en mejorar su servicio. 2. El tratamiento es necesario para identificar areas de mejora. 3. Los datos son agregados y anonimizados."),
        ("RAT-B2-Interes-Legitimo-SinTest",
         "Datos de uso del servicio", "Usuarios",
         "Mejora del servicio",
         "Interes legitimo", "Logs", "2 anos", {}, None),
        ("RAT-B3-Ejecucion-Contrato",
         "Datos de entrega", "Clientes con contrato",
         "Entrega de productos",
         "Ejecucion de contrato", "Sistema de logistica", "5 anos", {}, None),
        ("RAT-B4-Obligacion-Legal",
         "Datos tributarios", "Contribuyentes",
         "Declaraciones al SII",
         "Obligacion legal", "Sistema contable", "10 anos", {}, None),
        ("RAT-B5-Interes-Vital",
         "Datos de salud criticos y contactos de emergencia",
         "Personas en emergencia medica",
         "Atencion medica de urgencia",
         "Interes vital del titular", "Sistema de urgencias", "5 anos", {}, None),
        ("RAT-B7-Otra",
         "Datos varios", "Varios",
         "Caso especial documentado en base legal personalizada",
         "Otra (base legal custom: Art. 13 d)", "Sistema legacy", "5 anos", {}, None),
    ]
    for b in bases:
        ok = insert_rat(cur, b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], conn)
        print(f"  {'OK' if ok else 'WARN'} {b[0]}")

    # ========================================
    # AUDIT-1
    # ========================================
    print("\nInsertando AUDIT-1 (auditoria)...")
    ok = insert_rat(cur, "RAT-AUDIT-Cambios",
                    "Datos identificativos", "Clientes",
                    "Caso para prueba de auditoria",
                    "Consentimiento del titular", "Sistema", "3 anos",
                    {}, None, conn)
    # Add audit observation
    cur.execute("UPDATE rats SET observaciones_auditoria = %s WHERE nombre_proceso = 'RAT-AUDIT-Cambios'",
                ("AUDITORIA: RAT creado para verificar log de auditoria en detail view",))
    conn.commit()
    print(f"  {'OK' if ok else 'WARN'} RAT-AUDIT-Cambios")

    # ========================================
    # CONSENTIMIENTOS (5 para los RATs críticos)
    # ========================================
    print("\nInsertando consentimientos...")
    consentimientos_data = [
        ("RAT-C1-Biometrico-TransIntl", "Juan Perez Gonzalez", "juan.perez@empresa.com", "firma_digital",
         "Consentimiento expreso conforme al Art. 16 BIS de la Ley 21.719 para tratamiento de datos biometricos de identificacion mediante huella dactilar para control de asistencia."),
        ("RAT-C3-Salud-Pacientes", "Maria Lopez Silva", "maria.lopez@paciente.cl", "firma_digital",
         "Consentimiento expreso para tratamiento de datos de salud en el marco de la prestracion de servicios de salud conforme al Art. 16 de la Ley 21.719."),
        ("RAT-C7-Biometrico-EIPD-Completa", "Pedro Gomez Soto", "pedro.gomez@empresa.com", "papel",
         "Yo, Pedro Gomez Soto, RUT 12.345.678-9, declaro haber sido informado y otorgo mi consentimiento expreso para que mi empleador trate mis datos biometricos de identificacion (huella dactilar) para fines de control de asistencia conforme al Art. 16 BIS."),
        ("RAT-C8-Salud-ConSentimiento-EIPD-Pendiente", "Ana Martinez Rojas", "ana.martinez@paciente.cl", "web",
         "Consentimiento expreso para tratamiento de datos de salud para la prestracion de servicios medicos conforme al Art. 12 y 16 de la Ley 21.719."),
        ("RAT-EN2-Encargado-Con-Contrato", "Carlos Rodriguez Vega", "carlos.rodriguez@empresa.com", "papel",
         "Consentimiento para tratamiento de datos laborales mediante encargado del tratamiento (PayrollPro Chile SpA) conforme al Art. 14 quater."),
    ]
    for nombre_rat, nombre_tit, email, canal, texto in consentimientos_data:
        cur.execute("SELECT id FROM rats WHERE nombre_proceso = %s LIMIT 1", (nombre_rat,))
        row = cur.fetchone()
        if not row:
            print(f"  WARN No se encontro RAT {nombre_rat}")
            continue
        rat_id = row[0]
        try:
            cur.execute("""
                INSERT INTO consentimientos (
                    company_id, rat_id, nombre_titular, email_titular, canal,
                    texto_consentimiento, fecha_obtencion, activo, ip_origen, created_at
                ) VALUES (%s,%s,%s,%s,CAST(%s AS canalconsentimiento),%s,NOW(),TRUE,'192.168.1.100',NOW())
            """, (COMPANY_ID, rat_id, nombre_tit, email, canal.upper(), texto))
            conn.commit()
            print(f"  OK Consentimiento para {nombre_rat}")
        except Exception as e:
            conn.rollback()
            print(f"  WARN {nombre_rat}: {str(e)[:60]}")

    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    cur.execute("SELECT count(*) FROM rats WHERE nombre_proceso LIKE 'RAT-%'")
    total_rats = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM consentimientos WHERE texto_consentimiento LIKE '%Ley 21.719%' OR texto_consentimiento LIKE '%21 BIS%' OR texto_consentimiento LIKE '%14 quater%'")
    total_cons = cur.fetchone()[0]
    print(f"Total RATs insertados: {total_rats}")
    print(f"Total consentimientos: {total_cons}")

    cur.execute("""
        SELECT
            CASE WHEN datos_sensibles THEN 'Con sensibles' ELSE 'Sin sensibles' END,
            CASE WHEN transferencia_internacional THEN 'Con trans.intl' ELSE 'Sin trans.intl' END,
            estado_eipd,
            count(*)
        FROM rats WHERE nombre_proceso LIKE 'RAT-%'
        GROUP BY 1, 2, 3 ORDER BY 1, 2, 3
    """)
    print("\nDistribucion:")
    print(f"{'Sensibles':<15} {'Trans.Intl':<15} {'EIPD':<25} {'Cant':>5}")
    print("-" * 65)
    for row in cur.fetchall():
        print(f"{row[0]:<15} {row[1]:<15} {row[2]:<25} {row[3]:>5}")

    cur.close()
    conn.close()
    print("\n[OK] Script completado exitosamente.")


if __name__ == "__main__":
    main()