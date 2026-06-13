# Índice de Scripts — Custodio RAT

## Estructura

```
scripts/
├── deploy/          # Scripts de deploy y validación
├── smoke/           # Smoke tests automatizados
├── maintenance/    # Scripts de mantenimiento
├── debug/           # Scripts de debug (git ignored)
└── legacy/          # Scripts legacy (git ignored)
```

## Scripts de Deploy

| Script | Descripción |
|--------|-------------|
| [validate_env.py](deploy/validate_env.py) | Valida variables de entorno antes de deploy |
| [iniciar.bat](deploy/iniciar.bat) | Inicia backend + frontend |
| [matar_puertos.bat](deploy/matar_puertos.bat) | Detiene servicios en puertos |
| [run_server_backend.cmd](deploy/run_server_backend.cmd) | Inicia backend con uvicorn |
| [run_local_backend.cmd](deploy/run_local_backend.cmd) | Inicia backend local |
| [run_local_frontend.cmd](deploy/run_local_frontend.cmd) | Inicia frontend local |
| [run_tests.bat](deploy/run_tests.bat) | Ejecuta tests pytest |

## Smoke Tests

| Script | Descripción |
|--------|-------------|
| [smoke_test_prod.py](smoke/smoke_test_prod.py) | Smoke test post-deploy producción |
| [test_oci_e2e_qa.py](smoke/test_oci_e2e_qa.py) | Test E2E de OCI en QA |

## Scripts de Mantenimiento

| Script | Descripción |
|--------|-------------|
| [cleanup_orphans.py](maintenance/cleanup_orphans.py) | Limpia archivos huérfanos en OCI |
| [migrate_oci_storage.py](maintenance/migrate_oci_storage.py) | Migra archivos entre buckets |
| [migrate_to_neon.py](maintenance/migrate_to_neon.py) | Migra datos SQLite → Neon |
| [sync_sequences.py](maintenance/sync_sequences.py) | Sincroniza sequences de PostgreSQL |
| [seed_claudio_corp.py](maintenance/seed_claudio_corp.py) | Seed datos de prueba |
| [generar_manual.py](maintenance/generar_manual.py) | Genera manual de usuario |

## Scripts de Debug (git ignored)

| Script | Descripción |
|--------|-------------|
| [check_users.py](debug/check_users.py) | Verifica usuarios en BD |
| [check_claudio.py](debug/check_claudio.py) | Debug usuario claudio |
| [test_db_connection.py](debug/test_db_connection.py) | Test conexión BD |
| [verify_signature.py](debug/verify_signature.py) | Verifica firma OCI |
| [verify_key.py](debug/verify_key.py) | Verifica clave API |
| [test_oci_debug.py](debug/test_oci_debug.py) | Debug OCI |
| [compare_signatures.py](debug/compare_signatures.py) | Compara signatures |
| [check_oci_permissions.py](debug/check_oci_permissions.py) | Verifica permisos OCI |
| [check_fp.py](debug/check_fp.py) | Verifica fingerprint |
| [gen_curl.py](debug/gen_curl.py) | Genera comandos curl |
| [full_compare.py](debug/full_compare.py) | Comparación completa |
| [direct_compare.py](debug/direct_compare.py) | Comparación directa |
| [debug_headers.py](debug/debug_headers.py) | Debug headers HTTP |
| [_debug_oci_sign.py](debug/_debug_oci_sign.py) | Debug signing OCI |

## Scripts Legacy (git ignored)

| Script | Descripción |
|--------|-------------|
| [fix_claudio_pwd.py](legacy/fix_claudio_pwd.py) | Fix password claudio |
| [reset_admin.py](legacy/reset_admin.py) | Reset admin |
| [generate_doc.py](legacy/generate_doc.py) | Genera documento |
| [capture_sdk_signature.py](legacy/capture_sdk_signature.py) | Captura signature SDK |
| [capture_oci_headers.py](legacy/capture_oci_headers.py) | Captura headers OCI |

---

*Última actualización: 2026-06-13*
