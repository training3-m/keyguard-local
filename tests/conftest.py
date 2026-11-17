"""Shared test helpers: a fake Supabase client with sample data, and fake settings / users.

Tests never touch the real database: they run offline, in CI, and in under a few seconds.
Use the fixtures in any test file by naming them as parameters, for example:

    def test_something(fake_client):
        fake_client.tables["products"]  # the sample rows
        ...

Fixtures:
    fake_client  - replaces get_client() everywhere with FakeClient (sample products, profiles, orders)
    fake_settings - pretends SUPABASE_URL / SUPABASE_ANON_KEY are set (no secrets file needed)
    as_user      - call as_user("owner") / as_user("customer") / as_user(None) to pick who is signed in
"""

from __future__ import annotations

import copy
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from supabase_auth.errors import AuthApiError

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"

# --------------------------------------------------------------------------- sample data
# A few rows from supabase/seed, enough for tests. Money in cents.

SAMPLE_PRODUCTS: list[dict[str, Any]] = [
    {"id": 1, "sku": "KG-ESS-16", "name": "KeyGuard Essentials 16 GB", "category": "Essentials",
     "capacity_gb": 16, "color": "Slate Grey", "description": "A great first secure drive.", "specs": {},
     "price_cents": 4900, "community_gift_cents": 200, "stock_qty": 40, "image_url": None,
     "is_active": True, "featured_rank": 50},
    {"id": 3, "sku": "KG-PRO-64", "name": "KeyGuard Pro 64 GB", "category": "Pro", "capacity_gb": 64,
     "color": "Midnight Black", "description": "For client files.", "specs": {"read_only_mode": "yes"},
     "price_cents": 7900, "community_gift_cents": 300, "stock_qty": 25, "image_url": None,
     "is_active": True, "featured_rank": 10},
    {"id": 5, "sku": "KG-PRO-256", "name": "KeyGuard Pro 256 GB RGB Edition", "category": "Pro",
     "capacity_gb": 256, "color": "Midnight Black with RGB keypad glow", "description": "Biggest drive.",
     "specs": {"lighting": "RGB keypad glow (slow fade, no flashing)"}, "price_cents": 13900,
     "community_gift_cents": 500, "stock_qty": 3, "image_url": None, "is_active": True, "featured_rank": 30},
    {"id": 6, "sku": "KG-RCE-32", "name": "Rancho Community Edition 32 GB", "category": "Community",
     "capacity_gb": 32, "color": "River Blue (skyline engraving)", "description": "Supports the library.",
     "specs": {}, "price_cents": 6500, "community_gift_cents": 1000, "stock_qty": 30, "image_url": None,
     "is_active": True, "featured_rank": 20},
    {"id": 9, "sku": "KG-ACC-LAN", "name": "KeyGuard Lanyard & Cap Set", "category": "Accessories",
     "capacity_gb": None, "color": "Mixed", "description": "A lanyard and spare caps.", "specs": {},
     "price_cents": 900, "community_gift_cents": 50, "stock_qty": 60, "image_url": None,
     "is_active": True, "featured_rank": 80},
    {"id": 11, "sku": "KG-ESS-8", "name": "KeyGuard Essentials 8 GB", "category": "Essentials",
     "capacity_gb": 8, "color": "Slate Grey", "description": "Discontinued.", "specs": {},
     "price_cents": 3900, "community_gift_cents": 100, "stock_qty": 0, "image_url": None,
     "is_active": False, "featured_rank": 999},
]

DEMO_USERS = {  # email: (user id, password, full name, role). Fake passwords, tests only.
    "owner@example.com": ("00000000-0000-0000-0000-000000000001", "owner-pass-1", "Demo Owner", "owner"),
    "staff@example.com": ("00000000-0000-0000-0000-000000000002", "staff-pass-1", "Demo Staff", "staff"),
    "customer@example.com": ("00000000-0000-0000-0000-000000000003", "customer-pass-1", "Demo Customer",
                             "customer"),
}

