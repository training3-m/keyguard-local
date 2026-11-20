"""Checks for the checkout form (US-CHK-02 AC1, AC3). Owner: User 2.

These give quick, friendly messages under each field. The database function place_order (0007)
checks the same rules again, so a skipped check here can never save a bad order.
"""

from __future__ import annotations

import re

from validation.auth import full_name_error

ZIP_PATTERN = re.compile(r"^[0-9]{5}$")
ADDRESS_MAX = 120
CITY_MAX = 60


def address_error(address: str) -> str | None:
    """A message if the street address is empty or too long, otherwise None."""
    text = address.strip()
    if not text:
        return "Enter your street address."
    if len(text) > ADDRESS_MAX:
        return f"Address must be {ADDRESS_MAX} characters or fewer."
    return None


def city_error(city: str) -> str | None:
    """A message if the city is empty or too long, otherwise None."""
    text = city.strip()
    if not text:
        return "Enter your city."
    if len(text) > CITY_MAX:
        return f"City must be {CITY_MAX} characters or fewer."
    return None


def zip_error(zip_code: str) -> str | None:
    """A message unless the ZIP is exactly 5 digits, otherwise None."""
    if not ZIP_PATTERN.match(zip_code.strip()):
        return "ZIP code must be exactly 5 digits, for example 91730."
    return None


def checkout_errors(shipping: dict[str, str], demo_confirmed: bool) -> dict[str, str]:
    """Every problem with the form, as {field: message}. An empty dict means it can be sent."""
    checks = {
        "full_name": full_name_error(shipping.get("full_name", "")),
        "address": address_error(shipping.get("address", "")),
        "city": city_error(shipping.get("city", "")),
        "zip": zip_error(shipping.get("zip", "")),
        "demo": None if demo_confirmed else "Tick the box to confirm you understand this is a demo.",
    }
    return {field: message for field, message in checks.items() if message}
