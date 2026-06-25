"""Tests de prioridad de conexión BD (Vercel vs local)."""

from Infraestructure.Database import _connection_mode, db_connection_profile


def test_vercel_prefers_database_url_over_db_host(monkeypatch) -> None:
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("DB_HOST", "db.ref.supabase.co")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres.ref:secret@aws-0-us-west-2.pooler.supabase.com:6543/postgres",
    )
    assert _connection_mode() == "database_url"
    profile = db_connection_profile()
    assert profile["mode"] == "database_url"
    assert profile["uses_session_pooler"] is True
    assert profile.get("ignored_env_db_host") == "db.ref.supabase.co"


def test_local_prefers_db_host(monkeypatch) -> None:
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("DB_HOST", "db.ref.supabase.co")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/postgres")
    assert _connection_mode() == "db_host"
    profile = db_connection_profile()
    assert profile["mode"] == "db_host"