SAMPLE_ORDERS: list[dict[str, Any]] = [
    {"id": 1, "order_number": "KG-20261102-0001", "customer_id": DEMO_USERS["customer@example.com"][0],
     "customer_name": "Demo Customer", "customer_email": "customer@example.com", "status": "Shipped",
     "subtotal_cents": 7900, "shipping_cents": 0, "tax_cents": 632, "total_cents": 8532,
     "community_gift_cents": 300, "created_at": "2026-11-02T00:00:00+00:00", "email_file": None,
     "order_items": [{"sku": "KG-PRO-64", "product_name": "KeyGuard Pro 64 GB", "unit_price_cents": 7900,
                      "qty": 1, "line_total_cents": 7900, "community_gift_cents": 300}]},
]

# --------------------------------------------------------------------------- fake client


@dataclass
class FakeResponse:
    data: Any
    count: int | None = None


class FakeQuery:
    """Supports the common supabase-py chain: select / eq / neq / ilike / in_ / order / limit / single."""

    def __init__(self, client: FakeClient, table: str):
        self.client, self.table = client, table
        self.rows = [copy.deepcopy(r) for r in client.tables.get(table, [])]
        self._single = False
        self._write: tuple[str, Any] | None = None

    # reads
    def select(self, *_columns: str, **_kwargs: Any) -> FakeQuery:
        return self

    def eq(self, column: str, value: Any) -> FakeQuery:
        self.rows = [r for r in self.rows if r.get(column) == value]
        return self

    def neq(self, column: str, value: Any) -> FakeQuery:
        self.rows = [r for r in self.rows if r.get(column) != value]
        return self

    def ilike(self, column: str, pattern: str) -> FakeQuery:
        needle = pattern.strip("%").lower()
        self.rows = [r for r in self.rows if needle in str(r.get(column) or "").lower()]
        return self

    def in_(self, column: str, values: list[Any]) -> FakeQuery:
        self.rows = [r for r in self.rows if r.get(column) in values]
        return self

    def order(self, column: str, *, desc: bool = False, **_kwargs: Any) -> FakeQuery:
        self.rows.sort(key=lambda r: (r.get(column) is None, r.get(column)), reverse=desc)
        return self

    def limit(self, n: int) -> FakeQuery:
        self.rows = self.rows[:n]
        return self

    def single(self) -> FakeQuery:
        self._single = True
        return self

    def maybe_single(self) -> FakeQuery:
        return self.single()

    # writes are recorded, not applied: check them with fake_client.calls
    def insert(self, data: Any) -> FakeQuery:
        self._write = ("insert", data)
        return self

    def update(self, data: Any) -> FakeQuery:
        self._write = ("update", data)
        return self

    def delete(self) -> FakeQuery:
        self._write = ("delete", None)
        return self

    def execute(self) -> FakeResponse:
        if self._write:
            self.client.calls.append((self.table, *self._write))
        if self._single:
            return FakeResponse(self.rows[0] if self.rows else None)
        if not isinstance(self.rows, list):  # an RPC that returns one value, for example a number
            return FakeResponse(self.rows)
        return FakeResponse(self.rows, count=len(self.rows))


@dataclass
class FakeSession:
    access_token: str = "fake-access-token"
    refresh_token: str = "fake-refresh-token"
    expires_at: int = field(default_factory=lambda: int(time.time()) + 3600)


@dataclass
class FakeAuthUser:
    id: str
    email: str


@dataclass
class FakeAuthResponse:
    user: FakeAuthUser | None
    session: FakeSession | None


