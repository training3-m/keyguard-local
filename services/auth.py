"""Register, sign in, sign out and "who is signed in?" (US-AUTH-01, US-AUTH-02, US-AUTH-03, NFR-AUTH, NFR-SES).

Rules this file follows:
- Passwords go straight to Supabase, which stores them hashed. They are never logged or kept.
- Error messages never reveal whether an email has an account (NFR-AUTH-03).
- 5 wrong passwords lock the sign-in form for 5 minutes in this browser session (NFR-AUTH-05).
  Supabase's own rate limits still apply on the server.
- The login (tokens) lives only in this session's Supabase client (NFR-SES-01).
- After 30 minutes without activity the user is signed out (NFR-SES-04). The cart is kept.
"""

from __future__ import annotations

import logging
import time

import streamlit as st
from supabase_auth.errors import AuthApiError, AuthError as SupabaseAuthError

from models.user import UserProfile
from services.supabase_client import get_client, reset_client
from validation.auth import email_error, full_name_error, password_error

logger = logging.getLogger(__name__)  # events only: never emails, names, passwords or tokens

MAX_FAILED_SIGN_INS = 5
LOCKOUT_SECONDS = 5 * 60
IDLE_TIMEOUT_SECONDS = 30 * 60
SIGN_IN_ERROR = "Email or password is incorrect."
REGISTER_ERROR = "We couldn't create an account with these details. If you already have one, sign in instead."

# Session State keys used by this file (prefixed so pages can't clash with them)
_USER = "auth_user"
_LAST_ACTIVE = "auth_last_active"
_FAILED = "auth_failed_attempts"
_LOCKED_UNTIL = "auth_locked_until"
_SIGNED_OUT_REASON = "auth_signed_out_reason"


class AuthError(Exception):
    """A sign-in or register problem. The message is written for the user and safe to show."""


# --------------------------------------------------------------------------- lockout

def lockout_seconds_left() -> int:
    """How many seconds until the sign-in form unlocks; 0 if it isn't locked."""
    return max(0, int(st.session_state.get(_LOCKED_UNTIL, 0) - time.time()))


def _record_failed_sign_in() -> None:
    failed = st.session_state.get(_FAILED, 0) + 1
    st.session_state[_FAILED] = failed
    if failed >= MAX_FAILED_SIGN_INS:
        st.session_state[_LOCKED_UNTIL] = time.time() + LOCKOUT_SECONDS
        st.session_state[_FAILED] = 0
        logger.info("sign-in locked after %s failed attempts", MAX_FAILED_SIGN_INS)


# --------------------------------------------------------------------------- helpers

def _load_profile(user_id: str, email: str) -> UserProfile:
    """Reads the user's name and role. Security rules only let them read their own profile."""
    result = (
        get_client().table("profiles").select("full_name, role").eq("id", user_id).single().execute()
    )
    data = result.data
    if not isinstance(data, dict):
        raise AuthError("Your account profile is missing. Please contact the store owner.")
    full_name = data.get("full_name")
    role = data.get("role")
    return UserProfile(id=user_id, email=email,
                       full_name=full_name if isinstance(full_name, str) else None,
                       role=role if isinstance(role, str) else "customer")


def _start_session(user_id: str, email: str) -> UserProfile:
    profile = _load_profile(user_id, email)
    st.session_state[_USER] = profile
    st.session_state[_LAST_ACTIVE] = time.time()
    st.session_state.pop(_SIGNED_OUT_REASON, None)
    return profile


def _refresh_login_if_needed() -> None:
    """Swaps an almost-expired login token for a fresh one (NFR-SES-05)."""
    client = get_client()
    session = client.auth.get_session()
    if session is None:
        raise SupabaseAuthError("no session", None)
    if session.expires_at and session.expires_at - time.time() < 60:
        client.auth.refresh_session()


# --------------------------------------------------------------------------- public API

def sign_in(email: str, password: str) -> UserProfile:
    """Signs in with email and password. Raises AuthError with a user-friendly message."""
    if lockout_seconds_left():
        raise AuthError("Too many wrong attempts. Please wait before trying again.")
    if email_error(email) or not password:
        raise AuthError(SIGN_IN_ERROR)

    try:
        response = get_client().auth.sign_in_with_password(
            {"email": email.strip().lower(), "password": password}
        )
    except AuthApiError:
        _record_failed_sign_in()
        logger.info("sign-in failed")
        raise AuthError(SIGN_IN_ERROR) from None

    if response.user is None:
        raise AuthError(SIGN_IN_ERROR)
    st.session_state[_FAILED] = 0
    logger.info("sign-in succeeded")
    return _start_session(response.user.id, response.user.email or email.strip().lower())


def register(full_name: str, email: str, password: str) -> UserProfile:
    """Creates a customer account and signs it in. Raises AuthError with a user-friendly message.

    The role is always 'customer': the database sets it, whatever the form sends (NFR-ROLE-04).
    """
    for problem in (full_name_error(full_name), email_error(email), password_error(password)):
        if problem:
            raise AuthError(problem)

    try:
        response = get_client().auth.sign_up({
            "email": email.strip().lower(),
            "password": password,
            "options": {"data": {"full_name": full_name.strip()}},
        })
    except AuthApiError as error:
        logger.info("register failed (%s)", getattr(error, "code", "unknown"))
        if getattr(error, "code", None) == "weak_password":
            raise AuthError("That password is too weak. Try a longer one with letters and numbers.") from None
        raise AuthError(REGISTER_ERROR) from None

    if response.session is None or response.user is None:
        # Happens if "Confirm email" is still on in Supabase (it must be off, NFR-AUTH-04).
        logger.warning("register returned no session: is email confirmation turned off?")
        raise AuthError(REGISTER_ERROR)

    logger.info("register succeeded")
    return _start_session(response.user.id, response.user.email or email.strip().lower())


def sign_out(reason: str | None = None) -> None:
    """Signs out: ends the Supabase login and forgets the user. The cart is kept (US-AUTH-03)."""
    if _USER in st.session_state:
        try:
            get_client().auth.sign_out()
        except SupabaseAuthError:
            pass  # the login was already gone; forgetting it locally is enough
    st.session_state.pop(_USER, None)
    st.session_state.pop(_LAST_ACTIVE, None)
    reset_client()
    if reason:
        st.session_state[_SIGNED_OUT_REASON] = reason
    logger.info("signed out")


def current_user() -> UserProfile | None:
    """The signed-in user, or None. Also handles the idle timeout and token refresh."""
    user: UserProfile | None = st.session_state.get(_USER)
    if user is None:
        return None

    if time.time() - st.session_state.get(_LAST_ACTIVE, 0) > IDLE_TIMEOUT_SECONDS:
        sign_out(reason="You were signed out after 30 minutes without activity, for safety.")
        return None

    try:
        _refresh_login_if_needed()
    except SupabaseAuthError:
        sign_out(reason="Your session ended. Please sign in again.")
        return None

    st.session_state[_LAST_ACTIVE] = time.time()
    return user


def pop_signed_out_reason() -> str | None:
    """Why the user was signed out automatically (shown once on the sign-in page), if anything."""
    return st.session_state.pop(_SIGNED_OUT_REASON, None)


def change_password(current_password: str, new_password: str) -> None:
    """Changes the signed-in user's password after checking the current one.

    Stub for story US-AUTH-04 (pick code U1-07). Keep this name and these parameters.
    """
    raise NotImplementedError("US-AUTH-04: change password (U1-07)")
