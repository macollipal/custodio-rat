# Custodio RAT Manager — Flujo de Datos

> Generado: 2026-04-24 · Actualizado: 2026-05-12 (Módulo Onboarding, validación de sesión con /auth/me, redirect 401 automático)  
> Stack: FastAPI + SQLAlchemy + SQLite · Next.js 16 + TypeScript + Tailwind v4

---

## 1. Flujo de Usuario

```mermaid
flowchart TD
    START([INICIO]) --> LOGIN[Login\nusername + password]
    LOGIN --> AUTH{¿Credenciales\nválidas?}
    AUTH -- No --> ERR[Mostrar error]
    ERR --> LOGIN
    AUTH -- Sí --> JWT[Recibe JWT + datos de sesión\nGuarda en localStorage]
JWT --> ADMIN{¿Admin\nglobal?}
    ADMIN -- Sí --> ALLCOMP[Ve TODAS\nlas empresas]
    ADMIN -- No --> OWNCOMP[Ve solo sus empresas\nasignadas via user_companies]
    ALLCOMP --> EMPRESAS{¿Hay empresas\nregistradas?}
    OWNCOMP --> EMPRESAS
    EMPRESAS -- No empresas --> ONBOARDING[Onboarding\n/create company]
    ONBOARDING --> DASH
    EMPRESAS -- Sí empresas --> SELCOMP[Selecciona empresa activa]
    SELCOMP --> DASH[Dashboard
KPIs · alertas · revisión periódica]
    DASH --> ACTION{¿Qué acción?}

    ACTION -- Ver procesos --> RATLIST[Lista RAT\ncompletitud % · badge ⏰ Revisar]
    ACTION -- Nuevo proceso --> WIZARD[Wizard 4 pasos]
    ACTION -- Gestionar usuarios --> UPANEL[Panel de accesos\nsolo admin]

    RATLIST --> RATOP{Operación}
    RATOP -- Editar --> EDIT[Formulario edición]
    RATOP -- Duplicar --> DUP[Copia automática\nCopia de ...]
    RATOP -- Exportar --> EXP[CSV · PDF]
    RATOP -- Historial --> AUDIT[Log de auditoría]

    WIZARD --> W1[Paso 1: Identificación\nnombre · categorías titulares · fuente · destinatarios]
    W1 --> W2[Paso 2: Datos personales\ncategoría datos · tipo sensible · EIPD · decisiones automatizadas]
    W2 --> W3[Paso 3: Finalidad y ley\nfinalidad · base legal · alertas contextuales]
    W3 --> W4[Paso 4: Almacenamiento y transferencias\nplazo · medidas seguridad · país · garantías]
    W4 --> WREV[Revisión final]
    WREV --> SAVED
    W4 --> SAVED[RAT guardado\ncompletitud calculada automáticamente]

    UPANEL --> INVITE[Invitar por username]
    INVITE --> ROLE[Asignar rol\nadmin · editor · viewer]

    style START fill:#d5e8d4,stroke:#82b366
    style SAVED fill:#d5e8d4,stroke:#82b366
    style ALLCOMP fill:#d5e8d4,stroke:#82b366
    style OWNCOMP fill:#d5e8d4,stroke:#82b366
    style ERR fill:#f8cecc,stroke:#b85450
    style AUTH fill:#fff2cc,stroke:#d6b656
    style ADMIN fill:#fff2cc,stroke:#d6b656
    style ACTION fill:#fff2cc,stroke:#d6b656
    style RATOP fill:#fff2cc,stroke:#d6b656
```

---

## 2. Arquitectura Técnica

