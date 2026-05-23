# Migración SQLite → PostgreSQL (Neon)

## Tabla de contenido
1. [Estrategia](#estrategia)
2. [Pasos de migración](#pasos-de-migración)
3. [Cambios en el código](#cambios-en-el-código)
4. [Rollback](#rollback)

---

## Estrategia

### Problemas identificados
- `database.py` usa `PRAGMA table_info` → sintaxis SQLite específica
- `_migrate_*` functions usan `ALTER TABLE ... ADD COLUMN` con sintaxis SQLite
- `connect_args={"check_same_thread": False}` → solo para SQLite
- No hay sistema de migraciones formal (Alembic)

### Enfoque: Big Bang Migration
1. Nuevo branch `feature/postgres-migration`
2. Modificar código para soportar **ambos** motores (SQLite dev / PostgreSQL prod)
3. Hacer backup de SQLite a JSON
4. Crear schema en Neon con Alembic
5. Importar datos en Neon
6. Cambiar `DATABASE_URL` a Neon en producción
7. Validar y mergear

### ¿Por qué no incremental?
- Los models ya tienen todas las columnas definidas vía SQLAlchemy (`Base.metadata.create_all`)
- Las columnas se agregan via `_migrate_*` que son parches SQLite → PostgreSQL las crea automáticamente
- Neon requiere esquema limpio desde cero

---

## Pasos de migración

### 1. Pre-migración: Backup de datos

```bash
cd backend
python export_sqlite_to_json.py
```

Genera `backup_data.json` con todos los registros de cada tabla.

### 2. Configurar variables de entorno

En `.env` de producción (Neon):

```env
DATABASE_URL=postgresql://user:password@ep-xxx-xxx-123456.neon.tech/custodio?sslmode=require
ENVIRONMENT=production
SECRET_KEY=<generar nueva clave>
```

### 3. Aplicar migraciones

```bash
cd backend
alembic upgrade head
```

O crear schema directamente:

```bash
cd backend
python -c "from app.database.init_postgres import init_schema; init_schema()"
```

### 4. Importar datos

```bash
cd backend
python import_to_postgres.py
```

### 5. Validar

```bash
cd backend
pytest tests/ -v
```

### 6. Actualizar frontend

Cambiar `NEXT_PUBLIC_API_BASE` si cambia el dominio.

---

## Cambios en el código

### `database.py`
- Detecta motor automáticamente (`sqlite` vs `postgresql`)
- SQLite: mantiene `check_same_thread` y PRAGMA
- PostgreSQL: usa connection pool, sslmode, quit `PRAGMA`

### `core/config.py`
- Agrega `resolved_database_url` property que construye URL para Neon
- Soporta `DATABASE_URL` directa o variables individuales (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`)

### `init_postgres.py` (nuevo)
- Crea todas las tablas con `Base.metadata.create_all`
-代替 `_migrate_*` functions de SQLite

### `export_sqlite_to_json.py` (nuevo)
- Exporta todos los registros de cada tabla a JSON
- Preserva fechas ISO y enums

### `import_to_postgres.py` (nuevo)
- Lee JSON y hace bulk insert usando SQLAlchemy
- Maneja foreign keys en orden correcto (users → companies → rats → ...)
- Limpia sequences/postgres SERIAL después de importar

### `alembic.ini` + `alembic/` (nuevo)
- Sistema de versionado de schema para futuras migraciones

---

## Orden de importación de datos (respetando FK)

```
1. users
2. rubro
3. companies
4. rats_sugeridos
5. user_companies
6. rats
7. audit_logs
8. eipds
9. security_breaches
10. consentimientos
```

---

## Rollback

Si algo falla:

1. Cambiar `DATABASE_URL` de vuelta a SQLite local:
   ```env
   DATABASE_URL=sqlite:///database.db
   ```
2. El backup JSON preserva todos los datos
3. Recrear import si es necesario

---

## Modelos y sus columnas

| Tabla | Notas |
|-------|-------|
| `users` | Enum `RolGlobal` → string |
| `companies` | FK a `rubros` |
| `rubros` | Simple |
| `rats_sugeridos` | FK a `rubros` |
| `user_companies` | FK a `users` y `companies`, UniqueConstraint |
| `rats` | FK a `companies`, Enum `EstadoRAT`, `EstadoEIPD` |
| `audit_logs` | Sin FK (string only) |
| `eipds` | FK a `rats`, Enum `ResultadoEIPD` |
| `security_breaches` | FK a `companies` |
| `consentimientos` | FK a `companies` y `rats`, Enum `CanalConsentimiento` |