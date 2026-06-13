# diff_codigo_vs_docs.md — v1.4 vs v1.3
## Custodio RAT Manager

**Fecha:** 12 Junio 2026
**Comparación:** Código actual vs Documentos v1.3

---

## 1. ENDPOINTS: Código vs Documentación

### 1.1 ENDPOINTS NUEVOS EN CÓDIGO (no en docs v1.3)

| Endpoint | Método | Función | Archivo | Documentar en |
|----------|--------|---------|---------|---------------|
| `/rats/{rat_id}/archivo` | GET | descargar_archivo | `routes/rats.py:341` | 08_API, 04_CU |
| `/admin/asesor/index` | POST | index_endpoint | `routes/admin_asesor.py:30` | 08_API, 02_RF |
| `/admin/asesor/stats` | GET | stats_endpoint | `routes/admin_asesor.py:70` | 08_API |
| `/admin/asesor/documents/{chunk_id}` | DELETE | delete_chunk_endpoint | `routes/admin_asesor.py:80` | 08_API |

### 1.2 ENDPOINTS EN DOCS v1.3 NO EN CÓDIGO

_Ninguno — todos los endpoints documentados existen en el código._

### 1.3 ENDPOINTS CON CAMBIOS EN IMPLEMENTACIÓN

| Endpoint | Cambio | Impacto en docs |
|----------|--------|----------------|
| `/rats/{rat_id}/archivo` | Nueva implementación con fallback chain PAR→download→BYTEA | Agregar documentación |
| `storage.py` | Nuevos métodos: `copy_to_archive`, `delete_from_archive`, `list_archive_objects` | 12_Manual_Técnico |

---

## 2. MODELOS: Código vs Documentación

### 2.1 MODELOS NUEVOS EN CÓDIGO (no en docs v1.3)

| Modelo | Tabla | Archivo | Campos | Documentar en |
|--------|-------|---------|--------|---------------|
| AsesorChunk | asesor_chunks | `models/asesor.py` | id, content, source, chunk_index, created_at | 07_Modelo_Datos (verificar alcance) |

### 2.2 CAMBIOS EN MODELOS EXISTENTES

| Modelo | Campo nuevo | Tipo | Descripción | Documentar en |
|--------|------------|------|-------------|---------------|
| RAT | `archivo_base_legal_storage_url` | String (OCI URL) | URL del archivo en OCI Object Storage | 07_Modelo_Datos |

---

## 3. RUTAS FRONTEND: Código vs Documentación

### 3.1 RUTAS NUEVAS EN CÓDIGO (no en docs v1.3)

_Ninguna — todas las 19 páginas frontend ya estaban documentadas en v1.3._

### 3.2 CAMBIOS EN RUTAS FRONTEND

_Ninguno._

---

## 4. SERVICIOS: Código vs Documentación

### 4.1 SERVICIOS NUEVOS O CAMBIADOS

| Servicio | Archivo | Cambios | Documentar en |
|----------|---------|---------|---------------|
| `rat_service.py` | `services/rat_service.py` | Nueva función `download_rat_file()` con fallback chain | 12_Manual_Técnico |
| `storage.py` | `core/storage.py` | Nueva clase `OCISigner`, métodos `create_presigned_url`, `copy_to_archive`, `list_archive_objects` | 12_Manual_Técnico, 06_Arquitectura |
| `asesor_indexer.py` | `services/asesor_indexer.py` | Indexación de corpus para IA | 12_Manual_Técnico |

---

## 5. REQUISITOS FUNCIONALES: Código vs Documentación

### 5.1 RF NUEVOS A AGREGAR EN v1.4

| ID | Prioridad | Descripción | Módulo |
|----|----------|-------------|--------|
| RF-117 | Alta | _El sistema debe almacenar documentos de base legal en OCI Object Storage con fallback a BYTEA._ | RAT |
| RF-118 | Alta | _El sistema debe permitir a superadmin indexar, consultar estadísticas y eliminar chunks del corpus del asesor IA._ | Asesor IA |
| RF-119 | Media | _El sistema debe permitir descargar archivos de base legal con URL pre-firmada (PAR) o descarga directa firmada._ | RAT |

---

## 6. HISTORIAS DE USUARIO: Código vs Documentación

### 6.1 HU NUEVAS A AGREGAR EN v1.4

| ID | Descripción |
|----|-------------|
| HU-XXX | _Como superadmin, quiero gestionar el corpus del asesor IA (indexar, eliminar chunks, ver stats) para mantener las sugerencias actualizadas._ |
| HU-XXX | _Como usuario, quiero descargar el documento de base legal de un RAT de forma segura, con fallback automático si OCI no está disponible._ |

---

## 7. CASOS DE USO: Código vs Documentación

### 7.1 CU NUEVOS A AGREGAR EN v1.4

| ID | Descripción |
|----|-------------|
| CU-XXX | Descargar documento de base legal con fallback OCI |
| CU-XXX | Gestionar corpus del asesor IA (superadmin) |

---

## 8. CASOS DE PRUEBA: Código vs Documentación

### 8.1 TC NUEVOS A AGREGAR EN v1.4

| ID | Descripción |
|----|-------------|
| TC-XXX | Verificar descarga de archivo con PAR |
| TC-XXX | Verificar fallback a download directo cuando PAR falla |
| TC-XXX | Verificar fallback a BYTEA cuando OCI no disponible |
| TC-XXX | Verificar indexación de corpus por superadmin |
| TC-XXX | Verificar eliminación de chunk por superadmin |

---

## 9. ARQUITECTURA: Cambios

### 9.1 COMPONENTES NUEVOS

| Componente | Descripción | Tipo |
|------------|-------------|------|
| `OCISigner` | Firma requests para OCI API usando API Signing Key | Clase |
| `OCIStorageBackend` | Backend de almacenamiento OCI con todos los métodos | Clase |
| `AsesorChunk` | Modelo para fragmentos del corpus IA | Modelo |

### 9.2 DIAGRAMA DE ARQUITECTURA ACTUALIZADO

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                       │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routes    │  │  Services   │  │  Repositories       │  │
│  │  /rats      │  │rat_service  │  │  rat_repository     │  │
│  │  /breaches  │  │breach_service│ │                     │  │
│  │  /ai        │  │ai_service   │  │                     │  │
│  │  /admin/*   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────▼────────────────────────────────┐ │
│  │              Storage Backend (OCI + Local)               │ │
│  │  ┌─────────────────┐    ┌────────────────────────────┐  │ │
│  │  │ OCI Object Store│    │ LocalStorage (fallback)     │  │ │
│  │  │ cust.-documents │    │ backend/uploads/           │  │ │
│  │  │ cust.-archive   │    │                            │  │ │
│  │  └─────────────────┘    └────────────────────────────┘  │ │
│  │         ↑                                               │ │
│  │  PAR → download() → BYTEA (fallback chain)             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼────────────────────────────────────┐
│                   PostgreSQL (Neon)                           │
│  users, companies, rats, breaches, eipd, consentimientos,     │
│  audit_logs, task_queue, token_blacklist, asesor_chunks       │
└──────────────────────────────────────────────────────────────┘
```

---

*Documento generado: 12 Junio 2026*
*Diff código vs docs — Custodio RAT Manager v1.4*