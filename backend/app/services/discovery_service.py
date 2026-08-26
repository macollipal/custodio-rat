"""
Servicio de Data Discovery & Mapping.
Escanea bases de datos externas buscando columnas con datos personales (Ley 21.719).
"""

import logging
import re
import socket
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.crypto import _get_fernet
from app.models.discovery import DataSource, DiscoveryFinding, DiscoveryRun
from app.models.rat import RAT

logger = logging.getLogger(__name__)

# ── Clasificación de columnas ─────────────────────────────────────────────────
# (patron_en_nombre_columna, categoria, descripcion, confianza_base)

CLASIFICACION = [
    (r"rut|r\.u\.t|run|dni|cedula|documento_id|doc_id|nid|national_id|passport|pasaporte", "IDENTIFICADOR", "RUT / Documento de identidad", 95),
    (r"nombre_completo|full_name|nombre_titular|nombre_persona", "IDENTIFICADOR", "Nombre completo", 90),
    (r"\bnombre\b|first_name|nombre_cliente|nombre_usuario|cliente_nombre", "IDENTIFICADOR", "Nombre", 80),
    (r"apellido|last_name|segundo_nombre|segundo_apellido", "IDENTIFICADOR", "Apellido", 85),
    (r"fecha_nac|fecha_nacimiento|birthdate|birth_date|fec_nac|fnac|nacimiento", "IDENTIFICADOR", "Fecha de nacimiento", 95),
    (r"email|correo|e_mail|mail_address|email_address|titular_email|correo_electronico", "CONTACTO", "Correo electrónico", 95),
    (r"telefono|phone|celular|movil|fono|tel\b|mobile|numero_contacto|fono_contacto", "CONTACTO", "Teléfono", 90),
    (r"direccion|address|domicilio|calle\b|ciudad|commune|comuna|region|localidad|codigo_postal|zip_code", "CONTACTO", "Dirección", 85),
    (r"latitud|longitud|\blat\b|\blon\b|\blng\b|coordenada|gps|geoloc|ubicacion_geo", "UBICACION_PRECISA", "Coordenadas GPS", 95),
    (r"saldo|cuenta_bancaria|numero_cuenta|banco|tarjeta|credito|debito|iban|swift|cvc|cvv|numero_tarjeta", "FINANCIERO", "Datos financieros", 95),
    (r"salud|medic|diagn|enferm|health|patolog|clinico|hospital|atencion_medica|ficha_medica", "SENSIBLE_SALUD", "Datos de salud", 90),
    (r"biometri|huella|dactilar|facial|iris|retina|reconocimiento_facial", "SENSIBLE_BIOMETRICO", "Datos biométricos", 95),
    (r"religion|credo|\bfe\b|culto|creencia", "SENSIBLE_RELIGIOSO", "Creencias religiosas", 90),
    (r"partido_politico|afiliacion_politica|opinion_politica|sindicato|sindical", "SENSIBLE_POLITICO", "Opiniones políticas", 90),
    (r"genero|sexo\b|gender|orientacion_sexual|identidad_genero", "DEMOGRAFICO", "Género / Orientación sexual", 90),
    (r"\bedad\b|\bage\b|raza|etnia|nacionalidad|origen_etnico", "DEMOGRAFICO", "Datos demográficos", 80),
    (r"ip_address|ip_addr|user_agent|device_id|session_id|cookie_id|fingerprint", "TECNICO", "Identificador técnico", 85),
]


def _clasificar_columna(nombre: str) -> Optional[tuple]:
    """Retorna (categoria, descripcion, confianza) si la columna contiene datos personales."""
    nombre_lower = nombre.lower()
    for patron, categoria, descripcion, confianza in CLASIFICACION:
        if re.search(patron, nombre_lower):
            return categoria, descripcion, confianza
    return None


# ── Cifrado de credenciales ───────────────────────────────────────────────────

def encrypt_password(password: str) -> str:
    f = _get_fernet()
    return f.encrypt(password.encode()).decode()


def decrypt_password(password_enc: str) -> str:
    f = _get_fernet()
    return f.decrypt(password_enc.encode()).decode()


# ── Conexión directa con drivers nativos ─────────────────────────────────────
# Usamos psycopg2 / pymssql directamente (sin SQLAlchemy engine) para evitar
# diferencias de dialecto y opciones de ejecución incompatibles entre motores.

