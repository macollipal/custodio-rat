"""
Build 02 — Levantamiento de Requisitos v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/02_Requisitos_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- RF-117: OCI Object Storage para documentos de base legal con fallback chain
- RF-118: Admin Asesor IA (indexar, stats, eliminar chunks)
- RF-119: Descarga de archivos con URL pre-firmada (PAR) o signed GET
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.4"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
OUT_FILE = os.path.join(OUT_DIR, "02_Requisitos_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-02"
DOC_TITLE = "Levantamiento de Requisitos"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc,
              title="LEVANTAMIENTO DE REQUISITOS",
              subtitle="Requisitos Funcionales y No Funcionales · Ley 21.719",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del documento de requisitos."),
        ("1.1", "Junio 2026", "Auditoría técnica: módulos Consentimientos (RF-095 a RF-098) y Tickets ARCO (RF-099 a RF-105)."),
        ("1.2", "Junio 2026", "_Auditoría v1.2: módulo Feriados (RF-110 a RF-113), fixes P0 (token blacklist, IDOR, CSV sanitize, hash chain)._"),
        ("1.3", "Junio 2026", "_Beta Launch: RBAC fixes DT-014 (RF-114), DT-015 (RF-115), /health endpoint (RF-116)._"),
        ("1.4", "Junio 2026", "_Integración OCI Object Storage (RF-117), Admin Asesor IA (RF-118), descarga con PAR/signed GET (RF-119)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc,
                  "Este documento levanta, en formato numerado y trazable, los "
                  f"requisitos funcionales (RF) y no funcionales (RNF) del sistema "
                  f"{BRAND_FULL}, derivados del código fuente y de la documentación "
                  "existente. Cada requisito tiene un identificador único que será "
                  "referenciado por las Historias de Usuario (HU-###), los Casos de "
                  "Uso (CU-###) y los Casos de Prueba (TC-###).")

    doc.add_heading("2. Actores del sistema", level=1)
    actors = [
        ["AC-01", "Superadministrador (superadmin)", "Usuario con acceso total al sistema."],
        ["AC-02", "Administrador de empresa (admin_empresa)", "Gestiona usuarios, RATs, brechas de su empresa. No ve otras empresas."],
        ["AC-03", "Usuario (usuario)", "Consulta y operación limitada. No puede eliminar ni gestionar usuarios."],
        ["AC-04", "DPO", "Contacto en la empresa (contacto_dpo, email_dpo)."],
        ["AC-05", "Titular de datos (externo)", "Formulario público ARCO en /solicitud_derecho."],
        ["AC-06", "Auditor / APDC", "Descarga evidencia vía PDF, CSV, CNI."],
        ["AC-07", "Sistema de IA", "Servicio externo opcional (OpenAI/MiniMax)."],
    ]
    add_styled_table(doc, ["ID", "Actor", "Descripción"], actors,
                     col_widths_cm=[1.8, 4.5, 11.2], first_col_bold=True)

    doc.add_heading("3. Requisitos funcionales (RF)", level=1)

    doc.add_heading("3.1 Módulo de autenticación y usuarios", level=2)
    rf_auth = [
        ["RF-001", "Alta", "Implementado", "Login con JWT (8h) y cookie httpOnly."],
        ["RF-002", "Alta", "Implementado", "Cambiar password propio (6 chars mínimo)."],
        ["RF-003", "Alta", "Implementado", "Admin cambia password de cualquier usuario."],
        ["RF-004", "Alta", "Implementado", "_Logout con revocación de token (blacklist LRU 1000 slots)._"],
        ["RF-005", "Alta", "Implementado", "Rate limit login 5/min por IP."],
        ["RF-006", "Alta", "Implementado", "Auto-seed superadmin con SEED_ADMIN=true."],
        ["RF-007", "Alta", "Implementado", "Roles: superadmin, admin_empresa, usuario."],
        ["RF-008", "Alta", "Implementado", "Listar, actualizar y eliminar usuarios."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_auth,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.2 Módulo de empresas y multi-tenancy", level=2)
    rf_companies = [
        ["RF-010", "Alta", "Implementado", "CRUD empresas con RUT chileno validado."],
        ["RF-011", "Alta", "Implementado", "Editar y eliminar empresas (superadmin para eliminar)."],
        ["RF-012", "Alta", "Implementado", "Asignar usuarios a empresas (tabla user_companies)."],
        ["RF-013", "Alta", "Implementado", "_Aislamiento multi-tenant con check_company_access (IDOR protection)._"],
        ["RF-014", "Media", "Implementado", "Selección de empresa activa desde Topbar/sidebar."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_companies,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("3.3 Módulo RAT (Art. 15 y 16 Ley 21.719)", level=2)
    rf_rat = [
        ["RF-020", "Alta", "Implementado", "7 campos mínimos RAT del Art. 16."],
        ["RF-021", "Alta", "Implementado", "3 campos recomendados adicionales."],
        ["RF-022", "Alta", "Implementado", "Marcar RAT como 'datos_sensibles'."],
        ["RF-023", "Alta", "Implementado", "EIPD (Evaluación de Impacto) por RAT."],
        ["RF-024", "Alta", "Implementado", "Base legal (6 opciones)."],
        ["RF-025", "Media", "Implementado", "Test de 3 pasos para interés legítimo."],
        ["RF-026", "Alta", "Implementado", "Adjuntar documento de base legal (5 MB)."],
        ["RF-027", "Alta", "Implementado", "Cálculo automático de completitud."],
        ["RF-028", "Alta", "Implementado", "Cálculo de nivel de riesgo (bajo/medio/alto/crítico)."],
        ["RF-029", "Alta", "Implementado", "Transiciones de estado: borrador→completo→en_revision→aprobado."],
        ["RF-030", "Alta", "Implementado", "Duplicar RAT con prefijo 'Copia de'."],
        ["RF-031", "Alta", "Implementado", "Eliminar RAT con confirmación."],
        ["RF-032", "Alta", "Implementado", "_Registro de auditoría en audit_log con hash chain._"],
        ["RF-033", "Media", "Implementado", "Registrar revisión periódica (POST /rats/{id}/revision)."],
        ["RF-034", "Alta", "Implementado", "Aprobar RAT (POST /rats/{id}/aprobar)."],
        ["RF-035", "Alta", "Implementado", "_Descargar documento de base legal (GET /rats/{id}/archivo) con fallback OCI._"],
        ["RF-117", "Alta", "Implementado", "_Almacenar documentos de base legal en OCI Object Storage con fallback a BYTEA._"],
        ["RF-119", "Alta", "Implementado", "_Descarga de archivos con URL pre-firmada (PAR) o signed GET directo._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_rat,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.4 Módulo de sugerencias de RAT", level=2)
    rf_sug = [
        ["RF-040", "Alta", "Implementado", "Listar tipos de proceso (GET /rats/sugerencias/tipos)."],
        ["RF-041", "Alta", "Implementado", "Sugerencia precompletada por tipo (POST /rats/sugerencias)."],
        ["RF-042", "Media", "Implementado", "Gestionar rubros y RATs sugeridos."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_sug,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.5 Módulo de brechas de seguridad (Art. 14 bis)", level=2)
    rf_bre = [
        ["RF-050", "Alta", "Implementado", "Registro de brecha con descripción, fecha, RATs afectados, datos comprometidos."],
        ["RF-051", "Alta", "Implementado", "Alerta de plazo APDC 72h."],
        ["RF-052", "Alta", "Implementado", "Editar y eliminar brechas."],
        ["RF-053", "Media", "Implementado", "Filtrar brechas por empresa."],
        ["RF-114", "Alta", "Implementado", "_RBAC: rol usuario NO puede crear brechas (DT-015, 6209e2d). Retorna 403._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_bre,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("3.6 Módulo de derechos ARCO (Art. 14 y 16 bis)", level=2)
    rf_arco = [
        ["RF-060", "Alta", "Implementado", "Formulario público /solicitud_derecho para ejercer derechos ARCO."],
        ["RF-061", "Alta", "Implementado", "Token temporal 5 min contra ataques automatizados."],
        ["RF-062", "Alta", "Implementado", "Titular se identifica con nombre, RUT opcional, email, descripción 2000 chars."],
        ["RF-063", "Alta", "Implementado", "Ticket de gestión (TktSolicitudDerecho) creado automáticamente."],
        ["RF-064", "Alta", "Implementado", "Equipo responde: cambia estado y registra historial."],
        ["RF-065", "Alta", "Implementado", "Adjuntar notas y archivos al ticket."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_arco,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.7 Módulo de Consentimientos (Art. 12 Ley 21.719)", level=2)
    rf_cons = [
        ["RF-095", "Alta", "Implementado", "Registrar consentimiento expreso: nombre titular, email, canal, texto, fecha."],
        ["RF-096", "Alta", "Implementado", "Almacenar IP de origen (ip_origen) para cada consentimiento."],
        ["RF-097", "Alta", "Implementado", "Revocar consentimiento: marca como inactivo + fecha revocación."],
        ["RF-098", "Alta", "Implementado", "Asociar consentimiento a RAT (N:1) y empresa (N:1)."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_cons,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.8 Módulo de Tickets ARCO", level=2)
    rf_tkt = [
        ["RF-099", "Alta", "Implementado", "Crear ticket ARCO manualmente asociado a empresa."],
        ["RF-100", "Alta", "Implementado", "Gestionar estado: ABIERTO, EN_PROCESO, PENDIENTE, RESUELTO."],
        ["RF-101", "Alta", "Implementado", "Gestionar prioridad: BAJA, NORMAL, URGENTE."],
        ["RF-102", "Alta", "Implementado", "Registrar origen: WEB, EMAIL, TELEFONO, PRESENCIAL, MANUAL."],
        ["RF-103", "Alta", "Implementado", "Agregar notas internas con usuario y timestamp."],
        ["RF-104", "Alta", "Implementado", "Historial de cambios de estado."],
        ["RF-105", "Alta", "Implementado", "Fecha de vencimiento SLA 10 días hábiles Chile."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_tkt,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.9 Módulo EIPD (Art. 15 bis Ley 21.719)", level=2)
    rf_eipd = [
        ["RF-116", "Alta", "Implementado", "_Gestionar Evaluaciones de Impacto en Protección de Datos (EIPD) asociadas a RATs._"],
        ["RF-117", "Alta", "Implementado", "_Crear EIPD vinculado 1:1 a un RAT._"],
        ["RF-118", "Alta", "Implementado", "_Actualizar EIPD con workflow (borrador → en proceso → completado)._"],
        ["RF-119", "Alta", "Implementado", "_Listar EIPDs de la empresa con filtros._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_eipd,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True, underline_new=True)

    doc.add_heading("3.10 Módulo de reportes y exportaciones", level=2)
    rf_rep = [
        ["RF-070", "Alta", "Implementado", "_Sanitizar CSV contra inyección (=, +, -, @ prefix apostrophe)._"],
        ["RF-071", "Alta", "Implementado", "Exportar RATs a PDF (GET /rats/export/pdf)."],
        ["RF-072", "Alta", "Implementado", "Exportar RAT individual a PDF."],
        ["RF-073", "Media", "Implementado", "Exportar RAT en formato CNI."],
        ["RF-074", "Alta", "Implementado", "Filtros y ordenamiento con paginación."],
        ["RF-075", "Alta", "Implementado", "KPIs por empresa (GET /rats/dashboard/{company_id})."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_rep,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("3.11 Módulo de auditoría", level=2)
    rf_aud = [
        ["RF-080", "Alta", "Implementado", "Registrar operaciones CRUD en audit_log."],
        ["RF-081", "Alta", "Implementado", "_Hash chain en audit_log: SHA256(prev_hash + timestamp + ...)._"],
        ["RF-082", "Media", "Implementado", "Auditoría global por empresa."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_aud,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True, underline_new=True)

    doc.add_heading("3.12 Módulo de Inteligencia Artificial", level=2)
    rf_ai = [
        ["RF-090", "Baja", "Implementado (opcional)", "Chat IA contextual (POST /ai/ask)."],
        ["RF-091", "Baja", "Implementado (opcional)", "Integración configurable: MINIMAX_API_KEY u OPENAI_API_KEY."],
        ["RF-118", "Alta", "Implementado", "_Gestionar corpus del asesor IA (indexar, stats, eliminar chunks) por superadmin._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_ai,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True)

    doc.add_heading("3.13 Módulo de Feriados", level=2)
    rf_fer = [
        ["RF-110", "Alta", "Implementado", "_CRUD feriados nacionales chilenos (fecha, nombre, tipo)._"],
        ["RF-111", "Alta", "Implementado", "_Upload bulk CSV UTF-8 BOM._"],
        ["RF-112", "Alta", "Implementado", "_Exportar feriados a CSV._"],
        ["RF-113", "Alta", "Implementado", "_Cálculo de días hábiles Chile para SLA tickets ARCO._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Estado", "Descripción"], rf_fer,
                     col_widths_cm=[1.6, 1.6, 2.0, 12.3], first_col_bold=True, underline_new=True)

    doc.add_heading("4. Requisitos No Funcionales", level=1)

    doc.add_heading("4.1 Seguridad y autenticación", level=2)
    rnf_sec = [
        ["RNF-001", "Alta", "Contraseñas hasheadas con bcrypt (passlib + bcrypt)."],
        ["RNF-002", "Alta", "JWT HS256 con expiración 8h."],
        ["RNF-003", "Alta", "Cookies httpOnly y Secure en producción."],
        ["RNF-004", "Alta", "_Revocación de tokens con blacklist LRU (1000 slots)._"],
        ["RNF-005", "Alta", "Rate limiting: login 5/min, cambio password 5/min, ARCO 3/hora, logout 10/min."],
        ["RNF-006", "Alta", "CORS estricto: regex 'https://.*\\.vercel\\.app'."],
        ["RNF-007", "Alta", "SECRET_KEY obligatoria en producción."],
        ["RNF-008", "Alta", "_Sanitización CSV contra inyección de fórmulas._"],
        ["RNF-009", "Alta", "_Validación de acceso por empresa en todos los endpoints con company_id._"],
        ["RNF-114", "Alta", "_RBAC: admin_empresa solo crea RATs en sus empresas asignadas (DT-014)._"],
        ["RNF-115", "Alta", "_RBAC: rol usuario no puede crear brechas de seguridad (DT-015)._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], rnf_sec,
                     col_widths_cm=[1.8, 1.8, 13.9], first_col_bold=True, underline_new=True)

    doc.add_heading("4.2 Rendimiento y disponibilidad", level=2)
    rnf_perf = [
        ["RNF-010", "Alta", "_/health/db responde en menos de 500ms._"],
        ["RNF-011", "Media", "Paginación: 200 RATs por defecto, 50 por página en reportes."],
        ["RNF-012", "Alta", "Disponibilidad 99.5% en Vercel."],
        ["RNF-013", "Media", "PDF de RAT individual en menos de 3s."],
        ["RNF-014", "Alta", "_Optimización N+1 con selectinload/joinedload._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], rnf_perf,
                     col_widths_cm=[1.8, 1.8, 13.9], first_col_bold=True, underline_new=True)

    doc.add_heading("4.3 Cumplimiento normativo", level=2)
    rnf_comp = [
        ["RNF-020", "Alta", "Campos mínimos RAT del Art. 16."],
        ["RNF-021", "Alta", "Alertas: consentimiento inválido biometría, EIPD obligatoria, plazos 72h, transferencias."],
        ["RNF-022", "Alta", "Exportación RAT en formato CNI para APDC."],
        ["RNF-023", "Alta", "Ejercicio de derechos ARCO (Art. 14 y 16 bis)."],
        ["RNF-024", "Alta", "_PII masking en logs (email, RUT, IP, tokens, passwords)._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], rnf_comp,
                     col_widths_cm=[1.8, 1.8, 13.9], first_col_bold=True, underline_new=True)

    doc.add_heading("4.4 Usabilidad y accesibilidad", level=2)
    rnf_ux = [
        ["RNF-030", "Media", "Responsive: sidebar colapsa a menú hamburguesa < 768px."],
        ["RNF-031", "Media", "Navegación completa por teclado en flujos principales."],
        ["RNF-032", "Media", "Toasts (Sonner) en operaciones exitosas y erróneas."],
        ["RNF-033", "Media", "Wizard de 4 pasos con barra de progreso para RAT."],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], rnf_ux,
                     col_widths_cm=[1.8, 1.8, 13.9], first_col_bold=True)

    doc.add_heading("4.5 Mantenibilidad y calidad de código", level=2)
    rnf_maint = [
        ["RNF-040", "Alta", "Cobertura de tests mínima 80% en endpoints críticos."],
        ["RNF-041", "Alta", "Patrón: rutas → servicios → modelos con schemas Pydantic separados."],
        ["RNF-042", "Alta", "TypeScript strict mode en frontend."],
        ["RNF-043", "Alta", "Migración SQLite → PostgreSQL (Neon) sin pérdida."],
        ["RNF-044", "Media", "_Patrón Repository (app/repositories/) para separar lógica de acceso a datos._"],
    ]
    add_styled_table(doc, ["ID", "Prioridad", "Descripción"], rnf_maint,
                     col_widths_cm=[1.8, 1.8, 13.9], first_col_bold=True, underline_new=True)

    doc.add_heading("5. Restricciones y supuestos", level=1)
    add_bullet(doc, "Vercel serverless: máx 60s hobby, 300s pro por request.", bold_prefix="Plataforma: ")
    add_bullet(doc, "Archivos en OCI Object Storage con fallback a BYTEA (límite 5 MB).", bold_prefix="Almacenamiento: ")
    add_bullet(doc, "Dependencia de Neon PostgreSQL en producción.", bold_prefix="Disponibilidad: ")
    add_bullet(doc, "Ley 21.719 entra en vigencia general el 1-dic-2026.", bold_prefix="Marco legal: ")

    doc.add_heading("6. Trazabilidad", level=1)
    add_paragraph(doc, "La matriz de trazabilidad completa (CUST-DOC-MATRIZ) vincula RF → HU → CU → TC.")

    add_risks_appendix(doc, [
        ("R-RF-01", "Sin hash chain previo a v1.2, auditoría histórica no verificable.", "Medio"),
        ("R-RF-02", "Pendientes: CSRF (S14), encryption at rest (C1), service layer (A6).", "Alto"),
    ])
    add_id_glossary(doc, [
        ("RF-###", "Requisito Funcional", "Capacidad observable del sistema."),
        ("RNF-###", "Requisito No Funcional", "Restricción de calidad o seguridad."),
        ("AC-###", "Actor", "Persona o sistema que interactúa con el sistema."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()