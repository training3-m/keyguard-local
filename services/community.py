"""The live community total for the banner on every page (02-ui-ux.md §4.1, Q5). Owner: Tech Lead.

Calls public.community_total_cents (0009). The number is the same for everyone (not personal data),
so it is cached for 60 seconds instead of asking the database on every click.
"""

from __future__ import annotations

import logging

import streamlit as st

from services import supabase_client

logger = logging.getLogger(__name__)


@st.cache_data(ttl=60, show_spinner=False)
def community_total_cents() -> int | None:
    """Total given to the Rancho Library fund, in cents, or None if it can't be read right now."""
    try:
        result = supabase_client.get_client().rpc("community_total_cents").execute()
    except Exception:  # the banner must never break a page; details stay in the log (NFR-SEC-08)
        logger.warning("community total unavailable")
        return None
    data = result.data  # the function returns a single number
    if isinstance(data, (int, float)):
        return int(data)
    if isinstance(data, str) and data.isdigit():
        return int(data)
    return None
