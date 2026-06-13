"""
Seed script: Populate QA database with "Claudio Corp" demo data.

Creates:
  - 1 company (Claudio Corp SpA)
  - 2 users (claudio_admin admin_empresa, claudio_user usuario)
  - 10 RATs (varied base_legal, completitud, estado)
  - 5 brechas (varied nivel_riesgo, notificaciones)
  - 14 tickets ARCO (varied tipo/estado/prioridad/origen)

If "Claudio Corp" already exists, deletes via direct SQL first (cascade).
Uses direct SQL for ticket/brecha/rat/user cleanup because the API has
no DELETE endpoint for tickets, and the API is not transactional.

Environment:
  - API: https://custodio-api-qa.vercel.app (Vercel QA)
  - DB:  $DATABASE_URL from backend/.env (Neon PostgreSQL)

Usage:
  cd backend
  python seed_claudio_corp.py
"""
import json
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "psycopg2-binary"])
    import httpx

try:
    import psycopg2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

API_BASE = "https://custodio-api-qa.vercel.app"
BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"
MANIFEST_PATH = BACKEND_DIR / "seed_claudio_corp_manifest.json"

SUPERADMIN_CANDIDATES = [
    ("superadmin", "Admin1234!"),
    ("admin", "Admin1234!"),
    ("admin", "admin1234"),
]

COMPANY_NOMBRE = "Claudio Corp SpA"
COMPANY_RUT = "76.555.444-3"
COMPANY_RUBRO = "Tecnología"
COMPANY_DIRECCION = "Av. Apoquindo 4501, Las Condes, Santiago"
COMPANY_DPO = "Claudio Pérez"
COMPANY_EMAIL_DPO = "dpo@claudiocorp.cl"


def load_db_url() -> str:
    if not ENV_FILE.exists():
        raise RuntimeError(f"No se encontró {ENV_FILE}")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("DATABASE_URL="):
            url = line.split("=", 1)[1].strip().strip('"').strip("'")
            return url
    raise RuntimeError("DATABASE_URL no está definida en backend/.env")


def login(client: httpx.Client) -> dict:
    """Try superadmin candidates. Return login response with token + user."""
    last_err = None
    for username, password in SUPERADMIN_CANDIDATES:
        r = client.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password},
        )
        if r.status_code == 200:
            data = r.json()
            print(f"  [OK] Login: {username} (rol_global={data['user'].get('rol_global')})")
            return data
        last_err = f"{username} → {r.status_code}"
    raise RuntimeError(f"No se pudo hacer login con ningún candidato. Último error: {last_err}")


def db_connect():
    url = load_db_url()
    return psycopg2.connect(url, connect_timeout=10)


