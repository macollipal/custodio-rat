# MANUAL: Configurar Custodio RAT con OCI Object Storage

## Objetivo

Migrar el almacenamiento de archivos PDF de los RATs desde la columna `BYTEA` de PostgreSQL hacia **OCI Object Storage** (Oracle Cloud Infrastructure), manteniendo BYTEA como fallback en caso de falla.

---

## Prerequisites

- Cuenta Oracle Cloud Infrastructure (OCI)
- Bucket de Object Storage creado
- Clave de firma API (API Signing Key) generada

---

## Paso 1: Crear el Bucket en OCI

1. Login en [Oracle Cloud Console](https://cloud.oracle.com)
2. Ir a **Storage → Object Storage & Archive Storage**
3. Seleccionar el **Compartment** correcto
4. Click **Create Bucket**
   - **Nombre:** `custodio-documents-qa` (QA) o `custodio-documents-prod` (Producción)
   - **Storage Tier:** Standard
   - **Encryption:** Encrypt using Oracle managed keys (o clave KMS propia si tienes)
5. Anotar el **Namespace** del bucket (visible en la página del bucket, junto al nombre)

---

## Paso 2: Generar API Signing Key

**En local (máquina del desarrollador):**

### 2.1 Instalar OCI CLI

```bash
pip install oci-cli
```

### 2.2 Generar las claves

```bash
oci setup keys
```

- **Ubicación de la clave privada:** `/Users/tu_usuario/.oci/oci_api_key.pem`
- **Passphrase:** (vacío, presionar ENTER)

Esto genera dos archivos:
- `oci_api_key.pem` — clave privada (NUNCA compartir)
- `oci_api_key_public.pem` — clave pública

### 2.3 Subir la clave pública a OCI

1. Ir a **Identity → Users → [Tu usuario]**
2. Click **API Keys → Add API Key**
3. Seleccionar **"Upload public key (.pub)"**
4. Subir el archivo `oci_api_key_public.pem`
5. **Copiar el fingerprint** que aparece (ej: `58:5e:b3:62:fb:f1:6f:d7:a5:ff:41:9a:e7:b9:7c:db`)

---

## Paso 3: Obtener los valores de configuración de OCI

Desde la consola de OCI, anotar cada valor:

| Variable | Dónde encontrarla |
|----------|-------------------|
| `tenancy_ocid` | **Identity → Tenancy** → OCID (empieza con `ocid1.tenancy.oc1..`) |
| `user_ocid` | **Identity → Users → [Tu usuario]** → OCID (empieza con `ocid1.user.oc1..`) |
| `fingerprint` | **Identity → Users → [Tu usuario] → API Keys** → fingerprint de la key subida |
| `region` | **Regions** → tu región (ej: `sa-santiago-1`, `us-ashburn-1`) |
| `namespace` | **Storage → Object Storage** → namespace (es el mismo OCID del tenancy en cuentas gratuitas) |
| `bucket` | **Storage → Object Storage → Buckets** → nombre del bucket creado |

---

## Paso 4: Configurar Variables de Entorno en Vercel

Ir al dashboard de Vercel → proyecto **Custodio QA** → **Settings → Environment Variables**

Crear las siguientes variables para cada ambiente:

### QA

| Variable | Valor |
|----------|-------|
| `OCI_CONFIG` | `{"backend":"oci","namespace":"TU_NAMESPACE","region":"TU_REGION","bucket":"custodio-documents-qa","tenancy":"TU_TENANCY_OCID","user":"TU_USER_OCID","fingerprint":"TU_FINGERPRINT"}` |
| `OCI_KEY_CONTENT` | Contenido del archivo `oci_api_key.pem` con saltos de línea reemplazados por `\n` literal |

### Producción

| Variable | Valor |
|----------|-------|
| `OCI_CONFIG` | `{"backend":"oci","namespace":"TU_NAMESPACE","region":"TU_REGION","bucket":"custodio-documents-prod","tenancy":"TU_TENANCY_OCID","user":"TU_USER_OCID","fingerprint":"TU_FINGERPRINT"}` |
| `OCI_KEY_CONTENT` | Contenido del archivo `oci_api_key.pem` con saltos de línea reemplazados por `\n` literal |

### Cómo formatear OCI_KEY_CONTENT

El archivo `.pem` tiene saltos de línea reales. En la variable de entorno de Vercel hay que convertirlos a `\n` literal (backslash-barra-n).

**Manualmente:**
```bash
# En terminal Linux/Mac:
cat ~/.oci/oci_api_key.pem | tr '\n' '~' | sed 's/~/\\n/g'
# Esto reemplaza los saltos de línea reales por la secuencia literal \n
```

**Manualmente (copiar directo):**
1. Abrir `oci_api_key.pem` en un editor de texto
2. Reemplazar todos los saltos de línea con `\n` (literal)
3. Pegar en la variable de entorno

**Validación:**
La clave debe empezar con `-----BEGIN PRIVATE KEY-----\nMII...` y terminar con `...\n-----END PRIVATE KEY-----`

---

## Paso 5: Configurar en Desarrollo Local

En el archivo `backend/.env` (no commitear este archivo):

```bash
OCI_CONFIG={"backend":"oci","namespace":"TU_NAMESPACE","region":"TU_REGION","bucket":"custodio-documents-qa","tenancy":"TU_TENANCY_OCID","user":"TU_USER_OCID","fingerprint":"TU_FINGERPRINT"}
OCI_KEY_CONTENT=-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0B...\n-----END PRIVATE KEY-----
```

**Verificar que funcione localmente:**
```bash
cd backend
python -c "from app.core.storage import get_storage_backend; b = get_storage_backend(); print(b)"
# Debería mostrar: <app.core.storage.OCIStorageBackend object at ...>
```

---

## Paso 6: Verificar la Configuración

### 6.1 Test rápido local

```bash
cd backend
python -c "
from app.core.storage import OCIStorageBackend
from app.core.config import settings
import requests

cfg = settings.oci
backend = OCIStorageBackend(cfg, settings.OCI_KEY_CONTENT)
signed = backend.signer.sign_headers('GET', f'/n/{cfg[\"namespace\"]}/b/{cfg[\"bucket\"]}/o', backend.host)
resp = requests.get(backend.base_url + f'/n/{cfg[\"namespace\"]}/b/{cfg[\"bucket\"]}/o', headers=signed, timeout=10)
print(f'Status: {resp.status_code}')
print(f'Objects: {resp.json()}')
"
```

Debería devolver `Status: 200` con `{"objects": [...]}`.

### 6.2 Test en QA (desplegado)

1. Hacer push a la branch `qa`
2. Esperar ~2 minutos a que Vercel rebuilde
3. Abrir: `https://custodio-api-qa.vercel.app/debug/oci/test`
4. Verificar que `response_status` sea `200`

### 6.3 Test de upload real

1. Subir un RAT con archivo PDF en Custodio QA
2. Verificar en OCI Console → Storage → Buckets → `custodio-documents-qa` → Objects
3. El PDF debería aparecer con el nombre generado (ej: `rats/23dc5cd33e5a.pdf`)

---

## Cómo funciona el Sistema de Storage

### Flujo de Upload

```
Cliente sube archivo PDF
    ↓
rat_service.py
    ↓
Intenta: OCIStorageBackend.upload()
    ├── Éxito → guardar URL en DB (archivo_base_legal_storage_url)
    └── Falla (401, 500, timeout, etc.)
        ↓
    Guardar en BYTEA (fallback)
```

### Flujo de Download

```
Cliente pide archivo RAT
    ↓
rat_service.py
    ↓
Si archivo tiene storage_url (OCI)
    ↓
Intenta: OCIStorageBackend.download()
    ├── Éxito → retorna bytes
    └── Falla → fallback a BYTEA
Si archivo NO tiene storage_url
    ↓
Usar BYTEA directamente
```

### Columna de referencia

La columna `archivo_base_legal_storage_url` en la tabla `rats` indica dónde está el archivo:
- `NULL` → archivo en BYTEA
- `rats/abc123.pdf` → archivo en OCI (path dentro del bucket)

---

## Permisos IAM necesarios

El usuario de API necesita estos permisos en el compartment donde está el bucket:

```sql
Allow user <user_ocid> to read buckets in compartment <compartment_name>
Allow user <user_ocid> to read objects in compartment <compartment_name>
Allow user <user_ocid> to create objects in compartment <compartment_name>
Allow user <user_ocid> to update objects in compartment <compartment_name>
Allow user <user_ocid> to delete objects in compartment <compartment_name>
```

### Error común: NamespaceNotFound

Si al probar con el SDK de OCI obtienes:
```
NamespaceNotFound: You do not have authorization to perform this request
```

Significa que el usuario **sí se autenticó** (la firma funciona) pero **no tiene permisos** sobre el bucket. Verificar las políticas IAM.

---

## Troubleshooting

### Error 401 NotAuthenticated

**Causas posibles:**

1. **Fingerprint incorrecto** → Verificar que el fingerprint en `OCI_CONFIG` coincida con el de la API Key subida en OCI
2. **Clave privada incorrecta** → Verificar que `OCI_KEY_CONTENT` sea la clave correcta
3. **Orden de headers en signing string incorrecto** → El código ya está corregido para usar `date (request-target) host`
4. **Formato del Authorization header** → El código ya está corregido para coincidir con el SDK de OCI

**Debug endpoint:**
```
https://custodio-api-qa.vercel.app/debug/oci/test
```
Muestra el signing string, headers enviados y respuesta de OCI.

### Error: No module named 'requests'

Vercel no instaló las dependencias. Verificar que `requirements.txt` (en la raíz del proyecto, NO en `backend/`) contenga:
```
requests==2.32.3
cryptography==44.0.0
```

### El archivo se sube a OCI pero no aparece en la consola

- Verificar que el bucket esté en la región correcta
- Verificar que el namespace sea el correcto
- Esperar ~1 minuto para que OCI propague la lista de objetos

---

## Referencias

- [OCI Object Storage API](https://docs.oracle.com/en-us/iaas/tools/python/latest/api/object_storage.html)
- [OCI API Signing Documentation](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)
- [OCI Python SDK](https://docs.oracle.com/en-us/iaas/tools/python/latest/index.html)
- [HTTP Signatures (RFC 9421)](https://datatracker.ietf.org/doc/html/rfc9421)

---

## Historial de cambios

| Fecha | Cambio |
|-------|--------|
| 2026-06-13 | Fix: Orden de headers en signing string (`date (request-target) host` en vez de `(request-target) date host`) |
| 2026-06-13 | Fix: Formato del Authorization header para coincidir con OCI SDK |
| 2026-06-13 | Fix: Algoritmo `rsa-sha256` en vez de `SHA256withRSA` |
| 2026-06-12 | Versión inicial con API Signing Key manual |
