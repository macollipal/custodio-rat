# Respaldo y Recuperación — Custodio RAT Manager

## Política de Backup (Art. 13 y 46 Ley 21.719)

La normativa exige que el responsable del tratamiento implemente medidas técnicas y organizacionales
adecuadas para proteger los datos personales contra acceso no autorizado, pérdida o destrucción.

---

## Estrategia de Backup

### Frecuencia

| Tipo | Frecuencia | Retención |
|------|-----------|-----------|
| Backup completo | Semanal (domingo 02:00 CLT) | 4 semanas |
| Backup incremental | Diario (01:00 CLT) | 7 días |
| Backup de transacciones | Continuo (Wal-E / pg_basebackup) | 14 días |
| Snapshots Neon | Automático (Neon) | 7 días |

### Ubicación

- **Primario:** Neon PostgreSQL (replicación automática entre regiones AWS us-east-1)
- **Secundario:** Bucket S3 (us-east-1) con lifecycle policy
- **Terciario:** Glacier para archival (30 días)

---

## Cifrado de Backups

### En reposo (Encryption at Rest)

El proveedor Neon PostgreSQL ofrece encryption at rest mediante AES-256 en los servidores de base de datos.
Para verificar:

```sql
SELECT datname, datallowconn FROM pg_database WHERE datname = current_database();
```

### En tránsito (Encryption in Transit)

Todos los backups se transmiten por TLS 1.2+ con certificados válidos.

### En S3

Los archivos en S3 usan `SSE-S3` (AES-256) por defecto.
Para mayor seguridad, se recomienda `SSE-KMS` con clave gestionada por la organización.

Configuración recomendada en `vercel.json` o script de backup:

```bash
# Ejemplo: backup cifrado a S3
pg_dump -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME | \
  gzip | \
  openssl enc -aes-256-cbc -salt -pbkdf2 -out backup_$(date +%Y%m%d_%H%M%S).sql.gz.enc

aws s3 cp backup_*.enc s3://custodio-backups/ --sse aws:kms
```

---

## Procedimiento de Recuperación

### Restauración desde Neon (Point-in-Time Recovery)

1. Acceder al dashboard de Neon: https://neon.tech
2. Seleccionar el proyecto → Rama `main` → PITR
3. Elegir fecha y hora objetivo
4. Confirmar restauración → se crea una nueva rama temporal
5. Validar datos restaurados
6. Si todo OK, promover la rama restaurada a `main`

### Restauración desde S3

```bash
# 1. Descargar backup cifrado
aws s3 cp s3://custodio-backups/backup_YYYYMMDD_HHMMSS.sql.gz.enc /tmp/

# 2. Descifrar
openssl enc -aes-256-cbc -d -pbkdf2 -in /tmp/backup_*.enc -out /tmp/restore.sql.gz

# 3. Descomprimir
gunzip /tmp/restore.sql.gz

# 4. Restaurar (requiere DROP de la BD actual)
psql -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME < /tmp/restore.sql
```

---

## Verificación de Backups

### Test de Restauración

Trimestralmente se debe realizar un test de restauración en un entorno aislado:

```bash
# 1. Crear base de datos de test
psql -h $DATABASE_HOST -U $DATABASE_USER -d postgres -c \
  "CREATE DATABASE custodio_restore_test;"

# 2. Restaurar backup
pg_restore -h $DATABASE_HOST -U $DATABASE_USER -d custodio_restore_test backup.sql

# 3. Validar schema y datos críticos
psql -h $DATABASE_HOST -U $DATABASE_USER -d custodio_restore_test -c \
  "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM companies; SELECT COUNT(*) FROM rats;"

# 4. Limpiar entorno de test
psql -h $DATABASE_HOST -U $DATABASE_USER -d postgres -c \
  "DROP DATABASE custodio_restore_test;"
```

### Alertas de Fallo de Backup

Configurar en Vercel/Cron para verificar que los backups se ejecutan:

```bash
# Verificar último backup en S3
LAST_BACKUP=$(aws s3 ls s3://custodio-backups/ --recursive | sort | tail -n 1 | awk '{print $4}')
DAYS_OLD=$(echo $(date +%s) - $(aws s3api head-object --bucket custodio-backups --key "$LAST_BACKUP" --query 'LastModified' --output text) | bc)
if [ "$DAYS_OLD" -gt 2 ]; then
  echo "ALERTA: Backup tiene $DAYS_OLD días. Último: $LAST_BACKUP"
fi
```

---

## Roles y Responsabilidades

| Rol | Responsabilidad |
|-----|----------------|
| DevOps / Infra | Ejecutar backups, verificar integridad, restaurar |
| DPO | Validar que la política cumple con Art. 13 y 46 |
| CTO | Aprobar cambios en la estrategia de backup |

---

## Documento actualizado: $(date +%Y-%m-%d)

*Parte del Manual Técnico Custodio RAT Manager v1.2*