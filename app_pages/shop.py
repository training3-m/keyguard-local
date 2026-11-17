"""Shop / catalog. Placeholder until the catalog stories (US-SRCH-01..04, User 1).

Foundation Prompt E replaces this with the full stub; User 1 builds the real page in U1-01.
"""

import streamlit as st

from services.auth import current_user

user = current_user()
if user:
    st.success(f"Signed in as {user.display_name} ({user.role}).", icon=":material/lock_open:")

st.info("Coming soon: the KeyGuard catalog (US-SRCH-01).", icon=":material/construction:")