QUERY_COLUMNS_PG = """
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = %s
  AND table_name NOT IN ('alembic_version','django_migrations','spatial_ref_sys')
ORDER BY table_name, ordinal_position
"""

QUERY_COLUMNS_MSSQL = """
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = %s
ORDER BY TABLE_NAME, ORDINAL_POSITION
"""


def _fetch_columns(source: DataSource, schema: str) -> list[dict]:
    """Conecta al motor externo y retorna los metadatos de columnas."""
    password = decrypt_password(source.password_enc)

    if source.tipo == "postgresql":
        import psycopg2
        _prev = socket.getdefaulttimeout()
        socket.setdefaulttimeout(15)
        try:
            conn = psycopg2.connect(
                host=source.host,
                port=source.port,
                dbname=source.database_name,
                user=source.username,
                password=password,
                connect_timeout=10,
                options=f"-c search_path={schema}",
            )
        finally:
            socket.setdefaulttimeout(_prev)
        try:
            conn.set_session(readonly=True)
            cur = conn.cursor()
            cur.execute(QUERY_COLUMNS_PG, (schema,))
            rows = cur.fetchall()
        finally:
            conn.close()

    elif source.tipo == "sqlserver":
        import pymssql
        conn = pymssql.connect(
            server=source.host,
            port=str(source.port),
            database=source.database_name,
            user=source.username,
            password=password,
            timeout=10,
            login_timeout=10,
            tds_version="7.3",
            conn_properties="SET ANSI_WARNINGS ON;",
        )
        try:
            cur = conn.cursor()
            cur.execute(QUERY_COLUMNS_MSSQL, (schema,))
            rows = cur.fetchall()
        finally:
            conn.close()

    else:
        raise ValueError(f"Tipo de conector no soportado: {source.tipo}")

    return [
        {"table_name": row[0], "column_name": row[1], "data_type": row[2]}
        for row in rows
    ]


# ── Gap Analysis ──────────────────────────────────────────────────────────────

# Mapa de categoría detectada → palabras clave en RAT.categoria_datos
_CATEGORIA_KEYWORDS = {
    "IDENTIFICADOR": ["identificador", "nombre", "rut", "dni", "documento", "rut/rni", "nombre completo", "fecha nac"],
    "CONTACTO": ["contacto", "email", "correo", "teléfono", "telefono", "dirección", "direccion"],
    "UBICACION_PRECISA": ["ubicación", "ubicacion", "gps", "coordenada", "geoloc", "localización"],
    "FINANCIERO": ["financiero", "bancario", "cuenta", "tarjeta", "crédito", "debito", "saldo"],
    "SENSIBLE_SALUD": ["salud", "médico", "medico", "clínico", "clinico", "diagnóstico", "hospital"],
    "SENSIBLE_BIOMETRICO": ["biométrico", "biometrico", "huella", "facial", "iris", "dactilar"],
    "SENSIBLE_RELIGIOSO": ["religioso", "religión", "religion", "credo", "culto"],
    "SENSIBLE_POLITICO": ["político", "politico", "partido", "sindicato", "sindical"],
    "DEMOGRAFICO": ["demográfico", "demografico", "género", "genero", "sexo", "edad", "etnia", "raza"],
    "TECNICO": ["técnico", "tecnico", "identificador técnico", "cookie", "ip", "device"],
}


def _es_gap(categoria: str, rats: list[RAT]) -> bool:
    """True si ningún RAT de la empresa cubre esta categoría."""
    if not rats:
        return True
    keywords = _CATEGORIA_KEYWORDS.get(categoria, [])
    for rat in rats:
        cat_lower = (rat.categoria_datos or "").lower()
        if any(kw in cat_lower for kw in keywords):
            return False
    return True


# ── Endpoint principal ────────────────────────────────────────────────────────

