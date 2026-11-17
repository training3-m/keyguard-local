"""Sign in: one page for customers, staff and the owner (US-AUTH-02, 02-ui-ux.md section 4.7)."""

import math

import streamlit as st

from services.auth import AuthError, lockout_seconds_left, pop_signed_out_reason, sign_in

reason = pop_signed_out_reason()
if reason:
    st.info(reason, icon=":material/schedule:")

with st.container(border=True, width=480):
    st.subheader(":material/lock: Access terminal")

    seconds_left = lockout_seconds_left()
    if seconds_left:
        minutes = math.ceil(seconds_left / 60)
        st.error(f"Too many wrong attempts. Try again in about {minutes} minute(s).",
                 title="Locked", icon=":material/lock_clock:")

    with st.form("sign_in_form"):
        email = st.text_input("Email", placeholder="sam@example.com", autocomplete="email",
                              key="sign_in_email")
        password = st.text_input("Password", type="password", autocomplete="current-password",
                                 key="sign_in_password")
        submitted = st.form_submit_button("Sign in", type="primary", icon=":material/login:",
                                          width="stretch", disabled=bool(seconds_left),
                                          key="sign_in_submit")

    if submitted:
        try:
            sign_in(email, password)
        except AuthError as error:
            st.error(str(error), icon=":material/error:")
        else:
            # Back to where the user came from (set by the checkout gate later), otherwise the shop.
            st.switch_page(st.session_state.pop("return_to", "app_pages/shop.py"))

    st.page_link("app_pages/register.py", label="New here? Create an account", icon=":material/person_add:")
    st.caption(":material/info: Demo store: use an @example.com email. No real orders, payments or emails.")
