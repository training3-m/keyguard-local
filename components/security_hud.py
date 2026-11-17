"""The game-style Security HUD and the red/green lock light (02-ui-ux.md §2.3, UX-04)."""

from __future__ import annotations

import streamlit as st

from models.product import Product

# Each bar: label, how full (0-1), what it means. Demo marketing copy, not certified claims (03 §15 A4).
_HUD_STATS = [
    ("Encryption", 1.0, "AES-256 hardware"),
    ("Brute-force guard", 1.0, "Wipes after 10 wrong PINs"),
    ("Compatibility", 1.0, "Any OS, no software"),
    ("Auto-lock", 0.8, "On unplug or idle timer"),
]


def lock_indicator(locked: bool = True) -> None:
    """LED-style lock state that matches the real drive: red LOCKED or green UNLOCKED."""
    if locked:
        st.badge("LOCKED", color="red", icon=":material/lock:")
    else:
        st.badge("UNLOCKED", color="green", icon=":material/lock_open:")


def security_hud(product: Product | None = None, *, locked: bool = True) -> None:
    """The Security HUD panel with stat bars. Pass a product to add its lighting line if it has one."""
    with st.container(border=True, key="security_hud"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("**:material/shield: Security HUD**")
            lock_indicator(locked)
        for label, level, detail in _HUD_STATS:
            st.progress(level, text=f"**{label}** · {detail}")
        if product is not None and "lighting" in product.specs:
            st.caption(f":material/light_mode: {product.specs['lighting']}")
        st.caption("Fictional product: demo copy, not certified security claims.")
