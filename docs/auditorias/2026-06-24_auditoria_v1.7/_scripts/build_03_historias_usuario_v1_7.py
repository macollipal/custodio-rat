"""
Build 03 — Historias de Usuario v1.7 (Sprint 1: FORMADMIN ARCO + Sprint 2: SLA Alert T-2d + Export ARCO)
Genera: docs/documentacion_oficial/03_Historias_Usuario_Custodio_RAT_Manager_v1.7.docx
Cambios v1.7:
- Sprint 1: FORMADMIN ARCO QW1-QW10 (HU-072 a HU-078)
- Sprint 2: SLA Alert T-2d (HU-079 a HU-081), Export ARCO (HU-082 a HU-085)
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.7"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "03_Historias_Usuario_Custodio_RAT_Manager_v1.7.docx")
DOC_CODE = "CUST-DOC-03"
DOC_TITLE = "Historias de Usuario"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="HISTORIAS DE USUARIO",
              subtitle="Backlog priorizado por valor y rol",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial del backlog de historias de usuario."),
        ("1.1", "Junio 2026", "Auditoría técnica: HU-041 a HU-051 para Consentimientos y Tickets ARCO."),
        ("1.2", "Junio 2026", "_Auditoría v1.2: módulo Feriados (HU-052 a HU-055), fixes P0 (blacklist, IDOR, CSV)._"),
        ("1.3", "Junio 2026", "_Beta Launch: RBAC fixes DT-014/DT-015 (HU-056/HU-057), /health (HU-058), módulo EIPD (HU-059/HU-060)._"),
        ("1.4", "Junio 2026", "_Post-OCI: descarga con fallback chain (HU-061), Admin Asesor IA (HU-062/HU-063), OCI storage (EP-12)._"),
        ("1.5", "Junio 2026", "_Seguridad: CSRF (HU-064), Encryption at Rest (HU-065), Service Layer (HU-066), Schemas (HU-067)._"),
        ("1.6", "Junio 2026", "_UI/UX: RatDetailModal (HU-068), Drawer responsive (HU-069), Dashboard clickable (HU-070), Sort estable (HU-071)._"),
        ("1.7", "Junio 2026", "_Sprint 1: FORMADMIN ARCO QW1-QW10 (HU-072 a HU-078). Sprint 2: SLA Alert T-2d (HU-079 a HU-081), Export ARCO (HU-082 a HU-085)._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Introducción", level=1)
    add_paragraph(doc, f"Este documento contiene las historias de usuario (HU) de {BRAND_FULL} "
                      "en formato 'Como/Quiero/Para', con criterios de aceptación, prioridad "
                      "y complejidad estimada (Fibonacci). Organizadas por épicas y trazadas a RF-###.")

    doc.add_heading("2. Épicas del producto", level=1)
    epicas = [
        ["EP-01", "Autenticación y multi-tenancy", "Login, sesión, empresas, aislamiento por rol."],
        ["EP-02", "Gestión del RAT", "Crear, editar, duplicar, eliminar, aprobar."],
        ["EP-03", "Cumplimiento", "Alertas, completitud, riesgos, EIPD, consentimientos."],
        ["EP-04", "Brechas de seguridad", "Art. 14 bis, plazo APDC 72h, notificaciones."],
        ["EP-05", "Derechos ARCO", "Art. 14 y 16 bis, formulario público, ticket."],
        ["EP-06", "Reportes y exportaciones", "CSV, PDF, CNI, dashboard."],
        ["EP-07", "Sugerencias por rubro", "Plantillas prellenadas por industria."],
        ["EP-08", "Auditoría", "Bitácora con hash chain."],
        ["EP-09", "Asistente IA", "Chat contextual sobre la Ley 21.719."],
        ["EP-10", "Feriados nacionales", "Gestión de feriados chilenos para días hábiles."],
        ["EP-11", "Consentimientos y EIPD", "Registro de consentimientos (Art. 12) y Evaluaciones de Impacto (Art. 15 bis)."],
        ["EP-12", "_OCI Object Storage_", "_Almacenamiento de documentos en OCI con fallback a BYTEA._"],
    ]
    add_styled_table(doc, ["ID", "Épica", "Descripción"], epicas,
                     col_widths_cm=[1.8, 5.0, 10.7], first_col_bold=True, underline_new=True)

    doc.add_heading("3. Listado consolidado de historias de usuario", level=1)
    hus = [
        ["HU-001", "EP-01", "RF-001", "Alta", "M", "Login seguro"],
        ["HU-002", "EP-01", "RF-004", "Alta", "S", "Logout efectivo con blacklist"],
        ["HU-003", "EP-01", "RF-002", "Alta", "S", "Cambiar mi contraseña"],
        ["HU-004", "EP-01", "RF-003", "Media", "S", "Admin cambia contraseña de tercero"],
        ["HU-005", "EP-01", "RF-015", "Media", "M", "Onboarding de primera empresa"],
        ["HU-006", "EP-01", "RF-010", "Alta", "M", "Crear empresa"],
        ["HU-007", "EP-01", "RF-007", "Alta", "M", "Crear usuario con rol"],
        ["HU-008", "EP-01", "RF-012", "Alta", "M", "Asignar usuario a empresa"],
        ["HU-009", "EP-01", "RF-013", "Alta", "S", "Aislamiento multi-tenant (IDOR protection)"],
        ["HU-010", "EP-02", "RF-020", "Alta", "L", "Crear RAT con wizard 4 pasos"],
        ["HU-011", "EP-02", "RF-022", "Alta", "M", "Marcar RAT con datos sensibles"],
        ["HU-012", "EP-02", "RF-024", "Alta", "M", "Seleccionar base legal"],
        ["HU-013", "EP-02", "RF-025", "Media", "M", "Test de interés legítimo (3 pasos)"],
        ["HU-014", "EP-02", "RF-026", "Alta", "L", "Adjuntar documento de base legal"],
        ["HU-015", "EP-02", "RF-028", "Alta", "M", "Ver nivel de riesgo calculado"],
        ["HU-016", "EP-02", "RF-029", "Alta", "M", "Cambiar estado del RAT"],
        ["HU-017", "EP-02", "RF-030", "Media", "S", "Duplicar RAT"],
        ["HU-018", "EP-02", "RF-034", "Alta", "S", "Aprobar RAT"],
        ["HU-019", "EP-02", "RF-033", "Media", "S", "Registrar revisión periódica"],
        ["HU-020", "EP-04", "RF-050", "Alta", "L", "Registrar brecha de seguridad"],
        ["HU-021", "EP-04", "RF-051", "Alta", "M", "Alertar plazo APDC 72h"],
        ["HU-022", "EP-05", "RF-060", "Alta", "L", "Presentar formulario ARCO público"],
        ["HU-023", "EP-05", "RF-062", "Alta", "M", "Crear solicitud ARCO con token"],
        ["HU-024", "EP-05", "RF-064", "Alta", "M", "Responder solicitud ARCO"],
        ["HU-025", "EP-05", "RF-063", "Alta", "L", "Gestionar ticket TKT"],
        ["HU-026", "EP-06", "RF-074", "Alta", "L", "Filtrar y ordenar reportes"],
        ["HU-027", "EP-06", "RF-070", "Alta", "M", "Exportar RATs a CSV (sanitizado)"],
        ["HU-028", "EP-06", "RF-071", "Alta", "L", "Exportar RATs a PDF"],
        ["HU-029", "EP-06", "RF-072", "Alta", "M", "Exportar RAT individual a PDF"],
        ["HU-030", "EP-06", "RF-075", "Alta", "L", "Ver dashboard de cumplimiento"],
        ["HU-031", "EP-06", "RF-073", "Media", "M", "Exportar RAT en formato CNI"],
        ["HU-032", "EP-07", "RF-041", "Alta", "M", "Aplicar sugerencia al crear RAT"],
        ["HU-033", "EP-07", "RF-042", "Baja", "L", "Gestionar rubros y sugerencias"],
        ["HU-034", "EP-08", "RF-081", "Alta", "M", "Consultar auditoría con hash chain"],
        ["HU-035", "EP-08", "RF-082", "Media", "M", "Auditoría global por empresa"],
        ["HU-036", "EP-09", "RF-090", "Baja", "M", "Chat IA sobre Ley 21.719"],
        ["HU-037", "EP-03", "RF-027", "Alta", "S", "Ver completitud del RAT"],
        ["HU-038", "EP-03", "RF-023", "Alta", "M", "Marcar RAT con EIPD"],
        ["HU-039", "EP-01", "RF-006", "Alta", "S", "Auto-seed del superadmin inicial"],
        ["HU-040", "EP-03", "RF-031", "Alta", "S", "Eliminar RAT con confirmación"],
        ["HU-041", "EP-03", "RF-095", "Alta", "M", "Registrar consentimiento expreso"],
        ["HU-042", "EP-03", "RF-096", "Alta", "S", "Registrar IP de origen del consentimiento"],
        ["HU-043", "EP-03", "RF-097", "Alta", "S", "Revocar consentimiento"],
        ["HU-044", "EP-03", "RF-098", "Alta", "M", "Vincular consentimiento a RAT"],
        ["HU-045", "EP-05", "RF-099", "Alta", "M", "Crear ticket ARCO manualmente"],
        ["HU-046", "EP-05", "RF-100", "Alta", "S", "Gestionar estado del ticket"],
        ["HU-047", "EP-05", "RF-101", "Alta", "S", "Definir prioridad del ticket"],
        ["HU-048", "EP-05", "RF-102", "Alta", "S", "Registrar origen del ticket"],
        ["HU-049", "EP-05", "RF-103", "Alta", "M", "Agregar notas internas al ticket"],
        ["HU-050", "EP-05", "RF-104", "Alta", "M", "Ver historial de cambios del ticket"],
        ["HU-051", "EP-05", "RF-105", "Alta", "S", "Calcular fecha de vencimiento SLA"],
        ["HU-052", "EP-10", "RF-110", "Alta", "M", "Gestionar feriados nacionales (CRUD)"],
        ["HU-053", "EP-10", "RF-111", "Alta", "M", "Subir feriados en bulk por CSV"],
        ["HU-054", "EP-10", "RF-112", "Alta", "S", "Exportar feriados a CSV"],
        ["HU-055", "EP-10", "RF-113", "Alta", "S", "Verificar días hábiles en cálculo SLA"],
        ["_HU-056", "EP-02", "RF-114", "Alta", "S", "_admin_empresa crea RAT SOLO en sus empresas_"],
        ["_HU-057", "EP-04", "RF-115", "Alta", "S", "_usuario NO puede crear brechas de seguridad_"],
        ["_HU-058", "EP-01", "RF-116", "Media", "S", "_Ver estado del sistema con /health_"],
        ["_HU-059", "EP-03", "RF-117", "Alta", "M", "_Crear EIPD asociado a un RAT_"],
        ["_HU-060", "EP-03", "RF-118", "Alta", "M", "_Actualizar EIPD con workflow_"],
        ["_HU-061", "EP-12", "RF-117/RF-119", "Alta", "M", "_Descargar documento de base legal con fallback OCI_"],
        ["_HU-062", "EP-09", "RF-118", "Alta", "M", "_Indexar corpus del asesor IA_"],
        ["_HU-063", "EP-09", "RF-118", "Alta", "S", "_Ver stats y eliminar chunks del asesor IA_"],
        ["_HU-072", "EP-05", "RF-060", "Alta", "S", "_Validación RUT en vivo con dígito verificador y formateo automático_"],
        ["_HU-073", "EP-05", "RF-062", "Alta", "S", "_Confirmación de email (doble input) con validación visual_"],
        ["_HU-074", "EP-05", "RF-060", "Alta", "S", "_Tooltip en campo Tipo ARCO con referencia a Ley 21.719_"],
        ["_HU-075", "EP-05", "RF-101", "Alta", "S", "_Helper text en Prioridad (2/10 días hábiles / sin urgencia)_"],
        ["_HU-076", "EP-05", "RF-060", "Alta", "S", "_Detección titular duplicado con debounce 800ms + banner amarillo_"],
        ["_HU-077", "EP-05", "RF-023", "Alta", "S", "_Selector RAT con búsqueda debounce 300ms y pre-selección_"],
        ["_HU-078", "EP-05", "RF-060", "Alta", "S", "_Campos representante legal en sección colapsable_"],
        ["_HU-079", "EP-03", "RF-051", "Alta", "S", "_Date picker fecha retroactiva (max=hoy) + nuevos campos contacto_"],
        ["_HU-080", "EP-03", "RF-051", "Alta", "M", "_Notificación SLA Alert T-2 días a DPO por email grupal_"],
        ["_HU-081", "EP-03", "RF-051", "Alta", "M", "_GitHub Actions workflow SLA Alert (cron 4h + workflow_dispatch)_"],
        ["_HU-082", "EP-06", "RF-074", "Alta", "M", "_Exportar tickets ARCO a CSV con filtros_"],
        ["_HU-083", "EP-06", "RF-074", "Alta", "L", "_Exportar tickets ARCO a Excel con color coding_"],
        ["_HU-084", "EP-06", "RF-074", "Alta", "M", "_Exportar tickets ARCO a PDF con tabla compacta_"],
        ["_HU-085", "EP-06", "RF-074", "Alta", "S", "_Dropdown Exportar en UI con CSV/Excel/PDF_"],
    ]
    add_styled_table(doc, ["HU", "Épica", "Trazabilidad", "Prioridad", "Tamaño", "Título"],
                     hus, col_widths_cm=[1.3, 1.3, 1.6, 1.4, 1.2, 10.7], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("4. Especificación detallada de historias críticas", level=1)

    def hu(hu_id, title, epica, rf, rol, want, for_benefit, criterios, prioridad, tamano):
        doc.add_heading(f"{hu_id} — {title}", level=2)
        add_kv_table(doc, [
            ("ID", hu_id),
            ("Épica", epica),
            ("Trazabilidad RF", rf),
            ("Prioridad", prioridad),
            ("Tamaño", tamano),
        ])
        add_paragraph(doc, "Formato Como/Quiero/Para:", bold=True)
        add_paragraph(doc, f"Como {rol}, quiero {want} para {for_benefit}.")
        add_paragraph(doc, "Criterios de aceptación:", bold=True)
        for c in criterios:
            add_bullet(doc, c)

    hu("HU-001", "Login seguro", "EP-01", "RF-001",
       "usuario autenticado del sistema",
       "iniciar sesión con mi username y contraseña",
       "acceder al dashboard y a las funciones de mi rol",
       [
           "El sistema valida credenciales con bcrypt y emite JWT 8h.",
           "El sistema setea cookie httpOnly 'custodio_token'.",
           "_El sistema consulta el token blacklist antes de validar el JWT._",
           "Rate limit 5/min por IP.",
       ], "Alta", "M (3)")

    hu("_HU-056", "_admin_empresa crea RAT SOLO en sus empresas_", "EP-02", "RF-114",
       "_admin_empresa_",
       "_crear RAT únicamente dentro de las empresas que tiene asignadas_",
       "_garantizar aislamiento multi-tenant y prevenir creación de RAT en empresas ajenas_",
       [
           "_El sistema valida que admin_empresa solo pueda crear RAT para empresas donde tiene rol asignado._",
           "_Si admin_empresa intenta crear RAT en empresa no asignada, el sistema retorna error 403._",
           "_Las empresas asignadas se consultan desde la tabla empresa_usuarios._",
       ], "Alta", "S (2)")

    hu("_HU-057", "_usuario NO puede crear brechas de seguridad_", "EP-04", "RF-115",
       "usuario",
       "_acceder exclusivamente a funciones de gestión de brechas de seguridad según su rol_",
       "_impedir que usuarios regulares creen registros de brecha y garantizar que solo personal autorizado pueda hacerlo_",
       [
           "_El sistema verifica RBAC antes de mostrar el formulario de creación de brecha._",
           "_Solo roles admin_empresa y superadmin pueden acceder a POST /brechas._",
           "_Usuarios con rol usuario reciben error 403 al intentar crear brecha._",
       ], "Alta", "S (2)")

    hu("_HU-058", "_Ver estado del sistema con /health_", "EP-01", "RF-116",
       "admin_empresa o superadmin",
       "_consultar el estado de salud del sistema sin autenticación_",
       "_permitir monitoreo externo y alertas de disponibilidad_",
       [
           "_GET /health retorna 200 OK con {status: 'ok', version, timestamp}._",
           "_El endpoint no requiere JWT y está excluido de CSRF._",
           "_Se verifican: conexión a BD, OCI (si está configurado), disco._",
       ], "Media", "S (2)")

    hu("_HU-059", "_Crear EIPD asociado a un RAT_", "EP-03", "RF-117",
       "admin_empresa o DPO",
       "_crear una Evaluación de Impacto en la Protección de Datos (EIPD) vinculada a un RAT específico_",
       "_documentar el análisis de riesgos previo a tratamientos de alto riesgo conforme Art. 15 bis Ley 21.719_",
       [
           "_El usuario selecciona un RAT y solicita crear EIPD._",
           "_El sistema crea registro en eipd con estado 'borrador' y vinculo al RAT._",
           "_Se pre-llenan campos: nombre RAT, responsable, fecha solicitud._",
           "_El workflow de EIPD sigue los pasos definidos en el módulo EIPD._",
       ], "Alta", "M (3)")

    hu("_HU-060", "_Actualizar EIPD con workflow_", "EP-03", "RF-118",
       "admin_empresa o DPO",
       "_actualizar el estado y contenido de una EIPD siguiendo un workflow de aprobación_",
       "_gestionar el ciclo de vida completo de la evaluación de impacto_",
       [
           "_El EIPD transita por estados: borrador → revisión → aprobado/rechazado._",
           "_Cada transición genera auditoría en bitacora._",
           "_Solo DPO puede aprobar una EIPD._",
           "_Al aprobar, se genera hash del contenido y se registra en blockchain._",
       ], "Alta", "M (3)")

    hu("_HU-061", "_Descargar documento de base legal con fallback OCI_", "EP-12", "RF-117/RF-119",
       "admin_empresa o superadmin",
       "_descargar el documento de base legal de un RAT de forma segura, con fallback automático_",
       "_garantizar disponibilidad del documento incluso si OCI no está disponible_",
       [
           "_El sistema intenta generar PAR (pre-signed URL) para descarga directa desde OCI._",
           "_Si PAR falla, el sistema usa signed GET directo contra OCI Object Storage._",
           "_Si OCI falla, el sistema retorna los bytes almacenados en BYTEA (PostgreSQL)._",
           "_La descarga se registra en el log de auditoría._",
       ], "Alta", "M (3)")

    hu("_HU-062", "_Indexar corpus del asesor IA_", "EP-09", "RF-118",
       "superadmin",
       "_indexar nuevos documentos en el corpus del asesor IA_",
       "_mantener las sugerencias del chat IA actualizadas con la normativa vigente_",
       [
           "_El superadmin selecciona archivos o directorios para indexar._",
           "_El sistema chunkifica el contenido y lo almacena en asesor_chunks._",
           "_El sistema retorna estadísticas: chunks indexados, omitidos, errores._",
       ], "Alta", "M (3)")

    hu("_HU-063", "_Ver stats y eliminar chunks del asesor IA_", "EP-09", "RF-118",
       "superadmin",
       "_consultar estadísticas del corpus y eliminar chunks específicos_",
       "_mantener la calidad del corpus eliminando contenido irrelevante o duplicado_",
       [
           "_GET /admin/asesor/stats retorna: total chunks, fuentes, tamaño promedio._",
           "_DELETE /admin/asesor/documents/{chunk_id} elimina un chunk específico._",
           "_Las operaciones se registran en el log de auditoría._",
       ], "Alta", "S (2)")

    doc.add_heading("Sprint 1 — FORMADMIN ARCO QW1-QW10", level=2)

    hu("_HU-072", "_Validación RUT en vivo con dígito verificador y formateo automático_", "EP-05", "RF-060",
       "titular de datos",
       "_ingresar mi RUT con validación automática del dígito verificador y formateo visual_",
       "_facilitar el ingreso correcto de datos y reducir errores de digitación_",
       [
           "_AI validar el RUT en tiempo real mientras el usuario escribe._",
           "_Si el dígito verificador es incorrecto, mostrar error inline sin enviar formulario._",
           "_Aplicar formato XX.XXX.XXX-X automáticamente al perder foco._",
       ], "Alta", "S (2)")

    hu("_HU-073", "_Confirmación de email (doble input) con validación visual_", "EP-05", "RF-062",
       "titular de datos",
       "_ingresar mi email dos veces para confirmar que no hay errores de tipeo_",
       "_garantizar que las comunicaciones sean entregadas al email correcto_",
       [
           "_Mostrar dos campos de email consecutivos._",
           "_Al escribir en el segundo campo, comparar en tiempo real._",
           "_Si no coinciden, mostrar mensaje: 'Los emails no coinciden'._",
           "_El formulario no se envía hasta que ambos campos sean idénticos._",
       ], "Alta", "S (2)")

    hu("_HU-074", "_Tooltip en campo Tipo ARCO con referencia a Ley 21.719_", "EP-05", "RF-060",
       "titular de datos",
       "_conocer qué significa cada tipo de derecho ARCO al seleccionarlo_",
       "_ayudar al usuario a entender las diferencias entre Acceso, Rectificación, Cancelación y Oposición_",
       [
           "_Agregar icono (i) junto a la etiqueta 'Tipo ARCO'._",
           "_Al hacer hover o click, mostrar tooltip con referencia al Art. 14 y 16 bis._",
           "_Tooltip debe incluir ejemplo práctico de cada tipo._",
           "_Referencia: 'Ley 21.719, Art. 14 (Acceso, Rectificación) y 16 bis (Cancelación, Oposición)'._",
       ], "Alta", "S (2)")

    hu("_HU-075", "_Helper text en Prioridad (2/10 días hábiles / sin urgencia)_", "EP-05", "RF-101",
       "titular de datos o DPO",
       "_entender qué significa cada nivel de prioridad y sus plazos associated_",
       "_definir correctamente la urgencia de la solicitud ARCO_",
       [
           "_Bajo cada opción de prioridad, mostrar texto explicativo._",
           "_'2 días hábiles: tratamiento urgente con prioridad máxima'._",
           "_'10 días hábiles: tratamiento estándar'._",
           "_'Sin urgencia: sin plazo regulatorio, se procesa cuando sea posible'._",
       ], "Alta", "S (2)")

    hu("_HU-076", "_Detección titular duplicado con debounce 800ms + banner amarillo_", "EP-05", "RF-060",
       "DPO o admin",
       "_detectar si el titular que se está registrando ya existe en el sistema_",
       "_evitar duplicados y facilitar la gestión de solicitudes existentes_",
       [
           "_Después de 800ms sin escribir en campo RUT, consultar API /api/titulares/buscar._",
           "_Si se encuentra un titular con mismo RUT, mostrar banner amarillo: 'Este RUT ya está registrado'._",
           "_En el banner, incluir link para ver el registro existente._",
           "_El usuario puede continuar con el registro o cancelar._",
       ], "Alta", "S (2)")

    hu("_HU-077", "_Selector RAT con búsqueda debounce 300ms y pre-selección_", "EP-05", "RF-023",
       "DPO o admin",
       "_buscar y seleccionar un RAT existente de forma rápida y con autocompletado_",
       "_facilitar la vinculación de tickets ARCO a tratamientos registrados_",
       [
           "_Campo de búsqueda con autocompletado._",
           "_Debounce de 300ms antes de enviar solicitud._",
           "_Mostrar resultados con: ID RAT, nombre, empresa._",
           "_Si el usuario viene de una pantalla previa con RAT seleccionado, pre-seleccionar._",
           "_Permitir limpiar la selección con botón X._",
       ], "Alta", "S (2)")

    hu("_HU-078", "_Campos representante legal en sección colapsable_", "EP-05", "RF-060",
       "usuario registrando empresa",
       "_ingresar datos del representante legal solo cuando sea necesario_",
       "_mantener el formulario limpio y mostrar campos adicionales solo si aplica_",
       [
           "_Los campos de representante legal (nombre, RUT, cargo) van en sección colapsable._",
           "_Por defecto, la sección aparece colapsada._",
           "_Usuario expande solo si el tipo de tratamiento lo requiere._",
           "_Estado de expansión se guarda en sesión._",
       ], "Alta", "S (2)")

    hu("_HU-079", "_Date picker fecha retroactiva (max=hoy) + nuevos campos contacto_", "EP-03", "RF-051",
       "DPO o admin",
       "_seleccionar fechas de contacto en el pasado y disponer de campos adicionales de contacto_",
       "_registrar comunicaciones históricas y mantener información de contacto completa_",
       [
           "_Date picker permite seleccionar fechas hasta hoy (max=hoy)._",
           "_No permite fechas futuras para registros de contacto._",
           "_Agregar campos opcionales: teléfono de contacto, email alternativo, persona de contacto._",
           "_Validación de formato para cada campo._",
       ], "Alta", "S (2)")

    doc.add_heading("Sprint 2 — SLA Alert T-2d + Export ARCO", level=2)

    hu("_HU-080", "_Notificación SLA Alert T-2 días a DPO por email grupal_", "EP-03", "RF-051",
       "sistema automático",
       "_enviar alerta automática al DPO 2 días antes del vencimiento del SLA_",
       "_garantizar que las solicitudes ARCO se procesen dentro del plazo legal_",
       [
           "_Sistema identifica tickets ARCO con vencimiento en T-2 días hábiles._",
           "_Envío de email grupal a DPO configurado._",
           "_Email incluye: lista de tickets en riesgo, enlace directo a cada uno._",
           "_Se registra envío en bitácora con timestamp._",
       ], "Alta", "M (3)")

    hu("_HU-081", "_GitHub Actions workflow SLA Alert (cron 4h + workflow_dispatch)_", "EP-03", "RF-051",
       "devops / sistema",
       "_ejecutar verificación de SLA de forma programada y manual_",
       "_automatizar el monitoreo de vencimientos y permitir ejecuciones manuales de emergencia_",
       [
           "_Workflow con schedule: cron cada 4 horas (0,4,8,12,16,20)._",
           "_workflow_dispatch para ejecución manual inmediata._",
           "_El workflow ejecuta script Python que consulta tickets con vencimiento T-2d._",
           "_Si hay tickets en riesgo, dispara webhook/email._",
           "_Registra resultado en GitHub Actions logs._",
       ], "Alta", "M (3)")

    hu("_HU-082", "_Exportar tickets ARCO a CSV con filtros_", "EP-06", "RF-074",
       "DPO o admin",
       "_exportar tickets ARCO a CSV aplicando filtros por estado, fecha, tipo_",
       "_obtener datos para análisis externo y reporting_",
       [
           "_Filtros disponibles: estado (abierta/cerrada/en proceso), tipo ARCO, rango de fechas._",
           "_Generar archivo CSV con codificación UTF-8 y BOM._",
           "_Incluir columnas: ID, titular, tipo, estado, fecha creación, fecha vencimiento, prioridad._",
           "_El archivo se descarga directamente en el navegador._",
       ], "Alta", "M (3)")

    hu("_HU-083", "_Exportar tickets ARCO a Excel con color coding_", "EP-06", "RF-074",
       "DPO o admin",
       "_exportar tickets ARCO a Excel con formato profesional y codificación de colores_",
       "_facilitar el análisis visual de estados y prioridades_",
       [
           "_Archivo .xlsx con formato profesional._",
           "_Color coding: verde (cerrados), amarillo (en proceso), rojo (por vencer), gris (vencidos)._",
           "_Encabezados en azul oscuro con texto blanco._",
           "_Autoajustar ancho de columnas._",
           "_Incluir fila de totales y resumen por estado._",
       ], "Alta", "L (5)")

    hu("_HU-084", "_Exportar tickets ARCO a PDF con tabla compacta_", "EP-06", "RF-074",
       "DPO o admin",
       "_exportar tickets ARCO a PDF con tabla compacta apta para impresión_",
       "_generar documento oficial para auditoría o entrega regulatoria_",
       [
           "_Tabla compacta con todas las columnas visibles._",
           "_Encabezado con logo Custodio y fecha de generación._",
           "_Pié de página con número de página._",
           "_Sin imágenes, optimizado para impresión A4._",
           "_Maximum 50 tickets por página._",
       ], "Alta", "M (3)")

    hu("_HU-085", "_Dropdown Exportar en UI con CSV/Excel/PDF_", "EP-06", "RF-074",
       "DPO o admin",
       "_tener un único botón de exportar que despliegue opciones CSV/Excel/PDF_",
       "_unificar y simplificar la interfaz de exportación_",
       [
           "_Botón 'Exportar' con icono de flecha hacia abajo._",
           "_Click abre dropdown con 3 opciones: CSV, Excel, PDF._",
           "_Cada opción aplica los filtros activos actualmente._",
           "_Nomenclatura archivo: ARCO_tickets_YYYY-MM-DD_HHMMSS.formato._",
       ], "Alta", "S (2)")

    add_open_questions(doc, [
        "¿Se debe implementar autoguardo en wizard RAT?",
        "¿Se estiman HU con Planning Poker en sesiones de refinement?",
    ])
    add_risks_appendix(doc, [
        ("R-HU-01", "Pendientes S14 (CSRF) y C1 (encryption) bloquean compliance total.", "Alto"),
    ])
    add_id_glossary(doc, [
        ("HU-###", "Historia de Usuario", "Necesidad del usuario en formato 'Como/Quiero/Para'."),
        ("EP-###", "Épica", "Conjunto de HU relacionadas."),
        ("M (3)", "Tamaño medio", "3 puntos de historia: ~1-2 días."),
        ("L (5)", "Tamaño grande", "5 puntos de historia: ~3-5 días."),
        ("S (2)", "Tamaño pequeño", "2 puntos de historia: ~1 día."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()