```mermaid
graph TB
    subgraph BROWSER["🖥️  Navegador — Next.js 16  (puerto 3000)"]
        PAGES["Páginas React\ndashboard · rat · companies · breaches · reportes · login · onboarding"]
        CTX["AppContext — caché en memoria\ntoken · user · company · companies · rats · dashboardStats"]
        APILIB["lib/api.ts\nfetch() + Bearer JWT headers\ngetReportes() · askAI()\nexportCSV() · exportPDF()"]
        LS["localStorage\ntoken · user · company activa\ncustodio_saved_filters"]
        COMP["Componentes\nRatTable · RatWizard · RatEditForm\nSidebar · PasswordModal · KPICard\nStatusChart · AlertBanner · Drawer\nChatIA · CompletitudBar · Badge · Onboarding"]
    end

    subgraph BACKEND["⚙️  Backend — FastAPI  (puerto 8002)"]
        direction TB
        MW["CORSMiddleware\nJWT Guard — get_current_user()"]
        EP_A["POST /auth/login\nGET /auth/me · GET|POST /auth/users\nPUT /auth/me/password"]
        EP_C["GET|POST /companies/\nPUT|DELETE /companies/{id}"]
        EP_R["GET|POST /rats/\nGET|PUT|DELETE /rats/{id}\nGET /rats/dashboard/{cid}\nGET /rats/export/csv|pdf|cni\nGET /rats/{id}/auditoria\nGET /rats/reportes (con paginación + sort)\nPOST /rats/sugerencias\nGET /rats/sugerencias/tipos"]
        EP_B["GET|POST|PUT|DELETE /brechas/"]
        EP_AI["POST /ai/ask (MiniMax M2.7 u OpenAI)"]
        SVC["Services\nuser · company · rat · export · suggestion · user_company"]
        MDL["SQLAlchemy Models\nUser · Company · RAT · UserCompany · AuditLog"]
    end

    subgraph DB["🗄️  SQLite — rat.db"]
        T_U[users]
        T_C[companies]
        T_UC[user_companies]
        T_R[rats]
        T_AL[audit_logs]
    end

    PAGES <--> CTX
    CTX --> APILIB
    LS <--> CTX
    COMP --> CTX

    APILIB -->|"HTTP + Bearer JWT"| MW
    MW --> EP_A & EP_C & EP_R & EP_U
    EP_A & EP_C & EP_R & EP_U --> SVC
    SVC --> MDL
    MDL --> T_U & T_C & T_UC & T_R & T_AL
```

---

## 3. Modelo de Datos

```mermaid
erDiagram
    users {
        int      id          PK
        string   username
        string   email
        string   full_name
        string   hashed_password
        bool     is_active
        bool     is_admin
    }
    companies {
        int      id          PK
        string   nombre
        string   rut
        string   rubro
        string   direccion
        string   contacto_dpo
        string   email_dpo
        string   descripcion
        datetime created_at
    }
    user_companies {
        int      id          PK
        int      user_id     FK
        int      company_id  FK
        string   rol
        datetime created_at
    }
    rats {
        int      id                          PK
        int      company_id                 FK
        string   nombre_proceso
        string   categoria_datos
        string   categoria_titulares
        string   finalidad
        string   base_legal
        string   fuente_datos
        string   plazo_retencion
        string   transferencia_datos
        string   medidas_seguridad
        string   destinatarios
        bool     transferencia_internacional
        string   pais_destino
        string   garantias_transferencia_int
        bool     datos_sensibles
        string   tipo_dato_sensible
        bool     evaluacion_impacto
        bool     decisiones_automatizadas
        string   estado
        string   observaciones_auditoria
        datetime created_at
        datetime updated_at
    }
    audit_logs {
        int      id        PK
        int      rat_id    FK
        string   accion
        string   usuario
        datetime timestamp
        string   detalle
    }

    users         ||--o{ user_companies : "tiene acceso a"
    companies     ||--o{ user_companies : "acceso de usuarios"
    companies     ||--o{ rats           : "gestiona"
    rats          ||--o{ audit_logs     : "genera"
```

---

## 4. Flujo de Datos Completo

