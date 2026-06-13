# Changelog — Custodio RAT Manager

## [1.3.1] - 2026-06-13

### Fixed
- OCI: Fallback a download directo cuando PAR falla (commit `57cbffc`)
- OCI: `sign_headers()` acepta `content_type` como keyword argument
- storage.py: Content-Type para requests con body JSON

### Changed
- Reorganización de carpetas del proyecto
- Scripts movidos a `scripts/{debug,maintenance,legacy}/`
- Documentación movida a `docs/{arquitectura,auditorias,despliegue,...}/`
- Auditorías consolidadas en `docs/auditorias/`

## [1.3.0-beta] - 2026-06-09

### Fixed
- RBAC: `admin_empresa` no puede crear RAT en empresa ajena
- RBAC: `usuario` no puede crear brechas de seguridad
- Endpoint `/health` creado
- `_get_user()` wrapper corregido en consentimientos y eipd
- Token blacklist implementado

### Added
- Páginas `/consentimientos` y `/eipd` en frontend
- Hash chain de auditoría verificable
- PII masking en logs

### Changed
- Score de seguridad: 7/10 → 8.5/10
- Score general: 6.3/10 → 7.5/10

## [1.2.0] - 2026-06-08

### Fixed
- IDOR en `/companies/{id}`
- `/companies/publico` sin autenticación
- CSV injection en exports
- Índices faltantes en BD
- N+1 queries

### Added
- Repository pattern base
- Audit hash chain
- Token blacklist

## [1.1.0] - 2026-05-31

### Added
- Sistema de roles (superadmin, admin_empresa, usuario)
- Módulo de consentimientos (Art. 12)
- Módulo EIPD (Art. 15 bis)
- Cola de tareas asíncronas
- OnboardingChecklist

### Fixed
- Rate limiting en endpoints de auth
- Validación de RUT chileno

## [1.0.0] - 2026-05

### Added
- CRUD completo de RATs
- Gestión de empresas y usuarios
- Módulo de brechas de seguridad (Art. 14 bis)
- Módulo ARCO (Solicitudes de Derecho)
- Exportación PDF y CSV
- Chat IA

---

## Reglas de Versionado

- **MAJOR**: Breaking changes (ej: cambio de modelo de datos)
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Bug fixes y mejoras menores

## Formato de Commits

```
feat: nueva funcionalidad
fix: bug fix
chore: mantenimiento (deps, refactor, docs)
docs: solo documentación
test: solo tests
refactor: refactorización de código
security: fix de seguridad
```

---

*Generado: 2026-06-13*
