"""Reading products for the shop (public). Owner: User 1.

Pages never call Supabase directly: they call these functions (CLAUDE.md, layers).
Guests may read active products only; the database security rules enforce that (0005).
Keep every name and parameter; fill in the bodies in the stories listed.
"""

from __future__ import annotations

from typing import Literal

from models.product import Product

SortOption = Literal["featured", "price_asc", "price_desc", "capacity", "newest"]
CATEGORIES = ("Essentials", "Pro", "Community", "Bulk", "Accessories")


def search_products(
    term: str = "",
    category: str | None = None,
    capacity_gb: int | None = None,
    price_range: tuple[int, int] | None = None,  # (min_cents, max_cents)
    in_stock_only: bool = False,
    sort: SortOption = "featured",
) -> list[Product]:
    """Active products matching the search and filters (case-insensitive name/SKU/category/description).

    Stories: US-SRCH-01 (term, U1-01), US-SRCH-02 (filters, U1-02), US-SRCH-03 (sort, U1-06).
    """
    raise NotImplementedError("US-SRCH-01: search_products (U1-01)")


def get_product(sku: str) -> Product | None:
    """One ACTIVE product by SKU, or None if it doesn't exist or is hidden (US-PDP-01 AC2, U1-03)."""
    raise NotImplementedError("US-PDP-01: get_product (U1-03)")


def related(sku: str, limit: int = 3) -> list[Product]:
    """Up to `limit` other active products from the same category (US-PDP-02, U1-08)."""
    raise NotImplementedError("US-PDP-02: related (U1-08)")