```mermaid
sequenceDiagram
    actor U as 👤 Usuario
    participant FE as 🖥️ Frontend
    participant CTX as AppContext
    participant API as ⚙️ Backend
    participant DB as 🗄️ SQLite

    rect rgb(219,234,254)
        Note over U,DB: ── AUTENTICACIÓN ──
        U->>FE: Ingresa username + password
        FE->>API: POST /auth/login
        API->>DB: SELECT user WHERE username=?
        DB-->>API: user record
        API->>API: verify_password() → create_access_token()
        API-->>FE: {access_token, user}
        FE->>CTX: setToken() · setUser()
        CTX->>CTX: Persiste en localStorage
    end

    rect rgb(213,232,212)
        Note over U,DB: ── CARGA DE EMPRESAS (filtro por rol) ──
        FE->>API: GET /companies/  [Bearer JWT]
        API->>API: get_current_user() — valida JWT
        alt Admin global (is_admin = True)
            API->>DB: SELECT * FROM companies
        else Usuario normal
            API->>DB: SELECT c FROM companies c JOIN user_companies uc ON c.id=uc.company_id WHERE uc.user_id=?
        end
        DB-->>API: lista empresas
        API-->>FE: [Company]
        FE->>CTX: setCompanies()
        U->>FE: Selecciona empresa activa
        FE->>CTX: setCompany() → limpia caché rats y stats
    end

    rect rgb(225,213,231)
        Note over U,DB: ── CARGA Y CACHÉ DE RATs ──
        FE->>API: GET /rats/?company_id=X  [Bearer JWT]
        API->>DB: SELECT * FROM rats WHERE company_id=X
        DB-->>API: lista RATs
        API->>API: calcular_completitud() por cada RAT
        API-->>FE: [RAT] + campo completitud
        FE->>CTX: setRats()  ← caché inmediato
        Note over FE,CTX: Próximas navegaciones usan caché,<br/>refresco silencioso en background
    end

    rect rgb(255,230,204)
        Note over U,DB: ── CREAR RAT (wizard 4 pasos) ──
        U->>FE: Paso 1 — nombre, categoria_titulares, fuente, destinatarios
        U->>FE: Paso 2 — categoria_datos, tipo_dato_sensible, EIPD, decisiones_automatizadas
        U->>FE: Paso 3 — finalidad, base_legal (Art.12/13/16/16BIS)
        U->>FE: Paso 4 — plazo, medidas, transferencia + garantias_transferencia_int
        FE->>API: POST /rats/ {nombre_proceso, categoria_titulares, categoria_datos,\ntipo_dato_sensible, finalidad, base_legal, fuente_datos,\nplazo_retencion, medidas_seguridad, transferencia_internacional,\npais_destino, garantias_transferencia_int, datos_sensibles,\nevaluacion_impacto, decisiones_automatizadas, ...}
        API->>API: _generar_alertas_auditoria() — detecta riesgos automáticamente
        API->>API: _calcular_estado() — completo si 7 campos obligatorios presentes
        API->>DB: INSERT INTO rats (...)
        API->>DB: INSERT INTO audit_logs (accion='crear', usuario, rat_id)
        DB-->>API: nuevo RAT
        API-->>FE: RAT creado + completitud (0-100%)
        FE->>CTX: setRats([...rats, nuevo])
    end

    rect rgb(255,242,204)
        Note over U,DB: ── GESTIÓN DE ACCESOS (solo admin) ──
        U->>FE: Abre panel "Usuarios" de empresa X
        FE->>API: GET /companies/X/usuarios/
        API->>DB: SELECT uc, u FROM user_companies JOIN users
        DB-->>API: lista accesos
        API-->>FE: [UserCompany]
        U->>FE: Invita "jperez" con rol "editor"
        FE->>API: POST /companies/X/usuarios/ {username, rol}
        API->>DB: SELECT user WHERE username="jperez"
        API->>DB: INSERT INTO user_companies (user_id, company_id, rol)
        DB-->>API: nuevo acceso
        API-->>FE: UserCompany creado
    end
```
