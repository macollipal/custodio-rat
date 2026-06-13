"""
Script de limpieza para archivos huérfanos en OCI.

Un archivo huérfano es aquel que existe en el bucket de OCI pero NO está
referenciado en la tabla 'rats' de la base de datos (por bugs, migraciones parciales, etc.)

Uso:
    python cleanup_orphaned_files.py [--dry-run] [--days 7]

Opciones:
    --dry-run  : Solo muestra qué se eliminaría, no elimina nada
    --days N   : Solo considera archivos archivados hace más de N días (default: 7)

Este script es seguro: solo elimina archivos del bucket de ARCHIVO, no del bucket activo.
"""

import argparse
import base64
import json
import logging
import sys
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(__file__).replace("scripts/cleanup_orphaned_files.py", "backend"))

from app.core.config import settings
from app.core.storage import get_storage_backend, OCIStorageBackend


def get_storage_urls_from_db():
    """Obtiene todas las storage_urls de la tabla rats."""
    from app.database.database import SessionLocal

    db = SessionLocal()
    try:
        from app.models.rat import RAT

        urls = set()
        rats = db.query(RAT).all()
        for rat in rats:
            if rat.archivo_base_legal_storage_url:
                urls.add(rat.archivo_base_legal_storage_url)

        logger.info(f"Encontradas {len(urls)} storage_urls en DB")
        return urls
    finally:
        db.close()


def get_archive_objects_with_age(storage_backend: OCIStorageBackend, days_threshold: int = 7):
    """Lista objetos en archive bucket que tienen más de N días."""
    objects = storage_backend.list_archive_objects(prefix="rats")

    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)

    for obj in objects:
        name = obj.get("name", "")
        created_str = obj.get("created", "")

        if not created_str:
            continue

        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            if created < cutoff:
                results.append({
                    "name": name,
                    "size": obj.get("size", 0),
                    "created": created_str,
                    "age_days": (datetime.now(timezone.utc) - created).days
                })
        except Exception as e:
            logger.warning(f"Error parseando fecha de {name}: {e}")

    return results


def cleanup_orphaned_files(dry_run: bool = True, days_threshold: int = 7):
    """Elimina archivos huérfanos del bucket de archive."""

    logger.info("=" * 60)
    logger.info("CLEANUP DE ARCHIVOS HUÉRFANOS - CUSTODIO RAT")
    logger.info("=" * 60)

    if dry_run:
        logger.warning("MODO DRY-RUN: No se eliminará nada")

    cfg = settings.oci
    if not cfg:
        logger.error("OCI no configurado. Verificar OCI_CONFIG en .env")
        return

    if not cfg.get("archive_bucket"):
        logger.error("No hay archive_bucket configurado. Agregar 'archive_bucket' en OCI_CONFIG")
        return

    try:
        backend = get_storage_backend()
    except Exception as e:
        logger.error(f"Error inicializando storage backend: {e}")
        return

    if not isinstance(backend, OCIStorageBackend):
        logger.error("Este script solo funciona con OCIStorageBackend")
        return

    db_urls = get_storage_urls_from_db()
    logger.info(f"URLs en DB: {len(db_urls)}")

    orphaned = get_archive_objects_with_age(backend, days_threshold)
    logger.info(f"Archivos en archive bucket: {len(orphaned)}")

    to_delete = []
    for obj in orphaned:
        name = obj["name"]
        if name not in db_urls:
            to_delete.append(obj)

    logger.info(f"Archivos huérfanos encontrados: {len(to_delete)}")

    if not to_delete:
        logger.info("No hay archivos huérfanos para eliminar")
        return

    total_size = sum(obj["size"] for obj in to_delete)
    logger.info(f"Tamaño total a eliminar: {total_size / 1024 / 1024:.2f} MB")

    print("\n" + "=" * 60)
    print("ARCHIVOS HUÉRFANOS A ELIMINAR:")
    print("=" * 60)
    for obj in to_delete:
        print(f"  - {obj['name']}")
        print(f"    Tamaño: {obj['size'] / 1024:.1f} KB | Creado: {obj['created']} | Edad: {obj['age_days']} días")
    print("=" * 60)

    if dry_run:
        print("\n[DRY-RUN] Para eliminar realmente, ejecutar sin --dry-run")
        return

    confirm = input("\n¿Eliminar {} archivos? (escribir 'SI' para confirmar): ".format(len(to_delete)))
    if confirm != "SI":
        logger.info("Operación cancelada por el usuario")
        return

    deleted_count = 0
    error_count = 0
    for obj in to_delete:
        name = obj["name"]
        try:
            backend.delete_from_archive(name)
            logger.info(f"Eliminado: {name}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error eliminando {name}: {e}")
            error_count += 1

    logger.info("=" * 60)
    logger.info(f"RESULTADO: {deleted_count} eliminados, {error_count} errores")
    logger.info("=" * 60)


