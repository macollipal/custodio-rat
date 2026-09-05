"""
Tests para el parser SMTP_URL (smtp_config.py).
"""

import os


class TestSmtpConfig:
    def _clear_env(self):
        for k in ["SMTP_URL", "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME",
                  "SMTP_PASSWORD", "SMTP_FROM_EMAIL", "SMTP_FROM_NAME", "SMTP_USE_TLS"]:
            os.environ.pop(k, None)

    def _set_env(self, **kwargs):
        for k, v in kwargs.items():
            os.environ[k] = v

    def test_parse_sendgrid_full(self):
        self._clear_env()
        os.environ["SMTP_URL"] = (
            "smtplib://apikey:SG.test_key_abc123@smtp.sendgrid.net:587/"
            "?use_tls=true&from_email=test@yopmail.com&from_name=Custodio%20RAT%20Manager"
        )
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert cfg is not None
        assert cfg.host == "smtp.sendgrid.net"
        assert cfg.port == 587
        assert cfg.username == "apikey"
        assert cfg.password == "SG.test_key_abc123"
        assert cfg.use_tls is True
        assert cfg.from_email == "test@yopmail.com"
        assert cfg.from_name == "Custodio RAT Manager"

    def test_parse_with_plus_encoding(self):
        self._clear_env()
        os.environ["SMTP_URL"] = (
            "smtplib://user:pass@smtp.example.com:587/"
            "?use_tls=false&from_email=from@test.com&from_name=Name+With+Plus"
        )
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert cfg.from_name == "Name With Plus"

    def test_parse_default_values(self):
        self._clear_env()
        os.environ["SMTP_URL"] = "smtplib://apikey:SG.xxx@smtp.example.com:587/?from_email=a@b.com"
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert cfg.port == 587
        assert cfg.use_tls is True
        assert cfg.from_name == "Custodio RAT"

    def test_dry_run_no_config(self):
        self._clear_env()
        from app.core.smtp_config import get_smtp_config
        assert get_smtp_config() is None

    def test_legacy_fallback(self):
        self._clear_env()
        os.environ["SMTP_HOST"] = "smtp.sendgrid.net"
        os.environ["SMTP_PORT"] = "587"
        os.environ["SMTP_USERNAME"] = "apikey"
        os.environ["SMTP_PASSWORD"] = "SG.legacy_key"
        os.environ["SMTP_FROM_EMAIL"] = "legacy@yopmail.com"
        os.environ["SMTP_FROM_NAME"] = "Legacy Sender"
        os.environ["SMTP_USE_TLS"] = "true"
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert cfg is not None
        assert cfg.host == "smtp.sendgrid.net"
        assert cfg.port == 587
        assert cfg.username == "apikey"
        assert cfg.password == "SG.legacy_key"
        assert cfg.from_email == "legacy@yopmail.com"
        assert cfg.from_name == "Legacy Sender"
        assert cfg.use_tls is True

    def test_smtp_url_takes_priority_over_legacy(self):
        self._clear_env()
        os.environ["SMTP_URL"] = "smtplib://apikey:SG.new@smtp.new.com:587/?from_email=new@test.com"
        os.environ["SMTP_HOST"] = "smtp.old.com"
        os.environ["SMTP_PASSWORD"] = "SG.old"
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert cfg.host == "smtp.new.com"
        assert cfg.password == "SG.new"

    def test_bool_true_when_host_set(self):
        self._clear_env()
        os.environ["SMTP_URL"] = "smtplib://user:pass@smtp.test.com:587/?from_email=a@b.com"
        from app.core.smtp_config import get_smtp_config
        cfg = get_smtp_config()
        assert bool(cfg) is True

    def test_bool_false_when_empty(self):
        self._clear_env()
        from app.core.smtp_config import get_smtp_config
        assert bool(get_smtp_config()) is False