class FakeAuth:
    """Sign-in against DEMO_USERS. Wrong passwords raise AuthApiError, like Supabase."""

    def __init__(self, client: FakeClient):
        self.client = client
        self.session: FakeSession | None = None

    def sign_in_with_password(self, credentials: dict[str, str]) -> FakeAuthResponse:
        user = DEMO_USERS.get(credentials["email"])
        if user is None or user[1] != credentials["password"]:
            raise AuthApiError("Invalid login credentials", 400, "invalid_credentials")
        self.session = FakeSession()
        return FakeAuthResponse(FakeAuthUser(user[0], credentials["email"]), self.session)

    def sign_up(self, credentials: dict[str, Any]) -> FakeAuthResponse:
        email = credentials["email"]
        if email in DEMO_USERS:
            raise AuthApiError("User already registered", 422, "user_already_exists")
        user_id = f"00000000-0000-0000-0000-{len(self.client.tables['profiles']) + 100:012d}"
        full_name = credentials.get("options", {}).get("data", {}).get("full_name")
        self.client.tables["profiles"].append({"id": user_id, "full_name": full_name, "role": "customer"})
        self.session = FakeSession()
        return FakeAuthResponse(FakeAuthUser(user_id, email), self.session)

    def sign_out(self, *_args: Any) -> None:
        self.session = None

    def get_session(self) -> FakeSession | None:
        return self.session

    def refresh_session(self, *_args: Any) -> FakeAuthResponse:
        self.session = FakeSession()
        return FakeAuthResponse(None, self.session)


class FakeClient:
    """Stands in for supabase.Client. `tables` holds sample rows; `calls` records writes and RPCs."""

    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {
            "products": copy.deepcopy(SAMPLE_PRODUCTS),
            "profiles": [{"id": uid, "full_name": name, "role": role}
                         for uid, _pw, name, role in DEMO_USERS.values()],
            "orders": copy.deepcopy(SAMPLE_ORDERS),
        }
        self.calls: list[tuple[Any, ...]] = []
        self.rpc_results: dict[str, Any] = {}  # set fake_client.rpc_results["place_order"] = {...}
        self.auth = FakeAuth(self)

    def table(self, name: str) -> FakeQuery:
        return FakeQuery(self, name)

    def from_(self, name: str) -> FakeQuery:
        return self.table(name)

    def rpc(self, name: str, params: dict[str, Any] | None = None) -> FakeQuery:
        self.calls.append(("rpc", name, params or {}))
        result = self.rpc_results.get(name)
        if isinstance(result, Exception):
            raise result
        query = FakeQuery(self, "__rpc__")
        query.rows = result  # type: ignore[assignment]
        query._single = False
        return query


# --------------------------------------------------------------------------- fixtures


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> FakeClient:
    """Replaces get_client() in services/ with one FakeClient for the whole test."""
    client = FakeClient()
    import services.supabase_client as supabase_client

    monkeypatch.setattr(supabase_client, "get_client", lambda: client)
    for name, module in list(sys.modules.items()):
        if name.startswith("services.") and hasattr(module, "get_client"):
            monkeypatch.setattr(module, "get_client", lambda: client)
    monkeypatch.setattr(supabase_client, "reset_client", lambda: None)
    import services.auth as auth

    monkeypatch.setattr(auth, "reset_client", lambda: None)
    return client


@pytest.fixture
def fake_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pretends the Supabase settings exist, so pages run without a secrets file (for example in CI)."""
    from utils import config

    monkeypatch.setattr(config, "load_settings",
                        lambda: config.Settings("https://demo.supabase.co", "sb_publishable_test"))


@pytest.fixture
def as_user(monkeypatch: pytest.MonkeyPatch):
    """Returns a function that picks who is signed in for AppTest page tests: "owner", "staff",
    "customer", or None for a guest."""
    import services.auth as auth
    import utils.guards as guards
    from models.user import UserProfile

    def _set(role: str | None) -> UserProfile | None:
        user = None
        if role:
            email = f"{role}@example.com"
            user_id, _pw, name, user_role = DEMO_USERS[email]
            user = UserProfile(id=user_id, email=email, full_name=name, role=user_role)
        monkeypatch.setattr(auth, "current_user", lambda: user)
        monkeypatch.setattr(guards, "current_user", lambda: user)
        return user

    return _set


@pytest.fixture(autouse=True)
def _clean_session_state():
    """Each test starts with empty Session State (cart, login, lockout)."""
    import streamlit as st

    for key in list(st.session_state.keys()):
        del st.session_state[key]
    yield
