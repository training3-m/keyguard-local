# Service Contracts

Every function the stories need, built by the Tech Lead in foundation **Prompt E** with its final name, parameters, type hints and docstring. A story **fills in the body** and keeps the signature. Changing a signature needs the Tech Lead **and** every caller to review (work division plan §8).

**Status:** ✅ working now · 🧩 stub (`raise NotImplementedError`) until its story is built.

## How a click travels (layers)

```
app_pages/<page>.py  ->  services/<file>.py  ->  Supabase table + security rule (supabase/migrations)
        UI only            all database calls        the real lock (RLS, 0005) and database functions (0007-0008)
components/ = reusable UI     utils/ = helpers with no database     models/ = data shapes
```

Pages never call Supabase directly. Shared UI lives in `components/`.

## Services (database calls)

| Function | File | Story · pick | Owner | Status |
|---|---|---|---|---|
| `register(full_name, email, password) -> UserProfile` | `services/auth.py` | US-AUTH-01 | Lead | ✅ |
| `sign_in(email, password) -> UserProfile` | `services/auth.py` | US-AUTH-02 | Lead | ✅ |
| `sign_out(reason=None) -> None` | `services/auth.py` | US-AUTH-03 | Lead | ✅ |
| `current_user() -> UserProfile \| None` | `services/auth.py` | NFR-SES | Lead | ✅ |
| `change_password(current_password, new_password) -> None` | `services/auth.py` | US-AUTH-04 · U1-07 | User 1 | 🧩 |
| `get_client() -> Client` | `services/supabase_client.py` | NFR-SES-02 | Lead | ✅ |
| `community_total_cents() -> int \| None` | `services/community.py` | 02 §4.1, Q5 | Lead | ✅ |
| `search_products(term, category, capacity_gb, price_range, in_stock_only, sort) -> list[Product]` | `services/products.py` | US-SRCH-01/02/03 · U1-01/02/06 | User 1 | ✅ term (U1-01) · 🧩 filters, sort |
| `get_product(sku) -> Product \| None` | `services/products.py` | US-PDP-01 · U1-03 | User 1 | 🧩 |
| `related(sku, limit=3) -> list[Product]` | `services/products.py` | US-PDP-02 · U1-08 | User 1 | 🧩 |
| `list_users(term="") -> list[UserProfile]` | `services/users.py` | US-MGT-10 · U1-05 | User 1 | 🧩 |
| `set_user_role(user_id, role) -> None` | `services/users.py` | US-MGT-10 · U1-05 | User 1 | 🧩 |
| `load_cart_lines(cart) -> list[CartLine]` | `services/cart_lines.py` | US-CART-02 · U2-01 | User 2 | 🧩 |
| `place_order(cart, shipping, idempotency_key) -> dict` | `services/orders.py` | US-CHK-02/03 · U2-03 | User 2 | 🧩 |
| `get_order(order_number) -> Order \| None` | `services/orders.py` | US-CHK-05 · U2-04 | User 2 | 🧩 |
| `record_email_file(order_number, path) -> None` | `services/orders.py` | US-CHK-04 · U2-05 | User 2 | 🧩 |
| `list_my_orders() -> list[Order]` | `services/orders.py` | US-CHK-06 · U2-08 | User 2 | 🧩 |
| `write_confirmation(order) -> Path` | `services/email_outbox.py` | US-CHK-04 · U2-05 | User 2 | 🧩 |
| `metrics(role) -> dict[str, int]` | `services/dashboard.py` | US-MGT-08 · U2-06 | User 2 | 🧩 |
| `low_stock(threshold=5) -> list[Product]` | `services/dashboard.py` | US-MGT-08 · U2-06 | User 2 | 🧩 |
| `recent_orders(limit=10) -> list[Order]` | `services/dashboard.py` | US-MGT-08 · U2-06 | User 2 | 🧩 |
| `list_all_products(term="", include_inactive=True) -> list[Product]` | `services/admin_products.py` | US-MGT-02 · U3-01 | User 3 | 🧩 |
| `set_active(sku, active) -> None` | `services/admin_products.py` | US-MGT-05 · U3-02 | User 3 | 🧩 |
| `create_product(data) -> Product` | `services/admin_products.py` | US-MGT-03 · U3-03 | User 3 | 🧩 |
| `update_products(changes) -> int` | `services/admin_products.py` | US-MGT-04 · U3-04 | User 3 | 🧩 |
| `delete_product(sku) -> None` | `services/admin_products.py` | US-MGT-06 · U3-06 | User 3 | 🧩 |
| `upload_image(file_name, data) -> str` | `services/storage.py` | US-MGT-07 · U3-05 | User 3 | 🧩 |
| `list_orders(status=None, date_from=None, date_to=None) -> list[Order]` | `services/admin_orders.py` | US-MGT-09 · U3-07 | User 3 | 🧩 |
| `set_status(order_number, status) -> None` | `services/admin_orders.py` | US-MGT-09 · U3-07 | User 3 | 🧩 |
| `cancel_order(order_number) -> None` | `services/admin_orders.py` | US-MGT-09 · U3-07 | User 3 | 🧩 |

