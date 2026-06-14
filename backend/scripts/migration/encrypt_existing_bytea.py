"""
Migración one-shot: cifra BYTEA existentes con Fernet (C1-F5).

Idempotente. Hace backup automático en SQLite. Neon requiere pg_dump manual previo.

Tablas afectadas:
  - rats.archivo_base_legal_datos
  - encargados_contrato.archivo_pdf_datos
  - tkt_adjuntos.data

Detección de "ya cifrado" (heurística):
  Fernet produce output que empieza con byte 0x80 (versión) seguido de timestamp.
  En base64 url-safe esto se ve como prefijo "gAAAAA" en los primeros 8 bytes ASCII.

Uso:
  cd backend
  python scripts/migration/encrypt_existing_bytea.py [--dry-run] [--batch-size=100]
  python scripts/migration/encrypt_existing_bytea.py --tables=rats --batch-size=50

Variables de entorno requeridas:
  ENCRYPTION_KEY  (debe ser la MISMA que se usará en producción post-migración)
  DATABASE_URL    (PostgreSQL/Neon o SQLite)

⚠️  ADVERTENCIAS:
  - Cambiar ENCRYPTION_KEY después de migrar hace los datos irrecuperables.
  - En Neon/PostgreSQL, ejecutar pg_dump ANTES de correr este script.
  - Este script NO cifra uploads futuros (eso lo hace el código en runtime).
"""

import argparse
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Permitir imports del paquete app/
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.crypto import encrypt, _get_fernet
from cryptography.fernet import Fernet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("encrypt_existing_bytea")


FERNET_PREFIX = b"gAAAAA"  # base64 url-safe de 0x80 + primeros 4 bytes timestamp


def is_already_encrypted(data: bytes) -> bool:
    """Heurística: Fernet produce output que empieza con 'gAAAAA' en base64 url-safe."""
    if not data or len(data) < len(FERNET_PREFIX):
        return False
    return data[: len(FERNET_PREFIX)] == FERNET_PREFIX


def _check_prerequisites() -> tuple[str, Fernet]:
    """Verifica ENCRYPTION_KEY y devuelve (database_url, fernet_instance)."""
    db_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    if not db_url:
        logger.critical("DATABASE_URL no configurada. Abortando.")
        sys.exit(1)

    key = os.getenv("ENCRYPTION_KEY") or settings.ENCRYPTION_KEY
    if not key:
        logger.critical(
            "ENCRYPTION_KEY no configurada. "
            "Es OBLIGATORIA para migración (no se usa dev fallback). "
            "Generar: python -c \"from app.core.crypto import generate_key; print(generate_key())\""
        )
        sys.exit(1)

    try:
        fernet = Fernet(key.encode())
        fernet.encrypt(b"test")
    except Exception as e:
        logger.critical(f"ENCRYPTION_KEY inválida (no es Fernet válida): {e}. Abortando.")
        sys.exit(1)

    logger.info(f"ENCRYPTION_KEY válida (Fernet OK)")
    logger.info(f"DATABASE_URL: {'sqlite' if 'sqlite' in db_url else 'postgresql'}")
    return db_url, fernet


def _backup_sqlite(db_path: str) -> None:
    """Crea backup de SQLite con timestamp."""
    if not Path(db_path).exists():
        logger.warning(f"Archivo SQLite {db_path} no existe, skip backup")
        return
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"{db_path}.backup-{ts}"
    shutil.copy2(db_path, backup_path)
    logger.info(f"Backup SQLite creado: {backup_path}")


def _build_engine_and_session(db_url: str):
    """Crea engine y session según el tipo de BD."""
    is_sqlite = "sqlite" in db_url
    if is_sqlite:
        engine = create_engine(db_url, echo=False)
    else:
        engine = create_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            poolclass=QueuePool,
            pool_size=2,
            max_overflow=3,
        )
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return engine, Session


def _analyze_table(db, table_name: str, column: str, model, id_field: str) -> dict:
    """Cuenta registros totales, no nulos, en plano y cifrados."""
    logger.info(f"--- Análisis: {table_name}.{column} ---")
    total = db.query(model).count()
    no_nulos = db.query(model).filter(getattr(model, column).isnot(None)).count()

    en_plano = 0
    ya_cifrados = 0
    filas = db.query(getattr(model, column)).filter(getattr(model, column).isnot(None)).all()
    for (data,) in filas:
        if is_already_encrypted(data):
            ya_cifrados += 1
        else:
            en_plano += 1

    logger.info(f"  total registros: {total}")
    logger.info(f"  con datos no nulos: {no_nulos}")
    logger.info(f"  ya cifrados: {ya_cifrados}")
    logger.info(f"  en plano (a migrar): {en_plano}")
    return {"total": total, "no_nulos": no_nulos, "en_plano": en_plano, "ya_cifrados": ya_cifrados}


