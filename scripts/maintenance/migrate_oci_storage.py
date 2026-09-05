"""
Migraci├│n: Agrega columna archivo_base_legal_storage_url a tabla rats.
Idempotente: si la columna ya existe, no hace nada.

Uso:
    python scripts/migrate_oci_storage.py            # aplica migraci├│n
    python scripts/migrate_oci_storage.py --rollback # revierte migraci├│n
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text

from app.database.database import engine


TABLE = "rats"
COLUMN = "archivo_base_legal_storage_url"
COLUMN_TYPE = "VARCHAR(1000)"


def column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _print_header(env_label: str, action: str):
    host = engine.url.host or "?"
    db = engine.url.database or "?"
    print(f"=== Migraci├│n OCI Storage [{action}] ===")
    print(f"BD: {host}/{db}")
    print(f"Tabla: {TABLE}")
    print(f"Columna: {COLUMN} ({COLUMN_TYPE}, NULL)")
    print()


def migrate_up():
    _print_header("up", "ADD COLUMN")

    print("[1/3] Verificando si la columna ya existe...")
    if column_exists(TABLE, COLUMN):
        print(f"       La columna '{COLUMN}' ya existe. Nada que hacer.")
        return

    print(f"[2/3] Ejecutando ALTER TABLE...")
    sql = f"ALTER TABLE {TABLE} ADD COLUMN {COLUMN} {COLUMN_TYPE} NULL"
    print(f"       SQL: {sql}")

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"[3/3] Verificando resultado...")
    if column_exists(TABLE, COLUMN):
        print(f"       OK - Columna '{COLUMN}' creada correctamente.")
    else:
        print(f"       ERROR - La columna no aparece despu├®s del ALTER.")
        sys.exit(1)


def migrate_down():
    _print_header("down", "DROP COLUMN")

    print("[1/3] Verificando si la columna existe...")
    if not column_exists(TABLE, COLUMN):
        print(f"       La columna '{COLUMN}' no existe. Nada que hacer.")
        return

    print(f"[2/3] Ejecutando ALTER TABLE DROP COLUMN...")
    sql = f"ALTER TABLE {TABLE} DROP COLUMN {COLUMN}"
    print(f"       SQL: {sql}")

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"[3/3] Verificando resultado...")
    if not column_exists(TABLE, COLUMN):
        print(f"       OK - Columna '{COLUMN}' eliminada.")
    else:
        print(f"       ERROR - La columna sigue presente.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migraci├│n para agregar columna OCI storage URL a tabla rats."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--rollback",
        action="store_true",
        help="Revierte la migraci├│n (DROP COLUMN).",
    )
    args = parser.parse_args()

    try:
        if args.rollback:
            migrate_down()
        else:
            migrate_up()
        print("=== Completado ===")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
