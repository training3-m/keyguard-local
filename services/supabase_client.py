"""The connection to Supabase, one per browser session.

Why not @st.cache_resource? Cached resources are SHARED by every visitor. A Supabase client holds
the signed-in user's login, so a shared one would let one visitor act as another (NFR-SES-02).
Instead each browser session keeps its own client in st.session_state, and only there.
"""

from __future__ import annotations

import streamlit as st
from supabase import Client, ClientOptions, create_client

from utils.config import load_settings

_CLIENT_KEY = "_supabase_client"


def get_client() -> Client:
    """Returns this browser session's Supabase client, creating it on first use."""
    if _CLIENT_KEY not in st.session_state:
        settings = load_settings()
        st.session_state[_CLIENT_KEY] = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
            # Keep the login only in this object's memory: never written to disk or cookies,
            # and refreshed by us (services/auth.py) instead of a background timer.
            options=ClientOptions(persist_session=False, auto_refresh_token=False),
        )
    return st.session_state[_CLIENT_KEY]


def reset_client() -> None:
    """Throws away this session's client, and the login inside it (used by sign-out)."""
    st.session_state.pop(_CLIENT_KEY, None)
