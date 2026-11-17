"""Managing the catalog (staff and owner). Owner: User 3.

The database decides who may do what (0005): staff can't change prices or gifts, only the owner can
create or delete, and nobody can change a SKU. Show the database's refusal as a friendly message.
Keep every name and parameter; fill in the bodies in the stories listed.
"""

from __future__ import annotations

from typing import Any

from models.product import Product


def list_all_products(term: str = "", include_inactive: bool = True) -> list[Product]:
    """All products, hidden ones included, filtered by name or SKU (US-MGT-02, U3-01)."""
    raise NotImplementedError("US-MGT-02: list_all_products (U3-01)")


def create_product(data: dict[str, Any]) -> Product:
    """Adds a product (owner only). `data` has the product fields; SKU must be unique (US-MGT-03, U3-03)."""
    raise NotImplementedError("US-MGT-03: create_product (U3-03)")


def update_products(changes: list[dict[str, Any]]) -> int:
    """Saves bulk edits from the table, each {"sku": ..., field: value}. Returns rows saved (US-MGT-04, U3-04)."""
    raise NotImplementedError("US-MGT-04: update_products (U3-04)")


def set_active(sku: str, active: bool) -> None:
    """Shows or hides a product in the shop (US-MGT-05, U3-02)."""
    raise NotImplementedError("US-MGT-05: set_active (U3-02)")


def delete_product(sku: str) -> None:
    """Deletes a product that was never ordered (owner only); otherwise explain to deactivate (US-MGT-06, U3-06)."""
    raise NotImplementedError("US-MGT-06: delete_product (U3-06)")
