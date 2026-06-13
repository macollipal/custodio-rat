"""
Cleanup de emergencia por BD directa (psycopg2).
Elimina todos los registros que coincidan con el prefijo dado.

Uso:
    python cleanup_emergencia.py TEST_FLUIDO_DEMO_20260608_143022

Este script es el fallback cuando la limpieza por API falla.
Requiere DATABASE_URL en paso/.env
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

env_file = Path(__file__).parent.parent / "paso" / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

import psycopg2

TABLES_COLUMNS = [
    ("companies", "nombre"),
    ("users", "username"),
    ("rats", "nombre_proceso"),
    ("security_breaches", "descripcion"),
    ("solicitudes_derecho", "nombre_titular"),
    ("tkt_solicitud_derecho", "titular_nombre"),
    ("audit_logs", "usuario"),
]


def delete_by_prefix(conn, prefix):
    """Elimina registros cuyo campo contenga el prefijo."""
    total = 0
    for table, column in TABLES_COLUMNS:
        try:
            cur = conn.cursor()
            query = f'DELETE FROM "{table}" WHERE "{column}" LIKE %s'
            cur.execute(query, (f"%{prefix}%",))
            deleted = cur.rowcount
            if deleted > 0:
                print(f"  [OK] {table}: {deleted} filas eliminadas")
                total += deleted
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"  [WARN] {table}: {e}")
            conn.rollback()
    return total


def run(prefix):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL no encontrada en paso/.env")
        print("Alternativa: setearla directamente:")
        print("  $env:DATABASE_URL = 'postgresql://...'; python cleanup_emergencia.py <prefix>")
        return False

    print(f"Conectando a BD...")
    print(f"Prefijo a buscar: {prefix}")
    print("-" * 60)

    try:
        conn = psycopg2.connect(db_url)
        print("Conexion OK")
    except Exception as e:
        print(f"ERROR de conexion: {e}")
        return False

    print("Eliminando registros...")
    total = delete_by_prefix(conn, prefix)
    print("-" * 60)
    print(f"Total eliminados: {total} filas")

    conn.close()
    print("Cleanup completado")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python cleanup_emergencia.py <PREFIX>")
        print("Ejemplo: python cleanup_emergencia.py TEST_FLUIDO_DEMO_20260608_143022")
        sys.exit(1)

    prefix = sys.argv[1]
    success = run(prefix)
    sys.exit(0 if success else 1)
