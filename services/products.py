"""Reading products for the shop (public). Owner: User 1.

Pages never call Supabase directly: they call these functions (CLAUDE.md, layers).
Guests may read active products only; the database security rules enforce that (0005).
Keep every name and parameter; fill in the bodies in the stories listed.
"""

from __future__ import annotations

from typing import Any, Literal

import streamlit as st

from models.product import Product
from services import supabase_client

SortOption = Literal["featured", "price_asc", "price_desc", "capacity", "newest"]
CATEGORIES = ("Essentials", "Pro", "Community", "Bulk", "Accessories")


@st.cache_data(ttl=30, show_spinner=False)
def _active_product_rows() -> list[dict[str, Any]]:
    """Every ACTIVE product row, best-featured first. Cached for 30 seconds (NFR-PERF-01).

    Sharing this cache between visitors is safe because it only holds active products, which
    everyone may see. The explicit is_active filter matters: staff and owners are ALSO allowed
    to read hidden products (0005), and those must never end up in the shared shop list.
    Call _active_product_rows.clear() after a product edit or an order so stock is fresh.
    """
    result = (
        supabase_client.get_client()
        .table("products")
        .select("*")
        .eq("is_active", True)
        .order("featured_rank")
        .execute()
    )
    # Each row is a dict; anything else would be a broken response, so it is skipped.
    return [row for row in (result.data or []) if isinstance(row, dict)]


def _matches(product: Product, term: str) -> bool:
    """True if the search term is inside the name, SKU, category or description (any case)."""
    needle = term.strip().lower()
    if not needle:
        return True
    searchable = (product.name, product.sku, product.category, product.description or "")
    return any(needle in text.lower() for text in searchable)


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
    Database errors are not caught here: the page shows a friendly message instead.
    """
    # Filters and sorting come in later stories. Failing loudly beats silently ignoring them.
    if category or capacity_gb or price_range or in_stock_only:
        raise NotImplementedError("US-SRCH-02: filters (U1-02)")
    if sort != "featured":
        raise NotImplementedError("US-SRCH-03: sort (U1-06)")

    # The catalog is small (under 100 drives), so matching in Python is fast and simple. It also
    # means the shopper's text is never pasted into a database query.
    products = [Product.from_row(row) for row in _active_product_rows()]
    return [p for p in products if _matches(p, term)]


def get_product(sku: str) -> Product | None:
    """One ACTIVE product by SKU, or None if it doesn't exist or is hidden (US-PDP-01 AC2, U1-03).

    Uses the same cached active list as the search, so a hidden product can never be opened by
    typing its SKU into the address bar. SKUs are stored in capitals; "kg-pro-64" also works.
    """
    wanted = sku.strip().upper()
    for row in _active_product_rows():
        if row.get("sku") == wanted:
            return Product.from_row(row)
    return None


def related(sku: str, limit: int = 3) -> list[Product]:
    """Up to `limit` other active products from the same category (US-PDP-02, U1-08)."""
    raise NotImplementedError("US-PDP-02: related (U1-08)")
