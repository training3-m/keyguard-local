"""The header on every page: logo, tagline and the community banner (02-ui-ux.md §4.1)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from services.community import community_total_cents
from utils.formatting import money

_THEME_CSS = Path(__file__).resolve().parent.parent / "assets" / "styles" / "theme.css"


def load_theme_css() -> None:
    """Adds the glow / gradient / focus effects from assets/styles/theme.css (takes no space on the page)."""
    st.html(_THEME_CSS)


def app_header() -> None:
    """KEYGUARD LOCAL logo, tagline, and the live Rancho Library banner."""
    with st.container(key="app_header"):
        with st.container(horizontal=True, vertical_alignment="center", gap="medium"):
            st.markdown("### :material/lock: KEYGUARD :primary[LOCAL]")
            st.caption("Lock it. Carry it. Give back locally.")
        total = community_total_cents()
        if total:
            st.caption(f":material/volunteer_activism: **{money(total)}** raised for the Rancho Public "
                       "Library Digital Safety Fund (fictional, demo).")
        else:
            st.caption(":material/volunteer_activism: Every drive supports the Rancho Public Library "
                       "Digital Safety Fund (fictional, demo).")
