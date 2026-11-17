"""The signed-in person, as the app sees them."""

from __future__ import annotations

from dataclasses import dataclass

ROLES = ("customer", "staff", "owner")


@dataclass(frozen=True)
class UserProfile:
    """A signed-in user: their account id, email, name and role (from public.profiles)."""

    id: str
    email: str
    full_name: str | None
    role: str

    @property
    def display_name(self) -> str:
        """The name to show in the menu: their name, or the part of the email before the @."""
        return self.full_name or self.email.split("@")[0]

    @property
    def is_staff_or_owner(self) -> bool:
        """True for people who may open the Manage pages."""
        return self.role in ("staff", "owner")

    @property
    def is_owner(self) -> bool:
        """True only for the store owner."""
        return self.role == "owner"
