"""Tests for the settings loader (utils/config.py): missing values and unsafe keys are refused."""

import base64
import json

import pytest

from utils import config


def _jwt_with_role(role: str) -> str:
    """A fake (unsigned) JWT-shaped key whose payload says which role it is for."""
    def part(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")
    return f"{part({'alg': 'HS256'})}.{part({'role': role})}.signature"


@pytest.fixture
def no_secrets_file(monkeypatch):
    """Make the loader ignore any real secrets.toml / .env on this computer."""
    monkeypatch.setattr(config, "_read_secret", lambda name: None)
    monkeypatch.setattr(config, "load_dotenv", lambda: None)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)


def test_missing_settings_are_named(no_secrets_file):
    with pytest.raises(config.SettingsError, match="SUPABASE_URL and SUPABASE_ANON_KEY"):
        config.load_settings()


def test_placeholder_key_counts_as_missing(no_secrets_file, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "PASTE-YOUR-ANON-KEY-HERE")
    with pytest.raises(config.SettingsError, match="SUPABASE_ANON_KEY"):
        config.load_settings()


def test_publishable_key_is_accepted(no_secrets_file, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co/")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "sb_publishable_example")
    settings = config.load_settings()
    assert settings.supabase_url == "https://demo.supabase.co"


def test_anon_jwt_is_accepted(no_secrets_file, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", _jwt_with_role("anon"))
    assert config.load_settings().supabase_anon_key.count(".") == 2


@pytest.mark.parametrize("unsafe_key", ["sb_secret_example", _jwt_with_role("service_role")])
def test_secret_keys_are_refused(no_secrets_file, monkeypatch, unsafe_key):
    monkeypatch.setenv("SUPABASE_URL", "https://demo.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", unsafe_key)
    with pytest.raises(config.SettingsError, match="secret"):
        config.load_settings()


def test_url_must_be_https(no_secrets_file, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://demo.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "sb_publishable_example")
    with pytest.raises(config.SettingsError, match="https"):
        config.load_settings()