def _migrate_table(
    db,
    table_name: str,
    column: str,
    model,
    id_field: str,
    fernet: Fernet,
    batch_size: int,
    dry_run: bool,
) -> dict:
    """Migra una tabla. Retorna dict con estadísticas."""
    logger.info(f"--- {'DRY-RUN ' if dry_run else ''}Migrando: {table_name}.{column} ---")
    stats = {"migrados": 0, "ya_cifrados": 0, "errores": 0, "vacias": 0}

    filas = (
        db.query(model)
        .filter(getattr(model, column).isnot(None))
        .all()
    )

    batch = []
    for row in filas:
        data = getattr(row, column)
        row_id = getattr(row, id_field)

        if not data:
            stats["vacias"] += 1
            continue

        if is_already_encrypted(data):
            stats["ya_cifrados"] += 1
            continue

        try:
            cifrado = encrypt(data)
            if dry_run:
                logger.info(f"  [DRY-RUN] {table_name}.{id_field}={row_id}: {len(data)}B → {len(cifrado)}B cifrado")
            else:
                setattr(row, column, cifrado)
                batch.append(row_id)
                stats["migrados"] += 1

                if len(batch) >= batch_size:
                    db.commit()
                    logger.info(f"  Batch commit: {len(batch)} filas ({table_name})")
                    batch = []
        except Exception as e:
            stats["errores"] += 1
            logger.error(f"  Error migrando {table_name}.{id_field}={row_id}: {e}")

    if batch and not dry_run:
        db.commit()
        logger.info(f"  Batch final commit: {len(batch)} filas ({table_name})")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Cifra BYTEA existentes con Fernet (C1-F5)")
    parser.add_argument("--dry-run", action="store_true", help="Solo analizar, no modificar BD")
    parser.add_argument("--batch-size", type=int, default=100, help="Filas por commit (default 100)")
    parser.add_argument("--tables", type=str, default="rats,encargados_contrato,tkt_adjuntos",
                        help="Subset de tablas a migrar (comma-separated)")
    parser.add_argument("--force", action="store_true", help="No pedir confirmación interactiva")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("C1-F5: Migración de BYTEA a cifrado Fernet")
    logger.info("=" * 60)

    db_url, fernet = _check_prerequisites()

    is_sqlite = "sqlite" in db_url
    if is_sqlite and not args.dry_run:
        sqlite_path = db_url.replace("sqlite:///", "")
        _backup_sqlite(sqlite_path)

    engine, Session = _build_engine_and_session(db_url)

    from app.models.rat import RAT
    from app.models.encargado_contrato import EncargadoContrato
    from app.models.tkt_adjunto import TktAdjunto

    TABLAS = {
        "rats": ("archivo_base_legal_datos", RAT, "id"),
        "encargados_contrato": ("archivo_pdf_datos", EncargadoContrato, "id"),
        "tkt_adjuntos": ("data", TktAdjunto, "id"),
    }

    tablas_solicitadas = set(args.tables.split(","))
    tablas_a_procesar = {k: v for k, v in TABLAS.items() if k in tablas_solicitadas}
    if not tablas_a_procesar:
        logger.critical(f"Ninguna tabla válida. Disponibles: {list(TABLAS.keys())}")
        sys.exit(1)

    if not args.force and not args.dry_run:
        logger.warning("=" * 60)
        logger.warning("⚠️  ESTA OPERACIÓN ES IRREVERSIBLE")
        logger.warning("⚠️  Asegúrate de tener backup de la BD (pg_dump en Neon)")
        logger.warning("=" * 60)
        resp = input("¿Continuar? (yes/no): ").strip().lower()
        if resp != "yes":
            logger.info("Abortado por el usuario")
            sys.exit(0)

    db = Session()
    start = time.time()
    resumenes = {}

    try:
        logger.info("Fase 1: Análisis pre-migración")
        for nombre, (column, model, id_field) in tablas_a_procesar.items():
            resumenes[nombre] = _analyze_table(db, nombre, column, model, id_field)

        total_plano = sum(r["en_plano"] for r in resumenes.values())
        if total_plano == 0:
            logger.info("✅ No hay registros en plano. Nada que migrar.")
            return

        logger.info(f"Total a migrar: {total_plano} registros en plano")

        logger.info("Fase 2: Migración")
        for nombre, (column, model, id_field) in tablas_a_procesar.items():
            stats = _migrate_table(
                db, nombre, column, model, id_field,
                fernet, args.batch_size, args.dry_run
            )
            resumenes[nombre].update(stats)

        logger.info("Fase 3: Verificación post-migración")
        for nombre, (column, model, id_field) in tablas_a_procesar.items():
            post = _analyze_table(db, nombre, column, model, id_field)
            delta = post["en_plano"] - resumenes[nombre]["en_plano"] + resumenes[nombre]["migrados"]
            logger.info(f"  {nombre}: en_plano {resumenes[nombre]['en_plano']} → {post['en_plano']} (delta: {delta})")

    except Exception as e:
        logger.critical(f"Error fatal: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info(f"✅ Migración completada en {elapsed:.1f}s")
    if args.dry_run:
        logger.info("(DRY-RUN: no se modificó la BD)")
    logger.info("=" * 60)

    for nombre, stats in resumenes.items():
        logger.info(f"  {nombre}: migrados={stats.get('migrados', 0)}, "
                    f"ya_cifrados={stats.get('ya_cifrados', 0)}, "
                    f"errores={stats.get('errores', 0)}, "
                    f"vacías={stats.get('vacias', 0)}")


if __name__ == "__main__":
    main()