**Database functions** (already built, Prompt C): `public.place_order`, `public.cancel_order`, `public.set_user_role`, `public.set_order_email_file`. Call them with `get_client().rpc("<name>", {...})`.

## Helpers (no database), all ✅ working and tested

| Function | File | Used by |
|---|---|---|
| `get_cart()`, `add(sku, qty=1, max_qty=10)`, `update(sku, qty, max_qty=10)`, `remove(sku)`, `clear()`, `count()` | `utils/cart.py` | US-CART-01/02/04, checkout |
| `calculate_totals(lines) -> Totals`, `tax_for(subtotal_cents)` | `utils/pricing.py` | US-CART-02/03, checkout |
| `money(cents) -> str` | `utils/formatting.py` | everywhere |
| `require_signed_in(message, *, return_to=None)`, `require_role(*roles)` | `utils/guards.py` | every protected page |
| `load_settings()`, `require_settings()` | `utils/config.py` | app start |
| `password_checklist`, `password_error`, `email_error`, `full_name_error` | `validation/auth.py` | register, sign in |

## Shared components (UI), all ✅ working and tested

| Function | File | Used by |
|---|---|---|
| `product_card(product)` | `components/product_card.py` | catalog grid, "You may also like" |
| `security_hud(product=None, *, locked=True)`, `lock_indicator(locked=True)` | `components/security_hud.py` | home, product detail |
| `stock_badge(stock_qty, *, is_active=True)`, `order_status_badge(status)`, `role_badge(role)`, `community_chip(gift_cents)`, `security_strip()` | `components/badges.py` | cards, tables, menu |
| `order_detail(order)` | `components/order_detail.py` | My orders (U2-08), Manage orders (U3-07). **Shared: change only with both users + Lead** |
| `coming_soon(story_id, what)`, `empty_state(message, ...)`, `error_state(message, *, key)`, `access_denied(title)`, `not_found(what)`, `store_unavailable()` | `components/states.py` | every page (02 §13 system states) |
| `app_header()`, `load_theme_css()` | `components/app_header.py` | `streamlit_app.py` only |

## Story-owned component stubs (called from Lead-owned pages)

| Function | File | Story · pick | Owner |
|---|---|---|---|
| `render_account_profile(user)` | `components/account_profile.py` | US-AUTH-04 · U1-07 | User 1 |
| `render_my_orders(user)` | `components/my_orders.py` | US-CHK-06 · U2-08 | User 2 |

Stories create their other own components: `components/filters.py` and `components/product_detail.py` (User 1), `components/cart_summary.py` (User 2), `components/product_form.py` (User 3).

## Plan check (Prompt E): stories without a page or a function

Checked all 31 stories in `01-product.md` against the code. **Every story now has a page (or is part of one) and the code it needs.** Notes:

| Story | Finding |
|---|---|
| US-CHK-03 | No page of its own, by design: it's the database function `place_order` (0007), called by the checkout form (US-CHK-02). |
| US-AUTH-03 | The Sign out button lives in the sidebar in `streamlit_app.py` (Lead), not on a page. |
| US-SRCH-04 | No service function needed: keep the filters in the URL with the widgets' `bind="query-params"` option. |
| US-AUTH-05 | **Gap found and fixed:** the sign-in page now says "Forgot your password? Contact the store owner." |
| US-CART-02 | **Gap found and fixed:** the cart needs current prices, so a new User 2 file `services/cart_lines.py` was added (instead of editing User 1's `services/products.py`). |
| Community banner (02 §4.1, open question Q5) | **Done (Tech Lead follow-up):** `public.community_total_cents()` (0009) returns only the total, so guests may call it; `services/community.py` caches it for 60 seconds; the header shows it, or a fixed message if unavailable. |
