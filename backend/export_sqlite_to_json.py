"""
Exporta todos los datos de SQLite a JSON.
Usar antes de migrar a PostgreSQL/Neon para tener backup.
"""

import json
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import models to register them with Base.metadata
from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido  # noqa: F401
from app.database.database import Base

DB_PATH = Path(__file__).parent / "database.db"
EXPORT_FILE = Path(__file__).parent / "backup_data.json"


def export_to_json():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    db = Session()

    tables = [
        "users",
        "rubros",
        "companies",
        "rats_sugeridos",
        "user_companies",
        "rats",
        "audit_logs",
        "eipds",
        "security_breaches",
        "consentimientos",
    ]

    data = {}

    for table in tables:
        result = db.execute(text(f"SELECT * FROM {table}"))
        columns = result.keys()
        data[table] = [
            dict(zip(columns, row))
            for row in result.fetchall()
        ]
        print(f"  {table}: {len(data[table])} registros exportados")

    db.close()

    # Serialize datetime objects
    def serialize(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "value"):  # Enum
            return obj.value
        return obj

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, default=serialize, ensure_ascii=False, indent=2)

    print(f"\nBackup guardado en: {EXPORT_FILE}")
    return data


if __name__ == "__main__":
    print("Exportando datos de SQLite...")
    export_to_json()
    print("Listo.")