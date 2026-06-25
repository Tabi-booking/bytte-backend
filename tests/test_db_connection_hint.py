"""Tests para mensajes de ayuda de conexión BD."""

from Application.db_connection_hint import hint_for_operational_error


def test_hint_ipv6_cannot_assign():
    exc = Exception(
        'connection to server at "db.bakkcbqdcuktgmzztxcr.supabase.co" '
        "(2600:1f14:271:c001:43b3:e154:463e:15fc), port 5432 failed: "
        "Cannot assign requested address"
    )
    hint = hint_for_operational_error(exc)
    assert hint is not None
    assert "6543" in hint
    assert "Session pooler" in hint


def test_hint_direct_5432():
    exc = Exception("connection to db.foo.supabase.co:5432 refused")
    hint = hint_for_operational_error(exc)
    assert hint is not None
    assert "6543" in hint


def test_hint_none_for_generic():
    assert hint_for_operational_error(Exception("password authentication failed")) is None