def cleanup_expired_from_archive(days_threshold: int = 30, dry_run: bool = True):
    """
    Elimina archivos del bucket de archive que tienen más de N días.
    Esto se usa para la política de retención: archivos en archive se eliminan
    después de 30 días (Ley 21.719 Art. 11).

    Args:
        days_threshold: Días mínimo en archive antes de eliminar (default: 30)
        dry_run: Si True, solo muestra qué se eliminaría
    """
    logger.info("=" * 60)
    logger.info(f"LIMPIEZA DE ARCHIVE - Retención {days_threshold} días")
    logger.info("=" * 60)

    if dry_run:
        logger.warning("MODO DRY-RUN: No se eliminará nada")

    cfg = settings.oci
    if not cfg or not cfg.get("archive_bucket"):
        logger.error("OCI archive_bucket no configurado")
        return

    try:
        backend = get_storage_backend()
    except Exception as e:
        logger.error(f"Error inicializando storage: {e}")
        return

    expired = get_archive_objects_with_age(backend, days_threshold)
    logger.info(f"Archivos con más de {days_threshold} días en archive: {len(expired)}")

    if not expired:
        logger.info("No hay archivos vencidos para eliminar")
        return

    print("\n" + "=" * 60)
    print(f"ARCHIVOS VENCIDOS (más de {days_threshold} días en archive):")
    print("=" * 60)
    for obj in expired:
        print(f"  - {obj['name']} | {obj['age_days']} días")
    print("=" * 60)

    if dry_run:
        print("\n[DRY-RUN] Para eliminar realmente, ejecutar sin --dry-run")
        return

    confirm = input("\n¿Eliminar {} archivos vencidos? (escribir 'SI' para confirmar): ".format(len(expired)))
    if confirm != "SI":
        logger.info("Operación cancelada")
        return

    deleted = 0
    errors = 0
    for obj in expired:
        try:
            backend.delete_from_archive(obj["name"])
            deleted += 1
        except Exception as e:
            logger.error(f"Error: {obj['name']}: {e}")
            errors += 1

    logger.info(f"RESULTADO: {deleted} eliminados, {errors} errores")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpieza de archivos huérfanos en OCI")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Solo muestra qué se eliminaría (default: True)")
    parser.add_argument("--execute", action="store_false", dest="dry_run",
                        help="Ejecutar realmente la eliminación")
    parser.add_argument("--days", type=int, default=7,
                        help="Días mínimos para considerar archivo como huérfano (default: 7)")
    parser.add_argument("--expired", action="store_true",
                        help="Eliminar archivos vencidos del archive (política de retención)")
    parser.add_argument("--retention-days", type=int, default=30,
                        help="Días de retención en archive antes de eliminar (default: 30)")

    args = parser.parse_args()

    if args.expired:
        cleanup_expired_from_archive(
            days_threshold=args.retention_days,
            dry_run=args.dry_run
        )
    else:
        cleanup_orphaned_files(
            dry_run=args.dry_run,
            days_threshold=args.days
        )
