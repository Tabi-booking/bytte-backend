"""Tests for Supabase public URL normalization."""

from Application.storage_config import StorageSettings
from Application.storage_urls import build_public_url, normalize_media_url


def _settings() -> StorageSettings:
    return StorageSettings(
        supabase_url="https://bakkcbqdcuktgmzztxcr.supabase.co",
        service_role_key="key",
        bucket="restaurant-documents",
        public_url_base=(
            "https://bakkcbqdcuktgmzztxcr.supabase.co"
            "/storage/v1/object/public/restaurant-documents"
        ),
    )


def test_build_public_url_from_storage_key() -> None:
    url = build_public_url(
        _settings(),
        "restaurants/24/logo/d5e86fe3_Group_11.png",
    )
    assert url.endswith("/restaurant-documents/restaurants/24/logo/d5e86fe3_Group_11.png")


def test_normalize_legacy_host_url() -> None:
    raw = "https://bakkcbqdcuktgmzztxcr.supabase.co/restaurants/24/logo/d5e86fe3_Group_11.png"
    url = normalize_media_url(raw, settings=_settings())
    assert "/object/public/restaurant-documents/restaurants/24/logo/" in url


def test_normalize_wrong_public_bucket() -> None:
    raw = (
        "https://bakkcbqdcuktgmzztxcr.supabase.co"
        "/storage/v1/object/public/restaurants/24/logo/d5e86fe3_Group_11.png"
    )
    url = normalize_media_url(raw, settings=_settings())
    assert "/object/public/restaurant-documents/restaurants/24/logo/" in url


def test_normalize_prefers_storage_key() -> None:
    raw = "https://example.invalid/wrong"
    url = normalize_media_url(
        raw,
        storage_key="restaurants/24/cover/file.png",
        settings=_settings(),
    )
    assert url.endswith("/restaurant-documents/restaurants/24/cover/file.png")
