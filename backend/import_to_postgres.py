"""
Importa datos desde backup_data.json a PostgreSQL/Neon.
Orden de importación: users → rubro → companies → ... (respeta FK).
"""

import json
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import company, rat, user, audit_log, user_company, breach, eipd, consentimiento, rubro, rats_sugerido  # noqa: F401
from app.models.company import Company
from app.models.user import User
from app.models.rat import RAT, EstadoRAT, EstadoEIPD
from app.models.rubro import Rubro
from app.models.rats_sugerido import RATSugerido
from app.models.user_company import UserCompany, RolEmpresa
from app.models.audit_log import AuditLog
from app.models.eipd import EIPD, ResultadoEIPD
from app.models.breach import SecurityBreach
from app.models.consentimiento import Consentimiento, CanalConsentimiento
from app.database.database import Base

BACKUP_FILE = Path(__file__).parent / "backup_data.json"


def get_neon_engine():
    url = settings.resolved_database_url
    return create_engine(url, echo=False, pool_pre_ping=True)


def import_data():
    if not BACKUP_FILE.exists():
        print(f"ERROR: {BACKUP_FILE} no encontrado. Ejecuta primero export_sqlite_to_json.py")
        sys.exit(1)

    with open(BACKUP_FILE, encoding="utf-8") as f:
        data = json.load(f)

    engine = get_neon_engine()
    Session = sessionmaker(bind=engine)
    db = Session()

    def clean_val(val):
        """Convierte valores None string y dates."""
        if val is None:
            return None
        if isinstance(val, str) and val.lower() == "none":
            return None
        return val

    print("Importando datos...")

    # 1. Users
    for row in data.get("users", []):
        db.add(User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            full_name=row["full_name"],
            hashed_password=row["hashed_password"],
            is_active=bool(row.get("is_active", True)),
            is_admin=bool(row.get("is_admin", False)),
            rol_global=row["rol_global"],
        ))
    print(f"  users: {len(data.get('users', []))} registros")
    db.commit()

    # 2. Rubros
    for row in data.get("rubros", []):
        db.add(Rubro(
            id=row["id"],
            nombre=row["nombre"],
            orden=row.get("orden", 0),
        ))
    print(f"  rubros: {len(data.get('rubros', []))} registros")
    db.commit()

    # 3. Companies
    for row in data.get("companies", []):
        db.add(Company(
            id=row["id"],
            nombre=row["nombre"],
            rut=row["rut"],
            rubro=row.get("rubro"),
            rubro_id=clean_val(row.get("rubro_id")),
            direccion=clean_val(row.get("direccion")),
            contacto_dpo=clean_val(row.get("contacto_dpo")),
            email_dpo=clean_val(row.get("email_dpo")),
            descripcion=clean_val(row.get("descripcion")),
            canal_ejercicio_derechos=clean_val(row.get("canal_ejercicio_derechos")),
        ))
    print(f"  companies: {len(data.get('companies', []))} registros")
    db.commit()

    # 4. Rats sugeridos
    for row in data.get("rats_sugeridos", []):
        db.add(RATSugerido(
            id=row["id"],
            rubro_id=row["rubro_id"],
            nombre_proceso=row["nombre_proceso"],
            categoria_datos=row["categoria_datos"],
            categoria_titulares=clean_val(row.get("categoria_titulares")),
            finalidad=clean_val(row.get("finalidad")),
            base_legal=clean_val(row.get("base_legal")),
            plazo_retencion=clean_val(row.get("plazo_retencion")),
            datos_sensibles=bool(row.get("datos_sensibles", False)),
            evaluacion_impacto=bool(row.get("evaluacion_impacto", False)),
            decisiones_automatizadas=bool(row.get("decisiones_automatizadas", False)),
        ))
    print(f"  rats_sugeridos: {len(data.get('rats_sugeridos', []))} registros")
    db.commit()

    # 5. UserCompanies
    for row in data.get("user_companies", []):
        db.add(UserCompany(
            id=row["id"],
            user_id=row["user_id"],
            company_id=row["company_id"],
            rol=row["rol"],
        ))
    print(f"  user_companies: {len(data.get('user_companies', []))} registros")
    db.commit()

    # 6. Rats
    for row in data.get("rats", []):
        from datetime import datetime
        estado = row.get("estado", "borrador")
        if isinstance(estado, str):
            try:
                estado = EstadoRAT(estado)
            except ValueError:
                estado = EstadoRAT.BORRADOR
        estado_eipd = row.get("estado_eipd", "no_requerida")
        if isinstance(estado_eipd, str):
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
            id=row["id"],
            company_id=row["company_id"],
            nombre_proceso=row["nombre_proceso"],
            categoria_datos=row.get("categoria_datos", ""),
            finalidad=row.get("finalidad", ""),
            base_legal=row.get("base_legal", ""),
            fuente_datos=row.get("fuente_datos", ""),
            transferencia_datos=clean_val(row.get("transferencia_datos")),
            plazo_retencion=row.get("plazo_retencion", ""),
            categoria_titulares=clean_val(row.get("categoria_titulares")),
            medidas_seguridad=clean_val(row.get("medidas_seguridad")),
            destinatarios=clean_val(row.get("destinatarios")),
            transferencia_internacional=bool(row.get("transferencia_internacional", False)),
            pais_destino=clean_val(row.get("pais_destino")),
            garantias_transferencia_int=clean_val(row.get("garantias_transferencia_int")),
            datos_sensibles=bool(row.get("datos_sensibles", False)),
            tipo_dato_sensible=clean_val(row.get("tipo_dato_sensible")),
            evaluacion_impacto=bool(row.get("evaluacion_impacto", False)),
            estado_eipd=estado_eipd,
            fecha_eipd=fecha_eipd,
            decisiones_automatizadas=bool(row.get("decisiones_automatizadas", False)),
            nombre_encargado=clean_val(row.get("nombre_encargado")),
            tiene_contrato_encargado=bool(row.get("tiene_contrato_encargado", False)),
            test_interes_legitimo=clean_val(row.get("test_interes_legitimo")),
            estado=estado,
            observaciones_auditoria=clean_val(row.get("observaciones_auditoria")),
            created_by=clean_val(row.get("created_by")),
            updated_by=clean_val(row.get("updated_by")),
        ))
    print(f"  rats: {len(data.get('rats', []))} registros")
    db.commit()

    # 7. Audit logs
    for row in data.get("audit_logs", []):
        from datetime import datetime
        ts = row.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        db.add(AuditLog(
            id=row["id"],
            entidad=row["entidad"],
            entidad_id=row["entidad_id"],
            accion=row["accion"],
            usuario=clean_val(row.get("usuario")),
            detalle=clean_val(row.get("detalle")),
            ip_origen=clean_val(row.get("ip_origen")),
            timestamp=ts,
        ))
    print(f"  audit_logs: {len(data.get('audit_logs', []))} registros")
    db.commit()

    # 8. EIPDs
    for row in data.get("eipds", []):
        from datetime import date, datetime
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
            id=row["id"],
            rat_id=row["rat_id"],
            metodologia=clean_val(row.get("metodologia")),
            objetivos=clean_val(row.get("objetivos")),
            necesidad_proporcionalidad=clean_val(row.get("necesidad_proporcionalidad")),
            riesgos_identificados=clean_val(row.get("riesgos_identificados")),
            medidas_propuestas=clean_val(row.get("medidas_propuestas")),
            parecer_dpo=clean_val(row.get("parecer_dpo")),
            fecha_elaboracion=fecha_elab,
            fecha_aprobacion=fecha_aprob,
            resultado=resultado,
            created_by=clean_val(row.get("created_by")),
        ))
    print(f"  eipds: {len(data.get('eipds', []))} registros")
    db.commit()

    # 9. SecurityBreaches
    for row in data.get("security_breaches", []):
        from datetime import datetime
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
            id=row["id"],
            company_id=row["company_id"],
            descripcion=row["descripcion"],
            fecha_deteccion=fecha_det,
            rats_afectados=clean_val(row.get("rats_afectados")),
            datos_comprometidos=clean_val(row.get("datos_comprometidos")),
            medidas_adoptadas=clean_val(row.get("medidas_adoptadas")),
            notificado_apdc=bool(row.get("notificado_apdc", False)),
            fecha_notificacion_apdc=fecha_not_apdc,
            notificado_titulares=bool(row.get("notificado_titulares", False)),
            fecha_notificacion_titulares=fecha_not_tit,
            creado_por=clean_val(row.get("creado_por")),
        ))
    print(f"  security_breaches: {len(data.get('security_breaches', []))} registros")
    db.commit()

    # 10. Consentimientos
    for row in data.get("consentimientos", []):
        from datetime import datetime
        fecha_obt = row.get("fecha_obtencion")
        if isinstance(fecha_obt, str):
            fecha_obt = datetime.fromisoformat(fecha_obt.replace("Z", "+00:00"))
        fecha_rev = row.get("fecha_revocado")
        if isinstance(fecha_rev, str):
            fecha_rev = datetime.fromisoformat(fecha_rev.replace("Z", "+00:00")) if fecha_rev else None
        canal = row.get("canal", "web")
        try:
            canal = CanalConsentimiento(canal)
        except ValueError:
            canal = CanalConsentimiento.WEB
        db.add(Consentimiento(
            id=row["id"],
            company_id=row["company_id"],
            rat_id=clean_val(row.get("rat_id")),
            nombre_titular=row["nombre_titular"],
            email_titular=clean_val(row.get("email_titular")),
            canal=canal,
            texto_consentimiento=row["texto_consentimiento"],
            fecha_obtencion=fecha_obt,
            fecha_revocado=fecha_rev,
            activo=bool(row.get("activo", True)),
            ip_origen=clean_val(row.get("ip_origen")),
        ))
    print(f"  consentimientos: {len(data.get('consentimientos', []))} registros")
    db.commit()

    db.close()
    print("\nImportación completada.")

    # Reset sequences
    print("Reiniciando sequences...")
    engine = get_neon_engine()
    with engine.connect() as conn:
        tables_with_serial = [
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
        for table, col in tables_with_serial:
            result = conn.execute(text(f"SELECT MAX({col}) FROM {table}"))
            max_val = result.scalar() or 0
            if max_val > 0:
                conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', '{col}'), {max_val}, true)"))
    print("Sequences actualizadas.")


if __name__ == "__main__":
    import_data()
    print("Listo.")