def ejecutar_escaneo(db: Session, source: DataSource, ejecutado_por: str) -> DiscoveryRun:
    """
    Escanea information_schema de la fuente y guarda hallazgos.
    Sincrónico. Soporta PostgreSQL (psycopg2) y SQL Server (pymssql).
    """
    run = DiscoveryRun(
        source_id=source.id,
        company_id=source.company_id,
        estado="en_proceso",
        ejecutado_por=ejecutado_por,
    )
    db.add(run)
    db.flush()

    try:
        schema = source.schema_name or ("public" if source.tipo == "postgresql" else "dbo")
        columns = _fetch_columns(source, schema)

        # RATs existentes de la empresa para gap analysis
        rats = db.query(RAT).filter(
            RAT.company_id == source.company_id,
            RAT.deleted_at.is_(None) if hasattr(RAT, "deleted_at") else True,
        ).all()

        tablas_vistas = set()
        hallazgos = []

        for col in columns:
            tablas_vistas.add(col["table_name"])
            clasificacion = _clasificar_columna(col["column_name"])
            if not clasificacion:
                continue
            categoria, descripcion, confianza = clasificacion
            es_gap = _es_gap(categoria, rats)

            finding = DiscoveryFinding(
                run_id=run.id,
                table_name=col["table_name"],
                column_name=col["column_name"],
                data_type_sql=col["data_type"],
                categoria=categoria,
                descripcion=descripcion,
                confianza=confianza,
                es_gap=es_gap,
            )
            hallazgos.append(finding)

        db.bulk_save_objects(hallazgos)

        run.estado = "completado"
        run.finished_at = datetime.now(timezone.utc)
        run.total_tablas = len(tablas_vistas)
        run.total_columnas = len(columns)
        run.total_hallazgos = len(hallazgos)
        run.total_gaps = sum(1 for f in hallazgos if f.es_gap)
        db.commit()
        db.refresh(run)

        logger.info(
            "Discovery completado source_id=%s run_id=%s hallazgos=%s gaps=%s",
            source.id, run.id, run.total_hallazgos, run.total_gaps,
        )
        return run

    except Exception as exc:
        run.estado = "error"
        run.finished_at = datetime.now(timezone.utc)
        run.error_msg = str(exc)[:1000]
        db.commit()
        logger.error("Discovery error source_id=%s: %s", source.id, exc)
        raise


# ── Sugerencias de RAT ────────────────────────────────────────────────────────

