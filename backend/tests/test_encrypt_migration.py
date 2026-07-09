"""
Tests para scripts/migration/encrypt_existing_bytea.py (C1-F5).
Valida: heurÃ­stica de detecciÃ³n, idempotencia, dry-run, manejo de errores.
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import patch
from pathlib import Path

os.environ["ENV"] = "test"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def make_rat(company_id: int, nombre_proceso: str, archivo_datos=None, **kwargs):
    """Crea un RAT con todos los campos obligatorios."""
    from app.models.rat import RAT, EstadoRAT
    return RAT(
        company_id=company_id,
        nombre_proceso=nombre_proceso,
        categoria_datos="Nombre, email",
        finalidad="GestiÃ³n comercial",
        base_legal="Consentimiento",
        fuente_datos="Titular web",
        plazo_retencion="5 aÃ±os",
        estado=EstadoRAT.BORRADOR,
        archivo_base_legal_datos=archivo_datos,
        **kwargs
    )


class TestFernetHeuristic:
    """Tests de la heurÃ­stica is_already_encrypted()."""

    def test_plain_data_not_detected_as_encrypted(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        plain = os.urandom(256)
        assert is_already_encrypted(plain) is False

    def test_fernet_encrypted_data_detected(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        f = Fernet(key)
        plain = b"test data"
        encrypted = f.encrypt(plain)
        assert is_already_encrypted(encrypted) is True

    def test_empty_data_returns_false(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        assert is_already_encrypted(b"") is False
        assert is_already_encrypted(None) is False

    def test_short_data_less_than_prefix(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        short = b"abc"
        assert is_already_encrypted(short) is False

    def test_pdf_bytes_not_detected_as_encrypted(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        pdf_header = b"%PDF-1.4 mock content here" + b"x" * 200
        assert is_already_encrypted(pdf_header) is False

    def test_double_encryption_detected(self):
        from scripts.migration.encrypt_existing_bytea import is_already_encrypted
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        f = Fernet(key)
        plain = b"test"
        double_enc = f.encrypt(f.encrypt(plain))
        assert is_already_encrypted(double_enc) is True


class TestPrerequisites:
    """Tests de _check_prerequisites()."""

    def test_aborts_without_encryption_key(self):
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:", "ENCRYPTION_KEY": ""}, clear=False):
            with patch("sys.exit") as mock_exit:
                from scripts.migration.encrypt_existing_bytea import _check_prerequisites
                mock_exit.side_effect = SystemExit
                with pytest.raises(SystemExit):
                    _check_prerequisites()
                mock_exit.assert_called_once()

    def test_aborts_with_invalid_key(self):
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:", "ENCRYPTION_KEY": "invalid-key"}, clear=False):
            with patch("sys.exit") as mock_exit:
                from scripts.migration.encrypt_existing_bytea import _check_prerequisites
                mock_exit.side_effect = SystemExit
                with pytest.raises(SystemExit):
                    _check_prerequisites()
                mock_exit.assert_called_once()

    def test_accepts_valid_fernet_key(self):
        from cryptography.fernet import Fernet
        valid_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:", "ENCRYPTION_KEY": valid_key}, clear=False):
            from scripts.migration.encrypt_existing_bytea import _check_prerequisites
            db_url, fernet = _check_prerequisites()
            assert db_url == "sqlite:///:memory:"
            assert fernet is not None


class TestAnalyzeTable:
    """Tests de _analyze_table() con BD en memoria."""

    def test_counts_plain_vs_encrypted(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        f = Fernet(key)

        plain_data = b"%PDF-1.4 plain document"
        enc_data = f.encrypt(b"encrypted document")

        db.add(make_rat(1, "Test1", plain_data, archivo_base_legal_nombre="a.pdf", archivo_base_legal_tipo="application/pdf"))
        db.add(make_rat(1, "Test2", enc_data, archivo_base_legal_nombre="b.pdf", archivo_base_legal_tipo="application/pdf"))
        db.add(make_rat(1, "Test3", None, archivo_base_legal_nombre="c.pdf", archivo_base_legal_tipo="application/pdf"))
        db.commit()

        from scripts.migration.encrypt_existing_bytea import _analyze_table
        result = _analyze_table(db, "rats", "archivo_base_legal_datos", RAT, "id")

        assert result["total"] == 3
        assert result["no_nulos"] == 2
        assert result["en_plano"] == 1
        assert result["ya_cifrados"] == 1
        db.close()


class TestMigrateTable:
    """Tests de _migrate_table()."""

    def test_migrate_plain_data_is_encrypted(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from scripts.migration.encrypt_existing_bytea import _migrate_table, is_already_encrypted
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        plain_data = b"%PDF-1.4 test document"
        rat = make_rat(1, "Test", plain_data, archivo_base_legal_nombre="test.pdf", archivo_base_legal_tipo="application/pdf")
        db.add(rat)
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt") as mock_encrypt:
            mock_encrypt.side_effect = lambda d: fernet.encrypt(d)
            stats = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=False)

        assert stats["migrados"] == 1
        assert stats["ya_cifrados"] == 0
        assert stats["errores"] == 0

        db.refresh(rat)
        assert is_already_encrypted(rat.archivo_base_legal_datos) is True
        db.close()

    def test_dry_run_does_not_modify_db(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from scripts.migration.encrypt_existing_bytea import _migrate_table
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        plain_data = b"%PDF-1.4 test document"
        rat = make_rat(1, "Test", plain_data, archivo_base_legal_nombre="test.pdf", archivo_base_legal_tipo="application/pdf")
        db.add(rat)
        db.commit()

        stats = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=True)

        assert stats["migrados"] == 0
        db.refresh(rat)
        assert rat.archivo_base_legal_datos == plain_data
        db.close()

    def test_idempotent_second_run(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from scripts.migration.encrypt_existing_bytea import _migrate_table
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        plain_data = b"%PDF-1.4 test document"
        rat = make_rat(1, "Test", plain_data, archivo_base_legal_nombre="test.pdf", archivo_base_legal_tipo="application/pdf")
        db.add(rat)
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt") as mock_encrypt:
            mock_encrypt.side_effect = lambda d: fernet.encrypt(d)

            stats1 = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=False)
            assert stats1["migrados"] == 1

            db.refresh(rat)
            encrypted_once = rat.archivo_base_legal_datos

            stats2 = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=False)
            assert stats2["ya_cifrados"] == 1
            assert stats2["migrados"] == 0

            db.refresh(rat)
            assert rat.archivo_base_legal_datos == encrypted_once
        db.close()

    def test_mixed_plain_and_encrypted(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from scripts.migration.encrypt_existing_bytea import _migrate_table
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        plain_data = b"%PDF-1.4 plain"
        enc_data = fernet.encrypt(b"already encrypted")

        db.add(make_rat(1, "T1", plain_data, archivo_base_legal_nombre="a.pdf", archivo_base_legal_tipo="application/pdf"))
        db.add(make_rat(1, "T2", enc_data, archivo_base_legal_nombre="b.pdf", archivo_base_legal_tipo="application/pdf"))
        db.add(make_rat(1, "T3", None, archivo_base_legal_nombre="c.pdf", archivo_base_legal_tipo="application/pdf"))
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt") as mock_encrypt:
            mock_encrypt.side_effect = lambda d: fernet.encrypt(d)
            stats = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=False)

        assert stats["migrados"] == 1, f"expected migrados=1, got {stats['migrados']}"
        assert stats["ya_cifrados"] == 1, f"expected ya_cifrados=1, got {stats['ya_cifrados']}"
        assert stats["vacias"] == 0, f"expected vacias=0, got {stats['vacias']}"
        assert stats["errores"] == 0
        db.close()

    def test_error_continues_to_next_row(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from scripts.migration.encrypt_existing_bytea import _migrate_table
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        plain_data = b"%PDF-1.4 test"
        db.add(make_rat(1, "T1", plain_data, archivo_base_legal_nombre="a.pdf", archivo_base_legal_tipo="application/pdf"))
        db.add(make_rat(1, "T2", plain_data, archivo_base_legal_nombre="b.pdf", archivo_base_legal_tipo="application/pdf"))
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt", side_effect=[Exception("mock error"), Exception("mock error")]):
            stats = _migrate_table(db, "rats", "archivo_base_legal_datos", RAT, "id", fernet, batch_size=10, dry_run=False)

        assert stats["errores"] == 2
        assert stats["migrados"] == 0
        db.close()


class TestEncargadoContratoMigration:
    """Tests especÃ­ficos para encargados_contrato.archivo_pdf_datos."""

    def test_migrate_encargado_contrato_pdf(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.encargado_contrato import EncargadoContrato
        from scripts.migration.encrypt_existing_bytea import _migrate_table, is_already_encrypted
        from cryptography.fernet import Fernet
        from datetime import datetime, timezone

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        pdf_data = b"%PDF-1.4 contract document"
        contrato = EncargadoContrato(
            company_id=1, rat_id=None, nombre_encargado="Test Encargado", objeto="Processamento",
            duracion_inicio=datetime.now(timezone.utc), duracion_fin=None, finalidad="Test",
            tipo_datos="Personal", categorias_titulares="Clients",
            derechos_obligaciones="Standard",
            archivo_pdf_datos=pdf_data,
            archivo_pdf_nombre="contract.pdf",
            archivo_pdf_tipo="application/pdf",
        )
        db.add(contrato)
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt") as mock_encrypt:
            mock_encrypt.side_effect = lambda d: fernet.encrypt(d)
            stats = _migrate_table(db, "encargados_contrato", "archivo_pdf_datos", EncargadoContrato, "id", fernet, batch_size=10, dry_run=False)

        assert stats["migrados"] == 1
        db.refresh(contrato)
        assert is_already_encrypted(contrato.archivo_pdf_datos) is True
        db.close()


class TestTktAdjuntoMigration:
    """Tests especÃ­ficos para tkt_adjuntos.data."""

    def test_migrate_tkt_adjunto(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.tkt_adjunto import TktAdjunto
        from scripts.migration.encrypt_existing_bytea import _migrate_table, is_already_encrypted
        from cryptography.fernet import Fernet

        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        db = Session()

        key = Fernet.generate_key()
        fernet = Fernet(key)

        file_data = b"file content here"
        adjunto = TktAdjunto(
            ticket_id=1,
            filename="test.txt",
            content_type="text/plain",
            data=file_data,
        )
        db.add(adjunto)
        db.commit()

        with patch("scripts.migration.encrypt_existing_bytea.encrypt") as mock_encrypt:
            mock_encrypt.side_effect = lambda d: fernet.encrypt(d)
            stats = _migrate_table(db, "tkt_adjuntos", "data", TktAdjunto, "id", fernet, batch_size=10, dry_run=False)

            assert stats["migrados"] == 1
        db.refresh(adjunto)
        assert is_already_encrypted(adjunto.data) is True
        db.close()


class TestEndToEnd:
    """Test end-to-end del script completo via main()."""

    def test_dry_run_analyzes_without_modifying(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from app.database.database import Base
        from app.models.rat import RAT
        from cryptography.fernet import Fernet

        tmpfile = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_path = tmpfile.name
        tmpfile.close()
        db_url = f"sqlite:///{db_path}"

        try:
            engine = create_engine(db_url, echo=False)
            Base.metadata.create_all(bind=engine)
            Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
            db = Session()

            key = Fernet.generate_key()
            fernet = Fernet(key)

            plain_data = b"%PDF-1.4 test"
            enc_data = fernet.encrypt(b"already cipher")

            db.add(make_rat(1, "T1", plain_data, archivo_base_legal_nombre="a.pdf", archivo_base_legal_tipo="application/pdf"))
            db.add(make_rat(1, "T2", enc_data, archivo_base_legal_nombre="b.pdf", archivo_base_legal_tipo="application/pdf"))
            db.commit()
            db.close()

            with patch.dict(os.environ, {"DATABASE_URL": db_url, "ENCRYPTION_KEY": key.decode()}):
                with patch("sys.argv", ["encrypt_existing_bytea.py", "--dry-run", "--force", "--tables=rats"]):
                    import io
                    from scripts.migration.encrypt_existing_bytea import main
                    with patch("sys.stdin", io.StringIO("yes\n")):
                        main()

            engine2 = create_engine(db_url, echo=False)
            Session2 = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine2))
            db2 = Session2()
            rat1 = db2.query(RAT).filter(RAT.nombre_proceso == "T1").first()
            rat2 = db2.query(RAT).filter(RAT.nombre_proceso == "T2").first()
            assert rat1.archivo_base_legal_datos == plain_data
            assert rat2.archivo_base_legal_datos == enc_data
            db2.close()
            engine2.dispose()
            engine.dispose()
        finally:
            import time
            for _ in range(10):
                try:
                    Path(db_path).unlink(missing_ok=True)
                    break
                except PermissionError:
                    time.sleep(0.1)
