"""
Build 06 — Arquitectura de Software v1.4 (Post-OCI Integration)
Genera: docs/documentacion_oficial/06_Arquitectura_Software_Custodio_RAT_Manager_v1.4.docx
Cambios v1.4:
- OCI Object Storage con fallback chain documentado
- Admin Asesor IA documentado
- ADR nuevo: OCI Storage Strategy
"""
import os
import sys
_THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS)
from _theme_custodio import *
import _theme_custodio
_theme_custodio.DOC_VERSION = "v1.4"

OUT_DIR = r"C:\Users\chelo\Desktop\RAT_opencode\docs\documentacion_oficial"
ASSETS_DIR = os.path.join(OUT_DIR, "assets")
OUT_FILE = os.path.join(OUT_DIR, "06_Arquitectura_Software_Custodio_RAT_Manager_v1.4.docx")
DOC_CODE = "CUST-DOC-06"
DOC_TITLE = "Arquitectura de Software"


def build():
    doc = new_document()
    add_header_footer(doc, DOC_TITLE)
    add_cover(doc, title="ARQUITECTURA DE SOFTWARE",
              subtitle="Diagramas C4, despliegue, secuencias y decisiones técnicas",
              code=DOC_CODE)
    add_version_control(doc, DOC_CODE, DOC_TITLE, changes=[
        ("1.0", "Junio 2026", "Creación inicial de la arquitectura."),
        ("1.1", "Junio 2026", "Token blacklist LRU, hash chain en audit_log, patrón Repository, PII masking, optimización N+1."),
        ("1.2", "Junio 2026", "_Token blacklist, IDOR protection, CSV sanitize, hash chain, PII masking._"),
        ("1.3", "Junio 2026", "_Beta Launch: /health endpoint (ADR-12), RBAC fixes DT-014/DT-015, router fixes CB-01/CB-02._"),
        ("1.4", "Junio 2026", "_OCI Object Storage con fallback chain (ADR-14), Admin Asesor IA (ADR-15), MiniMax M2.7._"),
    ])
    add_toc(doc)

    doc.add_heading("1. Resumen ejecutivo", level=1)
    add_paragraph(doc, f"{BRAND_FULL} es una aplicación SaaS B2B para gestión del RAT (Ley 21.719). "
                      "Arquitectura modular, multi-tenant, desplegada en Vercel con Neon PostgreSQL. "
                      "Backend: FastAPI serverless. Frontend: Next.js 16 con App Router.")
    add_paragraph(doc, "_En v1.4 se implementó: OCI Object Storage con fallback chain (PAR→signed GET→BYTEA), "
                      "Admin Asesor IA para gestión del corpus, y soporte para MiniMax M2.7._")

    doc.add_heading("2. Diagrama de contexto (C4 Nivel 1)", level=1)
    c4_context = """
flowchart TB
    subgraph Actores["Actores humanos"]
        U1([Superadmin])
        U2([Admin de empresa])
        U3([Usuario regular])
        U4([Titular de datos])
        U5([Auditor / APDC])
    end
    subgraph Custodio["Sistema Custodio RAT Manager"]
        SYS[("Custodio<br/>Web App")]
    end
    subgraph Externos["Sistemas externos"]
        EXT1[(Neon PostgreSQL<br/>AES-256 at rest)]
        EXT2{{Servicio de IA<br/>MiniMax/OpenAI}}
        EXT3{{Vercel<br/>Serverless}}
        EXT4[_OCI Object Storage<br/>custodio-documents-qa_]
    end
    U1 --> SYS
    U2 --> SYS
    U3 --> SYS
    U4 -->|Formulario público| SYS
    U5 -->|Descarga de evidencia| SYS
    SYS -->|Lee/Escribe datos| EXT1
    SYS -->|Consulta IA| EXT2
    SYS -->|Despliegue y runtime| EXT3
    SYS -->|Almacena documentos| EXT4
"""
    add_figure(doc, c4_context,
               "Diagrama de contexto C4 Nivel 1: Custodio y sus interacciones externas.",
               ASSETS_DIR, [0], name_hint="c4_context", width_inches=6.8)

    doc.add_heading("3. Diagrama de contenedores (C4 Nivel 2)", level=1)
    c4_container = """
flowchart LR
    subgraph Cliente["Cliente (Navegador)"]
        BR1([Usuario humano])
    end
    subgraph Vercel["Plataforma Vercel"]
        FE["Frontend<br/>Next.js 16<br/>React 19 + TS"]
        API["Backend API<br/>FastAPI<br/>Python 3.9"]
    end
    subgraph Neon["Neon Cloud"]
        DB[("PostgreSQL 15<br/>+ SSL + AES-256")]
    end
    subgraph OCI["OCI Object Storage"]
        STORAGE["Object Storage<br/>custodio-documents-qa<br/>custodio-documents-qa-archive"]
    end
    subgraph IA["Servicio IA (opcional)"]
        AIIA{{"MiniMax M2.7 /<br/>OpenAI API"}}
    end
    BR1 -->|HTTPS + JWT| FE
    FE -->|HTTPS + JWT| API
    API -->|SQLAlchemy<br/>TCP+SSL| DB
    API -->|OCI REST API<br/>Signed GET| STORAGE
    API -->|HTTPS| AIIA
"""
    add_figure(doc, c4_container,
               "Diagrama de contenedores C4 Nivel 2: contenedores principales con OCI.",
               ASSETS_DIR, [0], name_hint="c4_container", width_inches=6.8)

    doc.add_heading("4. Componentes del backend", level=1)
    components = [
        ["Capa", "Paquete", "Responsabilidad"],
        ["Modelos", "app/models", "Mapeo ORM SQLAlchemy de las entidades."],
        ["Schemas", "app/schemas", "Validación y serialización con Pydantic."],
        ["Repositories", "app/repositories", "_Patrón Repository: abstracción de acceso a datos con selectinload/joinedload._"],
        ["Servicios", "app/services", "Lógica de negocio: CRUD, cálculos, integración IA, OCI storage."],
        ["Rutas", "app/routes", "_Endpoints HTTP, autorización, rate limiting, RBAC._"],
        ["Core", "app/core", "Configuración, seguridad (JWT, bcrypt, blacklist), logging, limiter, OCI storage._"],
    ]
    add_styled_table(doc, components[0], components[1:],
                     col_widths_cm=[2.5, 4.0, 11.0], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("4.1 Routers del backend (app/routes/)", level=2)
    add_paragraph(doc, "_Routers implementados en v1.4:_")
    routers = [
        ["auth.py", "Login, logout, refresh, users CRUD, password.", "10 endpoints"],
        ["companies.py", "CRUD companies + /publico (auth requerida).", "6 endpoints"],
        ["rats.py", "CRUD RATs, dashboard, sugerencias, auditoría, hash chain, archivo OCI.", "_20 endpoints (incl. OCI fallback)_"],
        ["breaches.py", "CRUD brechas, evaluación de riesgo.", "6 endpoints"],
        ["consentimientos.py", "_Listar, crear, revocar consentimientos._", "4 endpoints"],
        ["eipd.py", "_Listar, crear, actualizar EIPDs._", "4 endpoints"],
        ["tkt-solicitud-derecho.py", "Tickets ARCO, notas, historial.", "8 endpoints"],
        ["feriados.py", "CRUD feriados, upload CSV, export.", "5 endpoints"],
        ["ai.py", "Chat IA contextual (MiniMax M2.7 / OpenAI).", "1 endpoint"],
        ["health.py", "_GET /health, /health/db (sin auth)._", "2 endpoints"],
        ["admin_asesor.py", "_Indexar corpus, stats, eliminar chunks (solo superadmin)._", "_3 endpoints_"],
    ]
    add_styled_table(doc, ["Router", "Responsabilidad", "Endpoints"],
                     routers, col_widths_cm=[4.0, 8.5, 5.0], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("5. Patrones y estilos arquitectónicos", level=1)
    add_bullet(doc, "_Patrón Repository/Service sobre SQLAlchemy 2.0 (app/repositories/). selectinload para evitar N+1._", bold_prefix="Repository Pattern: ")
    add_bullet(doc, "App Router de Next.js 16 con grupos de rutas: '(app)' agrupa rutas autenticadas.", bold_prefix="App Router (Next.js): ")
    add_bullet(doc, "Estado global con AppContext (usuario, empresa activa).", bold_prefix="Single Source of Truth: ")
    add_bullet(doc, "_Token blacklist LRU (1000 slots) en get_current_user. JTI consultado en cada request._", bold_prefix="Token Blacklist: ")
    add_bullet(doc, "_Hash chain SHA256 en audit_log: prev_hash + SHA256(timestamp+usuario+accion+entidad+detalle)._", bold_prefix="Audit Hash Chain: ")
    add_bullet(doc, "_PIIMaskingFilter en logging_config.py: mask email, RUT, IP, tokens, passwords._", bold_prefix="PII Masking: ")
    add_bullet(doc, "_RBAC: admin_empresa solo crea RATs en empresas asignadas (DT-014, 6209e2d). usuario no crea brechas (DT-015, 6209e2d)._", bold_prefix="RBAC: ")
    add_bullet(doc, "_OCI Object Storage con fallback chain: PAR → signed GET → BYTEA (57cbffc)._", bold_prefix="OCI Storage: ")

    doc.add_heading("6. Decisiones técnicas relevantes", level=1)
    adrs = [
        ["ADR-01", "Next.js 16 + React 19", "Rendimiento, ecosistema, despliegue directo a Vercel, TypeScript."],
        ["ADR-02", "FastAPI sobre Flask o Django REST", "Tipado nativo, async/await, OpenAPI automático, Pydantic."],
        ["ADR-03", "SQLAlchemy 2.0", "Madurez, soporte Postgres, migraciones simples."],
        ["ADR-04", "Neon PostgreSQL", "Compatibilidad Vercel, plan gratuito, branching, AES-256."],
        ["ADR-05", "_OCI Object Storage para binarios_", "_Almacenamiento en OCI con fallback a BYTEA. bucket custodio-documents-qa._"],
        ["ADR-06", "JWT 8h + blacklist LRU", "Balance seguridad/UX. Blacklist permite logout efectivo."],
        ["ADR-07", "Rate limiting con slowapi", "Mitigación de fuerza bruta y abuso."],
        ["ADR-08", "Mermaid pre-renderizado a PNG", "Word no soporta Mermaid runtime."],
        ["ADR-09", "Audit log con hash chain", "Inmutabilidad del registro de auditoría."],
        ["ADR-10", "Patrón Repository (app/repositories/)", "Abstracción de acceso a datos; selectinload evitan N+1."],
        ["ADR-11", "PIIMaskingFilter en logging", "Mask email, RUT, IP, tokens y contraseñas."],
        ["ADR-12", "_GET /health y /health/db endpoints_", "_Health checks sin auth para monitoreo. /health stateless, /health/db prueba DB._"],
        ["ADR-13", "_RBAC: admin_empresa RAT + usuario breach_", "_DT-014: get_empresas_usuario() en POST /rats/. DT-015: validación de rol en POST /brechas/._"],
        ["ADR-14", "_OCI Object Storage con fallback chain_", "_PAR → signed GET → BYTEA. OCISigner para firma RSA. copy_to_archive antes de delete._"],
        ["ADR-15", "_Admin Asesor IA_", "_POST /admin/asesor/index, GET /admin/asesor/stats, DELETE /admin/asesor/documents/{id}. Solo superadmin._"],
    ]
    add_styled_table(doc, ["ID", "Decisión", "Justificación"], adrs,
                     col_widths_cm=[1.8, 5.0, 10.7], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("7. Diagrama de despliegue", level=1)
    deploy = """
flowchart TB
    subgraph Edge["Vercel Edge Network (CDN)"]
        EDGE(["HTTPS / TLS"])
    end
    subgraph Vercel_Prod["Vercel (Región: US East)"]
        FE2["Frontend<br/>custodio-qa.vercel.app<br/>Next.js 16"]
        API2["API Serverless<br/>custodio-api-qa.vercel.app<br/>FastAPI"]
    end
    subgraph NeonProd["Neon (Región: US East)"]
        PG[("PostgreSQL 15<br/>+ SSL + AES-256")]
    end
    subgraph OCI_Storage["OCI Object Storage"]
        BUCKET["Bucket: custododio-documents-qa<br/>Archive: custod-documents-qa-archive"]
    end
    subgraph External["Servicios externos"]
        OAI{{"MiniMax M2.7 / OpenAI API"}}
    end
    EDGE --> FE2
    EDGE --> API2
    FE2 -->|API calls| API2
    API2 -->|SQL over SSL| PG
    API2 -->|OCI REST API| BUCKET
    API2 -->|HTTPS| OAI
"""
    add_figure(doc, deploy,
               "Topología de despliegue: Vercel (FE+API), Neon (PostgreSQL), OCI (Object Storage).",
               ASSETS_DIR, [0], name_hint="deploy", width_inches=6.8)

    doc.add_heading("8. Diagramas de secuencia", level=1)

    doc.add_heading("8.1 Login con blacklist check", level=2)
    seq_login = """
sequenceDiagram
    autonumber
    actor U as Usuario
    participant FE as Frontend Next.js
    participant API as Backend FastAPI
    participant DB as PostgreSQL
    participant BL as Token Blacklist<br/>(LRU 1000)
    U->>FE: Ingresa credenciales
    FE->>API: POST /auth/login
    API->>API: rate limit (5/min)
    API->>DB: SELECT user WHERE username=?
    DB-->>API: user row
    API->>API: verify bcrypt(password)
    alt credenciales válidas
        API->>API: generar JWT (8h) con JTI único
        API-->>FE: 200 + JWT + Set-Cookie httpOnly
        FE-->>U: redirige a /dashboard
    else credenciales inválidas
        API-->>FE: 401 Unauthorized
    end
"""
    add_figure(doc, seq_login, "Secuencia de login con rate limiting y JWT.",
               ASSETS_DIR, [0], name_hint="seq_login", width_inches=6.5)

    doc.add_heading("8.2 OCI Storage Fallback Chain", level=2)
    seq_oci = """
sequenceDiagram
    autonumber
    actor U as Usuario
    participant API as Backend FastAPI
    participant OCI as OCI Object Storage
    participant DB as PostgreSQL
    U->>API: GET /rats/{id}/archivo
    API->>API: Paso 1: Intentar PAR
    API->>OCI: POST /p (create PAR)
    alt PAR disponible
        OCI-->>API: accessUri (URL pre-firmada)
        API-->>U: {url, expires_in_seconds}
    else PAR IAM no disponible
        API->>API: Paso 2: Signed GET directo
        API->>OCI: GET /n/.../o/... (signed)
        alt OCI disponible
            OCI-->>API: bytes del archivo
            API-->>U: {bytes, content_type}
        else OCI caído
            API->>API: Paso 3: BYTEA fallback
            API->>DB: SELECT archivo_base_legal_datos
            DB-->>API: bytes
            API-->>U: {bytes, content_type}
        end
    end
"""
    add_figure(doc, seq_oci,
               "_Secuencia OCI fallback chain: PAR → signed GET → BYTEA._",
               ASSETS_DIR, [0], name_hint="seq_oci", width_inches=6.5)

    doc.add_heading("9. Stack tecnológico", level=1)
    stack = [
        ["Frontend", "Next.js 16.2", "Framework React con App Router"],
        ["Frontend", "React 19", "UI declarativa"],
        ["Frontend", "TypeScript", "Tipado estático"],
        ["Frontend", "Tailwind CSS v4", "Estilos utility-first"],
        ["Frontend", "Sonner", "Notificaciones tipo toast"],
        ["Frontend", "React Hook Form + Zod", "Formularios y validación"],
        ["Backend", "FastAPI 0.115", "Framework web async"],
        ["Backend", "Uvicorn", "Servidor ASGI"],
        ["Backend", "SQLAlchemy 2.0", "ORM con selectinload/joinedload"],
        ["Backend", "Pydantic 2.10", "Validación y serialización"],
        ["Backend", "python-jose", "Tokens JWT (HS256)"],
        ["Backend", "passlib + bcrypt", "Hashing de contraseñas (12 rounds)"],
        ["Backend", "ReportLab", "Generación PDF servidor"],
        ["Backend", "slowapi", "Rate limiting"],
        ["Backend", "cachetools", "_LRU cache para token blacklist_"],
        ["Backend", "_OCI SDK (custom)_", "_OCI Object Storage con OCISigner (RSA SHA256)_"],
        ["Infraestructura", "Vercel", "Serverless Functions y hosting"],
        ["Infraestructura", "Neon", "PostgreSQL administrado con AES-256 at rest"],
        ["Infraestructura", "_OCI Object Storage_", "_Almacenamiento de documentos con bucket archive_"],
    ]
    add_styled_table(doc, ["Capa", "Tecnología", "Propósito"], stack,
                     col_widths_cm=[3.0, 5.0, 9.5], first_col_bold=True,
                     underline_new=True)

    doc.add_heading("10. Consideraciones de seguridad", level=1)
    add_bullet(doc, "Contraseñas hasheadas con bcrypt $2b$12$ (12 rounds).", bold_prefix="Contraseñas: ")
    add_bullet(doc, "Tokens JWT con expiración 8h, HS256. JTI único por token.", bold_prefix="Tokens: ")
    add_bullet(doc, "_Token blacklist LRU (1000 slots): cada logout agrega JTI. get_current_user consulta blacklist._", bold_prefix="Token Blacklist: ")
    add_bullet(doc, "Cookies httpOnly y Secure en producción.", bold_prefix="Cookies: ")
    add_bullet(doc, "Rate limiting: 5/min login, 5/min password, 3/hora ARCO, 10/min logout.", bold_prefix="Rate limiting: ")
    add_bullet(doc, "CORS estricto: regex 'https://.*\\.vercel\\.app'.", bold_prefix="CORS: ")
    add_bullet(doc, "_IDOR protection: check_company_access en todos los endpoints con company_id._", bold_prefix="Aislamiento: ")
    add_bullet(doc, "_RBAC: admin_empresa solo crea RATs en empresas asignadas (DT-014)._", bold_prefix="RBAC RAT: ")
    add_bullet(doc, "_RBAC: rol usuario no puede crear brechas (DT-015). Retorna 403._", bold_prefix="RBAC Breach: ")
    add_bullet(doc, "_CSV sanitization: apostrophe en =, +, -, @._", bold_prefix="CSV injection: ")
    add_bullet(doc, "_PII masking en todos los logs._", bold_prefix="PII en logs: ")
    add_bullet(doc, "_Audit log con hash chain SHA256._", bold_prefix="Audit inmutable: ")
    add_bullet(doc, "_OCI firmados con RSA SHA256 (OCISigner). No se exponen credenciales en cliente._", bold_prefix="OCI Storage: ")

    doc.add_heading("11. Modelo de datos simplificado", level=1)
    er_mermaid = """
erDiagram
    Company ||--o{ User : tiene
    Company ||--o{ RAT : contiene
    Company ||--o{ SecurityBreach : registra
    Company ||--o{ TktSolicitudDerecho : gestiona
    Company ||--o{ Consentimiento : tiene
    Company ||--o{ EncargadoContrato : designa
    Company ||--o{ Feriado : registra
    RAT ||--o| EIPD : puede_tener
    RAT ||--o{ Consentimiento : requiere
    RAT ||--o{ AsesorChunk : puede_tener
    TktSolicitudDerecho ||--o{ TktNota : tiene
    TktSolicitudDerecho ||--o{ TktAdjunto : tiene
    TktSolicitudDerecho ||--o| SolicitudDerecho : origen
    User ||--o{ UserCompany : pertenece
    UserCompany }o--|| Company : acceso
"""
    add_figure(doc, er_mermaid,
               "Diagrama ER: entidades principales y relaciones (v1.4 con OCI y AsesorChunk).",
               ASSETS_DIR, [0], name_hint="er_model", width_inches=6.5)

    add_open_questions(doc, [
        "¿Migrar de BYTEA a S3/R2 para archivos adjuntos en V2?",
        "¿Implementar WAF dedicado (Cloudflare) en producción?",
    ])
    add_risks_appendix(doc, [
        ("R-AR-01", "Regex CORS 'https://.*\\.vercel\\.app' permite cualquier subdominio Vercel. Mitigación: lista blanca explícita en V2.", "Alto"),
        ("R-AR-02", "Serverless cold starts: latencia 1-2s. Mitigación: min-instances en Vercel Pro.", "Medio"),
        ("R-AR-03", "Pendientes: CSRF (S14), encryption at rest (C1). Bloquean compliance total.", "Alto"),
        ("R-AR-04", "_PAR IAM permission no disponible. Signed GET requiere 'manage objects' en OCI._", "Bajo"),
    ])
    add_id_glossary(doc, [
        ("C4", "Conjunto de modelos C4", "Notación de diagramas de arquitectura por Simon Brown."),
        ("ADR", "Architecture Decision Record", "Documento que captura una decisión arquitectónica significativa."),
        ("JWT", "JSON Web Token", "Token de autenticación firmado digitalmente."),
        ("JTI", "JWT ID", "Identificador único del token usado para blacklist."),
        ("PAR", "Pre-Authenticated Request", "URL pre-firmada para acceso directo a OCI sin autenticación."),
    ])
    add_final_note(doc)
    doc.save(OUT_FILE)
    print(f"[OK] {OUT_FILE}")


if __name__ == "__main__":
    build()