def db_cleanup_claudio_corp(db_url: str) -> dict:
    """Delete all Claudio Corp data via direct SQL (cascade). Returns deletion summary."""
    counts = {"tickets": 0, "brechas": 0, "rats": 0, "users": 0, "company": 0}
    conn = psycopg2.connect(db_url, connect_timeout=10)
    try:
        with conn:
            with conn.cursor() as cur:
                # Find company
                cur.execute("SELECT id FROM companies WHERE rut = %s", (COMPANY_RUT,))
                row = cur.fetchone()
                if not row:
                    print("  [skip] No existe Claudio Corp, nada que limpiar")
                    return counts
                company_id = row[0]
                print(f"  [info] Encontrada company_id={company_id}, limpiando datos hijos...")

                # Delete in cascade order. TKT has no DELETE endpoint so direct SQL.
                cur.execute("SELECT id FROM tkt_solicitud_derecho WHERE company_id = %s", (company_id,))
                ticket_ids = [r[0] for r in cur.fetchall()]
                counts["tickets"] = len(ticket_ids)
                if ticket_ids:
                    cur.execute("DELETE FROM tkt_notas WHERE ticket_id = ANY(%s)", (ticket_ids,))
                    cur.execute("DELETE FROM tkt_historial WHERE ticket_id = ANY(%s)", (ticket_ids,))
                    cur.execute("DELETE FROM tkt_adjuntos WHERE ticket_id = ANY(%s)", (ticket_ids,))
                    cur.execute("DELETE FROM tkt_solicitud_derecho WHERE id = ANY(%s)", (ticket_ids,))

                cur.execute("SELECT id FROM security_breaches WHERE company_id = %s", (company_id,))
                brecha_ids = [r[0] for r in cur.fetchall()]
                cur.execute("DELETE FROM security_breaches WHERE id = ANY(%s)", (brecha_ids,))
                counts["brechas"] = cur.rowcount

                # Rats: also delete consentimientos, eipd, audit related
                cur.execute("SELECT id FROM rats WHERE company_id = %s", (company_id,))
                rat_ids = [r[0] for r in cur.fetchall()]
                counts["rats"] = len(rat_ids)
                if rat_ids:
                    cur.execute("DELETE FROM consentimientos WHERE rat_id = ANY(%s)", (rat_ids,))
                    cur.execute("DELETE FROM eipds WHERE rat_id = ANY(%s)", (rat_ids,))
                    cur.execute("DELETE FROM audit_logs WHERE entidad = 'rat' AND entidad_id = ANY(%s)", (rat_ids,))
                    cur.execute("DELETE FROM rats WHERE id = ANY(%s)", (rat_ids,))

                # audit_logs for breaches and tickets (audit_logs has no company_id column;
                # we only clean up entries for entities of THIS company)
                cur.execute("""
                    DELETE FROM audit_logs
                    WHERE (entidad = 'brecha' AND entidad_id = ANY(%s::int[]))
                       OR (entidad = 'ticket' AND entidad_id = ANY(%s::int[]))
                """, (brecha_ids, ticket_ids))

                # users associated to this company
                cur.execute("""
                    DELETE FROM users WHERE id IN (
                      SELECT user_id FROM user_companies WHERE company_id = %s
                    ) RETURNING id
                """, (company_id,))
                counts["users"] = cur.rowcount

                # Also delete users named claudio_admin / claudio_user (in case they exist
                # without company link from prior seed attempts — see fix_claudio_pwd.py)
                cur.execute("""
                    DELETE FROM users WHERE username IN ('claudio_admin', 'claudio_user') RETURNING id
                """)
                extra = cur.rowcount
                if extra:
                    print(f"  [info] Eliminados {extra} usuarios pre-existentes con username claudio_*")
                    counts["users"] += extra

                cur.execute("DELETE FROM companies WHERE id = %s RETURNING id", (company_id,))
                counts["company"] = cur.rowcount

                print(f"  [OK] Cleanup: {counts}")
    finally:
        conn.close()
    return counts


def create_company(client: httpx.Client, headers: dict) -> dict:
    payload = {
        "nombre": COMPANY_NOMBRE,
        "rut": COMPANY_RUT,
        "rubro": COMPANY_RUBRO,
        "direccion": COMPANY_DIRECCION,
        "contacto_dpo": COMPANY_DPO,
        "email_dpo": COMPANY_EMAIL_DPO,
        "descripcion": "Empresa de tecnología enfocada en soluciones SaaS B2B para el mercado chileno.",
        "canal_ejercicio_derechos": COMPANY_EMAIL_DPO,
    }
    r = client.post(f"{API_BASE}/companies/", json=payload, headers=headers)
    if r.status_code != 201:
        raise RuntimeError(f"Company create failed: {r.status_code} {r.text}")
    data = r.json()
    print(f"  [OK] Company creada: id={data['id']} {data['nombre']} (RUT {data['rut']})")
    return data


def create_user(client: httpx.Client, headers: dict, *, username: str, full_name: str, email: str,
                password: str, rol_global: str, company_id: int) -> dict:
    payload = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,
        "rol_global": rol_global,
        "company_id": company_id,
    }
    r = client.post(f"{API_BASE}/auth/users", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"User create failed ({username}): {r.status_code} {r.text}")
    data = r.json()
    print(f"  [OK] User creado: id={data['id']} {username} ({rol_global})")
    return data


# ---------- RAT data (10) ----------

