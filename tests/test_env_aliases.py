"""Tests de alias de variables de entorno."""

from Application.cors_origins import cors_allow_credentials, cors_origins
from Application.env_aliases import env_first
from Application.storage_config import load_storage_settings


def test_env_first_prefers_first_set(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "a")
    monkeypatch.setenv("SECRET_KEY", "b")
    assert env_first("JWT_SECRET", "SECRET_KEY") == "a"


def test_env_first_falls_back(monkeypatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("SECRET_KEY", "from-secret-key")
    assert env_first("JWT_SECRET", "SECRET_KEY") == "from-secret-key"


def test_cors_origins_wildcard(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "*")
    monkeypatch.delenv("FRONT_URL", raising=False)
    monkeypatch.delenv("VERCEL_URL", raising=False)
    monkeypatch.delenv("VERCEL_BRANCH_URL", raising=False)
    assert cors_origins() == ["*"]
    assert cors_allow_credentials() is False


def test_cors_origins_cors_origins_env(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com")
    monkeypatch.delenv("FRONT_URL", raising=False)
    monkeypatch.delenv("VERCEL_URL", raising=False)
    monkeypatch.delenv("VERCEL_BRANCH_URL", raising=False)
    assert cors_origins() == ["https://app.example.com"]
    assert cors_allow_credentials() is True


def test_storage_service_key_alias(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "service-key")
    monkeypatch.setenv("STORAGE_BUCKET", "restaurant-documents")
    settings = load_storage_settings()
    assert settings.service_role_key == "service-key"
    assert settings.public_url_base.endswith("/object/public/restaurant-documents")


def test_storage_url_alias(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "k")
    monkeypatch.setenv("STORAGE_URL", "https://x.supabase.co/storage/v1")
    monkeypatch.setenv("STORAGE_BUCKET", "restaurant-documents")
    settings = load_storage_settings()
    assert (
        settings.public_url_base
        == "https://x.supabase.co/storage/v1/object/public/restaurant-documents"
    )
