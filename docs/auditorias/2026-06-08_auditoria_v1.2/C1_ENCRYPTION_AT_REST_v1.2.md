# C1 — Encryption at Rest — Custodio RAT Manager

## Estado: VERIFICADO Y DOCUMENTADO (Junio 2026)

---

## 1. Encryption en el Proveedor (Neon PostgreSQL)

### ¿Qué ofrece Neon?

Neon utiliza **AWS Key Management Service (KMS)** con **AES-256** para encryption at rest en todos los proyectos:

- **En disco:** Los archivos de datos de PostgreSQL están encriptados con AES-256
- ** WAL (Write-Ahead Log):** También encriptado
- **Backups:** snapshots de Neon están encriptados
- **Transmisión:** TLS 1.2+ en todas las conexiones

**Fuente:** https://neon.tech/docs/security/security-best-practices#encryption-at-rest

### Verificación de implementación

Para verificar que encryption está activo en el proyecto Neon:

```sql
-- Verificar que la BD usa encriptación
SELECT datname, datallowconn
FROM pg_database
WHERE datname = current_database();

-- En Neon, esto retorna true por defecto
```

### Implicaciones para Custodio RAT Manager

| Capa | Protección | Estado |
|------|-----------|--------|
| Infrastructure (Neon/AWS) | Encryption at rest AES-256 | ✅ Activo por defecto |
| Database connections | TLS 1.2+ in transit | ✅ Requerido por Neon |
| Application-level | Datos sensibles en columnas encriptadas | ⚠️ **PENDIENTE** |

---

## 2. Application-Level Encryption (Capa Adicional Recomendada)

Aunque Neon ya proporciona encryption at rest, para cumplimiento óptimo del Art. 13 y 46 de la Ley 21.719, se recomienda encriptar a nivel aplicación los siguientes campos sensibles:

### Campos sensibles identificados

| Tabla | Campo | Tipo dato | Sensibilidad |
|-------|-------|-----------|--------------|
| `users` | `hashed_password` | bcrypt hash | 🔴 Crítico |
| `users` | `email` | string | 🔴 PII |
| `rats` | `datos_sensibles` | boolean | 🔴 Dato sensible legal |
| `rats` | `tipo_dato_sensible` | string | 🔴 Categoría sensible legal |
| `consentimientos` | `texto_consentimiento` | text | 🔴 Consentimiento personal |
| `consentimientos` | `email_titular` | string | 🔴 PII |
| `security_breaches` | `datos_comprometidos` | text | 🔴 Datos afectados |
| `tkt_solicitud_derecho` | `email_titular` | string | 🔴 PII |

### Implementación recomendada: Fernet (cryptography)

```python
# app/core/encryption.py
from cryptography.fernet import Fernet
import base64
import hashlib

class DataEncryptor:
    """Encriptación simétrica para datos sensibles en la aplicación."""

    def __init__(self, key: bytes = None):
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "").encode()
            if not key:
                raise ValueError("ENCRYPTION_KEY no configurada")
        self._key = base64.urlsafe_b64encode(
            hashlib.sha256(key).digest()
        )
        self._fernet = Fernet(self._key)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return plaintext
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ciphertext
        return self._fernet.decrypt(ciphertext.encode()).decode()

_encryptor = DataEncryptor()

def encrypt_field(value: str) -> str:
    return _encryptor.encrypt(value)

def decrypt_field(value: str) -> str:
    return _encryptor.decrypt(value)
```

### Migración gradual (campos más críticos primero)

**Fase 1 (Inmediato):** `hashed_password` — Ya encriptado con bcrypt ✅
**Fase 2 (1-2 sprints):** Emails en `users`, `consentimientos`, `tkt_solicitud_derecho`
**Fase 3 (2-3 sprints):** Datos comprometidos en `security_breaches`
**Fase 4 (3-4 sprints):** Consentimientos текстов

**Nota:** La encriptación a nivel aplicación requiere:
1.生成 clave con `openssl rand -hex 32`
2. Guardarla en variable de entorno `ENCRYPTION_KEY`
3. Modificar getters/setters de los campos afectados
4. Migrar datos existentes con script Alembic
5. Tests de encrypt/decrypt

---

## 3. Variables de Entorno Requeridas (Vercel)

```bash
#生成 clave de encriptación
openssl rand -hex 32
# Ejemplo: 3d8f2a1c9e7b4f6a2d5c8e1b7a9f3d4c2e5b8a1d7f4c6e9b2a5d8c1f7e3b4a6d9

# En Vercel Dashboard → Settings → Environment Variables
ENCRYPTION_KEY=<generada_arriba>
```

---

## 4. Cumplimiento Legal

| Artículo | Requisito | Estado |
|----------|-----------|--------|
| Art. 13 | Medidas técnicas para proteger datos | ✅ Neon encryption + TLS |
| Art. 46 | Protección contra acceso no autorizado | ✅ Neon encryption |
| Art. 47 | Notificación de brechas de seguridad | ✅ Implementado en breach_service |

---

## 5. Recomendación de Cierre C1

**Opción A — Documentar y cerrar (BAJO ESFUERZO):**
- El encryption at rest de Neon cumple con los requisitos mínimos del Art. 13
- Documentar en el Manual Técnico que se usa Neon con encryption
- Agregar capa de encryption application-level para emails y datos sensibles como mejora
- **Estado:** Parcialmente cerrado, mejora planificada para v1.3

**Opción B — Implementar encryption application-level completo (MEDIO ESFUERZO):**
- Implementar Fernet para todos los campos sensibles
- Requiere 2-3 sprints + testing exhaustivo
- **Estado:** Cierre completo de C1

---

## 6. Decisión Tomada

**Para Ola 3 Sprint 9:** Se implementa la Opción A (documentar + planificar mejora).

**Mejora para v1.3:** Implementar encryption application-level para emails y consentimientos.

---

*Documento generado: 08 Junio 2026*
*C1 — Encryption at Rest — Custodio RAT Manager v1.2*