RATS = [
    dict(
        nombre_proceso="Gestión de Clientes CRM",
        categoria_datos="Nombre, RUT, email, teléfono, dirección, historial de compras",
        categoria_titulares="Clientes activos y prospectos comerciales",
        finalidad="Gestión comercial, seguimiento de oportunidades, soporte postventa y fidelización",
        base_legal="Consentimiento del titular",
        fuente_datos="El propio titular mediante formulario web o contacto comercial",
        plazo_retencion="5 años desde la última interacción",
        medidas_seguridad="Cifrado TLS 1.3 en tránsito, AES-256 en reposo, control de acceso por rol, logs de auditoría",
        destinatarios="Equipo comercial y de soporte interno; proveedor CRM (Salesforce) con DPA firmado",
        transferencia_datos="Exportación a Salesforce (USA) bajo cláusulas contractuales tipo",
        transferencia_internacional=True,
        pais_destino="Estados Unidos",
        garantias_transferencia_int="Cláusulas Contractuales Tipo (CCT) UE 2021 + DPA firmado",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Procesamiento de Nómina",
        categoria_datos="RUT, nombre, datos bancarios, AFP, salud, ISAPRE, cargas familiares",
        categoria_titulares="Empleados activos y ex-empleados",
        finalidad="Liquidación de remuneraciones, cotizaciones previsionales y cumplimiento tributario",
        base_legal="Obligación legal",
        fuente_datos="El propio empleado al firmar contrato + organismos previsionales",
        plazo_retencion="10 años tras el término de la relación laboral (Código del Trabajo)",
        medidas_seguridad="Acceso restringido a equipo de RRHH, cifrado, MFA en sistema payroll",
        destinatarios="AFP, ISAPRE, FONASA, Tesorería, Mutual de Seguridad, SII",
        transferencia_datos="No se realizan transferencias internacionales",
        transferencia_internacional=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Onboarding de Empleados",
        categoria_datos="RUT, CV, certificaciones, referencias laborales, antecedentes",
        categoria_titulares="Candidatos y nuevos empleados",
        finalidad="Verificación de identidad, validación de antecedentes y alta contractual",
        base_legal="Ejecución de contrato",
        fuente_datos="El propio titular al enviar postulación y documentos de ingreso",
        plazo_retencion="Vida laboral + 5 años",
        medidas_seguridad="Acceso por rol, cifrado de archivos, MFA para acceso a plataforma RRHH",
        destinatarios="Equipo de RRHH, gerencia del área, Mutual de Seguridad",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Analítica Web con Cookies",
        categoria_datos="Dirección IP, user agent, comportamiento de navegación, cookies",
        categoria_titulares="Visitantes del sitio web corporativo",
        finalidad="Medición de audiencia, análisis de comportamiento y mejora de experiencia de usuario",
        base_legal="Consentimiento del titular",
        fuente_datos="El propio titular al aceptar cookies en el banner",
        plazo_retencion="2 años desde la última visita",
        medidas_seguridad="Anonimización de IP (último octeto), agregación, control de acceso al dashboard",
        destinatarios="Google Analytics 4, equipo de marketing interno",
        transferencia_datos="Exportación agregada a GA4 (USA)",
        transferencia_internacional=True,
        pais_destino="Estados Unidos",
        garantias_transferencia_int="Adequacy decision Privacy Framework + DPA",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Marketing por Email",
        categoria_datos="Nombre, email, preferencias de contenido, historial de clicks",
        categoria_titulares="Suscriptores al newsletter y leads de marketing",
        finalidad="Envío de newsletters, promociones, contenido educativo y segmentación de campañas",
        base_legal="Consentimiento del titular",
        fuente_datos="El propio titular al suscribirse vía formulario",
        plazo_retencion="Hasta revocación del consentimiento",
        medidas_seguridad="Doble opt-in, link de desuscripción en cada email, cifrado TLS",
        destinatarios="Proveedor de email marketing (Mailchimp)",
        datos_sensibles=False,
        decisiones_automatizadas=True,
    ),
    dict(
        nombre_proceso="Verificación de Identidad Biométrica",
        categoria_datos="Huella dactilar, reconocimiento facial, RUT, fecha de nacimiento",
        categoria_titulares="Usuarios que requieren KYC (Know Your Customer)",
        finalidad="Prevención de fraude y cumplimiento normativo anti-lavado de dinero",
        base_legal="Consentimiento del titular",
        fuente_datos="El propio titular al momento del enrolamiento biométrico",
        plazo_retencion="1 año tras la última verificación",
        medidas_seguridad="Cifrado AES-256, hash unidireccional del template biométrico, acceso restringido",
        destinatarios="Proveedor de biometría (Onfido) con DPA firmado",
        datos_sensibles=False,  # Set False: requiere Consentimiento activo previo. Cambiar a True + crear consent si se necesita.
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Reclutamiento y Selección",
        categoria_datos="CV, pretensiones de renta, evaluaciones psicométricas, referencias",
        categoria_titulares="Candidatos a puestos de trabajo",
        finalidad="Evaluación de postulantes, selección de personal y construcción de pipeline",
        base_legal="Consentimiento del titular",
        fuente_datos="El propio titular al enviar CV y completar assessments",
        plazo_retencion="2 años desde la última postulación",
        medidas_seguridad="Acceso restringido a equipo de RRHH, cifrado, control de acceso por rol",
        destinatarios="Empresa de head hunting externa (caso senior) y equipo interno de RRHH",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Encuestas de Satisfacción (NPS)",
        categoria_datos="Email, respuestas de encuesta, score NPS, comentarios",
        categoria_titulares="Clientes activos y usuarios del producto",
        finalidad="Medición de satisfacción, identificación de mejoras y benchmarking",
        base_legal="Interés legítimo",
        fuente_datos="El propio titular al responder la encuesta",
        plazo_retencion="3 años para análisis longitudinal",
        medidas_seguridad="Anonimización en reportes, agregación mínima de n=10",
        destinatarios="Equipo de Customer Success y dirección",
        test_interes_legitimo="1) Finalidad: mejorar servicio - 2) Necesidad: feedback directo de clientes - 3) Balance: bajo riesgo, no afecta derechos",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Gestión de Proveedores",
        categoria_datos="RUT, datos de contacto, información bancaria, contratos",
        categoria_titulares="Proveedores activos y potenciales",
        finalidad="Administración de la relación comercial, pagos y cumplimiento contractual",
        base_legal="Ejecución de contrato",
        fuente_datos="El propio proveedor al firmar contrato y entregar documentación",
        plazo_retencion="7 años tras el término del contrato (tributario)",
        medidas_seguridad="Acceso restringido a equipo de finanzas y operaciones, cifrado",
        destinatarios="Tesorería, SII, bancos para pagos",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
    dict(
        nombre_proceso="Logs de Auditoría del Sistema",
        categoria_datos="Username, IP, timestamp, endpoint accedido, user agent",
        categoria_titulares="Usuarios internos del sistema y usuarios externos con auto-registro",
        finalidad="Detección de incidentes de seguridad, auditoría de accesos y cumplimiento normativo",
        base_legal="Interés legítimo",
        fuente_datos="Generados automáticamente por el sistema",
        plazo_retencion="5 años en línea + 5 años en respaldo frío",
        medidas_seguridad="Hash chain SHA256, PII masking, acceso restringido al equipo de seguridad",
        destinatarios="Equipo de seguridad informática y auditores externos",
        test_interes_legitimo="1) Finalidad: detectar accesos no autorizados - 2) Necesidad: trazabilidad legal - 3) Balance: técnica estándar, no invasiva",
        datos_sensibles=False,
        decisiones_automatizadas=False,
    ),
]


def create_rats(client: httpx.Client, headers: dict, company_id: int) -> list:
    created = []
    for i, rat in enumerate(RATS, 1):
        payload = {**rat, "company_id": company_id}
        r = client.post(f"{API_BASE}/rats/", json=payload, headers=headers)
        if r.status_code not in (200, 201):
            print(f"  [ERROR] RAT {i} '{rat['nombre_proceso']}': {r.status_code} {r.text[:200]}")
            continue
        data = r.json()
        created.append(data)
        print(f"  [OK] RAT {i:2}/10 id={data['id']:3} {rat['nombre_proceso'][:50]}")
    return created


def approve_rat(client: httpx.Client, headers: dict, rat_id: int) -> bool:
    r = client.post(f"{API_BASE}/rats/{rat_id}/aprobar", headers=headers)
    if r.status_code not in (200, 201):
        print(f"  [WARN] No se pudo aprobar RAT {rat_id}: {r.status_code} {r.text[:200]}")
        return False
    return True


# ---------- Brechas data (5) ----------

def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def make_brechas(company_id: int) -> list:
    base = datetime(2026, 4, 1, tzinfo=timezone.utc)
    return [
        dict(
            company_id=company_id,
            descripcion="Phishing dirigido al jefe de operaciones. Correo suplantó identidad del CFO solicitando transferencia urgente a cuenta no verificada. Un empleado realizó la transferencia antes de verificar.",
            fecha_deteccion=iso(base.replace(month=4, day=15, hour=10, minute=30)),
            rats_afectados="1, 9",  # CRM, Gestión de Proveedores
            datos_comprometidos="Credenciales email corporativo, datos bancarios de proveedores",
            medidas_adoptadas="Rotación inmediata de contraseñas, MFA forzado, bloqueo de transferencia bancaria, capacitación anti-phishing al equipo",
            nivel_riesgo="medio",
            volumen_titulares_afectados=120,
            incluye_datos_sensibles=False,
            incluye_datos_financieros=True,
            notificado_apdc=True,
            fecha_notificacion_apdc=iso(base.replace(month=4, day=17, hour=14, minute=0)),
            notificado_titulares=False,
        ),
        dict(
            company_id=company_id,
            descripcion="Ataque de ransomware en servidor secundario que aloja respaldos. El atacante cifró archivos y solicitó rescate en criptomonedas. No se vio afectado el sistema principal de producción.",
            fecha_deteccion=iso(base.replace(month=5, day=2, hour=3, minute=45)),
            rats_afectados="1, 2, 9",
            datos_comprometidos="Respaldos de nóminas históricas, datos de proveedores, contratos",
            medidas_adoptadas="Aislamiento del servidor afectado, restauración desde respaldo offline, denuncia a PDI, auditoría forense, hardening de servidores de respaldo",
            nivel_riesgo="critico",
            volumen_titulares_afectados=850,
            incluye_datos_sensibles=False,
            incluye_datos_financieros=True,
            notificado_apdc=True,
            fecha_notificacion_apdc=iso(base.replace(month=5, day=3, hour=11, minute=0)),
            notificado_titulares=True,
            fecha_notificacion_titulares=iso(base.replace(month=5, day=8, hour=9, minute=0)),
        ),
        dict(
            company_id=company_id,
            descripcion="Bucket S3 de respaldos temporales quedó configurado como público por error humano durante una mantención. Expuesto durante 6 días antes de ser detectado por un auditor externo.",
            fecha_deteccion=iso(base.replace(month=5, day=20, hour=16, minute=15)),
            rats_afectados="3, 7",
            datos_comprometidos="CVs de candidatos y documentación de onboarding",
            medidas_adoptadas="Cierre inmediato del acceso público, revisión de todos los buckets, cambio de políticas IAM, alerta automatizada en CloudTrail",
            nivel_riesgo="alto",
            volumen_titulares_afectados=320,
            incluye_datos_sensibles=False,
            incluye_datos_financieros=False,
            notificado_apdc=True,
            fecha_notificacion_apdc=iso(base.replace(month=5, day=22, hour=10, minute=30)),
            notificado_titulares=False,
        ),
        dict(
            company_id=company_id,
            descripcion="Notebook corporativa robada desde el vehículo de una empleada. El disco estaba cifrado con BitLocker y contaba con protección TPM, sin acceso biométrico configurado.",
            fecha_deteccion=iso(base.replace(month=5, day=25, hour=8, minute=0)),
            rats_afectados="2, 3",
            datos_comprometidos="Información corporativa cifrada (sin evidencia de acceso)",
            medidas_adoptadas="Wipe remoto vía Intune, denuncia en Carabineros, cambio de contraseñas corporativas, seguro de equipos activado",
            nivel_riesgo="bajo",
            volumen_titulares_afectados=5,
            incluye_datos_sensibles=False,
            incluye_datos_financieros=False,
            notificado_apdc=False,
            notificado_titulares=False,
        ),
        dict(
            company_id=company_id,
            descripcion="Credenciales de API key de un servicio de producción fueron expuestas accidentalmente en un repositorio público de GitHub por un desarrollador junior.",
            fecha_deteccion=iso(base.replace(month=6, day=1, hour=11, minute=20)),
            rats_afectados="10",
            datos_comprometidos="Logs de auditoría potencialmente accesibles",
            medidas_adoptadas="Rotación inmediata de la API key, escaneo de logs por accesos no autorizados, implementación de git-secrets, capacitación al equipo de desarrollo",
            nivel_riesgo="alto",
            volumen_titulares_afectados=2100,
            incluye_datos_sensibles=False,
            incluye_datos_financieros=False,
            notificado_apdc=False,
            notificado_titulares=False,
        ),
    ]


def create_brechas(client: httpx.Client, headers: dict, company_id: int) -> list:
    brechas = make_brechas(company_id)
    created = []
    for i, b in enumerate(brechas, 1):
        r = client.post(f"{API_BASE}/brechas/", json=b, headers=headers)
        if r.status_code not in (200, 201):
            print(f"  [ERROR] Brecha {i}: {r.status_code} {r.text[:200]}")
            continue
        data = r.json()
        created.append(data)
        print(f"  [OK] Brecha {i}/5 id={data['id']:3} nivel={b['nivel_riesgo']:9} desc={b['descripcion'][:60]}...")
    return created


# ---------- Tickets ARCO data (14) ----------

def make_tickets(company_id: int) -> list:
    return [
        # 4 acceso
        dict(company_id=company_id, tipo="acceso", prioridad="normal", origen="web",
             titular_nombre="Juan Pérez González", titular_email="juan.perez.gonzalez@example.cl",
             titular_rut="12.345.678-5", descripcion="Solicita copia de todos los datos personales que la empresa mantiene sobre él."),
        dict(company_id=company_id, tipo="acceso", prioridad="alta", origen="email",
             titular_nombre="María José Soto", titular_email="mjsoto@example.cl",
             titular_rut="15.678.234-9", descripcion="Requiere acceso urgente a sus datos para presentar recurso legal. Plazo judicial próximo."),
        dict(company_id=company_id, tipo="acceso", prioridad="normal", origen="telefono",
             titular_nombre="Pedro Ramírez Vidal", titular_email="pramirez@example.cl",
             titular_rut="10.234.567-2", descripcion="Solicita conocer qué datos se recopilaron durante el proceso de selección del cual fue descartado."),
        dict(company_id=company_id, tipo="acceso", prioridad="baja", origen="manual",
             titular_nombre="Carolina Espinoza", titular_email="c.espinoza@example.cl",
             titular_rut="17.890.123-K", descripcion="Solicita acceso a sus datos de cliente. Caso derivado desde formulario público."),

        # 4 rectificacion
        dict(company_id=company_id, tipo="rectificacion", prioridad="normal", origen="web",
             titular_nombre="Andrés Muñoz Torres", titular_email="amunoz@example.cl",
             titular_rut="13.456.789-3", descripcion="Solicita corregir su dirección registrada. Nueva dirección: Av. Providencia 1234, Depto 502."),
        dict(company_id=company_id, tipo="rectificacion", prioridad="alta", origen="email",
             titular_nombre="Valentina Rojas", titular_email="vrojas@example.cl",
             titular_rut="18.765.432-1", descripcion="Rectificación urgente de email de contacto. Cambió de correo corporativo a personal por término de relación laboral."),
        dict(company_id=company_id, tipo="rectificacion", prioridad="normal", origen="presencial",
             titular_nombre="Felipe Castro", titular_email="fcastro@example.cl",
             titular_rut="11.222.333-4", descripcion="Solicita corregir error en su estado civil registrado en el sistema de nómina."),
        dict(company_id=company_id, tipo="rectificacion", prioridad="baja", origen="web",
             titular_nombre="Camila Vargas", titular_email="cvargas@example.cl",
             titular_rut="16.543.210-8", descripcion="Actualización de número de teléfono de contacto."),

        # 3 cancelacion
        dict(company_id=company_id, tipo="cancelacion", prioridad="normal", origen="email",
             titular_nombre="Rodrigo Sepúlveda", titular_email="rsepulveda@example.cl",
             titular_rut="19.876.543-2", descripcion="Solicita cancelación completa de su cuenta y eliminación de todos los datos asociados."),
        dict(company_id=company_id, tipo="cancelacion", prioridad="alta", origen="web",
             titular_nombre="Isidora Pérez", titular_email="iperez@example.cl",
             titular_rut="14.321.098-7", descripcion="Cancelación de suscripción a newsletter y eliminación de email de todas las bases de marketing."),
        dict(company_id=company_id, tipo="cancelacion", prioridad="normal", origen="telefono",
             titular_nombre="Matías González", titular_email="mgonzalez@example.cl",
             titular_rut="20.123.456-6", descripcion="Solicita eliminación de datos de cliente tras cierre de relación comercial."),

        # 3 oposicion
        dict(company_id=company_id, tipo="oposicion", prioridad="normal", origen="web",
             titular_nombre="Daniela Fuentes", titular_email="dfuentes@example.cl",
             titular_rut="21.654.987-3", descripcion="Se opone al tratamiento de sus datos con fines de marketing directo."),
        dict(company_id=company_id, tipo="oposicion", prioridad="baja", origen="manual",
             titular_nombre="Sebastián Morales", titular_email="smorales@example.cl",
             titular_rut="22.987.654-K", descripcion="Se opone al envío de encuestas de satisfacción. Prefiere no ser contactado nuevamente."),
        dict(company_id=company_id, tipo="oposicion", prioridad="normal", origen="presencial",
             titular_nombre="Francisca Silva", titular_email="fsilva@example.cl",
             titular_rut="23.210.987-5", descripcion="Se opone a que sus datos sean compartidos con terceros (proveedores de marketing)."),
    ]


def create_tickets(client: httpx.Client, headers: dict, company_id: int) -> list:
    tickets = make_tickets(company_id)
    created = []
    for i, t in enumerate(tickets, 1):
        r = client.post(f"{API_BASE}/tkt-solicitud-derecho/", json=t, headers=headers)
        if r.status_code not in (200, 201):
            print(f"  [ERROR] Ticket {i}: {r.status_code} {r.text[:200]}")
            continue
        data = r.json()
        created.append(data)
        print(f"  [OK] Ticket {i:2}/14 id={data['id']:3} tipo={t['tipo']:13} prio={t['prioridad']:6} titular={t['titular_nombre']}")
    return created


def update_ticket_state(client: httpx.Client, headers: dict, ticket_id: int, *,
                        estado: str, respuesta_texto: str = None) -> bool:
    payload = {"estado": estado}
    if respuesta_texto:
        payload["respuesta_texto"] = respuesta_texto
    r = client.patch(f"{API_BASE}/tkt-solicitud-derecho/{ticket_id}", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"  [WARN] No se pudo actualizar ticket {ticket_id}: {r.status_code} {r.text[:200]}")
        return False
    return True


def verify_counts(client: httpx.Client, headers: dict, company_id: int) -> dict:
    counts = {}
    r = client.get(f"{API_BASE}/rats/?company_id={company_id}", headers=headers)
    counts["rats"] = len(r.json()) if r.status_code == 200 else -1
    r = client.get(f"{API_BASE}/brechas/?company_id={company_id}", headers=headers)
    body = r.json() if r.status_code == 200 else {}
    counts["brechas"] = body.get("total", -1) if isinstance(body, dict) else len(body)
    r = client.get(f"{API_BASE}/tkt-solicitud-derecho/?company_id={company_id}&limit=100", headers=headers)
    body = r.json() if r.status_code == 200 else {}
    counts["tickets"] = body.get("total", -1) if isinstance(body, dict) else len(body)
    return counts


def main():
    print("=" * 70)
    print("CUSTODIO RAT Manager — Seed Claudio Corp SpA")
    print("=" * 70)
    print(f"API: {API_BASE}")
    print(f"DB:  {load_db_url().split('@')[-1]}")  # hide credentials
    print()

    # Step 0: cleanup
    print("=" * 70)
    print("STEP 0 — Cleanup (DB directo, cascade)")
    print("=" * 70)
    db_cleanup_claudio_corp(load_db_url())
    print()

    with httpx.Client(timeout=30.0) as client:
        # Step 1: login
        print("=" * 70)
        print("STEP 1 — Login superadmin")
        print("=" * 70)
        login_data = login(client)
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print()

        # Step 2: create company
        print("=" * 70)
        print("STEP 2 — Crear empresa Claudio Corp SpA")
        print("=" * 70)
        company = create_company(client, headers)
        company_id = company["id"]
        print()

        # Step 3: create users
        print("=" * 70)
        print("STEP 3 — Crear usuarios (claudio_admin, claudio_user)")
        print("=" * 70)
        admin_user = create_user(
            client, headers,
            username="claudio_admin",
            full_name="Claudio Pérez",
            email="admin@claudiocorp.cl",
            password="Claudio2026!",
            rol_global="admin_empresa",
            company_id=company_id,
        )
        user = create_user(
            client, headers,
            username="claudio_user",
            full_name="Andrea Silva",
            email="user@claudiocorp.cl",
            password="Claudio2026!",
            rol_global="usuario",
            company_id=company_id,
        )
        print()

        # Step 4: create 10 RATs
        print("=" * 70)
        print("STEP 4 — Crear 10 RATs")
        print("=" * 70)
        rats = create_rats(client, headers, company_id)

        # Approve 2 of them for realism
        if len(rats) >= 2:
            print()
            print("  Aprobando 2 RATs (CRM y Nómina):")
            approve_rat(client, headers, rats[0]["id"])
            approve_rat(client, headers, rats[1]["id"])
            print(f"  [OK] RATs {rats[0]['id']} y {rats[1]['id']} aprobados")
        print()

        # Step 5: create 5 brechas
        print("=" * 70)
        print("STEP 5 — Crear 5 brechas de seguridad")
        print("=" * 70)
        brechas = create_brechas(client, headers, company_id)
        print()

        # Step 6: create 14 tickets
        print("=" * 70)
        print("STEP 6 — Crear 14 tickets ARCO")
        print("=" * 70)
        tickets = create_tickets(client, headers, company_id)

        # Mark 3 tickets as resolved with response (the urgent ones)
        if len(tickets) >= 3:
            print()
            print("  Resolviendo 3 tickets (urgentes) con respuesta:")
            # María José Soto (alta prioridad) - acceso urgente legal
            update_ticket_state(client, headers, tickets[1]["id"], estado="resuelto",
                                respuesta_texto="Se entrega archivo ZIP con todos los datos personales encriptado con clave enviada por canal separado. Plazo cumplido.")
            # Valentina Rojas (alta prioridad) - rectificación email
            update_ticket_state(client, headers, tickets[5]["id"], estado="resuelto",
                                respuesta_texto="Email actualizado correctamente en todos los sistemas. Confirmación enviada al nuevo correo.")
            # Isidora Pérez (alta prioridad) - cancelación marketing
            update_ticket_state(client, headers, tickets[9]["id"], estado="resuelto",
                                respuesta_texto="Cancelación procesada. Email eliminado de Mailchimp y CRM. Confirmación enviada.")

            # Mark 2 as en_proceso
            if len(tickets) > 11:
                update_ticket_state(client, headers, tickets[11]["id"], estado="en_proceso")
                update_ticket_state(client, headers, tickets[12]["id"], estado="en_proceso")
            print(f"  [OK] 3 tickets resueltos con respuesta, 2 marcados en_proceso")
        print()

        # Step 7: verify
        print("=" * 70)
        print("STEP 7 — Verificación final")
        print("=" * 70)
        counts = verify_counts(client, headers, company_id)
        print(f"  RATs:     {counts['rats']} (esperado 10)")
        print(f"  Brechas:  {counts['brechas']} (esperado 5)")
        print(f"  Tickets:  {counts['tickets']} (esperado 14)")
        print()

        # Save manifest
        manifest = {
            "company": {"id": company_id, "nombre": COMPANY_NOMBRE, "rut": COMPANY_RUT},
            "users": {
                "claudio_admin": {"id": admin_user["id"], "username": "claudio_admin",
                                  "password": "Claudio2026!", "rol": "admin_empresa"},
                "claudio_user": {"id": user["id"], "username": "claudio_user",
                                 "password": "Claudio2026!", "rol": "usuario"},
            },
            "rats": [{"id": r["id"], "nombre_proceso": r["nombre_proceso"]} for r in rats],
            "brechas": [{"id": b["id"], "nivel_riesgo": b["nivel_riesgo"]} for b in brechas],
            "tickets": [{"id": t["id"], "tipo": t["tipo"], "titular": t["titular_nombre"]} for t in tickets],
            "counts": counts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  [OK] Manifest guardado: {MANIFEST_PATH}")
        print()

    print("=" * 70)
    print("DONE — Claudio Corp poblada")
    print("=" * 70)


if __name__ == "__main__":
    main()