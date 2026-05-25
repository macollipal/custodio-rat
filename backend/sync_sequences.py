"""
Sincroniza todas las secuencias de PostgreSQL (Neon) con el valor máximo de cada tabla.
Uso: python sync_sequences.py

Requiere DATABASE_URL configurada en .env o variable de entorno.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import sqlalchemy as sa
from app.core.config import settings


def sync_all_sequences():
    url = settings.DATABASE_URL
    is_postgres = url.startswith("postgresql")
    if not is_postgres:
        print("ERROR: Este script solo funciona con PostgreSQL (Neon).")
        print(f"DATABASE_URL parece ser: {url[:50]}...")
        sys.exit(1)

    engine = sa.create_engine(url, echo=False, pool_pre_ping=True)

    tables_with_seqs = [
        ("users", "id"),
        ("rubros", "id"),
        ("companies", "id"),
        ("rats_sugeridos", "id"),
        ("user_companies", "id"),
        ("rats", "id"),
        ("audit_logs", "id"),
        ("eipds", "id"),
        ("security_breaches", "id"),
        ("consentimientos", "id"),
    ]

    print(f"Conectando a: {url.split('@')[1] if '@' in url else url[:50]}...")
    with engine.connect() as conn:
        for table, col in tables_with_seqs:
            result = conn.execute(sa.text(f"SELECT MAX({col}) FROM {table}"))
            max_val = result.scalar()
            if max_val is not None and max_val > 0:
                conn.execute(sa.text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), {max_val}, true)"
                ))
                print(f"  {table}.{col}: setval({max_val}) ✓")
            else:
                conn.execute(sa.text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), 1, false)"
                ))
                print(f"  {table}.{col}: setval(1, false) ✓ (tabla vacía)")

        conn.commit()

    print("\nTodas las secuencias sincronizadas.")


if __name__ == "__main__":
    sync_all_sequences()