# Mapa categoría → template de RAT sugerido
_RAT_TEMPLATES = {
    "IDENTIFICADOR": {
        "nombre_proceso": "Gestión de identificadores personales",
        "categoria_datos": "Identificadores (RUT, nombre completo, fecha de nacimiento)",
        "categoria_titulares": "Clientes / Usuarios",
        "finalidad": "Identificación y autenticación de titulares",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Proporcionados directamente por el titular",
        "plazo_retencion": "Mientras dure la relación contractual + 5 años",
    },
    "CONTACTO": {
        "nombre_proceso": "Gestión de datos de contacto",
        "categoria_datos": "Datos de contacto (email, teléfono, dirección)",
        "categoria_titulares": "Clientes / Usuarios",
        "finalidad": "Comunicación y notificación al titular",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Proporcionados directamente por el titular",
        "plazo_retencion": "Mientras dure la relación contractual",
    },
    "UBICACION_PRECISA": {
        "nombre_proceso": "Tratamiento de datos de ubicación",
        "categoria_datos": "Datos de geolocalización (coordenadas GPS, ubicación precisa)",
        "categoria_titulares": "Usuarios del servicio",
        "finalidad": "Prestación del servicio basado en ubicación",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Recopilados automáticamente del dispositivo del titular",
        "plazo_retencion": "90 días desde recolección",
    },
    "FINANCIERO": {
        "nombre_proceso": "Gestión de datos financieros",
        "categoria_datos": "Datos financieros y bancarios",
        "categoria_titulares": "Clientes",
        "finalidad": "Procesamiento de pagos y facturación",
        "base_legal": "Ejecución de contrato",
        "fuente_datos": "Proporcionados por el titular al realizar transacciones",
        "plazo_retencion": "7 años (plazo tributario chileno)",
    },
    "SENSIBLE_SALUD": {
        "nombre_proceso": "Tratamiento de datos de salud",
        "categoria_datos": "Datos de salud y médicos (categoría especial)",
        "categoria_titulares": "Pacientes / Usuarios del servicio de salud",
        "finalidad": "Prestación de atención médica y gestión clínica",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Proporcionados por el titular o su médico tratante",
        "plazo_retencion": "15 años según normativa sanitaria",
    },
    "SENSIBLE_BIOMETRICO": {
        "nombre_proceso": "Tratamiento de datos biométricos",
        "categoria_datos": "Datos biométricos (huella dactilar, reconocimiento facial)",
        "categoria_titulares": "Empleados / Usuarios del sistema de control de acceso",
        "finalidad": "Control de acceso e identificación segura",
        "base_legal": "Datos biométricos de identificación (Art. 16 BIS)",
        "fuente_datos": "Recopilados directamente del titular con su consentimiento",
        "plazo_retencion": "Hasta término de la relación laboral/contractual",
    },
    "DEMOGRAFICO": {
        "nombre_proceso": "Análisis demográfico",
        "categoria_datos": "Datos demográficos (género, edad, etnia, nacionalidad)",
        "categoria_titulares": "Usuarios / Clientes",
        "finalidad": "Análisis estadístico y segmentación de servicios",
        "base_legal": "Interés legítimo",
        "fuente_datos": "Proporcionados por el titular o inferidos del perfil",
        "plazo_retencion": "Mientras dure la relación contractual",
        "test_interes_legitimo": '{"paso1":"Existe interés legítimo real en analizar datos demográficos para mejorar los servicios ofrecidos a los titulares.","paso2":"El tratamiento es necesario para segmentar y personalizar adecuadamente los servicios, no existe alternativa menos invasiva.","paso3":"El tratamiento no perjudica los derechos de los titulares ya que los datos se usan en forma agregada y anonimizada."}',
    },
    "TECNICO": {
        "nombre_proceso": "Tratamiento de identificadores técnicos",
        "categoria_datos": "Identificadores técnicos (dirección IP, cookies, device ID)",
        "categoria_titulares": "Usuarios de la plataforma digital",
        "finalidad": "Seguridad, autenticación y mejora del servicio",
        "base_legal": "Interés legítimo",
        "fuente_datos": "Recopilados automáticamente al usar el servicio",
        "plazo_retencion": "13 meses (normativa cookies EU — referencia)",
        "test_interes_legitimo": '{"paso1":"Existe interés legítimo real en recopilar identificadores técnicos para garantizar la seguridad y el correcto funcionamiento del servicio.","paso2":"El tratamiento es necesario para autenticar usuarios y prevenir fraudes, sin alternativa técnica menos intrusiva.","paso3":"El impacto en los titulares es mínimo y proporcional, ya que los datos técnicos no revelan contenido personal sensible."}',
    },
    "SENSIBLE_RELIGIOSO": {
        "nombre_proceso": "Tratamiento de datos de creencias religiosas",
        "categoria_datos": "Creencias religiosas (categoría especial)",
        "categoria_titulares": "Usuarios / Clientes",
        "finalidad": "Personalización de servicios conforme a creencias del titular",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Proporcionados directamente por el titular",
        "plazo_retencion": "Mientras dure la relación contractual",
    },
    "SENSIBLE_POLITICO": {
        "nombre_proceso": "Tratamiento de datos de opiniones políticas",
        "categoria_datos": "Opiniones políticas y afiliación sindical (categoría especial)",
        "categoria_titulares": "Empleados / Afiliados",
        "finalidad": "Gestión de representación sindical o participación política",
        "base_legal": "Consentimiento del titular",
        "fuente_datos": "Proporcionados directamente por el titular",
        "plazo_retencion": "Mientras dure la relación laboral/afiliación",
    },
}


def generar_sugerencias_rat(findings: list[DiscoveryFinding]) -> list[dict]:
    """
    Genera sugerencias de RAT para los hallazgos marcados como gap.
    Agrupa por categoría y fuente (tabla con más hallazgos de esa categoría).
    """
    from collections import defaultdict

    gaps_por_categoria = defaultdict(list)
    for f in findings:
        if f.es_gap and not f.descartado:
            gaps_por_categoria[f.categoria].append(f)

    sugerencias = []
    for categoria, gap_findings in gaps_por_categoria.items():
        template = _RAT_TEMPLATES.get(categoria)
        if not template:
            continue

        # Tablas involucradas (las más frecuentes primero)
        tablas = sorted(
            set(f.table_name for f in gap_findings),
            key=lambda t: -sum(1 for f in gap_findings if f.table_name == t),
        )
        columnas_ejemplo = [f"{f.table_name}.{f.column_name}" for f in gap_findings[:5]]

        sugerencias.append({
            "categoria": categoria,
            "template_rat": {
                **template,
                "sistema_almacenamiento": ", ".join(tablas[:3]),
            },
            "tablas_involucradas": tablas,
            "columnas_ejemplo": columnas_ejemplo,
            "cantidad_hallazgos": len(gap_findings),
        })

    return sugerencias
