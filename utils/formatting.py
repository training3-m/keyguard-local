"""Turning stored values into text for people."""


def money(cents: int) -> str:
    """Formats cents as dollars, for example 123456 -> "$1,234.56"."""
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) / 100:,.2f}"
