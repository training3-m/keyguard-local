"""Tests for the live community total on the banner (services/community.py, migration 0009)."""

import pytest

from services.community import community_total_cents


@pytest.fixture(autouse=True)
def _fresh_cache():
    community_total_cents.clear()
    yield
    community_total_cents.clear()


def test_total_comes_from_the_database_function(fake_client):
    fake_client.rpc_results["community_total_cents"] = 1650
    assert community_total_cents() == 1650
    assert ("rpc", "community_total_cents", {}) in fake_client.calls


def test_banner_survives_a_database_error(fake_client):
    fake_client.rpc_results["community_total_cents"] = RuntimeError("database down")
    assert community_total_cents() is None
