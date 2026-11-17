"""Register: creates a customer account and signs it in (US-AUTH-01, 02-ui-ux.md section 4.7)."""

import streamlit as st

from services.auth import AuthError, register
from validation.auth import PASSWORD_MAX, password_checklist

with st.container(border=True, width=480):
    st.subheader(":material/person_add: Create your account")

    full_name = st.text_input("Full name", max_chars=80, autocomplete="name", key="register_full_name")
    email = st.text_input("Email", placeholder="sam@example.com", autocomplete="email",
                          key="register_email")
    # live=True updates the checklist below while typing.
    password = st.text_input("Password", type="password", max_chars=PASSWORD_MAX,
                             autocomplete="new-password", live=True, key="register_password")

    with st.container(horizontal=True, gap="small"):
        for rule, met in password_checklist(password).items():
            st.badge(rule, color="green" if met else "gray",
                     icon=":material/check_circle:" if met else ":material/radio_button_unchecked:")

    confirm = st.text_input("Confirm password", type="password", max_chars=PASSWORD_MAX,
                            autocomplete="new-password", key="register_confirm")
    agreed = st.checkbox("I understand this is a demo store: no real orders, payments or emails",
                         key="register_agreed")

    if st.button("Create account", type="primary", icon=":material/person_add:", width="stretch",
                 key="register_submit"):
        if password != confirm:
            st.error("The two passwords don't match.", icon=":material/error:")
        elif not agreed:
            st.error("Please tick the demo store box first.", icon=":material/error:")
        else:
            try:
                register(full_name, email, password)
            except AuthError as error:
                st.error(str(error), icon=":material/error:")
            else:
                # Back to where they were (for example Checkout), otherwise the shop.
                st.session_state["redirect_to"] = st.session_state.pop("return_to", "app_pages/shop.py")
                st.rerun()

    st.page_link("app_pages/sign_in.py", label="Already have an account? Sign in", icon=":material/login:")
    st.caption(":material/info: Demo store: use an @example.com email and a made-up name.")
