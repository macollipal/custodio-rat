"""
Scripts de utilidad para la migración SQLite → Neon PostgreSQL.
Uso:
  1. python migrate_to_neon.py export    # Exporta datos SQLite → backup_data.json
  2. python migrate_to_neon.py init     # Crea schema en Neon (requiere DATABASE_URL de Neon)
  3. python migrate_to_neon.py import   # Importa datos desde backup_data.json a Neon
  4. python migrate_to_neon.py verify   # Verifica conexión a Neon

Pasos completos:
  python migrate_to_neon.py export
  python migrate_to_neon.py init --check  # Verifica conexión primero
  python migrate_to_neon.py import
"""

import json
import sys
from pathlib import Path

import sqlalchemy as sa

from app.core.config import settings
from app.database.database import Base

BACKUP_FILE = Path(__file__).parent / "backup_data.json"


def cmd_export():
    """Exporta todos los datos de SQLite a JSON."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    DB_PATH = Path(__file__).parent / "database.db"
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    db = Session()

    tables = [
        "users", "rubros", "companies", "rats_sugeridos",
        "user_companies", "rats", "audit_logs",
        "eipds", "security_breaches", "consentimientos",
    ]
    data = {}
    for table in tables:
        rows = db.execute(text(f"SELECT * FROM {table}")).fetchall()
        cols = [desc[0] for desc in db.execute(text(f"PRAGMA table_info({table})")).fetchall()]
        data[table] = [{col: val for col, val in zip(cols, row)} for row in rows]
        print(f"  {table}: {len(rows)} registros")

    db.close()

    def serialize(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if hasattr(obj, "value"):
            return obj.value
        return obj

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, default=serialize, ensure_ascii=False, indent=2)

    print(f"\nBackup guardado en: {BACKUP_FILE}")


def cmd_init():
    """Crea todas las tablas en PostgreSQL/Neon."""
    engine = sa.create_engine(settings.resolved_database_url, echo=False, pool_pre_ping=True)

    from app.models import (
        company, rat, user, audit_log, user_company,
        breach, eipd, consentimiento, rubro, rats_sugerido
    )

    print("Creando tablas en PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    with engine.connect() as conn:
        for table, col in [
            ("users", "id"), ("rubros", "id"), ("companies", "id"),
            ("rats_sugeridos", "id"), ("user_companies", "id"), ("rats", "id"),
            ("audit_logs", "id"), ("eipds", "id"),
            ("security_breaches", "id"), ("consentimientos", "id"),
        ]:
            result = conn.execute(sa.text(f"SELECT MAX({col}) FROM {table}"))
            max_val = result.scalar() or 0
            if max_val > 0:
                conn.execute(sa.text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), {max_val}, true)"
                ))
        print("Sequences reiniciadas.")


def cmd_import():
    """Importa datos desde JSON a PostgreSQL/Neon."""
    from sqlalchemy.orm import sessionmaker
    if not BACKUP_FILE.exists():
        print(f"ERROR: {BACKUP_FILE} no existe. Ejecuta 'export' primero.")
        sys.exit(1)

    with open(BACKUP_FILE, encoding="utf-8") as f:
        data = json.load(f)

    engine = sa.create_engine(settings.resolved_database_url, echo=False, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    db = Session()

    def c(val):
        if val is None:
            return None
        if isinstance(val, str) and val.lower() == "none":
            return None
        return val

    print("Importando...")

    from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido
    from app.models.company import Company
    from app.models.user import User
    from app.models.rat import RAT, EstadoRAT, EstadoEIPD
    from app.models.rubro import Rubro
    from app.models.rats_sugerido import RATSugerido
    from app.models.user_company import UserCompany
    from app.models.audit_log import AuditLog
    from app.models.eipd import EIPD, ResultadoEIPD
    from app.models.breach import SecurityBreach
    from app.models.consentimiento import Consentimiento, CanalConsentimiento
    from datetime import datetime, date

    for row in data.get("users", []):
        db.add(User(id=row["id"], username=row["username"], email=row["email"],
                   full_name=row["full_name"], hashed_password=row["hashed_password"],
                   is_active=bool(row.get("is_active", True)),
                   is_admin=bool(row.get("is_admin", False)),
                   rol_global=row["rol_global"]))
    print(f"  users: {len(data.get('users', []))}")
    db.commit()

    for row in data.get("rubros", []):
        db.add(Rubro(id=row["id"], nombre=row["nombre"], orden=row.get("orden", 0)))
    print(f"  rubros: {len(data.get('rubros', []))}")
    db.commit()

    for row in data.get("companies", []):
        db.add(Company(id=row["id"], nombre=row["nombre"], rut=row["rut"],
                       rubro=c(row.get("rubro")), rubro_id=c(row.get("rubro_id")),
                       direccion=c(row.get("direccion")),
                       contacto_dpo=c(row.get("contacto_dpo")),
                       email_dpo=c(row.get("email_dpo")),
                       descripcion=c(row.get("descripcion")),
                       canal_ejercicio_derechos=c(row.get("canal_ejercicio_derechos"))))
    print(f"  companies: {len(data.get('companies', []))}")
    db.commit()

    for row in data.get("rats_sugeridos", []):
        db.add(RATSugerido(
            id=row["id"], rubro_id=row["rubro_id"], nombre_proceso=row["nombre_proceso"],
            categoria_datos=row["categoria_datos"],
            categoria_titulares=c(row.get("categoria_titulares")),
            finalidad=c(row.get("finalidad")), base_legal=c(row.get("base_legal")),
            plazo_retencion=c(row.get("plazo_retencion")),
            datos_sensibles=bool(row.get("datos_sensibles", False)),
            evaluacion_impacto=bool(row.get("evaluacion_impacto", False)),
            decisiones_automatizadas=bool(row.get("decisiones_automatizadas", False))))
    print(f"  rats_sugeridos: {len(data.get('rats_sugeridos', []))}")
    db.commit()

    for row in data.get("user_companies", []):
        db.add(UserCompany(id=row["id"], user_id=row["user_id"],
                         company_id=row["company_id"], rol=row["rol"]))
    print(f"  user_companies: {len(data.get('user_companies', []))}")
    db.commit()

    for row in data.get("rats", []):
        estado = row.get("estado", "borrador")
        try:
            estado = EstadoRAT(estado)
        except ValueError:
            estado = EstadoRAT.BORRADOR
        estado_eipd = row.get("estado_eipd", "no_requerida")
        try:
            estado_eipd = EstadoEIPD(estado_eipd)
        except ValueError:
            estado_eipd = EstadoEIPD.NO_REQUERIDA
        fecha_eipd = row.get("fecha_eipd")
        if fecha_eipd and isinstance(fecha_eipd, str):
            try:
                fecha_eipd = datetime.fromisoformat(fecha_eipd.replace("Z", "+00:00")).date()
            except ValueError:
                fecha_eipd = None
        db.add(RAT(
            id=row["id"], company_id=row["company_id"],
            nombre_proceso=row["nombre_proceso"],
            categoria_datos=row.get("categoria_datos", ""),
            finalidad=row.get("finalidad", ""), base_legal=row.get("base_legal", ""),
            fuente_datos=row.get("fuente_datos", ""),
            transferencia_datos=c(row.get("transferencia_datos")),
            plazo_retencion=row.get("plazo_retencion", ""),
            categoria_titulares=c(row.get("categoria_titulares")),
            medidas_seguridad=c(row.get("medidas_seguridad")),
            destinatarios=c(row.get("destinatarios")),
            transferencia_internacional=bool(row.get("transferencia_internacional", False)),
            pais_destino=c(row.get("pais_destino")),
            garantias_transferencia_int=c(row.get("garantias_transferencia_int")),
            datos_sensibles=bool(row.get("datos_sensibles", False)),
            tipo_dato_sensible=c(row.get("tipo_dato_sensible")),
            evaluacion_impacto=bool(row.get("evaluacion_impacto", False)),
            estado_eipd=estado_eipd, fecha_eipd=fecha_eipd,
            decisiones_automatizadas=bool(row.get("decisiones_automatizadas", False)),
            nombre_encargado=c(row.get("nombre_encargado")),
            tiene_contrato_encargado=bool(row.get("tiene_contrato_encargado", False)),
            test_interes_legitimo=c(row.get("test_interes_legitimo")),
            estado=estado,
            observaciones_auditoria=c(row.get("observaciones_auditoria")),
            created_by=c(row.get("created_by")), updated_by=c(row.get("updated_by")),
        ))
    print(f"  rats: {len(data.get('rats', []))}")
    db.commit()

    for row in data.get("audit_logs", []):
        ts = row.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        db.add(AuditLog(id=row["id"], entidad=row["entidad"], entidad_id=row["entidad_id"],
                        accion=row["accion"], usuario=c(row.get("usuario")),
                        detalle=c(row.get("detalle")), ip_origen=c(row.get("ip_origen")), timestamp=ts))
    print(f"  audit_logs: {len(data.get('audit_logs', []))}")
    db.commit()

    for row in data.get("eipds", []):
        fecha_elab = row.get("fecha_elaboracion")
        if fecha_elab and isinstance(fecha_elab, str):
            fecha_elab = date.fromisoformat(fecha_elab)
        fecha_aprob = row.get("fecha_aprobacion")
        if fecha_aprob and isinstance(fecha_aprob, str):
            fecha_aprob = date.fromisoformat(fecha_aprob)
        resultado = row.get("resultado", "en_proceso")
        try:
            resultado = ResultadoEIPD(resultado)
        except ValueError:
            resultado = ResultadoEIPD.EN_PROCESO
        db.add(EIPD(
            id=row["id"], rat_id=row["rat_id"],
            metodologia=c(row.get("metodologia")), objetivos=c(row.get("objetivos")),
            necesidad_proporcionalidad=c(row.get("necesidad_proporcionalidad")),
            riesgos_identificados=c(row.get("riesgos_identificados")),
            medidas_propuestas=c(row.get("medidas_propuestas")),
            parecer_dpo=c(row.get("parecer_dpo")),
            fecha_elaboracion=fecha_elab, fecha_aprobacion=fecha_aprob,
            resultado=resultado, created_by=c(row.get("created_by"))))
    print(f"  eipds: {len(data.get('eipds', []))}")
    db.commit()

    for row in data.get("security_breaches", []):
        fecha_det = row.get("fecha_deteccion")
        if isinstance(fecha_det, str):
            fecha_det = datetime.fromisoformat(fecha_det.replace("Z", "+00:00"))
        fecha_not_apdc = row.get("fecha_notificacion_apdc")
        if isinstance(fecha_not_apdc, str):
            fecha_not_apdc = datetime.fromisoformat(fecha_not_apdc.replace("Z", "+00:00"))
        fecha_not_tit = row.get("fecha_notificacion_titulares")
        if isinstance(fecha_not_tit, str):
            fecha_not_tit = datetime.fromisoformat(fecha_not_tit.replace("Z", "+00:00"))
        db.add(SecurityBreach(
            id=row["id"], company_id=row["company_id"], descripcion=row["descripcion"],
            fecha_deteccion=fecha_det, rats_afectados=c(row.get("rats_afectados")),
            datos_comprometidos=c(row.get("datos_comprometidos")),
            medidas_adoptadas=c(row.get("medidas_adoptadas")),
            notificado_apdc=bool(row.get("notificado_apdc", False)),
            fecha_notificacion_apdc=fecha_not_apdc,
            notificado_titulares=bool(row.get("notificado_titulares", False)),
            fecha_notificacion_titulares=fecha_not_tit,
            creado_por=c(row.get("creado_por"))))
    print(f"  security_breaches: {len(data.get('security_breaches', []))}")
    db.commit()

    for row in data.get("consentimientos", []):
        fecha_obt = row.get("fecha_obtencion")
        if isinstance(fecha_obt, str):
            fecha_obt = datetime.fromisoformat(fecha_obt.replace("Z", "+00:00"))
        fecha_rev = row.get("fecha_revocado")
        if isinstance(fecha_rev, str) and fecha_rev:
            fecha_rev = datetime.fromisoformat(fecha_rev.replace("Z", "+00:00"))
        elif fecha_rev:
            fecha_rev = datetime.fromisoformat(fecha_rev.replace("Z", "+00:00"))
        else:
            fecha_rev = None
        canal = row.get("canal", "web")
        try:
            canal = CanalConsentimiento(canal)
        except ValueError:
            canal = CanalConsentimiento.WEB
        db.add(Consentimiento(
            id=row["id"], company_id=row["company_id"], rat_id=c(row.get("rat_id")),
            nombre_titular=row["nombre_titular"], email_titular=c(row.get("email_titular")),
            canal=canal, texto_consentimiento=row["texto_consentimiento"],
            fecha_obtencion=fecha_obt, fecha_revocado=fecha_rev,
            activo=bool(row.get("activo", True)), ip_origen=c(row.get("ip_origen"))))
    print(f"  consentimientos: {len(data.get('consentimientos', []))}")
    db.commit()

    db.close()
    print("\nImportación completada.")


def cmd_verify():
    """Verifica conexión a la base de datos configurada."""
    from app.core.config import settings
    url = settings.resolved_database_url
    print(f"Conectando a: {url.split('@')[1] if '@' in url else url[:50]}...")
    try:
        engine = sa.create_engine(url, echo=False, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        print("Conexión: OK")
        return True
    except Exception as e:
        print(f"Conexión fallida: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "export":
        cmd_export()
    elif cmd == "init":
        cmd_init()
    elif cmd == "import":
        cmd_import()
    elif cmd == "verify":
        ok = cmd_verify()
        sys.exit(0 if ok else 1)
    else:
        print(f"Comando desconocido: {cmd}")
        print(__doc__)
        sys.exit(1)