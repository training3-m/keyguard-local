"""Loads the Supabase settings the app needs, and refuses to start without them.

Where the values come from (first one found wins):
1. `.streamlit/secrets.toml` locally, or the Secrets box on Streamlit Community Cloud
2. `.env` (used by scripts and tests)

Only the public anon / publishable key is allowed. A secret or service-role key is
refused, because it would bypass every security rule in the database (NFR-SEC-01).
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv


class SettingsError(Exception):
    """The settings are missing or unsafe. The message is safe to show to a user."""


@dataclass(frozen=True)
class Settings:
    """The two values every Supabase call needs."""

    supabase_url: str
    supabase_anon_key: str


def _read_secret(name: str) -> str | None:
    """Reads one value from st.secrets, or None if there is no secrets file or no such key."""
    try:
        value = st.secrets.get(name)
    except Exception:  # no secrets.toml at all: fall back to .env
        return None
    return str(value).strip() if value else None


def _is_secret_key(key: str) -> bool:
    """True for keys that must never be used in the app (they skip all security rules)."""
    if key.startswith("sb_secret_"):
        return True
    # Older keys are JWTs: the middle part says which role the key has.
    parts = key.split(".")
    if len(parts) == 3:
        try:
            padded = parts[1] + "=" * (-len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(padded))
        except (ValueError, json.JSONDecodeError):
            return False
        return payload.get("role") == "service_role"
    return False


def load_settings() -> Settings:
    """Returns the settings, or raises SettingsError with a message that says what to fix."""
    load_dotenv()  # reads .env if it exists; never overrides real environment variables

    url = _read_secret("SUPABASE_URL") or os.getenv("SUPABASE_URL", "").strip()
    key = _read_secret("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY", "").strip()

    missing = [name for name, value in (("SUPABASE_URL", url), ("SUPABASE_ANON_KEY", key))
               if not value or value.upper().startswith("PASTE")]
    if missing:
        raise SettingsError(
            f"Missing {' and '.join(missing)}. Copy .streamlit/secrets.toml.example to "
            ".streamlit/secrets.toml and fill in your Supabase project URL and anon key."
        )
    if not url.startswith("https://"):
        raise SettingsError("SUPABASE_URL must start with https:// (for example https://abcd.supabase.co).")
    if _is_secret_key(key):
        raise SettingsError(
            "SUPABASE_ANON_KEY is a secret / service-role key. Use the anon or publishable key "
            "instead (Supabase > Project Settings > API Keys), and keep the secret key out of every file."
        )
    return Settings(supabase_url=url.rstrip("/"), supabase_anon_key=key)


def require_settings() -> Settings:
    """For pages: shows a clear message and stops the page if the settings are missing."""
    try:
        return load_settings()
    except SettingsError as error:
        st.error(str(error), title="The store isn't set up yet", icon=":material/settings:")
        st.stop()
