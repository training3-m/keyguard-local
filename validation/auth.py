"""Checks for the register and sign-in forms (NFR-AUTH-02, NFR-SEC-03).

These run in the browser session for quick, friendly feedback. Supabase checks again on its side,
so a skipped check here can never let a weak password through.
"""

from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN = 8
PASSWORD_MAX = 72  # the most Supabase (bcrypt) uses


def password_checklist(password: str) -> dict[str, bool]:
    """Each password rule and whether it is met, for the live checklist on the register page."""
    return {
        f"{PASSWORD_MIN}+ characters": len(password) >= PASSWORD_MIN,
        "A letter": any(ch.isalpha() for ch in password),
        "A number": any(ch.isdigit() for ch in password),
    }


def password_error(password: str) -> str | None:
    """A message if the password breaks a rule, otherwise None."""
    if len(password) > PASSWORD_MAX:
        return f"Password must be {PASSWORD_MAX} characters or fewer."
    unmet = [rule for rule, ok in password_checklist(password).items() if not ok]
    if unmet:
        return "Password needs: " + ", ".join(rule.lower() for rule in unmet) + "."
    return None


def email_error(email: str) -> str | None:
    """A message if the email doesn't look like an email address, otherwise None."""
    if not EMAIL_PATTERN.match(email.strip()):
        return "Enter a valid email address, for example sam@example.com."
    return None


def full_name_error(full_name: str) -> str | None:
    """A message if the name is too short or too long (2 to 80 characters), otherwise None."""
    if not 2 <= len(full_name.strip()) <= 80:
        return "Full name must be 2 to 80 characters."
    return None
